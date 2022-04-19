from ruamel.yaml.parser import ParserError
from cerberus import Validator
from io import BufferedReader
from ruamel.yaml import YAML
from pathlib import Path
from box import Box
import logging
import pprint


# Schema for validating SAME config files.
schema = {
    "apiVersion": {"type": "string", "required": True},
    "metadata": {
        "type": "dict",
        "schema": {
            "version": {"type": "string", "required": True},
            "labels": {"type": "list"},
            "sha": {"type": "string"},
            "name": {"type": "string", "required": True, "regex": r"^[\d\w ]+"},
        },
        "required": True,
    },
    "datasets": {
        "type": "dict",
        "keysrules": {"type": "string", "regex": r"^[\d\w]+"},
        "valuesrules": {
            "type": "dict",
            "schema": {
                "schema_uri": {"type": "string"},
                "environments": {
                    "type": "dict",
                    "must_have_default": True,
                },
            },
        },
    },
    "environments": {
        "type": "dict",
        "must_have_default": True,
        "keysrules": {"type": "string", "regex": r"^[\d\w]+"},
        "valuesrules": {
            "type": "dict",
            "schema": {
                "image_tag": {"type": "string", "required": True, "regex": ".*/.*"},
                "private_registry": {"type": "boolean"},
                "credentials": {
                    "type": "dict",
                    "schema": {
                        "image_pull_secret_name": {"type": "string"},
                        "image_pull_secret_registry_uri": {"type": "string"},
                        "image_pull_secret_username": {"type": "string"},
                        "image_pull_secret_password": {"type": "string"},
                        "image_pull_secret_email": {"type": "string"},
                    },
                },
            },
        },
    },
    "notebook": {
        "type": "dict",
        "schema": {
            "name": {"type": "string", "required": True},
            "path": {"type": "string", "required": True}
        }
    },
    "run": {
        "type": "dict",
        "schema": {
            "name": {"type": "string", "required": True},
            "sha": {"type": "string", "required": True},
            "parameters": {
                "type": "dict",
            },
        },
    },
}


class SameValidator(Validator):
    """Validator for SAME config files."""

    def _validate_must_have_default(self, constraint, field_name, values_needing_default):
        """Constrains 'dict' types to have at least one field called 'default'."""
        if constraint and (values_needing_default is None or values_needing_default.get("default", None) is None):
            self._error(field_name, f"{field_name} does not contain a 'default' entry.")

    @staticmethod
    def get_validator() -> Validator:
        return SameValidator(schema)


class SameConfig(Box):
    """Container for SAME config file data."""

    def __init__(self, yaml_string: str):
        data = Box.from_yaml(yaml_string=yaml_string)

        validator = SameValidator.get_validator()
        if not validator.validate(data):
            raise SyntaxError(f"SAME config file is invalid: {validator.errors}")

        super(Box, self).__init__(
            data,
            frozen_box=True,
        )

    def write(self, path: str):
        Path(path).write_text(self.to_yaml())
