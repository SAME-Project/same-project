from sameproject.data.config import SameConfig
from sameproject.ops import helpers
from pathlib import Path
import importlib
import kfp
import python_pachyderm


def deploy(base_path: Path, root_file: str, config: SameConfig):

    from python_pachyderm.service import pps_proto

    # Create a pipeline that logs frequency of the word "hello" in `test`
    # repo to a file in the `word_count` repo (which is created automatically)
    # Any time data is committed to the `test` repo, this pipeline will
    # automatically trigger.
    client.create_pipeline(
        "word_count",
        transform=pps_proto.Transform(
            cmd=["bash"],
            stdin=[
                "grep -roh hello /pfs/test/ | wc -w > /pfs/out/count.txt"
            ]
        ),
        input=pps_proto.Input(
            pfs=pps_proto.PFSInput(repo="test", branch="master", glob="/")
        )
    )

    # with helpers.add_path(str(base_path)):
    #     root_module = importlib.import_module(root_file)  # python module

    #     kfp_client = kfp.Client()  # only supporting 'kubeflow' namespace
    #     return kfp_client.create_run_from_pipeline_func(
    #         root_module.root,
    #         arguments={},
    #     )
