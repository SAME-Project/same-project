from .context import notebook_processing
from .context import Step
import json
import pytest
import requests


AZFUNC_IP = "localhost"
AZFUNC_PORT = 7071
EXECUTE_STEP_URL = f"http://{AZFUNC_IP}:{AZFUNC_PORT}/api/execute_step"


@pytest.fixture
def setup():
    pass


def test_single_step_execution_with_output():
    # Setup test parameters
    notebook_path = "test/backends/testdata/sample_notebooks/single_cell_code_with_output.ipynb"
    connect_timeout_sec = 10
    read_timeout_sec = 60

    # Read inputs
    notebook_dict = notebook_processing.read_notebook(notebook_path)
    steps = notebook_processing.get_steps(notebook_dict)

    # Serialize input Steps into JSON to send over HTTP to the Azure Function application instance
    steps_serialized = []
    for _, step in steps.items():
        step_serialized = Step.to_json(step)
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
    response = session.post(EXECUTE_STEP_URL, data=params_json, timeout=(connect_timeout_sec, read_timeout_sec))

    # Verify that the HTTP request succeeded
    assert response.status_code == 200

    # Verify the response content and execution result
    response_json = response.json()
    stdout = response_json["result"]["stdout"]
    status = response_json["result"]["status"]
    assert stdout == "SAME OUTPUT\n"
    assert status == "success"
