from cerberus import Validator
from box import Box


class SAMEValidator(Validator):
    def _validate_must_have_default(self, constraint, field_name, values_needing_default):
        """Test to ensure that a list of keys has at least one entry that matches 'default'
        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if constraint and (values_needing_default is None or values_needing_default.get("default", None) is None):
            self._error(field_name, f"{field_name} does not contain a 'default' entry.")


schema = {
    "apiVersion": {"type": "string", "required": True},
    "metadata": {
        "type": "dict",
        "schema": {
            "name": {"type": "string", "required": True, "regex": r"^[\d\w]+"},
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
    "base_images": {
        "type": "dict",
        "keysrules": {"type": "string", "regex": r"^[\d\w]+"},
        "valuesrules": {
            "type": "dict",
            "schema": {
                "image_tag": {"type": "string", "required": True, "regex": ".*/.*"},
                "packages": {"type": "list"},
                "private_registry": {"type": "boolean"},
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
}


class SAME_config(Box):
    """Class for SAME Config Object. Currently, just subclasses Box, but building in now as I expect we'll need custom processing here."""

    _config_file_path = ""


# type RepositoryCredentials struct {
# 	SecretName string `yaml:"secretname,omitempty"`
# 	Server     string `yaml:"server,omitempty"`
# 	Username   string `yaml:"username,omitempty"`
# 	Password   string `yaml:"password,omitempty"`
# 	Email      string `yaml:"email,omitempty"`
# }
