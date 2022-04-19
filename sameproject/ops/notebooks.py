from sameproject.ops.helpers import REQUIRED_SECRET_VALUES, missing_secrets, lowerAlphaNumericOnly
from .code import get_magic_lines, get_installable_packages
from sameproject.data.config import SameConfig
from sameproject.data import Step
from typing import Tuple, List
from io import BufferedReader
from pathlib import Path
import sameproject.ops.backends
import jupytext
import logging
import click


def compile(same_file: BufferedReader, target: str, secret_dict: dict = {}, aml_dict: dict = {}) -> Tuple[Path, str]:
    same_config = SameConfig(same_file)
    same_config = _add_secrets_to_same_config(secret_dict, same_config)
    same_config = _add_aml_values_to_same_config(aml_dict, same_config)

    notebook_path = get_notebook_path(same_file.name, same_config)
    notebook = read_notebook(notebook_path)
    all_steps = get_steps(notebook)

    return sameproject.ops.backends.render(
        target=target,
        steps=all_steps,
        same_config=same_config
    )


def get_notebook_path(same_config_path, same_config_file_contents) -> str:
    """Returns absolute value of the pipeline path relative to current file execution"""
    return str(Path.joinpath(Path(same_config_path).parent, same_config_file_contents["notebook"]["path"]))


def read_notebook(notebook_path) -> dict:
    logging.info(f"Using notebook from here: {notebook_path}")
    try:
        notebook_file_handle = Path(notebook_path)
        ntbk_dict = jupytext.read(str(notebook_file_handle))
    except FileNotFoundError:
        logging.fatal(f"No notebook found at {notebook_path}")
        exit(1)

    return ntbk_dict


def get_steps(notebook: dict) -> dict:
    """
    Given a notebook (in the form of a dictionary), converts it into a dictionary of Steps. The key is the Step name
    and the value is the Step object.
    """
    return_steps = {}

    # Start with a default step (if no step tags detected, everything will be added here)
    this_step = Step()
    this_step.index = 0
    this_step.name = "same_step_000"
    code_buffer = []

    all_code = ""

    for num, cell in enumerate(notebook["cells"]):
        if len(cell["metadata"]) > 0 and "tags" in cell["metadata"] and len(cell["metadata"]["tags"]) > 0:
            for tag in cell["metadata"]["tags"]:
                if tag.startswith("same_step_"):
                    # Skip over this logic if it's the zeroth cell (cleaner way to do this? probably)
                    if num > 0:
                        # New step detected. First, we'll add the existing step to the return steps
                        this_step.code = "\n".join(code_buffer)
                        all_code += "\n" + this_step.code
                        return_steps[this_step.name] = this_step
                        step_tag_num = int(tag.split("same_step_")[1])

                        code_buffer = []
                        this_step = Step()
                        this_step.index = step_tag_num

                        # left padding numbering because it's prettier
                        this_step.name = f"same_step_{step_tag_num:03}"
                elif str.startswith(tag, "cache="):
                    this_step.cache_value = str.split(tag, "=")[1]
                elif str.startswith(tag, "environment="):
                    this_step.environment_name = str.split(tag, "=")[1]
                else:
                    this_step.tags.append(tag)

        code_buffer.append("\n".join(jupytext.cell_to_text.LightScriptCellExporter(cell, "py").source))

    this_step.code = "\n".join(code_buffer)
    all_code += "\n" + this_step.code
    return_steps[this_step.name] = this_step

    magic_lines = get_magic_lines(all_code)
    if len(magic_lines) > 0:
        magic_lines_string = "\n".join(magic_lines)
        logging.fatal(
            f"""
We cannot continue because the following lines cannot be converted into standard python code. Please correct them:
{ magic_lines_string }"""
        )
        raise SyntaxError(f"Magic lines are not supported:\n{magic_lines_string}")

    for k in return_steps:
        return_steps[k].packages_to_install = get_installable_packages(all_code)

    return return_steps


def get_sorted_list_of_steps(notebook: dict) -> list:
    """
    Given a notebook (as a dict), get a list of Step objects, sorted by their index in the notebook.
    """
    steps_dict = get_steps(notebook)
    steps = list(steps_dict.values())
    steps_sorted_by_index = sorted(steps, key=lambda x: x.index)
    return steps_sorted_by_index


def _add_secrets_to_same_config(secret_dict, same_config) -> dict:
    # Start by checking for secrets (if something is hinky, no reason to go forward).

    # Cowardly, we're only supporting one secret_dict right now, meaning all private images need to be pulled
    # from a single registry. This is probably good enough for a long time.

    # I'm also not error checking - assuming if someone has set five values, then we're good, but who knows where
    # that could fall down.
    num_of_secrets = 0
    for k in secret_dict:
        if secret_dict[k] != "":
            num_of_secrets += 1

    missing_secrets_dict = {}

    if secret_dict.get(REQUIRED_SECRET_VALUES.IMAGE_PULL_SECRET_NAME, None) is None:
        secret_dict[REQUIRED_SECRET_VALUES.IMAGE_PULL_SECRET_NAME] = same_config.metadata.name

    # Make the secret name safe for a Secret (if the rest of the secret name is not set, don't worry about it)
    secret_dict[REQUIRED_SECRET_VALUES.IMAGE_PULL_SECRET_NAME] = lowerAlphaNumericOnly(
        secret_dict[REQUIRED_SECRET_VALUES.IMAGE_PULL_SECRET_NAME]
    )

    # Below, we're going to inject these secrets into the in-memory struct of same_config, which will later render it into the compiled template.
    # This only makes sense if there are environments and one of them is private
    if same_config.get("environments", None) is not None:
        for name in same_config.environments:
            if same_config.environments[name].get("private_registry", False):
                these_missing_secrets = missing_secrets(secret_dict)
                if len(these_missing_secrets) > 0:
                    missing_secrets_dict[name] = these_missing_secrets
                else:
                    same_config.environments[name]["credentials"] = {}
                    same_config.environments[name].credentials[
                        REQUIRED_SECRET_VALUES.IMAGE_PULL_SECRET_NAME
                    ] = secret_dict[REQUIRED_SECRET_VALUES.IMAGE_PULL_SECRET_NAME]
                    same_config.environments[name].credentials[
                        REQUIRED_SECRET_VALUES.IMAGE_PULL_SECRET_REGISTRY_URI
                    ] = secret_dict[REQUIRED_SECRET_VALUES.IMAGE_PULL_SECRET_REGISTRY_URI]
                    same_config.environments[name].credentials[
                        REQUIRED_SECRET_VALUES.IMAGE_PULL_SECRET_USERNAME
                    ] = secret_dict[REQUIRED_SECRET_VALUES.IMAGE_PULL_SECRET_USERNAME]
                    same_config.environments[name].credentials[
                        REQUIRED_SECRET_VALUES.IMAGE_PULL_SECRET_PASSWORD
                    ] = secret_dict[REQUIRED_SECRET_VALUES.IMAGE_PULL_SECRET_PASSWORD]
                    same_config.environments[name].credentials[
                        REQUIRED_SECRET_VALUES.IMAGE_PULL_SECRET_EMAIL
                    ] = secret_dict[REQUIRED_SECRET_VALUES.IMAGE_PULL_SECRET_EMAIL]

    if len(missing_secrets_dict):
        click.echo(
            "You set an environment with as 'private' but did not supply all the necessary secrets. Please correct this:"
        )
        for k in missing_secrets_dict:
            these_missing_secrets = missing_secrets_dict[k]
            if len(these_missing_secrets) > 0:
                click.echo(f"\t{k}:")
                for v in these_missing_secrets:
                    click.echo(f"\t\t{v}:")
        raise ValueError("Missing secrets for declared private registry.")

    return same_config


def _add_aml_values_to_same_config(aml_dict, same_config) -> dict:
    same_config["aml"] = {}
    for k in aml_dict.keys():
        same_config["aml"][k] = aml_dict[k]

    return same_config
