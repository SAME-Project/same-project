import io
import json
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

def deploy(base_path: Path, root_file: str, config: SameConfig):

    buffer = io.BytesIO()
    make_tarfile(buffer, base_path)

    # read from buffer
    buffer.seek(0)
    tar_data = buffer.read()
    encoded_source = b64encode(tar_data)

    # for now, read the image straight out of the same config, since we run all
    # the steps in a single pachyderm pipeline, and assume we are using the
    # default config. TODO: refactor this so we can have different images per
    # step (and have the user specify non-default environments using cell tags
    # as documented).
    image = config.environments["default"].image_tag

    micro_entrypoint = (
        'print("Greetings from Pachyderm-SAME"); '
        + 'import io; '
        + 'import site; '
        + 'import sys; '
        + 'from base64 import b64decode; '
        + 'from importlib import import_module, reload; '
        + 'from pathlib import Path; '
        + 'from subprocess import run; '
        + 'import tarfile; '
        + 'from tempfile import TemporaryDirectory; '
        + 'dependencies = sys.argv[2:]; '
        + 'run(["pip", "--disable-pip-version-check", "install", *dependencies]); '
        + 'reload(site); '
        + 'tar_bytes = sys.argv[1]; '
        + 'buffer = io.BytesIO(b64decode(tar_bytes)); '
        + 'root_module = sys.argv[2]; '
        + 'import tempfile; '
        + 'tempdir = tempfile.TemporaryDirectory(); '
        + 'tar = tarfile.open(fileobj=buffer, mode="r:gz"); '
        + 'tar.extractall(tempdir.name); '
        + 'p = Path(tempdir.name) / "context" / "requirements.txt"; '
        + 'p.exists() and run(["pip", "--disable-pip-version-check", "install", "-r", p.as_posix()]); '
        + 'sys.path.append((Path(tempdir.name) / "context").as_posix()); '
        + 'script = import_module(root_module); '
        + 'script.root()'
    )

    cmd=["python3", "-c", micro_entrypoint, encoded_source.decode(), root_file]

    # print("CMD", cmd)
    # print("IMAGE", image)

    # # hack hack hack (to allow for quick iteration)
    # stringify_args = "-c " + " ".join(map(lambda x: f"'{x}'", cmd[2:]))
    # f = open(Path(os.getcwd()) / "_test_run.sh", "w")
    # f.write(f'docker run --user=root --rm --name=samepachtest -ti '+
    #     f'--entrypoint="{cmd[0]}" {image} {stringify_args}')
    # f.close()

    client = python_pachyderm.Client()

    # TODO: consider allowing user to specify pachyderm input specs in
    # same.yaml, as well as via options.

    input_ = config.runtime_options.get("input", None)
    input_repo = config.runtime_options.get("input_repo", None)
    input_glob = config.runtime_options.get("input_glob", None)

    input_dict = {
        "pfs": {
            "glob": "/",
        },
    }

    if input_repo is not None:
        input_dict["pfs"]["repo"] = input_repo
    if input_glob is not None:
        input_dict["pfs"]["glob"] = input_glob

    # input_ overwrites other settings
    if input_ is not None:
        input_dict = json.loads(input_)

    # User might have specified more complex non-pfs input spec, in which case
    # we let python_pachyderm do the validation, however, we give user friendly
    # error message in case nothing is specified
    if "pfs" in input_dict and input_dict["pfs"].get("repo", None) is None:
        raise Exception("Must specify input repo name in pfs input, e.g. --input-repo=test")

    spec = {
        "pipeline": {
            "name": config.metadata.name,
        },
        "description": "Auto-generated from notebook",
        "transform": {
            "cmd": cmd,
            "image": image,
        },
        "input": input_dict,
        "update": True,
        "reprocess": True,
    }

    print("Submitting pachyderm pipeline spec:\n")
    import pprint
    import copy
    q = copy.deepcopy(spec)
    q["transform"]["cmd"] = "<elided>"
    pprint.pprint(q)

    req = python_pachyderm.parse_dict_pipeline_spec(spec)
    client.create_pipeline_from_request(req)

    # client.create_pipeline(
    #     config.metadata.name,
    #     transform=pps_proto.Transform(
    #         cmd=cmd,
    #         image=image,
    #         user="jovyan",
    #     ),
    #     # TODO: read repo from 'same run' commandline args
    #     input=pps_proto.Input(
    #         pfs=pps_proto.PFSInput(repo="test", branch="master", glob="/")
    #     ),
    #     update=True,
    #     reprocess=True,
    # )