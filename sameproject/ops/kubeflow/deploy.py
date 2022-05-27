from sameproject.data.config import SameConfig
from sameproject.ops import helpers
from pathlib import Path
import importlib
import kfp
import sys
import sys
from pathlib import Path
from kfp.compiler import Compiler
from kfp.v2 import compiler
import importlib
import os
from kfp.v2 import dsl
from kfp.v2.dsl import (
    component,
    Output,
    HTML
)
from google.cloud import aiplatform

def deploy(base_path: Path, root_file: str, config: SameConfig):
    with helpers.add_path(str(base_path)):
        root_module = importlib.import_module(root_file)  # python module

        kfp_client = kfp.Client()  # only supporting 'kubeflow' namespace
        return kfp_client.create_run_from_pipeline_func(
            root_module.root,
            arguments={},
            # You can optionally override your pipeline_root when submitting the run too:
            # pipeline_root='gs://my-pipeline-root/example-pipeline',
            # arguments={
            #     'url': 'https://storage.googleapis.com/ml-pipeline-playground/iris-csv-files.tar.gz'
            # }
        )