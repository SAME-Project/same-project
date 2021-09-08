import logging
from pathlib import Path
import jupytext
from typing import List
import re
from cli.same.objects import Slice, Step


def get_pipeline_path(same_config_path, same_config_file_contents) -> str:
    """Returns absolute value of the pipeline path relative to current file execution"""
    return str(Path.joinpath(Path(same_config_path), same_config_file_contents["pipeline"]["package"]))


def convert_notebook_to_text(notebook_path) -> str:
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


def get_tags_from_tag_line(tag_line: str) -> str:
    """Parse each tag line to see if there is a step identifier in it"""

    found_tags = re.findall(r"tags=\[([^\]]*)\]", tag_line)
    logging.debug(" - Tags found: %v\n", len(found_tags))

    returned_tags = []
    for tag_line in found_tags:
        all_tags_in_line = str.split(tag_line, ",")
        for tag in all_tags_in_line:
            # Clean space and quote from front and back
            tag = tag.strip('" ')
            returned_tags.append(tag)

    return returned_tags


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
