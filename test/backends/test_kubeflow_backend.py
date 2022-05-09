from sameproject.ops.explode import ExplodingVariable
from sameproject.ops import notebooks as nbproc
from sameproject.data.config import SameConfig
from sameproject.ops.backends import deploy
from base64 import urlsafe_b64decode, urlsafe_b64encode
from pathlib import Path
import tempfile
import tarfile
import pytest
import dill
import json
import time
import kfp
import sys
import io


@pytest.mark.kubeflow
def test_kubeflow_function_references():
    """
    Tests kubeflow execution for notebooks with functions defined in the
    global scope that call other functions defined in the global scope.
      see: https://github.com/SAME-Project/same-project/issues/69
    """

    compiled_path, root_file = compile_testdata("function_references")
    deployment = deploy("kubeflow", compiled_path, root_file)
    assert fetch_status(deployment) == "Succeeded"

    # Check that the output context has 'x' set to '1'.
    artifacts = fetch_output_contexts(deployment)
    assert get_artifact_attr(artifacts, 0, "x") == 1


@pytest.mark.kubeflow
def test_kubeflow_imported_functions():
    """
    Tests kubeflow execution for notebooks with functions defined in the
    global scope that use imported functions.
      see: https://github.com/SAME-Project/same-project/issues/71
    """
    compiled_path, root_file = compile_testdata("imported_functions")
    deployment = deploy("kubeflow", compiled_path, root_file)
    assert fetch_status(deployment) == "Succeeded"

    # Check that the output context has a json dump in it.
    artifacts = fetch_output_contexts(deployment)
    dump = json.loads(get_artifact_attr(artifacts, 0, "x"))
    assert dump["x"] == 0


@pytest.mark.kubeflow
def test_kubeflow_multistep():
    """
    Tests kubeflow execution for notebooks with multiple steps.
    """
    compiled_path, root_file = compile_testdata("multistep")
    deployment = deploy("kubeflow", compiled_path, root_file)
    assert fetch_status(deployment) == "Succeeded"

    # Check that the context was passed correctly from step to step.
    artifacts = fetch_output_contexts(deployment)
    assert get_artifact_attr(artifacts, 0, "x") == 0
    assert get_artifact_attr(artifacts, 1, "x") == 1
    assert get_artifact_attr(artifacts, 2, "y") == "1"


@pytest.mark.kubeflow
def test_kubeflow_exploding_variables():
    """
    Tests that unserialisable variables are replaced with exploding ones.
    """
    compiled_path, root_file = compile_testdata("exploding_variables")
    deployment = deploy("kubeflow", compiled_path, root_file)
    assert fetch_status(deployment) == "Succeeded"

    # Fetch variables.
    artifacts = fetch_output_contexts(deployment)

    # Check that the generator 'x' was replaced with an exploding variable:
    x = get_artifact_attr(artifacts, 0, "x")
    with pytest.raises(Exception):
        next(x)  # boom - see ops/explode.py

    # Check that the large 'y' was replaced with an exploding variable:
    x = get_artifact_attr(artifacts, 0, "y")
    with pytest.raises(Exception):
        next(x)  # boom - see ops/explode.py


@pytest.mark.kubeflow
def test_kubeflow_requirements_file():
    """
    Tests that requirements.txt dependencies are installed before execution.
    """
    compiled_path, root_file = compile_testdata("requirements_file")
    deployment = deploy("kubeflow", compiled_path, root_file)
    assert fetch_status(deployment) == "Succeeded"


@pytest.mark.kubeflow
def test_kubeflow_serialised_modules():
    """
    Tests that modules imported in one step are accessible in another step.
    """
    compiled_path, root_file = compile_testdata("serialised_modules")
    deployment = deploy("kubeflow", compiled_path, root_file)
    assert fetch_status(deployment) == "Succeeded"

    expected_value = urlsafe_b64encode("test".encode())
    artifacts = fetch_output_contexts(deployment)
    assert get_artifact_attr(artifacts, 1, "x") == expected_value
    assert get_artifact_attr(artifacts, 1, "y") == expected_value
    assert get_artifact_attr(artifacts, 1, "z") == expected_value


def extract_artifact_data(data):
    path = tempfile.mktemp()
    with Path(path).open("wb") as writer:
        writer.write(urlsafe_b64decode(data))

    with tarfile.open(path, "r") as reader:
        return reader.extractfile("data").read()


def get_artifact_attr(artifacts, step_num, attr):
    # Monkey-patch of the main module to support loading exploding vars:
    sys.modules["__main__"].__dict__["ExplodingVariable"] = ExplodingVariable

    # Dill seems to load modules into the global module cache, so if we load
    # every artifact module up front they clobber each other.
    artifact_data = get_artifact_for_step(artifacts, step_num)
    module = dill.loads(artifact_data)
    return getattr(module, attr)


def get_artifact_for_step(artifacts, step_num):
    for k in artifacts:
        if k.startswith(f"same-step-{step_num:03}"):
            return artifacts[k]
    return None


def compile_testdata(name):
    path = Path(__file__).parent / f"./testdata/kubeflow/{name}.yaml"
    with open(path, "r") as file:
        config = SameConfig.from_yaml(file.read())
        config = config.resolve(path.parent)

    return nbproc.compile(config, "kubeflow")


def fetch_status(deployment, timeout=300):
    client = kfp.Client()
    run_id = deployment.run_info.id

    try:
        client.wait_for_run_completion(run_id, timeout)
        return client.get_run(run_id).run.status
    except TimeoutError:
        pytest.fail(f"Failed to fetch kubeflow status for run {deployment.run_info.id} after waiting for {timeout}s.")


def fetch_output_contexts(deployment):
    client = kfp.Client()
    run_id = deployment.run_info.id
    run = client.get_run(run_id)
    manifest = json.loads(run.pipeline_runtime.workflow_manifest)

    artifacts = {}
    for node_id in manifest["status"]["nodes"]:
        outputs = manifest["status"]["nodes"][node_id].get("outputs", None)
        if outputs is not None:
            for artifact_data in outputs["artifacts"]:
                name = artifact_data["name"]
                if not name.startswith("same-step"):  # only contexts
                    continue

                artifact = client.runs.read_artifact(run_id, node_id, name)
                artifacts[name] = extract_artifact_data(artifact.data)

    return artifacts
