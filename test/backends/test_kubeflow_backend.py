from sameproject.program.compile import notebook_processing as nbproc
from sameproject.backends.executor import deploy
from base64 import urlsafe_b64decode
from pathlib import Path
import tempfile
import tarfile
import pytest
import dill
import json
import time
import kfp
import io


def extract_artifact_data(data):
    path = tempfile.mktemp()
    with Path(path).open("wb") as writer:
        writer.write(urlsafe_b64decode(data))

    with tarfile.open(path, "r") as reader:
        extracted_data = reader.extractfile("data").read()
        return dill.loads(urlsafe_b64decode(extracted_data))


def compile_testdata(name):
    path = Path(__file__).parent / f"./testdata/kubeflow/{name}.yaml"
    return nbproc.compile(path.open("rb"), "kubeflow")


def fetch_status(deployment, timeout=300):
    client = kfp.Client()
    run_id = deployment.run_info.id

    try:
        client.wait_for_run_completion(run_id, timeout)
        return client.get_run(run_id).run.status
    except TimeoutError:
        pytest.fail(f"Failed to fetch kubeflow status for run {deployment.run_info.id} after waiting for {timeout}s.")


def fetch_output_artifacts(deployment):
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
                artifact = client.runs.read_artifact(run_id, node_id, name)
                artifacts[name] = extract_artifact_data(artifact.data)

    return artifacts


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
    artifacts = fetch_output_artifacts(deployment)
    assert artifacts["component-fn-output_context"]["x"] == 1


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
    artifacts = fetch_output_artifacts(deployment)
    dump = json.loads(artifacts["component-fn-output_context"]["x"])
    assert dump["x"] == 0
