from cli import same
from objects.step import Step
from pathlib import Path
from cli.same import helpers
from jinja2 import Environment, FileSystemLoader, select_autoescape

import kfp
from pprint import pprint

import logging


def deploy_function(compiled_path: str):
    import sys

    sys.path.append(compiled_path)

    from root_pipeline import root

    kfp_client = kfp.Client()
    kfp_client.create_run_from_pipeline_func(root, arguments={})
