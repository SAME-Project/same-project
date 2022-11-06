from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from typing import Tuple
from uuid import uuid4
from base64 import urlsafe_b64encode
import logging
import os
import time

from sameproject.data.step import Step
from sameproject.ops import helpers
import sameproject.ops.explode


from sameproject.ops.code import get_magic_lines, remove_magic_lines, get_installable_packages
from sameproject.data.config import SameConfig
from sameproject.data import Step
from typing import Tuple, List
from io import BufferedReader
from pathlib import Path
import jupytext
import logging
import click


def compile(config: SameConfig, target: str) -> Tuple[Path, str]:
    notebook = read_notebook(config.notebook.path)
    all_steps = get_steps(notebook, config)

    return render(
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
            code=remove_magic_lines(this_step_code),
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
        if "metadata" not in cell:  # sanity check
            continue

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

        if cell["cell_type"] == "code":  # might be a markdown cell
            code_buffer.append("\n".join(jupytext.cell_to_text.LightScriptCellExporter(cell, "py").source))

    this_step_code = "\n".join(code_buffer)
    all_code += "\n" + this_step_code
    save_step()

    magic_lines = get_magic_lines(all_code)
    if len(magic_lines) > 0:
        magic_lines_string = "\n".join(magic_lines)
        logging.warning(f"""Notebook contains magic lines, which will be ignored:\n{magic_lines_string}""")

        # Remove magic lines from code so that we can continue:
        all_code = remove_magic_lines(all_code)

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
        if cell["cell_type"] != "code":
            continue

        code.append("\n".join(
            jupytext.cell_to_text.LightScriptCellExporter(cell, "py").source
        ))

    return "\n".join(code)


ocean_step_template = "step.jinja"


def render(compile_path: str, steps: list, same_config: dict) -> Tuple[Path, str]:
    """Renders the notebook into a root file and a series of step files according to the target requirements. Returns an absolute path to the root file for deployment."""
    
    templateDir = os.path.dirname(os.path.abspath(__file__))
    templateLoader = FileSystemLoader(templateDir)
    env = Environment(trim_blocks=True, loader=templateLoader)

    root_file_string = _build_step_file(env, next(iter(steps.values())), same_config)
    root_pipeline_name = f"root_pipeline_{uuid4().hex.lower()}"
    root_path = Path(compile_path) / f"{root_pipeline_name}.py"
    helpers.write_file(root_path, root_file_string)
    
    # for storing in the docker image
    docker_path = same_config['notebook']['path'][:-5] + 'py'
    helpers.write_file(docker_path, root_file_string)
    os.remove(same_config['notebook']['path'])
    return (compile_path, root_file_string) # note: root_file_string replaced root_pipeline_name

def _build_step_file(env: Environment, step: Step, same_config) -> str:
    with open(sameproject.ops.explode.__file__, "r") as f:
        explode_code = f.read()

    requirements_file = None
    if "requirements_file" in step:
        requirements_file = urlsafe_b64encode(bytes(step.requirements_file, "utf-8")).decode()

    memory_limit = same_config.runtime_options.get(
        "serialisation_memory_limit",
        512 * 1024 * 1024,  # 512MB
    )

    same_env = same_config.runtime_options.get(
        "same_env",
        "default",
    )

    step_contract = {
        "name": step.name,
        "same_env": same_env,
        "memory_limit": memory_limit,
        "unique_name": step.unique_name,
        "requirements_file": requirements_file,
        "user_code": step.code,
        "explode_code": urlsafe_b64encode(bytes(explode_code, "utf-8")).decode(),
        "same_yaml": urlsafe_b64encode(bytes(same_config.to_yaml(), "utf-8")).decode(),
    }

    return env.get_template(ocean_step_template).render(step_contract)

if __name__ == "__main__":
    compile("same.yaml", "notebook.ipynb")