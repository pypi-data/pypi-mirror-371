from pathlib import Path
from typing import Union

import click
import yaml
from enoslib import Host, Roles
from enoslib.api import EnosInventory
from jinja2 import Environment, FileSystemLoader

from e2clab import ENV_FILE
from e2clab.constants import (
    CONF_FILES_LIST,
    ENV_AUTO_PREFIX,
    PATH_TEMPLATES,
    WORKFLOW_TASKS,
    Command,
    ConfFiles,
)
from e2clab.errors import E2clabFileError
from e2clab.log import get_logger
from e2clab.providers.plugins.Chameleonedge import E2CEdgeDevice
from e2clab.schemas import is_valid_conf

logger = get_logger(__name__, ["UTILS"])


def is_valid_setup(
    scenario_dir: Path,
    artifacts_dir: Union[Path, None],
    command: Command,
    is_app_conf: bool = False,
) -> bool:
    """Checks if E2cLab configuration files follow the right schema.

    Args:
        scenario_dir (Path):
            Path to folder containing experiment configuration files
        artifacts_dir (Union[Path, None]):
            Path to folder containing experiment artifacts
        command (Command):
            E2clab command you intend to run (e.g. 'network' or 'layer-services')
        is_app_conf (bool, optional):
            Are we going to use an 'app_conf' parameter. Defaults to False.

    Returns:
        bool: Validity of the experiment setup
    """

    is_valid = True

    # CHECK SCENARIO_DIR
    if not scenario_dir.exists():
        logger.error(f"Scenario dir path does not exist: {scenario_dir}")
        return False

    # CHECK IF CONFIG FILES EXIST AND ARE VALID IN SCENARIO_DIR
    if command == Command.LYR_SVC or command == Command.DEPLOY:
        res = validate_conf(
            conf_file=scenario_dir / ConfFiles.LAYERS_SERVICES, type="layers_services"
        )
        is_valid = res and is_valid

    if command == Command.NETWORK or command == Command.DEPLOY:
        res = validate_conf(conf_file=scenario_dir / ConfFiles.NETWORK, type="network")
        is_valid = res and is_valid

    if (
        command == Command.WORKFLOW
        or command == Command.DEPLOY
        or command == Command.FINALIZE
    ):
        res = validate_conf(
            conf_file=scenario_dir / ConfFiles.WORKFLOW, type="workflow"
        )
        is_valid = res and is_valid

        # CHECK "workflow_env.yaml"
        if is_app_conf:
            res = validate_conf(
                conf_file=scenario_dir / ConfFiles.WORKFLOW_ENV, type="workflow_env"
            )
            is_valid = res and is_valid

    # CHECK ARTIFACTS_DIR
    if artifacts_dir is not None and not artifacts_dir.exists():
        logger.error(f"Artifact path does not exist: {artifacts_dir}")
        return False

    return is_valid


def is_valid_task(task: str) -> bool:
    is_valid = True
    if task.lower() not in WORKFLOW_TASKS:
        logger.error(
            f"Task {task.lower()} is not valid, "
            "choose one of the following [prepare, launch, finalize]"
        )
        is_valid = False
    return is_valid


def load_yaml_file(file: Path) -> Union[dict, list]:
    """Loads an E2clab yaml configuration file

    Args:
        file (Path): Yaml configuration file

    Raises:
        E2clabFileError: if file does not exist
        E2clabFileError: if there is a yaml syntax error
        E2clabFileError: if there is any other unexpected error

    Returns:
        dict[str, str]: python object containing configuration description
    """
    try:
        with open(file, "r") as f:
            content = yaml.safe_load(f)
            return content
    except FileNotFoundError as e:
        raise E2clabFileError(file, "File does not exist") from e
    except yaml.YAMLError as e:
        raise E2clabFileError(file, f"Yaml syntax error in file: {e}") from e
    except Exception as e:
        raise E2clabFileError(file, f"Unknown error {e}") from e


def validate_conf(conf_file: Path, type: str) -> bool:
    """Validate if the configuration file follows the right syntax

    Args:
        conf_file (Path): path to the file
        type (str): "layers_services" | "network" | "workflow" | "workflow_env"

    Returns:
        bool: is the configuration valid
    """
    try:
        conf = load_yaml_file(conf_file)
    except E2clabFileError as e:
        logger.error(e)
        return False
    return is_valid_conf(conf, type)


def write_dot_param(file, envname: str, value, comment: bool = False) -> None:
    """Writes a dotfile parameter to the file

    Args:
        file (file buffer): file to write to
        envname (str): E2Clab parameter envame without prefix
        value (Any): value to set
        comment (bool, optional): comment the line to write. Defaults to False.
    """
    line = f"{ENV_AUTO_PREFIX}_{envname}={value}\n"
    if comment:
        line = "# " + line
    file.write(line)


def run_init(
    dir: Path,
    scenario_dirname: str,
    artifacts_dirname: str,
    workflow_env: bool,
    env_only: bool = False,
) -> None:
    """Quick init a directory for e2clab experimentation

    Args:
        dir (Path): directory
        scenario_dirname (str): SCENARIO_NAME
        artifacts_dirname (str): ARTIFACTS_NAME
        workflow_env (bool): if we want to use app_conf
        env_only (bool): if we only want to create the ENV_FILE
    """
    scenario_dir = dir / scenario_dirname
    artifacts_dir = dir / artifacts_dirname
    envfile_path = dir / ENV_FILE

    write_env = True
    if envfile_path.exists():
        write_env = click.prompt(
            f"{envfile_path} already exists, overwrite ?", default=False, type=bool
        )

    if write_env:
        _write_init_dotenv(scenario_dir, artifacts_dir, envfile_path)

    if env_only:
        return
    scenario_dir.mkdir(exist_ok=True)
    artifacts_dir.mkdir(exist_ok=True)

    # We use different variables start and end strings as 'workflow.yaml'
    # itself contains other jinja variables within it that we don't want to render
    env = Environment(
        loader=FileSystemLoader(PATH_TEMPLATES),
        variable_start_string="<<",
        variable_end_string=">>",
        keep_trailing_newline=True,
    )
    context = {
        "job_name": scenario_dir.stem,
        "is_app_conf": workflow_env,
    }

    # Render templates
    for file in [*CONF_FILES_LIST, ".gitignore"]:
        if file == ConfFiles.WORKFLOW_ENV and not workflow_env:
            continue
        template = env.get_template(f"{file}.jinja")
        output = template.render(context)
        out_file = scenario_dir / file
        with open(out_file, "w") as f:
            f.write(output)


def _write_init_dotenv(
    scenario_dir: Path, artifacts_dir: Path, envfile_path: Path
) -> None:
    """Inits an envfile file with provided information

    Args:
        scenario_dir (str): scenario dir name
        artifacts_dir (str): artifacts dir name
        envfile_path (Path): path to .e2c_env file
    """
    with envfile_path.open("w") as f:
        write_dot_param(f, "SCENARIO_DIR", str(scenario_dir))
        write_dot_param(f, "ARTIFACTS_DIR", str(artifacts_dir))
        f.write("\n# Examples\n")
        f.write("# Debug logging\n")
        write_dot_param(f, "DEBUG", "true", True)
        f.write("# Mute Ansible\n")
        write_dot_param(f, "MUTE_ANSIBLE", "true", True)
        f.write("# Mute EnOSlib logging\n")
        write_dot_param(f, "MUTE_ENOSLIB", "true", True)
        f.write("# Set deployment duration\n")
        write_dot_param(f, "DURATION", 60, True)
        f.write("# Set deployment experiment repeat\n")
        write_dot_param(f, "REPEAT", 1, True)


def is_chameleon_device(host: Union[Host, E2CEdgeDevice]) -> bool:
    return isinstance(host, E2CEdgeDevice)


def get_hosts_from_pattern(roles: Roles, pattern: str) -> list[Host]:
    """
        Uses fake Host to use the convenient get_hosts method to pattern match the
        roles.
        We use a fake inventory with madeup keys and roles as addresses because we
        want ansible to only match the roles and not the actual addresses of the
        hosts, otherwise different hosts with different roles (and extra info)
        might be matched. Also hence why we do not use the enoslib api.

    :param patter_selector: pattern (as string) used to filter hosts
    :return: ansible.hosts
    """

    fake_roles = {}
    i = 0
    for role, hosts in roles.items():
        fake_roles[str(i)] = [Host(role, extra={"__app_info__": hosts})]
        i += 1
    fake_inventory = EnosInventory(roles=fake_roles)
    ret = fake_inventory.get_hosts(pattern=pattern.lower())
    if len(ret) == 0:
        print(f"Pattern '{pattern}' not found in the experiment's resources")
    output = [h.vars["__app_info__"][0] for h in ret]
    filtered_output = []
    # Filtering as we might have multiple hosts with the same address
    unique_addr = {}
    for h in output:
        if h.address not in unique_addr:
            unique_addr[h.address] = True
            filtered_output.append(h)
    return filtered_output
