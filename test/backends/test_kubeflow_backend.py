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


def fetch_status(deployment, max_polls=10, poll_sleep=10):
    client = kfp.Client()

    polls = 0
    while polls < max_polls:
        time.sleep(poll_sleep)
        api_result = client.get_run(deployment.run_info.id)
        if api_result.run.status is not None and not api_result.run.status == "Running":
            return api_result.run.status

        polls += 1

    pytest.fail(f"Failed to fetch kubeflow status for run {deployment.run_info.id} after waiting for {max_polls*poll_sleep}s.")


@pytest.mark.kubeflow
def test_kubeflow_function_references():
    """
    Tests kubeflow execution for notebooks with functions defined in the
    global scope that call other functions defined in the global scope.
      see: https://github.com/SAME-Project/same-project/issues/69
    """
    compiled_path, root_file = compile_testdata("function_references")
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
    deployment = deploy("kubeflow", compiled_path, root_file)
    assert fetch_status(deployment) == "Success"
