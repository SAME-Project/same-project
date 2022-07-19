import json
import os
import sys

from inspect import getmembers, isfunction
from importlib import import_module
from pathlib import Path
from shutil import copyfile
from subprocess import run
from tempfile import TemporaryDirectory
from types import ModuleType
from typing import Dict, Callable, List

from .constants import DEPENDENCIES_ATTR, ENTRYPOINT_ATTR, PIPELINE_ENV_VAR


def get_dependencies(entrypoint: Callable) -> List[str]:
    return getattr(entrypoint, DEPENDENCIES_ATTR, [])


def in_container() -> bool:
    return bool(os.environ.get(PIPELINE_ENV_VAR))


def is_entrypoint(func: Callable) -> bool:
    return hasattr(func, ENTRYPOINT_ATTR)


def pip_list() -> Dict[str, str]:
    process = run(["pip", "list", "--format", "json"], capture_output=True)
    packages = json.loads(process.stdout)
    return {pkg["name"]: pkg["version"] for pkg in packages}


def script_to_module(script: os.PathLike) -> ModuleType:
    module_name = "__pipeline_script"
    with TemporaryDirectory() as tempdir:
        test_script = Path(tempdir, f"{module_name}.py")
        copyfile(script, test_script)

        sys.path.append(tempdir)
        try:
            module = import_module(module_name)
            del sys.modules[module_name]
        except ImportError as err:
            print (
                "Could not import the script. "
                "The script must be entirely self contained. "
                "Are all your dependencies installed? "
            )
            raise err
        assert sys.path.pop() == tempdir

    return module


def get_entrypoint(module: ModuleType) -> Callable:
    """Returns the only function within the specified module marked with the
    @pipeline decorator.

    Args:
        module: The module to search.

    Raises:
        RuntimeError: If none or multiple entrypoints are found.

    Returns:
        Entrypoint function to the pipeline.
    """
    entrypoints = [
        func for _name, func in getmembers(module, isfunction)
        if is_entrypoint(func)
    ]
    if not entrypoints:
        raise RuntimeError(
            "No entrypoints found. "
            "Did you mark a function with the @pipeline decorator?"
        )
    if len(entrypoints) > 1:
        raise RuntimeError(
            "Multiple entrypoints found. "
            "Please only mark a single function with the @pipeline decorator."
        )
    return entrypoints[0]