import logging
from pathlib import Path
import jupytext


def get_pipeline_path(same_config_path, same_config_file_contents):
    """Returns absolute value of the pipeline path relative to current file execution"""
    return str(Path.joinpath(Path(same_config_path), same_config_file_contents["pipeline"]["package"]))


def convert_notebook_to_text(notebook_path):
    logging.info(f"Using notebook from here: {notebook_path}")
    notebook_raw_text = ""
    try:
        notebook_file_handle = Path(notebook_path)
        notebook_raw_text = notebook_file_handle.read_text(encoding="ascii")
    except FileNotFoundError:
        logging.fatal(f"No notebook found at {notebook_path}")
        exit(1)

    ntbk_object = jupytext.reads(notebook_raw_text)
    return jupytext.writes(ntbk_object, fmt="py:percent")
