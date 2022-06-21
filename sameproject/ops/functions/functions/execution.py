from types import ModuleType
from typing import Optional
from tempfile import mktemp
import importlib
import dill
import sys


# Private name used by sameproject for temporary modules. Must remain the same
# for all executions so that loading session_context doesn't clobber module
# names and cause problems with the loader.
_module_name = "__sameproject_user_code__"


def execute(code: str, session_context: Optional[bytes]) -> bytes:
    """
    Runs the given code in a fresh execution frame, with session context
    provided by a dill.dump_session(...) pickle. Returns the resulting
    session context so that execution can be chained for multiple steps.
    """
    # Writes the module code to a temporary python file:
    module_path = mktemp(".py")
    with open(module_path, "w") as file:
        file.write(code)

    # Dynamically load the module into memory:
    spec = importlib.util.spec_from_file_location(_module_name, module_path)
    module = importlib.util.module_from_spec(spec)

    # If we have a session context, load it into the newly created module:
    context_path = mktemp()
    if session_context is not None:
        with open(context_path, "wb") as file:
            file.write(session_context)
        with cache_module(module, _module_name):
            dill.load_session(context_path, main=module)

    # Execute the module and return the resulting session context:
    spec.loader.exec_module(module)
    with cache_module(module, _module_name):
        dill.dump_session(context_path, main=module)
    with open(context_path, "rb") as file:
        return file.read()


def load(session_context: bytes) -> ModuleType:
    """
    Loads the given session context as a dictionary of attributes. Can be used
    to inspect the results of an execution run.
    """
    # Write an empty module to a temporary python file:
    module_path = mktemp(".py")
    with open(module_path, "w") as file:
        file.write("")

    # Dynamically load the module into memory:
    spec = importlib.util.spec_from_file_location(_module_name, module_path)
    module = importlib.util.module_from_spec(spec)

    # Load session context into the new module:
    context_path = mktemp()
    with open(context_path, "wb") as file:
        file.write(session_context)
    with cache_module(module, _module_name):
        dill.load_session(context_path, main=module)

    return module


class cache_module:
    """Context manager that temporarily caches a module in sys.modules."""
    def __init__(self, module, module_name):
        self.module = module
        self.module_name = module_name

    def __enter__(self):
        sys.modules[self.module_name] = self.module

    def __exit__(self, type, value, traceback):
        del sys.modules[self.module_name]
