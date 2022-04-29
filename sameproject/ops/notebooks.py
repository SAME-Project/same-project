from sameproject.ops.code import get_magic_lines, get_installable_packages
from sameproject.data.config import SameConfig
from sameproject.data import Step
from typing import Tuple, List
from io import BufferedReader
from pathlib import Path
import sameproject.ops.backends as backends
import jupytext
import logging
import click


def compile(same_run_config: SameConfig, execution_target: str) -> Tuple[Path, str]:
    notebook = read_notebook(same_run_config.notebook.path)
    all_steps = get_steps(notebook, same_run_config)

    return backends.render(execution_target=execution_target, steps=all_steps, same_run_config=same_run_config)


def read_notebook(notebook_path) -> dict:
    logging.info(f"Using notebook from here: {notebook_path}")
    try:
        notebook_file_handle = Path(notebook_path)
        ntbk_dict = jupytext.read(str(notebook_file_handle))
    except FileNotFoundError:
        logging.fatal(f"No notebook found at {notebook_path}")
        exit(1)

    return ntbk_dict


def get_name(notebook: dict, default="") -> str:
    """Returns a notebook's configured name, or a default if none is found."""
    if "metadata" not in notebook or "name" not in notebook["metadata"]:
        return default

    return notebook["metadata"]["name"]


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
    Given a notebook (as a dict), get a list of Step objects, sorted by their
    index in the notebook.
    """
    steps_dict = get_steps(notebook, config)
    steps = list(steps_dict.values())
    steps_sorted_by_index = sorted(steps, key=lambda x: x.index)
    return steps_sorted_by_index


def get_code(notebook: dict) -> str:
    """Combines and returns all python code in the given notebook."""
    if "cells" not in notebook:
        return ""

    code = []
    for cell in notebook["cells"]:
        code.append("\n".join(
            jupytext.cell_to_text.LightScriptCellExporter(cell, "py").source
        ))

    return "\n".join(code)
