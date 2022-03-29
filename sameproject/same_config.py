from cerberus import Validator
from box import Box
from pathlib import Path
from ruamel.yaml import YAML
from ruamel.yaml.parser import ParserError
import logging
import pprint

from io import BufferedReader


class SameValidator(Validator):
    def _validate_must_have_default(self, constraint, field_name, values_needing_default):
        """Test to ensure that a list of keys has at least one entry that matches 'default'
        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if constraint and (values_needing_default is None or values_needing_default.get("default", None) is None):
            self._error(field_name, f"{field_name} does not contain a 'default' entry.")

    @staticmethod
    def get_validator() -> Validator:
        return SameValidator(SameValidator.schema)

    schema = {
        "apiVersion": {"type": "string", "required": True},
        "metadata": {
            "type": "dict",
            "schema": {
                "name": {"type": "string", "required": True, "regex": r"^[\d\w ]+"},
                "version": {"type": "string", "required": True},
                "labels": {"type": "list"},
                "sha": {"type": "string"},
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
                        # TODO: Figure out why we can't check for datasets->environments not having a default field
                        # "must have default": True, -- could not get this to work for some reason
                    },
                },
            },
            "allow_unknown": True,
        },
        "environments": {
            "type": "dict",
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
            "allow_unknown": True,
            "must have default": True,
        },
        "notebook": {"type": "dict", "schema": {"name": {"type": "string", "required": True}, "path": {"type": "string", "required": True}}},
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
        "path": {"type": "string"},
    }


class SameConfig(Box):
    """Class for SAME Config Object. Currently, just subclasses Box, but building in now as I expect we'll need custom processing here."""

    def __init__(self, buffered_reader: BufferedReader = None, content: str = ""):
        # NB: The default path value has to be set on self, not as a class
        # variable, otherwise the __setattr__ hack below doesn't work.
        self.path = ""
        if buffered_reader is not None and content != "":
            raise ValueError("SameConfig accepts either a buffered reader or content value, but not both.")
        elif buffered_reader is not None:
            self.path = buffered_reader.name
            same_config_content = "".join(map(bytes.decode, buffered_reader.readlines()))
        elif content == "":
            raise ValueError("Content is empty.")
        else:
            same_config_content = content

        yaml = YAML(typ="safe")
        try:
            same_config_dict = yaml.load(same_config_content)
        except ParserError as e:
            logging.fatal(f"Content does not appear to be well-formed yaml. Error: {str(e)}")

        if same_config_dict is None:
            raise ValueError(f"SAME file at '{self.path}' is empty.")

        v = SameValidator.get_validator()
        if not v.validate(same_config_dict):
            raise SyntaxError(f"SAME file at '{self.path}' is invalid: {v.errors}; {pprint.pformat(same_config_dict)}")

        temp_box = Box(same_config_dict)
        self.update(temp_box)

    def __setattr__(self, name, value):
        if name == "path":
            if not Path(value).exists():
                raise FileNotFoundError(value)

        super(SameConfig, self).__setattr__(name, value)

    def write(self, path=""):
        same_config_yaml = self.to_yaml()
        v = SameValidator.get_validator()
        if not v.validate(same_config_yaml):
            raise SyntaxError("SAME Config object is invalid. \n %s" % "\n".join(v.errors))

        if path == "":
            if self.path == "":
                raise ValueError("Need to specify location to write same file.")
        else:
            logging.info(f"Overwriting location of SAME config file ({self.path} -> {path})")
            self.path = path

        Path(self.path).write_text(same_config_yaml)


# type RepositoryCredentials struct {
# 	SecretName string `yaml:"secretname,omitempty"`
# 	Server     string `yaml:"server,omitempty"`
# 	Username   string `yaml:"username,omitempty"`
# 	Password   string `yaml:"password,omitempty"`
# 	Email      string `yaml:"email,omitempty"`
# }
