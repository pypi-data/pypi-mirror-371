from jsonschema import Draft7Validator

import e2clab.constants.default as default
from e2clab.constants import ARRAY_INFO_LIST, GROUPING_LIST, WORKFLOW_TASKS
from e2clab.constants.workflow import (
    ARRAY_INFO,
    DEPENDS_ON,
    GROUPING,
    PREFIX,
    SERV_SELECT,
    TARGET,
)

task_schema: dict = {
    "description": "Ansible task definition.",
    "type": "array",
}

workflow_schema_tasks: dict = {task: task_schema for task in WORKFLOW_TASKS}

depends_on_schema = {
    "description": "Description of hosts interconnections",
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            SERV_SELECT: {
                "description": "",
                "type": "string",
            },
            GROUPING: {
                "description": "Grouping strategy between hosts, defaults: round_robin",
                "type": "string",
                "enum": GROUPING_LIST,
            },
            PREFIX: {
                "description": "Prefix to access linked hosts parameters",
                "type": "string",
            },
            ARRAY_INFO: {
                "description": "Information passed in the array",
                "type": "string",
                "default": default.ARRAY_INFO,
                "enum": ARRAY_INFO_LIST,
            },
        },
        "required": [SERV_SELECT, PREFIX, GROUPING],
    },
}

# TODO: finalize workflow schema
SCHEMA: dict = {
    "description": "Non-described properties will be passed to ansible in a play.",
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            TARGET: {
                "description": "hosts description on which to execute workflow",
                "type": "string",
            },
            DEPENDS_ON: {"$ref": "#/definitions/depends_on"},
            **workflow_schema_tasks,
        },
        "required": [TARGET],
        # "additionalProperties": False,
    },
    "definitions": {"depends_on": depends_on_schema},
}

WorkflowValidator: Draft7Validator = Draft7Validator(SCHEMA)
