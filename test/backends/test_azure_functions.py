import logging
import pytest
import requests
from .context import notebook_processing
from .context import serialization_utils


@pytest.fixture
def setup():
    pass


def test_single_step_execution_with_output():
    notebook_path = "test/backends/testdata/sample_notebooks/code_with_output.ipynb"
    url = "http://localhost:7071/api/exec_step"
    connect_timeout_sec = 10
    read_timeout_sec = 60
    session = requests.Session()

    notebook_dict = notebook_processing.read_notebook(notebook_path)
    steps = notebook_processing.get_steps(notebook_dict)
    assert len(steps) == 1

    for name, step in steps.items():
        code = step.code

        serialized_code = serialization_utils.serialize_obj(code)
        params = {
            "code": serialized_code,
        }

        response = session.get(url, params=params, timeout=(connect_timeout_sec, read_timeout_sec))
        assert response.status_code == 200

        response_json = response.json()
        stdout = response_json['stdout']
        assert stdout == 'SAME OUTPUT\n'

        logging.info(f"Executed step {name} and got response: {response}")
