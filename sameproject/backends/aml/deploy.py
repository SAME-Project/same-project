from sameproject import helpers

import importlib

import logging


def deploy_function(compiled_path: str, root_module_name: str):
    import sys

    # Doing this inside a context manager because we only need to add this path during this execution
    with helpers.add_path(str(compiled_path)):
        root_module = importlib.import_module(root_module_name)  # type: ignore noqa

        root_module.root()  # type: ignore noqa
