import logging
from pathlib import Path
import jupytext
from cli.same.objects import Step


def get_pipeline_path(same_config_path, same_config_file_contents) -> str:
    """Returns absolute value of the pipeline path relative to current file execution"""
    return str(Path.joinpath(Path(same_config_path), same_config_file_contents["pipeline"]["package"]))


def read_notebook(notebook_path) -> dict:
    logging.info(f"Using notebook from here: {notebook_path}")
    try:
        notebook_file_handle = Path(notebook_path)
        ntbk_dict = jupytext.read(str(notebook_file_handle))
    except FileNotFoundError:
        logging.fatal(f"No notebook found at {notebook_path}")
        exit(1)

    return ntbk_dict


def get_steps(notebook_dict: dict) -> dict:

    i = 0
    return_steps = {}

    # Start with a default step (if no step tags detected, everything will be added here)
    this_step = Step()
    this_step.index = 0
    this_step.name = "same_step_000"
    code_buffer = []

    for num, cell in enumerate(notebook_dict["cells"]):
        if len(cell["metadata"]) > 0 and len(cell["metadata"]["tags"]) > 0:
            for tag in cell["metadata"]["tags"]:
                if tag.startswith("same_step_"):
                    # Skip over this logic if it's the zeroth cell (cleaner way to do this? probably)
                    if num > 0:
                        # New step detected. First, we'll add the existing step to the return steps
                        this_step.code = "\n".join(code_buffer)
                        return_steps[this_step.name] = this_step

                        # This will cause a bug later - we basically ignore whatever
                        # people have set as the step number and just increment it. Further, we
                        # also only support linear DAGs.
                        # TODO: When we actually build a DAG parser, we should change
                        # index to something more DAG meaningful.
                        i += 1

                        code_buffer = []
                        this_step = Step()
                        this_step.index = i

                        # left padding numbering because it's prettier
                        this_step.name = f"same_step_{i:03}"
                elif str.startswith(tag, "cache="):
                    this_step.cache_value = str.split(tag, "=")[1]
                elif str.startswith(tag, "environment="):
                    this_step.environment_name = str.split(tag, "=")[1]
                else:
                    this_step.tags.append(tag)

        code_buffer.append("\n".join(jupytext.cell_to_text.LightScriptCellExporter(cell, "py").source))

    this_step.code = "\n".join(code_buffer)
    return_steps[this_step.name] = this_step

    return return_steps
