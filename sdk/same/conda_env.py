from cerberus import Validator
from box import Box
from pathlib import Path
from ruamel.yaml import YAML
from ruamel.yaml.parser import ParserError
import logging

from io import BufferedReader


VALID_KEYS = ("name", "dependencies", "prefix", "channels", "variables", "extras")


class CondaEnvValidator(Validator):
    @staticmethod
    def get_validator() -> Validator:
        return CondaEnvValidator(CondaEnvValidator.schema)

    schema = {
        "name": {"type": "string", "required": True},
        "dependencies": {"type": "list", "regex": r"^[\d\w]+==[\d\w]+", "required": True},
        "channels": {"type": "list", "regex": r"^[\d\w-]+"},
        "prefix": {"type": "string"},
        "variables": {"type": "dict"},
        "extras": {"type": "dict"},
    }


class CondaEnv(Box):
    """Class for ConndaEnv Object."""

    def __init__(self, buffered_reader: BufferedReader = None, content: str = ""):
        if buffered_reader is not None and content != "":
            raise ValueError("CondaEnv accepts either a buffered reader or content value, but not both.")
        elif buffered_reader is not None:
            conda_env_content = "".join(map(bytes.decode, buffered_reader.readlines()))
        elif content == "":
            raise ValueError("Content is empty.")
        else:
            conda_env_content = content

        yaml = YAML(typ="safe")
        try:
            conda_env_dict = yaml.load(conda_env_content)
        except ParserError as e:
            logging.fatal(f"Content does not appear to be well-formed yaml. Error: {str(e)}")

        v = CondaEnvValidator.get_validator()
        if conda_env_dict is None:
            raise ValueError("Conda Env is empty.")

        if not v.validate(conda_env_dict):
            raise SyntaxError(f"Conda Env is invalid. \n {v.errors}")

        temp_box = Box(conda_env_dict)
        self.update(temp_box)

    def __setattr__(self, name, value):
        if name == "path":
            if not Path(value).exists():
                raise FileNotFoundError(value)

        super(CondaEnv, self).__setattr__(name, value)

    def write(self, path):
        same_config_yaml = self.to_yaml()
        v = CondaEnvValidator.get_validator()
        if not v.validate(same_config_yaml):
            raise SyntaxError("Conda Env object is invalid. \n %s" % "\n".join(v.errors))

        if Path(path).exists():
            logging.info(f"Overwriting location of Conda Env file ({path})")

        Path(path).write_text(same_config_yaml)
