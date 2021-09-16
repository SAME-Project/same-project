from .context import notebook_processing
from .context import Step
import json
import time
import pytest
import requests


# Constants
AZFUNC_IP = "localhost"
AZFUNC_PORT = 7071
EXECUTE_WORKFLOW_URL = f"http://{AZFUNC_IP}:{AZFUNC_PORT}/api/orchestrators/execute_steps_workflow"


@pytest.fixture
def setup():
    pass


def test_single_step_execution_with_output():
    # Setup test parameters
    notebook_path = "test/backends/testdata/sample_notebooks/single_cell_code_with_output.ipynb"
    connect_timeout_sec = 10
    read_timeout_sec = 60
    status_query_timeout_sec = 10
    retry_interval_sec = 1

    # Read inputs
    notebook_dict = notebook_processing.read_notebook(notebook_path)
    steps = notebook_processing.get_steps(notebook_dict)

    # Serialize input Steps into JSON to send over HTTP to the Azure Function application instance
    steps_serialized = []
    for _, step in steps.items():
        step_serialized = json.dumps(step, default=Step.to_dict)
        steps_serialized.append(step_serialized)

    # For this test, we expect the input notebook to have a single Step
    assert len(steps_serialized) == 1

    # Prepare HTTP request payload
    params = {
        "steps": steps_serialized,
    }
    params_json = json.dumps(params)

    # Send the HTTP request
    session = requests.Session()
    response = session.post(EXECUTE_WORKFLOW_URL, data=params_json, timeout=(connect_timeout_sec, read_timeout_sec))

    # Verify that the HTTP request has been accepted
    assert response.status_code == 202

    # Parse the endpoint to query for workflow progress and result
    response_json = response.json()
    status_query_url = response_json["statusQueryGetUri"]

    # Query for the progress, keep trying until we timeout or get the completion status
    is_completed = False
    for _ in range(read_timeout_sec):
        response = session.get(status_query_url, timeout=(connect_timeout_sec, status_query_timeout_sec))
        response_json = response.json()
        runtime_status = response_json["runtimeStatus"]
        if runtime_status == "Completed":
            is_completed = True
            break
        time.sleep(retry_interval_sec)

    # Verify that the workflow completed execution
    assert is_completed == True
    output = response_json["output"]

    # Verify that there was only one step execution
    assert len(output) == 1

    # Verify the response content and workflow execution result
    step_output = output[0]
    stdout = step_output["result"]["stdout"]
    status = step_output["result"]["status"]
    assert stdout == "SAME OUTPUT\n"
    assert status == "success"
