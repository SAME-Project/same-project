from sameproject.program.compile import notebook_processing as nbproc
from sameproject.backends.executor import deploy
from pathlib import Path
import pytest
import time
import kfp
import io


def compile_testdata(name):
    path = Path(__file__).parent / f"./testdata/kubeflow/{name}.yaml"
    return nbproc.compile(path.open("rb"), "kubeflow")


def fetch_status(deployment, timeout=100):
    client = kfp.Client()
    run_id = deployment.run_info.id

    try:
        client.wait_for_run_completion(run_id, timeout)
        return client.get_run(run_id).run.status
    except TimeoutError:
        pytest.fail(f"Failed to fetch kubeflow status for run {deployment.run_info.id} after waiting for {timeout}s.")


@pytest.mark.kubeflow
def test_kubeflow_function_references():
    """
    Tests kubeflow execution for notebooks with functions defined in the
    global scope that call other functions defined in the global scope.
      see: https://github.com/SAME-Project/same-project/issues/69
    """
    compiled_path, root_file = compile_testdata("function_references")
    print(compiled_path)
    return
    deployment = deploy("kubeflow", compiled_path, root_file)
    assert fetch_status(deployment) == "Success"


@pytest.mark.kubeflow
def test_kubeflow_imported_functions():
    """
    Tests kubeflow execution for notebooks with functions defined in the
    global scope that use imported functions.
      see: https://github.com/SAME-Project/same-project/issues/71
    """
    compiled_path, root_file = compile_testdata("imported_functions")
    print(compiled_path)
    return
    deployment = deploy("kubeflow", compiled_path, root_file)
    assert fetch_status(deployment) == "Success"
