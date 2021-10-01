from cli import same
from objects.step import Step
from pathlib import Path
from cli.same import helpers
from jinja2 import Environment, FileSystemLoader, select_autoescape

import kfp
from pprint import pprint

import logging


def deploy_function(compiled_path: Path):
    import sys

    original_sys_modules = sys.modules.copy()

    # Doing this inside a context manager because we only need to add this path during this execution
    with helpers.add_path(str(compiled_path)):
        from root_pipeline import root  # type: ignore noqa

        # Only works with the 'kubeflow' namespace for now
        kfp_client = kfp.Client()
        kfp_client.create_run_from_pipeline_func(root, arguments={})
