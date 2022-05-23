from sameproject.ops.notebooks import compile, get_steps
from base64 import urlsafe_b64decode, urlsafe_b64encode
from sameproject.ops.explode import ExplodingVariable
from sameproject.data.config import SameConfig
from sameproject.ops.backends import deploy
from pathlib import Path
import test.testdata
import kubernetes
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
@test.testdata.notebooks("features")
def test_kubeflow_features(config, notebook, requirements, validation_fn):
    compiled_path, root_file = compile(config, "kubeflow")
    deployment = deploy("kubeflow", compiled_path, root_file)
    steps = get_steps(notebook, config)
    status = _fetch_status(deployment)
    artifacts, logs = _fetch_node_data(deployment)

    last_log = _get_for_step(logs, 0)
    for i in range(1, len(steps)):
        if _get_for_step(logs, i) is not None:
            last_log = _get_for_step(logs, i)
    assert status == "Succeeded", f"Kubeflow run failed:\n{last_log}"

    # Validate the output context of the last step in the notebook:
    if validation_fn is not None:
        last_ctx = _get_artifact_context(artifacts, len(steps) - 1)
        assert validation_fn(last_ctx)


@pytest.mark.kubeflow
@pytest.mark.external
@test.testdata.notebooks("pytorch", "tensorflow", "sklearn")
def test_kubeflow_external(config, notebook, requirements, validation_fn):
    compiled_path, root_file = compile(config, "kubeflow")
    deployment = deploy("kubeflow", compiled_path, root_file)
    steps = get_steps(notebook, config)
    status = _fetch_status(deployment)
    artifacts, logs = _fetch_node_data(deployment)

    last_log = _get_for_step(logs, 0)
    for i in range(1, len(steps)):
        if _get_for_step(logs, i) is not None:
            last_log = _get_for_step(logs, i)
    assert status == "Succeeded", f"Kubeflow run failed:\n{last_log}"


def _extract_artifact_data(data):
    path = tempfile.mktemp()
    with Path(path).open("wb") as writer:
        writer.write(urlsafe_b64decode(data))

    with tarfile.open(path, "r") as reader:
        return reader.extractfile("data").read()


def _get_artifact_context(artifacts, step_num):
    # Monkey-patch of the main module to support loading exploding vars:
    # TODO(guy): Why is this necessary for classes?
    sys.modules["__main__"].__dict__["ExplodingVariable"] = ExplodingVariable

    # Dill seems to load modules into the global module cache, so if we load
    # every artifact module up front they clobber each other.
    artifact_data = _get_for_step(artifacts, step_num)
    module = dill.loads(artifact_data)

    # Convert module to a dictionary so validation can use subscripts:
    return dict(map(lambda k: (k, getattr(module, k)), dir(module)))


def _get_for_step(dict, step_num):
    for k in dict:
        if k.startswith(f"same-step-{step_num:03}"):
            return dict[k]
    return None


def _fetch_status(deployment, timeout=600):
    client = kfp.Client()
    run_id = deployment.run_info.id

    try:
        client.wait_for_run_completion(run_id, timeout)
        return client.get_run(run_id).run.status
    except TimeoutError:
        pytest.fail(f"Failed to fetch kubeflow status for run {deployment.run_info.id} after waiting for {timeout}s.")


def _fetch_node_data(deployment):
    client = kfp.Client()
    run_id = deployment.run_info.id
    run = client.get_run(run_id)
    manifest = json.loads(run.pipeline_runtime.workflow_manifest)

    logs = {}
    artifacts = {}
    for node_id in manifest["status"]["nodes"]:
        if manifest["status"]["nodes"][node_id]["type"] == "Pod":
            display_name = manifest["status"]["nodes"][node_id]["displayName"]
            logs[display_name] = _fetch_logs(node_id)

        outputs = manifest["status"]["nodes"][node_id].get("outputs", None)
        if outputs is not None:
            for artifact_data in outputs["artifacts"]:
                name = artifact_data["name"]
                if not name.startswith("same-step"):  # only contexts
                    continue

                artifact = client.runs.read_artifact(run_id, node_id, name)
                artifacts[name] = _extract_artifact_data(artifact.data)

    return artifacts, logs


def _fetch_logs(node_id):
    kubernetes.config.load_kube_config()
    client = kubernetes.client.CoreV1Api()

    return client.read_namespaced_pod_log(
        name=node_id,  # pod name matches node id in kubeflow
        namespace="kubeflow",  # only supports default namespace for now
        container="main",
    )
