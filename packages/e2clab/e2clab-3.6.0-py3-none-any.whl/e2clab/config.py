from copy import deepcopy
from dataclasses import dataclass
from typing import Iterator, Optional

import e2clab.constants.default as default
from e2clab.constants import (
    SUPPORTED_ENVIRONMENTS,
    WORKFLOW_TASKS,
    ArrayInfo,
    Environment,
    GroupingType,
    MonitoringType,
    WorkflowTasks,
)
from e2clab.constants.layers_services import (
    DEFAULT_SERVICE_NAME,
    DSTAT_DEFAULT_OPTS,
    DSTAT_OPTIONS,
    ENVIRONMENT,
    ID,
    LAYER_ID,
    LAYER_NAME,
    LAYERS,
    MONITORING_SVC,
    MONITORING_SVC_AGENT_CONF,
    MONITORING_SVC_TYPE,
    NAME,
    PROVENANCE_SVC,
    PROVENANCE_SVC_DATAFLOW_SPEC,
    PROVENANCE_SVC_PARALLELISM,
    REPEAT,
    SERVICE_ID,
    SERVICE_PLUGIN_NAME,
    SERVICES,
)
from e2clab.constants.network import DELAY, LOSS, NETWORKS, RATE
from e2clab.constants.workflow import (
    ANSIBLE_TASKS,
    ARRAY_INFO,
    DEPENDS_ON,
    GROUPING,
    PREFIX,
    SERV_SELECT,
    TARGET,
)
from e2clab.errors import E2clabConfigError
from e2clab.log import get_logger
from e2clab.managers import Managers
from e2clab.schemas import is_valid_conf
from e2clab.services import get_available_services


class E2clabConfig:
    pass


class InfrastructureConfig(dict, E2clabConfig):
    """
    Class to manage infrastructure configuration
    """

    def __init__(self, data: dict, refined: bool = False) -> None:
        """Infrastructure configuration

        Args:
            data (dict): Input data parsed from "layers_services.yaml"
            refined (bool, optional): For producer child classes,
                yielded from "refine_to_environment". Defaults to False.

        Raises:
            E2clabConfigError: Schema error in the input data
        """
        super().__init__(deepcopy(data))
        self.logger = get_logger(__name__, ["INF_CONF"])

        if not refined:
            if not is_valid_conf(self, "layers_services"):
                raise E2clabConfigError
            # pre-process configuration
            self._prepare()

    def _prepare(self):
        """
        Repeats services and generates services ids
        """
        self._repeat_services()
        self._generate_service_id()
        self._set_master_environment()

        self.logger.debug(f"[MASTER ENV]: {self.master_environment}")

    def is_provenance_def(self):
        return PROVENANCE_SVC in self.keys()

    def get_provenance_parallelism(self) -> int:
        # No parallelism defined defaults to 1
        parallelism = self[PROVENANCE_SVC].get(
            PROVENANCE_SVC_PARALLELISM, default.PARALLELISM
        )
        return parallelism

    def get_provenance_dataflow_spec(self):
        dataflow_spec = self[PROVENANCE_SVC].get(PROVENANCE_SVC_DATAFLOW_SPEC, "")
        return dataflow_spec

    def get_monitoring_agent_conf(self) -> Optional[str]:
        return self[MONITORING_SVC].get(MONITORING_SVC_AGENT_CONF, None)

    def is_manager_defined(self, manager: Managers) -> bool:
        return manager.value.get_config_key() in self.keys()

    def get_manager_conf(self, manager: Managers) -> Optional[dict]:
        return self.get(manager.value.get_config_key(), None)

    def get_monitoring_type(self) -> Optional[MonitoringType]:
        # If there is Monitoring scv, type is defined per schema
        monitoring_conf = self.get_manager_conf(Managers.MONITORING)
        if monitoring_conf:
            # Key presence defined by schema
            return MonitoringType(monitoring_conf[MONITORING_SVC_TYPE])
        else:
            return None

    def get_dstat_options(self) -> str:
        try:
            opt = self[MONITORING_SVC][DSTAT_OPTIONS]
        except KeyError:
            self.logger.info(f"DSTAT options defaulting to: {DSTAT_DEFAULT_OPTS}")
            return DSTAT_DEFAULT_OPTS
        return opt

    def get_services_to_load(self) -> list[str]:
        """Parses configuration to find types of services to load.

        Args:
            infra_config (dict[str, str]): yaml dump of layers_services.yaml
                configuration file

        Returns:
            services_to_load (list[str]): List of types of services
                present in the configuration
        """
        available_services = get_available_services()
        services_to_load = []
        # List services to load
        for layer in self[LAYERS]:
            for service in layer[SERVICES]:
                service_name = service[NAME]
                if service_name not in available_services:
                    self.logger.info(
                        f"'{service_name}' not foud in registered services. "
                        f"Will deploy '{DEFAULT_SERVICE_NAME}' service."
                    )
                    self.logger.debug(
                        "Run `e2clab services list` to see registered services"
                    )
                    service_name = DEFAULT_SERVICE_NAME
                # Register service plugin name
                service[SERVICE_PLUGIN_NAME] = service_name
                if service_name not in services_to_load:
                    services_to_load.append(service_name)
        return services_to_load

    def get_providers_to_load(self) -> list[Environment]:
        """
        Scans for the requested environments.
        :param infra_config: refers to the 'layers_services.yaml' file.
        :return: An environment array.
        """
        # Structure of the config is garenteed by the layers-services schema
        prov2load: list[Environment] = []
        for environment_key in self[ENVIRONMENT]:
            # Filtering out the job name and common definitions
            if environment_key in SUPPORTED_ENVIRONMENTS:
                prov2load.append(Environment(environment_key))

        for layer in self[LAYERS]:
            for service in layer[SERVICES]:
                service_env = service.get(ENVIRONMENT)
                if (
                    service_env is not None
                    and Environment(service_env) not in prov2load
                ):
                    self.logger.warning(
                        f"Environment {service_env} "
                        f"implicitly defined in layer {layer[NAME]} "
                        "added to requested environments"
                    )
                    prov2load.append(Environment(service_env))

        self.logger.info(f"Environments to load = {[e.name for e in prov2load]}")
        return prov2load

    def refine_to_environment(self, target_env: str):
        """Refines the configuration to an environment configuration

        Args:
            target_env (str): environment name
        """
        # Move taget env definition into top level
        if self[ENVIRONMENT].get(target_env):
            self[ENVIRONMENT].update(self[ENVIRONMENT].pop(target_env))

        # Filter other envs definition
        env_defs = list(
            filter(lambda x: x in SUPPORTED_ENVIRONMENTS, self[ENVIRONMENT])
        )
        for env_def in env_defs:
            if env_def != target_env:
                self[ENVIRONMENT].pop(env_def)

        # Filter services
        for layer in reversed(self[LAYERS]):
            for service in reversed(layer[SERVICES]):
                service_env = service.get(ENVIRONMENT, self.master_environment)
                # service_env = service.get(ENVIRONMENT)
                if service_env != target_env:
                    layer[SERVICES].remove(service)

            # Remove empty layers
            if not layer[SERVICES]:
                self[LAYERS].remove(layer)

        # Filtering managers
        for manager in Managers:
            self._filter_manager(manager, Environment(target_env))

    def _filter_manager(self, e_manager: Managers, target_env: Environment):
        """Removes manager configurations to cater to target environment.

        Args:
            manager (ManagerSvcs): _description_
            target_env (Environment): _description_
        """
        # dict type ensured by schema
        manager_key = e_manager.value.get_config_key()
        manager_conf = self.get_manager_conf(e_manager)
        if manager_conf is None:
            return
        manager = e_manager.value(manager_conf)
        if not manager.compare_environment(target_env):
            self.pop(manager_key)

    def _set_master_environment(self):
        """Save the top-level environment (default for services)"""
        # Master environment is the first one
        envs = filter(lambda x: x in SUPPORTED_ENVIRONMENTS, self[ENVIRONMENT])
        self.master_environment = next(envs)

    def _repeat_services(self):
        """Repeats the Service configuration in the 'layers_services.yaml' file.
        :param infra_config: refers to the 'layers_services.yaml' file.
        """
        for layer in self[LAYERS]:
            for service in layer[SERVICES]:
                if REPEAT in service:
                    for _ in range(service.pop(REPEAT)):
                        layer[SERVICES].append(deepcopy(service))

    def _generate_service_id(self):
        """
        Updates infra_config (layers_services.yaml file defined by users) with
        the _id at the service level.
        An INITIAL (incomplete) Service ID is defined as: "LayerID_ServiceID".
            For example: a Service with ID = "1_1", means first Layer and first
            Service in that layer (as defined in "layers_services.yaml")

        NOTE: The FINAL (complete) "ServiceID" is: "LayerID_ServiceID_MachineID"
            and is generated after Service registration
            (see e2clab.services.Service.__service_key()).
        :param infra_config: refers to the 'layers_services.yaml' file.
        """
        for i, layer in enumerate(self[LAYERS]):
            for j, service in enumerate(layer[SERVICES]):
                layer_id = i + 1
                service_id = j + 1
                service[ID] = str(layer_id) + "_" + str(service_id)
                service[LAYER_NAME] = layer[NAME]
                service[LAYER_ID] = layer_id
                service[SERVICE_ID] = service_id

    def get_layers(self) -> list:
        ret = self.get(LAYERS)
        assert isinstance(ret, list)
        return ret

    def get_layer_names(self) -> list[str]:
        return [layer[NAME] for layer in self.get_layers()]

    def iterate_services(self):
        "Iterator over all services"
        for layer in self[LAYERS]:
            for service in layer[SERVICES]:
                yield service


class NetworkConfig(dict, E2clabConfig):
    """
    Class to manage network configuration
    """

    def __init__(self, data: Optional[dict]) -> None:
        if data is None:
            data = {}
        super().__init__(deepcopy(data))
        if not is_valid_conf(self, "network"):
            raise E2clabConfigError

    def get_networks(self):
        return self.get(NETWORKS, None)

    def get_netconfs(self) -> list["NetConf"]:
        networks = self.get_networks()
        if networks is None:
            return []
        return [NetConf(**conf) for conf in networks]


@dataclass
class NetConf(dict, E2clabConfig):
    """
    Class to manage individual network configurations
    """

    src: str
    dst: str
    delay: str
    rate: str
    loss: Optional[str] = None
    symmetric: bool = False

    def get_netem_command(self) -> str:
        command = ""
        command += f"{DELAY} {self.delay} "
        command += f"{RATE} {self.rate} "
        if self.loss is not None:
            command += f"{LOSS} {self.loss} "
        return command.strip()

    def get_netem_key(self) -> str:
        sym = "symmetric" if self.symmetric else "asymmetric"
        key = f"{self.src}-{self.dst}-{sym}"
        return key


class WorkflowConfig(list, E2clabConfig):
    """
    Class to manage workflow configuration
    """

    def __init__(self, data: list, is_filtered: bool = False) -> None:
        super().__init__(deepcopy(data))
        if not is_valid_conf(self, "workflow"):
            raise E2clabConfigError
        self.is_filtered = is_filtered

    def get_task_filtered_workflow_config(
        self, task: WorkflowTasks
    ) -> "WorkflowConfig":
        """
            Returns a list of hosts in workflow.yaml (-hosts:)
        with a single task [prepare, launch, finalize] defined in task_filter
        :param task: prepare, or launch, or finalize
        :return: A filtered WorkflowConfig
        """
        if self.is_filtered:
            raise Exception("Cannot filter a Workflow config twice !")
        filtered_host = []
        for host in deepcopy(self):
            if task.value in host:
                host[ANSIBLE_TASKS] = host.pop(task.value)
                for other_task in WORKFLOW_TASKS:
                    host.pop(other_task, None)
                filtered_host.append(host)
        return WorkflowConfig(filtered_host, True)

    def iter_tasks(self) -> Iterator["TaskConfig"]:
        for task in self:
            yield TaskConfig(task)

    @staticmethod
    def get_depends_on_list_from_task(task_list: dict):
        return task_list.pop(DEPENDS_ON)


class TaskConfig(dict, E2clabConfig):
    def pop_depends_on(self) -> list["DependsOnConfig"]:
        """
        Pops the 'depends_on' key from the task configuration.
        Returns:
            list: The list of dependencies if exists, otherwise an empty list.
        """
        ret = [
            DependsOnConfig(
                service_selector=dep[SERV_SELECT],
                prefix=dep[PREFIX],
                grouping=GroupingType(dep[GROUPING]),
                array_info=ArrayInfo(dep.get(ARRAY_INFO, default.ARRAY_INFO)),
            )
            for dep in self.pop(DEPENDS_ON, [])
        ]
        return ret

    @property
    def target(self) -> str:
        return self[TARGET]

    @target.setter
    def target(self, value: str) -> None:
        self[TARGET] = value


@dataclass
class DependsOnConfig:
    service_selector: str
    prefix: str
    grouping: GroupingType
    array_info: ArrayInfo


class WorkflowEnvConfig(dict, E2clabConfig):
    """
    Class to manage workflow environment configuration

    Adds prefix to all values
    """

    def __init__(self, data: dict) -> None:
        super().__init__(deepcopy(data))
        if not is_valid_conf(data, "workflow_env"):
            raise E2clabConfigError
        self._prefix_env_variables()

    def get_env(self, key: str, default={}) -> dict:
        return super(WorkflowEnvConfig, self).get(key, default)

    def _prefix_env_variables(self):
        """Prefixes workflow environment variables"""
        _prefix = default.WORKFLOW_ENV_PREFIX
        for k, v in self.items():
            self[k] = {f"{_prefix}{key}": val for key, val in v.items()}


# TODO: use this object
class ServiceConfig(dict):
    """
    Class to manage Service information
    """

    def __init__(self, data: dict) -> None:
        super().__init__(deepcopy(data))
        pass
