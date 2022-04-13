from pathlib import Path
from sameproject.ops import helpers

import kfp
from pprint import pprint

import logging

import importlib


def deploy_function(compiled_path: Path, root_module_name: str):
    import sys

    # Doing this inside a context manager because we only need to add this path during this execution
    with helpers.add_path(str(compiled_path)):
        root_module = importlib.import_module(root_module_name)

        # TODO: support kubeflow-specific config like kubeflow namespace
        kfp_client = kfp.Client()
        return kfp_client.create_run_from_pipeline_func(root_module.root, arguments={})
