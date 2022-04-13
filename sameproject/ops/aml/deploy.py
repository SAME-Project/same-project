from sameproject.ops import helpers
import importlib


def deploy(compiled_path: str, root_module_name: str):
    with helpers.add_path(str(compiled_path)):
        root_module = importlib.import_module(root_module_name)
        root_module.root()
