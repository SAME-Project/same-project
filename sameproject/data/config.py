from sameproject.ops.runtime_options import list_options, get_option_value
from ruamel.yaml.parser import ParserError
from cerberus import Validator
from io import BufferedReader
from ruamel.yaml import YAML
from pathlib import Path
from box import Box
import logging

# Subschemas used for validating input to `same init`.
name_schema = {"type": "string", "required": True, "regex": r"^[\d\w ]+"}
image_schema = {"type": "string", "required": True, "regex": ".*/.*"}
datasets_schema = {"type": "string", "regex": r"^[\d\w]+"}
environment_schema = {"type": "string", "regex": r"^[\d\w]+"}

# Schema for validating SAME config files.
schema = {
    "apiVersion": {"type": "string", "required": True},
    "metadata": {
        "type": "dict",
        "schema": {
            "version": {"type": "string", "required": True},
            "labels": {"type": "list"},
            "sha": {"type": "string"},
            "name": name_schema,
        },
        "required": True,
    },
    "datasets": {
        "type": "dict",
        "keysrules": datasets_schema,
        "valuesrules": {
            "type": "dict",
            "schema": {
                "schema_uri": {"type": "string"},
                "environments": {
                    "type": "dict",
                    "must_have_default": True,
                    "keysrules": {"type": "string"},  # TODO: env name regex
                    "valuesrules": {"type": "string"},  # TODO: URI regex
                },
            },
        },
    },
    "environments": {
        "type": "dict",
        "must_have_default": True,
        "keysrules": environment_schema,
        "valuesrules": {
            "type": "dict",
            "schema": {
                "image_tag": image_schema,
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
        "required": True,
        "schema": {
            "name": {"type": "string", "required": True},
            "path": {"type": "string", "required": True},
            "requirements": {"type": "string"}
        }
    },
    "run": {
        "type": "dict",
        "schema": {
            "name": {"type": "string", "required": True},
            "sha": {"type": "string"},
            "parameters": {
                "type": "dict",
            },
        },
    },

    # Injected by SAME automatically based on environment variables and
    # command-line flags. This also lets users specify runtime options in
    # their SAME config file if they like:
    "runtime_options": {
        "type": "dict",
    },
}


class SameValidator(Validator):
    """Custom cerberus validation rules for SAME config files."""

    def _validate_must_have_default(self, constraint, field_name, values_needing_default):
        """
        Constrains 'dict' types to have at least one field called 'default'.

        The rule's arguments are validated against this schema:
          { 'type': 'boolean' }
        """
        if constraint and (values_needing_default is None or values_needing_default.get("default", None) is None):
            self._error(field_name, f"{field_name} does not contain a 'default' entry.")

    @staticmethod
    def get_validator() -> Validator:
        return SameValidator(schema)


class SameConfig(Box):
    """Container for SAME config file data."""

    def __init__(self, *args, frozen_box=True, **kwargs):
        data = Box(*args, **kwargs)
        validator = SameValidator.get_validator()
        if not validator.validate(data):
            raise SyntaxError(f"SAME config file is invalid: {validator.errors}")

        # Uses Box as the child box_class so we don't recursively validate:
        super().__init__(*args, frozen_box=frozen_box, box_class=Box, **kwargs)

    def resolve(self, base_path):
        """
        Returns a new SAME config file with the notebook and requirements paths
        resolved against the given base path.
        """
        data = Box(self)
        base_path = Path(base_path)
        data.notebook.path = str(base_path / data.notebook.path)
        if "requirements" in data.notebook:
            data.notebook.requirements = str(base_path / data.notebook.requirements)

        return SameConfig(data, frozen_box=self._box_config["frozen_box"])

    def inject_runtime_options(self):
        """
        Returns a new SAME config file with all present runtime options merged
        into the 'runtime_options' field.
        """
        data = Box(self)
        if "runtime_options" not in data:
            data.runtime_options = {}

        for opt in list_options():
            if get_option_value(opt) is not None:
                data.runtime_options[opt] = get_option_value(opt)

        return SameConfig(data, frozen_box=self._box_config["frozen_box"])
