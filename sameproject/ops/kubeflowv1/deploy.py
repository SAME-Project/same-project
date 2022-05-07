from sameproject.ops import helpers
from pathlib import Path
import importlib
import kfp


def deploy(compiled_path: Path, root_module_name: str):
    with helpers.add_path(str(compiled_path)):
        kfp_client = kfp.Client()  # only supporting 'kubeflow' namespace
        root_module = importlib.import_module(root_module_name)

        return kfp_client.create_run_from_pipeline_func(
            root_module.root,
            arguments={},
        )
