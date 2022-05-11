from sameproject.ops.notebooks import read_notebook
from sameproject.data.config import SameConfig
from typing import Optional, Callable, List
from pathlib import Path
from box import Box
import pytest

# Registry of fully-configured notebooks, same configs and requirements.txt
# files. Tests can request notebooks as pytest fixtures by name or group,
# and each notebook comes with a success condition that should validated by
# the test to ensure it has been executed correctly.
_registry = {}


def get_by_name(name: str) -> Callable:
    """
    Returns a pytest decorator for the given name - see _get_decorator().
    """
    if name not in _registry:
        raise Exception("Attempted to fetch non-existent testdata '{name}'.")

    return _get_decorator([_registry[name]])


def get_by_group(group: str) -> Callable:
    """
    Returns a pytest decorator for the given group - see _get_decorator().
    """
    entries = []
    for entry in _registry.values():
        if entry.group == group:
            entries.append(entry)

    if len(entries) == 0:
        raise Exception("Attempted to fetch non-existent testdata group '{group}'.")

    return _get_decorator(entries)


def _get_decorator(entries: List[dict]) -> Callable:
    """
    Returns a pytest parametrize decorator for the given list of registry
    entries. Entries are parametrized with the fields 'config', 'notebook',
    'requirements' and 'validation_fn' for the config file, notebook
    dictionary, requirements.txt file and validation function respectively.
    """
    ids = [entry.name for entry in entries]
    params = "config, notebook, requirements, validation_fn"
    data = [(
        entry.config,
        entry.notebook,
        entry.requirements,
        entry.validation_fn,
    ) for entry in entries]

    return pytest.mark.parametrize(params, data, ids)


def _register_notebook(
    name: str,
    desc: str,
    group: str,
    config_path: Path,
    validation_fn: Optional[Callable[dict, bool]] = None,
):
    """Registers a notebook with the given name, path and callback function."""
    if not config_path.exists():
        raise Exception(f"Attempted to register testdata '{name}' with a non-existent notebook: {config_path}")

    with config_path.open("r") as file:
        config = SameConfig.from_yaml(file.read())
        config = config.resolve(config_path.parent)
        config = config.inject_runtime_options()

    nb_path = Path(config.notebook.path)
    if not nb_path.exists():
        raise Exception(f"Attempted to register testdata '{name}' with a non-existent notebook: {nb_path}")
    nb = read_notebook(nb_path)

    req = None
    if "requirements" in config.notebook:
        req_path = Path(config.notebook.requirements)
        if not req_path.exists():
            raise Exception(f"Attempted to register testdata '{name}' with a non-existent requirements.txt: {req_path}")

        with req_path.open("r") as file:
            req = file.read()

    _registry[name] = Box({
        "name": name,
        "desc": desc,
        "group": group,
        "config": config,
        "notebook": nb,
        "requirements": req,
        "validation_fn": validation_fn,
    })
