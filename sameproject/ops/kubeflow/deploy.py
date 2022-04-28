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

def deploy(compiled_path: Path, root_module_name: str):
    with helpers.add_path(str(compiled_path)):

        sys.path.append(compiled_path)
        p = Path(compiled_path)
        root_files = [f for f in p.glob("root_pipeline_*")]
        if len(root_files) < 1:
            raise ValueError(f"No root files found in {compiled_path}")
        elif len(root_files) > 1:
            raise ValueError(f"More than one root file found in {compiled_path}: {', '.join(root_files)}")
        else:
            root_file = root_files.pop()

        print(f"Root file: {root_file}")
        mod = root_file.stem

        root_module = importlib.import_module(mod)

        package_yaml_path = p / f"{root_file.stem}.yaml"

        print(f"Package path: {package_yaml_path}")

        Compiler(mode=kfp.dsl.PipelineExecutionMode.V2_COMPATIBLE).compile(pipeline_func=root_module.root, package_path=str(package_yaml_path))

        root_module = importlib.import_module(root_module_name)

        client = kfp.Client()

        return client.create_run_from_pipeline_func(
            pipeline_func=root_module.root,
            mode=kfp.dsl.PipelineExecutionMode.V2_COMPATIBLE,
            arguments={},
            # You can optionally override your pipeline_root when submitting the run too:
            # pipeline_root='gs://my-pipeline-root/example-pipeline',
            # arguments={
            #     'url': 'https://storage.googleapis.com/ml-pipeline-playground/iris-csv-files.tar.gz'
            # }
        )