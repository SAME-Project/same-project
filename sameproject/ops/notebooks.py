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


def compile(config_file: BufferedReader, target: str, secret_dict: dict = {}, aml_dict: dict = {}) -> Tuple[Path, str]:
    # TODO: Make the config box immutable.
    config = SameConfig.from_yaml(config_file.read(), frozen_box=False)
    config = config.resolve(Path(config_file.name).parent)
    config = _add_secrets_to_config(secret_dict, config)
    config = _add_aml_values_to_config(aml_dict, config)

    notebook = read_notebook(config.notebook.path)
    all_steps = get_steps(notebook, config)

    return sameproject.ops.backends.render(
        target=target,
        steps=all_steps,
        config=config
    )


def read_notebook(notebook_path) -> dict:
    logging.info(f"Using notebook from here: {notebook_path}")
    try:
        notebook_file_handle = Path(notebook_path)
        ntbk_dict = jupytext.read(str(notebook_file_handle))
    except FileNotFoundError:
        logging.fatal(f"No notebook found at {notebook_path}")
        exit(1)

    return ntbk_dict


def get_steps(notebook: dict, config: SameConfig) -> dict:
    """Parses the code in a notebook into a series of SAME execution steps."""

    steps = {}
    all_code = ""
    code_buffer = []
    this_step_index = 0
    this_step_name = "same_step_000"
    this_step_code = ""
    this_step_cache_value = "P0D"
    this_step_environment_name = "default"
    this_step_tags = []

    def save_step():
        steps[this_step_name] = Step(
            name=this_step_name,
            code=this_step_code,
            index=this_step_index,
            cache_value=this_step_cache_value,
            environment_name=this_step_environment_name,
            tags=this_step_tags,
            parameters=[],
            packages_to_install=[],
            frozen_box=False,  # TODO: make immutable
        )

        # Inject pip requirements file if configured:
        if "requirements" in config.notebook:
            with open(config.notebook.requirements, "r") as file:
                steps[this_step_name].requirements_file = file.read()

    for num, cell in enumerate(notebook["cells"]):
        if len(cell["metadata"]) > 0 and "tags" in cell["metadata"] and len(cell["metadata"]["tags"]) > 0:
            for tag in cell["metadata"]["tags"]:
                if tag.startswith("same_step_"):
                    if num > 0:  # don't create empty step
                        this_step_code = "\n".join(code_buffer)
                        all_code += "\n" + this_step_code
                        save_step()

                        code_buffer = []
                        step_tag_num = int(tag.split("same_step_")[1])
                        this_step_index = step_tag_num
                        this_step_name = f"same_step_{step_tag_num:03}"
                        this_step_code = ""
                        this_step_cache_value = "P0D"
                        this_step_environment_name = "default"
                        this_step_tags = []

                elif str.startswith(tag, "cache="):
                    this_step_cache_value = str.split(tag, "=")[1]
                elif str.startswith(tag, "environment="):
                    this_step_environment_name = str.split(tag, "=")[1]
                else:
                    this_step_tags.append(tag)

        code_buffer.append("\n".join(jupytext.cell_to_text.LightScriptCellExporter(cell, "py").source))

    this_step_code = "\n".join(code_buffer)
    all_code += "\n" + this_step_code
    save_step()

    magic_lines = get_magic_lines(all_code)
    if len(magic_lines) > 0:
        magic_lines_string = "\n".join(magic_lines)
        logging.fatal(
            f"""
We cannot continue because the following lines cannot be converted into standard python code. Please correct them:
{ magic_lines_string }"""
        )
        raise SyntaxError(f"Magic lines are not supported:\n{magic_lines_string}")

    for k in steps:
        steps[k].packages_to_install = get_installable_packages(all_code)

    return steps


def get_sorted_list_of_steps(notebook: dict, config: SameConfig) -> list:
    """
    Given a notebook (as a dict), get a list of Step objects, sorted by their index in the notebook.
    """
    steps_dict = get_steps(notebook, config)
    steps = list(steps_dict.values())
    steps_sorted_by_index = sorted(steps, key=lambda x: x.index)
    return steps_sorted_by_index


def _add_secrets_to_config(secret_dict, config) -> dict:
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
        secret_dict[REQUIRED_SECRET_VALUES.IMAGE_PULL_SECRET_NAME] = config.metadata.name

    # Make the secret name safe for a Secret (if the rest of the secret name is not set, don't worry about it)
    secret_dict[REQUIRED_SECRET_VALUES.IMAGE_PULL_SECRET_NAME] = lowerAlphaNumericOnly(
        secret_dict[REQUIRED_SECRET_VALUES.IMAGE_PULL_SECRET_NAME]
    )

    # Below, we're going to inject these secrets into the in-memory struct of config, which will later render it into the compiled template.
    # This only makes sense if there are environments and one of them is private
    if config.get("environments", None) is not None:
        for name in config.environments:
            if config.environments[name].get("private_registry", False):
                these_missing_secrets = missing_secrets(secret_dict)
                if len(these_missing_secrets) > 0:
                    missing_secrets_dict[name] = these_missing_secrets
                else:
                    config.environments[name]["credentials"] = {}
                    config.environments[name].credentials[
                        REQUIRED_SECRET_VALUES.IMAGE_PULL_SECRET_NAME
                    ] = secret_dict[REQUIRED_SECRET_VALUES.IMAGE_PULL_SECRET_NAME]
                    config.environments[name].credentials[
                        REQUIRED_SECRET_VALUES.IMAGE_PULL_SECRET_REGISTRY_URI
                    ] = secret_dict[REQUIRED_SECRET_VALUES.IMAGE_PULL_SECRET_REGISTRY_URI]
                    config.environments[name].credentials[
                        REQUIRED_SECRET_VALUES.IMAGE_PULL_SECRET_USERNAME
                    ] = secret_dict[REQUIRED_SECRET_VALUES.IMAGE_PULL_SECRET_USERNAME]
                    config.environments[name].credentials[
                        REQUIRED_SECRET_VALUES.IMAGE_PULL_SECRET_PASSWORD
                    ] = secret_dict[REQUIRED_SECRET_VALUES.IMAGE_PULL_SECRET_PASSWORD]
                    config.environments[name].credentials[
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

    return config


def _add_aml_values_to_config(aml_dict, config) -> dict:
    config["aml"] = {}
    for k in aml_dict.keys():
        config["aml"][k] = aml_dict[k]

    return config
