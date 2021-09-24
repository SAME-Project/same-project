from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO

import regex as re

from pathlib import Path


def dict_to_yaml(input_dict: dict) -> dict:
    yaml = YAML(typ="safe")
    s = StringIO()
    try:
        yaml.dump(input_dict, stream=s)
        return s.getvalue()
    except SyntaxError as e:
        raise SyntaxError(f"Failure converting dict to yaml: {e}")


def removeIllegalExperimentNameCharacters(s: str) -> str:
    return re.sub(r"[^\d\w-_]*", "", s)


def alphaNumericOnly(s: str) -> str:
    return re.sub(r"[^\d\w]*", "", s)


def write_file(
    path: str,
    s: str,
):
    Path(path).write_text(s)
    return
