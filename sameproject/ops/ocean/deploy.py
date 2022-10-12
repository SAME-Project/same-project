from sameproject.data.config import SameConfig
from sameproject.ops import helpers
from pathlib import Path
import importlib
import boto3


def deploy(base_path: Path, root_file: str, config: SameConfig):
    with helpers.add_path(str(base_path)):
        root_module = importlib.import_module(root_file)  # python module

        client = boto3.client('ec2')
        return client.create_run_from_pipeline_func(
            root_module.root,
            arguments={},
        )
