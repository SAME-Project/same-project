from sameproject.data.config import SameConfig
from sameproject.ops import helpers
from pathlib import Path
import importlib
import kfp


def deploy(base_path: Path, root_file: str, config: SameConfig):
    with helpers.add_path(str(base_path)):
        root_module = importlib.import_module(root_file)  # python module

        kfp_client = kfp.Client()  # only supporting 'kubeflow' namespace
        return kfp_client.create_run_from_pipeline_func(
            root_module.root,
            arguments={},
        )
