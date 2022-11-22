from sameproject.data.config import SameConfig
from sameproject.ops import helpers
from pathlib import Path
import importlib
import kfp


def deploy(base_path: Path, root_file: str, config: SameConfig):
    with helpers.add_path(str(base_path)):
        root_module = importlib.import_module(root_file)  # python module

        print("getting kfp_client")
        kfp_client = kfp.Client(host="http://ml_pipeline.kubeflow.svc.cluster.local:8888")  # only supporting 'kubeflow' namespace
        print("got kfp_client")
        return kfp_client.create_run_from_pipeline_func(
            root_module.root,
            arguments={},
        )
