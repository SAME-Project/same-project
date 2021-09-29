import ast
import logging
from pathlib import Path
import jupytext
from .context import Step
from cli.same.stdlib import stdlibs
from cli.same.mapping import library_mapping
import re
import traceback

import backends.executor
from io import BufferedReader
from same_config import SameConfig

REGEXP = [re.compile(r"^import (.+)$"), re.compile(r"^from ((?!\.+).*?) import (?:.*)$")]


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


def get_steps(notebook_dict: dict) -> dict[Step]:
    """Given a notebook (in the form of a dictionary), converts it into a dictionary of Steps. The key is the Step name
    and the value is the Step object.
    """
    i = 0
    return_steps = {}

    # Start with a default step (if no step tags detected, everything will be added here)
    this_step = Step()
    this_step.index = 0
    this_step.name = "same_step_000"
    code_buffer = []

    all_code = ""

    for num, cell in enumerate(notebook_dict["cells"]):
        if len(cell["metadata"]) > 0 and len(cell["metadata"]["tags"]) > 0:
            for tag in cell["metadata"]["tags"]:
                if tag.startswith("same_step_"):
                    # Skip over this logic if it's the zeroth cell (cleaner way to do this? probably)
                    if num > 0:
                        # New step detected. First, we'll add the existing step to the return steps
                        this_step.code = "\n".join(code_buffer)
                        all_code += "\n" + this_step.code
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
    all_code += "\n" + this_step.code
    return_steps[this_step.name] = this_step

    magic_lines = []
    for i, line in enumerate(all_code.split("\n")):
        if jupytext.magics.is_magic(line, "python"):
            magic_lines.append(f"line {i}: {line}")

    if len(magic_lines) > 0:
        magic_lines_string = "\n".join(magic_lines)
        logging.fatal(
            f"""
We cannot continue because the following lines cannot be converted into standard python code. Please correct them:
{ magic_lines_string }"""
        )
        # After logging.error, what's pythonic? Raising? I'm doing it, but curious.
        raise SyntaxError

    for k in return_steps:
        # If we want to do it just by code block, uncomment the below
        # return_steps[k].packages_to_install = parse_code_block_for_imports(return_steps[k].code)
        return_steps[k].packages_to_install = parse_code_block_for_imports(all_code)

    return return_steps


def get_sorted_list_of_steps(notebook_dict: dict) -> list[Step]:
    """Given a notebook (as a dict), get a list of Step objects, sorted by their index in the notebook."""
    steps_dict = get_steps(notebook_dict)
    steps = list(steps_dict.values())
    steps_sorted_by_index = sorted(steps, key=lambda x: x.index, reverse=True)
    return steps_sorted_by_index


# Liberally stolen^W borrowed from here - https://github.com/bndr/pipreqs/blob/master/pipreqs/pipreqs.py
# Possibly should steal more of these tests? https://github.com/bndr/pipreqs/blob/dea950dd077cd95a8de7aedcd6668b5942e8afc4/tests/test_pipreqs.py
def parse_code_block_for_imports(code: str) -> list[str]:
    imports = set()
    raw_imports = set()
    candidates = []
    ignore_errors = False

    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for subnode in node.names:
                    raw_imports.add(subnode.name)
            elif isinstance(node, ast.ImportFrom):
                raw_imports.add(node.module)
    except Exception as exc:
        logging_error_text = "Failed on detecting imports"
        if ignore_errors:
            traceback.print_exc(exc)
            logging.warn(logging_error_text)
        else:
            logging.error(logging_error_text)
            raise exc

    # Clean up imports
    for name in [n for n in raw_imports if n]:
        # Sanity check: Name could have been None if the import
        # statement was as ``from . import X``
        # Cleanup: We only want to first part of the import.
        # Ex: from django.conf --> django.conf. But we only want django
        # as an import.
        cleaned_name, _, _ = name.partition(".")
        imports.add(cleaned_name)

    packages = imports - (set(candidates) & imports)
    logging.debug("Found packages: {0}".format(packages))

    data = {x.strip() for x in stdlibs}

    return_list = list(packages - data)

    # Clean up package names with a manual lookup
    mapped_list = get_pkg_names(return_list)

    return mapped_list


def get_pkg_names(pkgs: list[str]) -> list[str]:
    """Get PyPI package names from a list of imports.
    Args:
        pkgs (List[str]): List of import names.
    Returns:
        List[str]: The corresponding PyPI package names.
    """
    result = set()

    # Clean up if there are empty lines
    library_mapping_lines = [s for s in library_mapping.splitlines() if s]

    data = dict(x.strip().split(":") for x in library_mapping_lines)
    for pkg in pkgs:
        # Look up the mapped requirement. If a mapping isn't found,
        # simply use the package name.
        result.add(data.get(pkg, pkg))
    # Return a sorted list for backward compatibility.
    return sorted(result, key=lambda s: s.lower())


def compile(same_file: BufferedReader, target: str) -> str:
    same_config = SameConfig(same_file)

    notebook_path = get_notebook_path(same_file.name, same_config)  # noqa: F841

    notebook_dict = read_notebook(notebook_path)

    all_steps = get_steps(notebook_dict)

    return backends.executor.render(target=target, steps=all_steps, same_config=same_config)

    # compileProgramCmd.Flags().String("image-pull-secret-server", "", "Image pull server for any private repos (only one server currently supported for all private repos)")
    # compileProgramCmd.Flags().String("image-pull-secret-username", "", "Image pull username for any private repos (only one username currently supported for all private repos)")
    # compileProgramCmd.Flags().String("image-pull-secret-password", "", "Image pull password for any private repos (only one password currently supported for all private repos)")
    # compileProgramCmd.Flags().String("image-pull-secret-email", "", "Image pull email for any private repos (only one email currently supported for all private repos)")
