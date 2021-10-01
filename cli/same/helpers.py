from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO

import regex as re

from pathlib import Path

from box import Box

import sys

REQUIRED_SECRET_VALUES = Box(
    {
        "IMAGE_PULL_SECRET_NAME": "image_pull_secret_name",
        "IMAGE_PULL_SECRET_REGISTRY_URI": "image_pull_secret_registry_uri",
        "IMAGE_PULL_SECRET_USERNAME": "image_pull_secret_username",
        "IMAGE_PULL_SECRET_PASSWORD": "image_pull_secret_password",
        "IMAGE_PULL_SECRET_EMAIL": "image_pull_secret_email",
    }
)


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


def lowerAlphaNumericOnly(s: str) -> str:
    return re.sub(r"[^\d\w]*", "", s).lower()


def write_file(
    path: str,
    s: str,
):
    Path(path).write_text(s)
    return


def recursively_remove_dir(path: Path):
    for child in path.glob("*"):
        if child.is_file():
            child.unlink()
        else:
            recursively_remove_dir(child)
    path.rmdir()


def create_secret_dict(
    image_pull_secret_name: str,
    image_pull_secret_registry_uri: str,
    image_pull_secret_username: str,
    image_pull_secret_password: str,
    image_pull_secret_email: str,
) -> dict:
    # Using values from the list, so there's only one place in the whole app where we name the string explicitly
    return {
        REQUIRED_SECRET_VALUES.IMAGE_PULL_SECRET_NAME: image_pull_secret_name,
        REQUIRED_SECRET_VALUES.IMAGE_PULL_SECRET_REGISTRY_URI: image_pull_secret_registry_uri,
        REQUIRED_SECRET_VALUES.IMAGE_PULL_SECRET_USERNAME: image_pull_secret_username,
        REQUIRED_SECRET_VALUES.IMAGE_PULL_SECRET_PASSWORD: image_pull_secret_password,
        REQUIRED_SECRET_VALUES.IMAGE_PULL_SECRET_EMAIL: image_pull_secret_email,
    }


def missing_secrets(secret_dict):
    missing_secrets_list = []
    for key, value in REQUIRED_SECRET_VALUES.items():
        if value not in secret_dict:
            missing_secrets_list.append(key)
    return missing_secrets_list


# Building a context manager for adding a path to sys only when necessary
class add_path:
    def __init__(self, path: Path):
        self.path = str(path)

    def __enter__(self):
        sys.path.insert(0, self.path)

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            sys.path.remove(self.path)
        except ValueError:
            pass
