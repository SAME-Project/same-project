import io
import time
from sameproject.data.config import SameConfig
from sameproject.ops import helpers
from pathlib import Path
import importlib
import kfp
import python_pachyderm
from python_pachyderm.service import pps_proto
from base64 import b64encode

import tarfile
import os.path

def make_tarfile(f, source_dir):
    with tarfile.open(fileobj=f, mode="w:gz") as tar:
        tar.add(source_dir, arcname="context")

# hack to import vendored script_to_pipeline, for experiment...
# import sys
# script_dir = Path(__file__).parent.parent.parent.parent
# sys.path.append((script_dir / "vendor" / "script_to_pipeline").as_posix())

# from script_to_pipeline import _internal

def deploy(base_path: Path, root_file: str, config: SameConfig):

    # with helpers.add_path(str(base_path)):

    # create buffer
    buffer = io.BytesIO()

    # tar up base_path
    print(f"base_path = {base_path}")
    make_tarfile(buffer, base_path)

    # read from buffer
    buffer.seek(0)
    tar_data = buffer.read()
    encoded_source = b64encode(tar_data)

    DEFAULT_TAG = "v0.1.0"
    IMAGE = f"pachyderm/script_to_pipeline"
    tag = DEFAULT_TAG
    image = f"{IMAGE}:{tag}"

    cmd=["python3", "entrypoint.py", encoded_source.decode(), root_file, *[]] # dependencies go here
    image=image
    print("CMD", cmd)
    print("IMAGE", image)

    # print pwd
    f = open(Path(os.getcwd()) / "_test_run.sh", "w")
    # hack hack hack (to allow for quick iteration)
    f.write(f'docker run --user=root --rm --name=samepachtest -ti '+
        f'-v /home/luke/ps/same-project/vendor/script_to_pipeline/entrypoint.py:/home/pipeline/entrypoint.py '+
        f'--entrypoint="{cmd[0]}" {image} -- {" ".join(cmd[1:])}')
    f.close()

    #root_module = importlib.import_module(root_file)  # python module

    # Create a pipeline that logs frequency of the word "hello" in `test`
    # repo to a file in the `word_count` repo (which is created automatically)
    # Any time data is committed to the `test` repo, this pipeline will
    # automatically trigger.
    client = python_pachyderm.Client()

    # TODO: want apply_pachyderm_pipeline as follows:
    # utils.apply_pachyderm_pipeline(
    #     module=root_module,
    #     image=image, # XXX how to get?
    #     requirements=requirements, # XXX how to get?
    # )

    client.create_pipeline(
        "word_count",
        transform=pps_proto.Transform(
            cmd=cmd, #["bash"],
            # stdin=[
            #     "grep -roh hello /pfs/test/ | wc -w > /pfs/out/count.txt"
            # ],
            image=image, # XXX how to get the image defined by same here? how does kubeflow do it?
        ),
        input=pps_proto.Input(
            pfs=pps_proto.PFSInput(repo="test", branch="master", glob="/")
        ),
        update=True,
    )

    #     kfp_client = kfp.Client()  # only supporting 'kubeflow' namespace
    #     return kfp_client.create_run_from_pipeline_func(
    #         root_module.root,
    #         arguments={},
    #     )

