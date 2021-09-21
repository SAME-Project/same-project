from cerberus import Validator
from box import Box
from pathlib import Path
from ruamel.yaml import YAML
from ruamel.yaml.parser import ParserError
import logging

from conda_env.env import Dependencies as CondaDependencies
from conda.cli.common import spec_from_line, MatchSpec, arg2spec

from io import BufferedReader

import cli.same.helpers as helpers


VALID_KEYS = ("name", "dependencies", "prefix", "channels", "variables", "extras")


class CondaEnvValidator(Validator):
    @staticmethod
    def get_validator() -> Validator:
        return CondaEnvValidator(CondaEnvValidator.schema)

    schema = {
        "name": {"type": "string", "required": True},
        "dependencies": {"type": "list", "required": True},
        "channels": {"type": "list", "regex": r"^[\d\w-]+"},
        "prefix": {"type": "string"},
        "variables": {"type": "dict"},
        "extras": {"type": "dict"},
    }


class CondaEnv(Box):
    """Class for CondaEnv Object."""

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

        # Final check - verify the Dependencies are compatible with Conda - if not, will fail with TypeError
        try:
            # Instantiate the CondaDependency object to reuse their error checking and parsing
            conda_dependencies = CondaDependencies(conda_env_dict["dependencies"])

            # Reformat the dependencies into objects before creating the final object
            conda_env_dict.pop("dependencies")
            conda_env_dict["dependencies"] = {}
            for dependency in conda_dependencies.raw:
                # Conda also supports detailing pip versions - we're just going to punt on this for now (and continue)
                if isinstance(dependency, dict):
                    continue
                spec = MatchSpec(arg2spec(dependency))
                conda_env_dict["dependencies"][spec.name] = getattr(spec, "version", None)
        except TypeError as e:
            raise ValueError(f"File did not match Conda base environment requirements: {str(e)}")

        temp_box = Box(conda_env_dict)
        self.update(temp_box)

    def __setattr__(self, name, value):
        if name == "path":
            if not Path(value).exists():
                raise FileNotFoundError(value)

        super(CondaEnv, self).__setattr__(name, value)

    # Couple of thoughts about export:
    # 1) There's a chance I could do a merge here with the file on disk. However, to keep things
    #    cheap and cheerful for now, I'm just doing a one-way write (not even checking what's there
    #    already). This feels like a mostly ok assumption, since we're capturing the source of truth
    #    (the environment that the notebook is running in), but it's not hard to imagine someone
    #    doing some external tweaks to the conda file that we're now blowing away.
    # 2) I'd love to reuse this (https://github.com/conda/conda/blob/33a142c16530fcdada6c377486f1c1a385738a96/conda/cli/main_list.py#L35) because
    #    this is how conda exports its packages, but the library is really non-extensible. I have no idea
    #    why they chose a pip incompatible format (single equal instead of two), but this is going to be something
    #    that will annoy us for a long time, I know it.
    def write(self, path):

        # First, I make a copy of the object. This is because the ACTUAL export object differs from
        # the one we maintain in memory (using a list for packages, instead of a dict)
        export_object = self.to_dict()

        # Next we pop off the dependencies object (which is a standard dict) and turn it into a list
        # according to conda naming style
        # https://github.com/conda/conda/blob/ed96a06244eb820781dc872eb381f51b95ee48ae/conda_env/env.py#L125
        dependencies_dict = export_object.pop("dependencies")

        # Now build a list in the form of conda
        dependencies_list = []

        for package_name in dependencies_dict:
            version_spec = dependencies_dict[package_name]
            if version_spec is not None:
                dependencies_list.append("=".join((package_name, version_spec.cmp.norm_version)))
            else:
                dependencies_list.append(package_name)

        export_object["dependencies"] = dependencies_list

        v = CondaEnvValidator.get_validator()
        if not v.validate(export_object):
            raise SyntaxError("Conda Env object is invalid. \n %s" % "\n".join(v.errors))

        if Path(path).exists():
            logging.info(f"Overwriting location of Conda Env file ({path})")

        same_config_yaml = helpers.dict_to_yaml(export_object)
        Path(path).write_text(same_config_yaml)
