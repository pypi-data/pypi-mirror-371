from jsonschema import Draft7Validator

from e2clab.constants.network import DELAY, DST, LOSS, NETWORKS, RATE, SRC, SYMMETRIC

SCHEMA: dict = {
    "description": "Experiment Network description",
    "type": ["null", "object"],
    "properties": {
        NETWORKS: {
            "type": ["array", "null"],
            "items": {"$ref": "#/definitions/network"},
        }
    },
    "required": [NETWORKS],
    "additionalProperties": False,
    "definitions": {
        "network": {
            "title": "Network emulation",
            "type": "object",
            "properties": {
                SRC: {
                    "description": "Source services name",
                    "type": "string",
                    "examples": ["cloud", "cloud.kafka.*"],
                },
                DST: {
                    "description": "Destination services name",
                    "type": "string",
                    "example": ["edge", "fog.gateway.*"],
                },
                DELAY: {
                    "description": "The delay to apply",
                    "type": "string",
                    "examples": ["10ms", "1ms"],
                },
                RATE: {
                    "description": "The rate to apply",
                    "type": "string",
                    "examples": ["1gbit", "100mbit"],
                },
                LOSS: {
                    "description": "The percentage of loss",
                    "type": "string",
                    "pattern": r"\d*.?\d*%",
                    "examples": ["1%", "5%"],
                },
                SYMMETRIC: {
                    "description": "True for symmetric rules to be applied",
                    "type": "boolean",
                },
            },
            "required": [SRC, DST, DELAY, RATE],
            "additionalProperties": False,
        }
    },
}

NetworkValidator: Draft7Validator = Draft7Validator(SCHEMA)
