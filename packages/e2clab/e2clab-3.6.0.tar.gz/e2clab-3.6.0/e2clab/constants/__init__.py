"""
Constants module
Defined for all managers in config
Default paramters in the default module
"""

from enum import Enum
from pathlib import Path

from . import layers_services

PATH_ROOT_E2CLAB = Path(__file__).parent.parent.resolve()
PATH_SERVICES_PLUGINS = PATH_ROOT_E2CLAB / "services" / "plugins"
PATH_TEMPLATES = PATH_ROOT_E2CLAB / "templates"

STATE_DIR = ".e2c_state"
SSH_STATE_NAME = ".ssh_state"


class ConfFiles:
    LAYERS_SERVICES = "layers_services.yaml"
    NETWORK = "network.yaml"
    WORKFLOW = "workflow.yaml"
    WORKFLOW_ENV = "workflow_env.yaml"


CONF_FILES_LIST = [
    ConfFiles.LAYERS_SERVICES,
    ConfFiles.NETWORK,
    ConfFiles.WORKFLOW,
    ConfFiles.WORKFLOW_ENV,
]

"""
    Environments yaml keys
"""


class Environment(Enum):
    G5K = layers_services.G5K
    IOT_LAB = layers_services.IOT_LAB
    CHAMELEON_CLOUD = layers_services.CHAMELEON_CLOUD
    CHAMELEON_EDGE = layers_services.CHAMELEON_EDGE


SUPPORTED_ENVIRONMENTS = [e.value for e in Environment]

"""
    CLI constants
"""

ENV_SCENARIO_DIR = "E2C_SCENARIO_DIR"
ENV_ARTIFACTS_DIR = "E2C_ARTIFACTS_DIR"

ENV_AUTO_PREFIX = "E2C"


class Command(Enum):
    DEPLOY = "deploy"
    LYR_SVC = "layers-services"
    NETWORK = "network"
    WORKFLOW = "workflow"
    FINALIZE = "finalize"


COMMAND_RUN_LIST = [e.value for e in Command]

"""
    Workflow tasks
"""


class WorkflowTasks(Enum):
    PREPARE = "prepare"
    LAUNCH = "launch"
    FINALIZE = "finalize"


WORKFLOW_TASKS = [e.value for e in WorkflowTasks]

"""
    Workflow grouping
"""


class GroupingType(Enum):
    ROUND_ROBIN = "round_robin"
    ASARRAY = "asarray"
    AGGREGATE = "aggregate"
    ADDRESS_MATCH = "address_match"


GROUPING_LIST = [e.value for e in GroupingType]


class ArrayInfo(Enum):
    ID = "id"
    HOSTNAME = "hostname"
    G5K_IPV6_HOSTNAME = "g5k_ipv6_hostname"


ARRAY_INFO_LIST = [e.value for e in ArrayInfo]


"""
    Managers
"""


class ManagerSvcs(Enum):
    PROVENANCE = layers_services.PROVENANCE_SVC
    MONITORING = layers_services.MONITORING_SVC
    MONITORING_IOT = layers_services.MONITORING_IOT_SVC


class MonitoringType(Enum):
    TIG = layers_services.MONITORING_SVC_TIG
    TPG = layers_services.MONITORING_SVC_TPG
    DSTAT = layers_services.MONITORING_SVC_DSTAT
