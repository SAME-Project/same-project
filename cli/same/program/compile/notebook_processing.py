import logging
from pathlib import Path
import jupytext
from typing import List
import re
from cli.same.objects import Slice, Step


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


def get_tags_from_tag_line(all_tag_lines):
    pass


def parse_raw_slices_into_list(raw_slice: Slice, all_tags: list, code: str) -> Slice:
    """Parses a code into a slice object and assigns tags properly. There's
    almost certainly a better way to do this (ideally as a lexer/parser)."""

    for slice_tag in all_tags:
        # Drop tags into one  of three categories (should be more extensible in the future)
        if str.startswith(slice_tag, "same_step_"):
            current_step_name = slice_tag
            current_index = str.split(slice_tag, "_")[2]
            raw_slice.name = current_step_name
            raw_slice.index = current_index
        elif str.startswith(slice_tag, "cache="):
            raw_slice.cache_value = str.split(slice_tag, "=")[1]
        elif str.startswith(slice_tag, "environment="):
            raw_slice.environment_name = str.split(slice_tag, "=")[1]
        else:
            raw_slice.tags.append(slice_tag)

    raw_slice.code = raw_slice.code

    return raw_slice


def find_all_slices(notebook_text) -> List:
    """Look for all lines in the file with tags in them."""

    # Need to enable multiline for beginning of the line checking - (?m)
    # Looking for something of the format:
    # - ...
    # or
    # # + tags=[...]
    # tag_regex = r"(?m)^\s*# (?:\+|\-) ?(.*?)$"

    # Simplifying to just look for lines with tags for now until we
    # build a much better lexer/parser
    tag_regex = r"(?m)^\s*# (?:\+|\-) tags\=.*?$"

    # First we look for all Jupytext generated lines that look like they might have tags in them
    all_tag_lines = re.findall(tag_regex, notebook_text)
    all_slices_content = re.split(tag_regex, notebook_text)

    combined_slices = []
    i = 0

    # If the entire notebook only has one slice, then we'll treat it
    # as a single step. Could either be because there's only one tag
    # or no tags.
    if len(all_slices_content) <= 1:
        logging.debug("no tag separators found in the file - treating the entire file as a single step.")
        slice = Slice()
        slice.name = "same_step_0"
        slice.index = 0
        slice.code = notebook_text
        slice.tags = None

        combined_slices.append(slice)
    else:
        logging.debug("Found at least one step with a 'same_step_#' format, breaking up the file")

        # Then we look through each tag line to see if there are any interesting tags in them
        for i, slice_content in enumerate(all_slices_content):
            # Start with sane defaults (i = 0, same_step_0)
            slice = Slice()

            # When splitting cells, you can often have a zero cell
            # at the start, so skipping it
            if (i == 0) and (slice_content == ""):
                continue

            all_tags = get_tags_from_tag_line(all_tag_lines[i - 1])
            for tag in all_tags:
                if tag.startswith("same_step_"):
                    # This will cause a bug later - we basically ignore whatever
                    # people have set as the index and just increment it. Further, we
                    # also only support linear DAGs.
                    # TODO: When we actually build a DAG parser, we should change
                    # index to something more DAG meaningful.
                    # Just setting it to 1 to indicate this is a step change, don't
                    # care about the actual number right now
                    slice.index = 1
                    slice.name = tag
                else:
                    slice.tags.append(tag)
            slice = parse_raw_slices_into_list(slice, all_tags, slice_content)
            combined_slices.append(slice)

    return combined_slices


def combine_slices_into_steps(all_slices: list[Slice]) -> list[Step]:
    return_steps = {}
    current_step_name = all_slices[0].name
    current_step_index = 1
    for i, slice in enumerate(all_slices):
        logging.debug(f"Current step: {slice.name}")
        logging.debug(f"Current slice: {slice.code}")

        # Second half of the bug around indexing - when we detect
        # the index has changed (is different than the current index
        # and not -1), we create a new step and move forward.

        # Skipping assignment if i is 0, so we start with 1
        if (slice.index == 1) and i != 0:
            current_step_index += 1

        this_step = return_steps.get(current_step_name, Step())

        this_step.code += slice.code
        this_step.name = current_step_name
        this_step.cache_value = slice.cache_value
        this_step.environment_name = slice.environment_name
        this_step.tags = slice.tags
        this_step.index = current_step_index
        return_steps[slice.name] = this_step

    return return_steps


def find_all_steps(notebook_text) -> List:
    all_slices = find_all_slices(notebook_text)

    return combine_slices_into_steps(all_slices)
