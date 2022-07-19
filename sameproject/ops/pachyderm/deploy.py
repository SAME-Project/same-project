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

    DEFAULT_TAG = "0.9"
    IMAGE = f"combinatorml/jupyterlab-tensorflow-opencv"
    tag = DEFAULT_TAG
    image = f"{IMAGE}:{tag}"

    micro_entrypoint = 'print("Greetings from Pachyderm-SAME"); import io; import site; import sys; from base64 import b64decode; from importlib import import_module, reload; from pathlib import Path; from subprocess import run; import tarfile; from tempfile import TemporaryDirectory; dependencies = sys.argv[2:]; run(["pip", "--disable-pip-version-check", "install", *dependencies]); reload(site); tar_bytes = sys.argv[1]; buffer = io.BytesIO(b64decode(tar_bytes)); root_module = sys.argv[2]; import tempfile; tempdir = tempfile.TemporaryDirectory(); print("==============="); print(tempdir); tar = tarfile.open(fileobj=buffer, mode="r:gz"); tar.extractall(tempdir.name); p = Path(tempdir.name) / "context" / "requirements.txt"; p.exists() and run(["pip", "--disable-pip-version-check", "install", "-r", p.as_posix()]); sys.path.append((Path(tempdir.name) / "context").as_posix()); script = import_module(root_module); script.root()'

    cmd=["python3", "-c", micro_entrypoint, encoded_source.decode(), root_file, *[]] # dependencies go here
    image=image
    print("CMD", cmd)
    print("IMAGE", image)

    stringify_args = "-c " + " ".join(map(lambda x: f"'{x}'", cmd[2:]))

    # import pdb; pdb.set_trace()
    # print pwd
    f = open(Path(os.getcwd()) / "_test_run.sh", "w")
    # hack hack hack (to allow for quick iteration)
    f.write(f'docker run --user=root --rm --name=samepachtest -ti '+
        f'--entrypoint="{cmd[0]}" {image} {stringify_args}')
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
        config.metadata.name,
        transform=pps_proto.Transform(
            cmd=cmd, #["bash"],
            # stdin=[
            #     "grep -roh hello /pfs/test/ | wc -w > /pfs/out/count.txt"
            # ],
            image=image, # XXX how to get the image defined by same here? how does kubeflow do it?
            user="jovyan",
        ),
        input=pps_proto.Input(
            pfs=pps_proto.PFSInput(repo="test", branch="master", glob="/")
        ),
        update=True,
        reprocess=True,
    )

    #     kfp_client = kfp.Client()  # only supporting 'kubeflow' namespace
    #     return kfp_client.create_run_from_pipeline_func(
    #         root_module.root,
    #         arguments={},
    #     )

