"""
Workflow manager for E2Clab
"""

from pathlib import Path
from typing import Any, Optional

import yaml
from enoslib import Host, Roles, run_play
from enoslib.api import Results
from enoslib.errors import EnosFailedHostsError, EnosUnreachableHostsError
from jinja2 import Template

import e2clab.constants.default as default
from e2clab.providers.plugins.Chameleonedge import E2CEdgeDevice

from .config import TaskConfig, WorkflowConfig, WorkflowEnvConfig
from .constants import WorkflowTasks
from .constants.workflow import SELF_PREFIX
from .errors import E2clabFileError, E2clabWorkflowError
from .grouping import get_grouping
from .log import get_logger
from .utils import get_hosts_from_pattern, load_yaml_file

ALL = "all"


class Workflow:
    """
    Workflow manager for E2Clab.
    Enforces ``workflow.yaml`` configuration file
    """

    def __init__(
        self,
        config: Path,
        experiment_dir: Path,
        scenario_dir: Path,
        artifacts_dir: Path,
        roles: Roles,
        all_serv_extra_inf: dict,
        app_conf: Optional[str] = None,
        env_config: Optional[Path] = None,
        optimization_config: Optional[dict[str, Any]] = None,
    ) -> None:
        """Create an application for the experiment

        Args:
            config (Path): Path to 'workflow.yaml' file
            experiment_dir (Path): Folder for experiment results
            scenario_dir (Path): Path to experiment definition
            artifacts_dir (Path): Path to experiment artifacts
            roles (Roles): EnOSlib.Roles associated with our experiment
            all_serv_extra_inf (dict): Extra information from deployed services
            app_conf (str, optional): Application configuration. Defaults to None.
            env_config (Path, optional): Path to 'workflow_env.yaml'. Defaults to None.
            optimization_config (dict[str, any], optional): Optimization configuration.
                Defaults to None.
        """
        self.logger = get_logger(__name__, ["WORKFLOW"])
        self.config = self._load_config(config)

        # Relevant directories
        self.experiment_dir = experiment_dir
        self.scenario_dir = scenario_dir
        self.artifacts_dir = artifacts_dir

        # Global Experiment infrastructure Roles
        self.roles = roles
        # Global Experiment services extra information
        self.all_serv_extra_inf = all_serv_extra_inf

        self.app_conf = app_conf
        self.optimization_config = optimization_config

        if not app_conf:
            self.output_dir = self.experiment_dir
        else:
            # If we are running a specific configuration, we output in another dir
            self.output_dir = self.experiment_dir / app_conf
            if env_config:
                self.workflow_env = self._load_env_config(env_config)
        self.workflow_validate_dir = self.output_dir / default.WORKFLOW_VALIDATE_FILE

        # Application directory i.e. where to output
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self, config_path: Path) -> WorkflowConfig:
        """Loads yaml 'workflow' file into a WorkflowConfig

        Args:
            config_path (Path): Path to the 'workflow.yaml' file

        Returns:
            WorkflowConfig: E2clab workflow config object
        """
        c = load_yaml_file(config_path)
        # Validated by schema
        assert isinstance(c, list)
        return WorkflowConfig(c)

    def _load_env_config(self, env_config_path: Path) -> WorkflowEnvConfig:
        try:
            c = load_yaml_file(env_config_path)
        except E2clabFileError:
            self.logger.warning(
                f"{env_config_path} does not exist, "
                "only adding 'app_conf' parameter to ansible env"
            )
            return WorkflowEnvConfig(dict())
        assert isinstance(c, dict)
        return WorkflowEnvConfig(c)

    def run_task(
        self,
        task: WorkflowTasks,
        current_repeat: Optional[int] = None,
    ) -> None:
        """Enfroce task from the workflow configuration

        Args:
            task (WorkflowTasks): PREPARE, RUN, FINALIZE
            current_repeat (Optional[int], optional): current optimization loop.
             Defaults to None.

        Raises:
            E2clabWorkflowError: If a host is unreachable or fails
        """
        # Prepare working directory for the current task
        if task != WorkflowTasks.FINALIZE:
            working_dir = self.artifacts_dir
        else:
            # Useful for backing up results
            working_dir = self.output_dir

        # Prepare extra variables for ansible commands
        ansible_vars = self._get_ansible_vars(current_repeat, working_dir)

        # Prepare task configuration
        task_config = self.config.get_task_filtered_workflow_config(task=task)

        self.logger.debug(f"[WORKING DIR] {working_dir}")
        self.logger.debug(f"[CURRENT REPEAT] {current_repeat}")
        self.logger.debug(f"[ANSIBLE VARS] {ansible_vars}")
        self.logger.debug(f"[TASK CONFIG] {task_config}")

        for task_conf in task_config.iter_tasks():
            selected_task_hosts = self._prepare_task_hosts(task_conf)

            if len(selected_task_hosts) == 0:
                self.logger.warning(
                    f"No hosts found for task {task.value} target: {task_conf.target}"
                )
                continue

            # Enforce on E2CEdgeDevice
            task_chameleon_edge_hosts: list[E2CEdgeDevice] = []
            for h in reversed(selected_task_hosts):
                if isinstance(h, E2CEdgeDevice):
                    task_chameleon_edge_hosts.append(h)
                    selected_task_hosts.remove(h)
            self.logger.debug(f"[CHAMELEON_EDGE_DEVICES]: {task_chameleon_edge_hosts}")
            for dev in task_chameleon_edge_hosts:
                self.logger.debug(f"Enforcing task on dev: {dev}")
                self._enforce_task_on_dev(dev, task_conf, ansible_vars)
            # Done enforcing on E2CEdgeDevice

            # Enforce task on other hosts
            # prepare run ansible play
            task_conf.target = ALL
            task_roles = Roles({ALL: selected_task_hosts})

            self.logger.debug("Printing hosts extra vars")
            for h in task_roles[ALL]:
                self.logger.debug(f"{h.alias} extra vars: {h.extra}")
            self.logger.debug(f"[TASK HOSTS] {task_roles}")

            try:
                ret = run_play(task_conf, roles=task_roles, extra_vars=ansible_vars)
            except EnosUnreachableHostsError as e:
                raise E2clabWorkflowError(e)
            except EnosFailedHostsError as e:
                raise E2clabWorkflowError(e)

            # Print results to logfile
            self._writes_workflow_validate(
                task, ansible_vars, task_conf, task_roles, ret
            )

    def _writes_workflow_validate(
        self,
        task: WorkflowTasks,
        ansible_vars: dict,
        task_conf: TaskConfig,
        task_roles: Roles,
        ret: Results,
    ):
        data: dict[str, Any] = {}
        data["ANSIBLE_PLAY"] = task_conf
        data["EXTRA_VARS"] = ansible_vars
        data["HOSTS"] = [h.alias for h in task_roles[ALL]]
        data["RETURN"] = [r.to_dict() for r in ret]
        with open(self.workflow_validate_dir, "a+") as f:
            f.write("---\n")
            yaml.dump({"TASK": task.value.upper()}, f)
            yaml.dump(data, f)

    def _prepare_task_hosts(self, task_conf: TaskConfig) -> list[Host]:
        """Prepares the hosts for the execution of the task:
        - Filters the hosts based on the desired targets
        - Applies grouping based on the "depends_on" configuration

        Args:
            task_conf (TaskConfig): filtered task configuration

        Returns:
            list[Host]: prepared list of hosts for the task
        """
        depends_on_conf_list = task_conf.pop_depends_on()
        self.logger.debug(f"[DEPENDS ON LIST] {depends_on_conf_list}")
        # prepare task hosts
        selected_task_hosts = self._get_hosts_from_pattern(self.roles, task_conf.target)
        if len(selected_task_hosts) == 0:
            return []

        # TODO: only allow "user" roles to be used in grouping
        # e.g. "edge.producer.1.1" and not "edge"
        for depends_on in depends_on_conf_list:
            depends_on_extra_info = [
                # Extra info was added to the host at the service deployment
                h.extra[SELF_PREFIX]
                for h in self._get_hosts_from_pattern(
                    self.roles, depends_on.service_selector
                )
            ]
            # TODO: check if we need to merge depends_host like in app ?
            # TODO: check that we are indeed copying the hosts
            selected_task_hosts = get_grouping(
                grouping=depends_on.grouping.value,
                prefix=depends_on.prefix,
                array_info=depends_on.array_info.value,
                hosts=selected_task_hosts,
                selected_service_extra_info=depends_on_extra_info,
            ).distribute()

            # Adding gateway into prefix ? Should be done already
        for h in selected_task_hosts:
            if "gateway" in h.extra:
                h.extra[SELF_PREFIX].update({"gateway": h.extra["gateway"]})
        return selected_task_hosts

    def _get_ansible_vars(
        self, current_repeat: Optional[int], working_dir: Path
    ) -> dict:
        """Prepares ansible extra variables for the current task

        Args:
            current_repeat (int): current optimization repeat
            working_dir (Path): current working dir

        Returns:
            dict: ansible extra variables
        """
        ansible_vars: dict[str, Any] = {
            "working_dir": str(working_dir),
            "scenario_dir": str(self.scenario_dir),
            "artifacts_dir": str(self.artifacts_dir),
        }
        if self.optimization_config:
            ansible_vars.update({"optimization_config": str(self.optimization_config)})
        if self.app_conf:
            # Feeding workflow environment into the ansible commands
            ansible_vars.update({"app_conf": self.app_conf})
            ansible_vars.update(self.workflow_env.get_env(self.app_conf, {}))
        if current_repeat:
            ansible_vars.update({"current_repeat": current_repeat})
        else:
            ansible_vars.update({"current_repeat": 1})
        return ansible_vars

    def _get_hosts_from_pattern(
        self, roles: Roles, pattern_selector: str
    ) -> list[Host]:
        return get_hosts_from_pattern(roles=roles, pattern=pattern_selector)

    # ChameleonDevice stuff

    def _enforce_task_on_dev(self, dev: E2CEdgeDevice, task: dict, ansible_vars: dict):
        if "copy" in task:
            dev.upload(
                self._build_dev_command_from_ansible(
                    task["copy"]["src"], ansible_vars, dev.extra
                ),
                self._build_dev_command_from_ansible(
                    task["copy"]["dest"], ansible_vars, dev.extra
                ),
            )
        elif "shell" in task:
            dev.execute(
                self._build_dev_command_from_ansible(
                    task["shell"], ansible_vars, dev.extra
                )
            )
        elif "fetch" in task:
            dev.download(
                self._build_dev_command_from_ansible(
                    task["fetch"]["src"], ansible_vars, dev.extra
                ),
                self._build_dev_command_from_ansible(
                    task["fetch"]["dest"], ansible_vars, dev.extra
                ),
            )
        else:
            self.logger.warning(f"Chameleon Device task: {task} is not in authorized ")

    def _build_dev_command_from_ansible(
        self,
        raw_command: str,
        extra_vars: dict,
        device_extra: dict,
    ) -> str:
        """Build a ChameleonDevice command from an ansible command

        Args:
            raw_command (str): Raw ansible command
            extra_vars (dict): Extra experiment variables e.g. 'working_dir'
            device_extra (dict): Extra device variables e.g. 'depends_on' variables

        Returns:
            str: Executable ChameleonDevice command
        """
        command = self._inject_vars(
            command=raw_command, extra_vars=extra_vars, device_extra=device_extra
        )

        self.logger.debug(f"[DEVICE ANSIBLE RAW COMMAND] {raw_command}")
        self.logger.debug(f"[DEVICE ANSIBLE COMMAND] {command}")

        return command

    @staticmethod
    def _inject_vars(command: str, extra_vars: dict, device_extra: dict) -> str:
        """Injects vars into the device command like ansible with jinja.
        e.g. replaces  Jija template expressions like {{ test }} with the value in
        `extra_vars={test: 123}`: 123

        Args:
            command (str): base command
            extra_vars (dict): extra vars
            device_extra (dict): device extra information

        Returns:
            str: base command with injected vars
        """
        cmd_template = Template(command)
        template_data = {}
        template_data.update(extra_vars)
        template_data.update(device_extra)
        rendered_cmd = cmd_template.render(template_data)
        return rendered_cmd
