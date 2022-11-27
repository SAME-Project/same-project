from sameproject.data.config import SameConfig
from sameproject.ops import helpers
from pathlib import Path
import importlib

import kfp.dsl as dsl 
import kfp



def deploy(base_path: Path, root_file: str, config: SameConfig):
    with helpers.add_path(str(base_path)):
        root_module = importlib.import_module(root_file)  # python module

        print("getting kfp_client")
        kfp_client = kfp.Client(host="http://aff7367d8c2254073b6f563f2eb8efdc-b6898d80ac5be12c.elb.us-east-1.amazonaws.com")  # only supporting 'kubeflow' namespace
        print("got kfp_client")

        # dsl.BaseOp(name="data_collector").add_volume("/data/input")

        return kfp_client.create_run_from_pipeline_func(
            root_module.root,
            arguments={},
        )
