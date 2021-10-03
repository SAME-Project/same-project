from cli import same
from objects.step import Step
from pathlib import Path
from cli.same import helpers
from jinja2 import Environment, FileSystemLoader, select_autoescape


import logging


def deploy_function(compiled_path: str):
    import sys

    # Doing this inside a context manager because we only need to add this path during this execution
    with helpers.add_path(str(compiled_path)):
        from root_pipeline import root  # type: ignore noqa

        root()
