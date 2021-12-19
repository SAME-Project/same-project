from .context import notebook_processing
from .context import Step
from .context import EXECUTE_WORKFLOW_ACTIVITY_NAME
from .context import DURABLE_FUNCTIONS_BACKEND_TEST_HOST_ENV_VAR
from .context import DURABLE_FUNCTIONS_BACKEND_URL_AZURE
import json
import logging
import os
import time
import requests
import uuid
import pytest


class TestDurableFunctionsBackend():
    def setup_class(self):
        # Check if a user specified host is specified for the backend, otherwise use the Azure Functions URL.
        test_host = os.environ.get(DURABLE_FUNCTIONS_BACKEND_TEST_HOST_ENV_VAR, DURABLE_FUNCTIONS_BACKEND_URL_AZURE)
        if test_host.endswith('/'):
            test_host = test_host[-1]
        self.workflow_url = f"{test_host}/api/orchestrators/{EXECUTE_WORKFLOW_ACTIVITY_NAME}"
        logging.info(f"Workflow URL being used: {self.workflow_url}")
        self.session = requests.Session()

    def teardown_class(self):
        self.session.close()

    @pytest.mark.skip("Skipping until we mock or create Azure Functions account")
    def test_single_step_execution_with_output(self):
        # Setup test parameters
        notebook_path = "test/backends/testdata/sample_notebooks/single_cell_code_with_output.ipynb"
        connect_timeout_sec = 10
        read_timeout_sec = 60
        status_query_timeout_sec = 10
        retry_interval_sec = 1
        user = str(uuid.uuid4())

        # Read inputs
        notebook_dict = notebook_processing.read_notebook(notebook_path)
        steps = notebook_processing.get_sorted_list_of_steps(notebook_dict)

        # Serialize input Steps into JSON to send over HTTP to the Azure Function application instance
        steps_serialized = Step.to_json_array(steps)

        # For this test, we expect the input notebook to have a single Step
        assert len(steps_serialized) == 1

        # Prepare HTTP request payload
        params = {
            "steps": steps_serialized,
            "user": user,
        }
        params_json = json.dumps(params)

        # Send the HTTP request
        response = self.session.post(
            self.workflow_url,
            data=params_json,
            timeout=(connect_timeout_sec, read_timeout_sec))

        # Verify that the HTTP request has been accepted
        assert response.status_code == 202

        # Parse the endpoint to query for workflow progress and result
        response_json = response.json()
        status_query_url = response_json["statusQueryGetUri"]

        # Query for the progress, keep trying until we timeout or get the completion status
        is_completed = False
        iterations = read_timeout_sec // retry_interval_sec
        for _ in range(iterations):
            response = self.session.get(status_query_url, timeout=(connect_timeout_sec, status_query_timeout_sec))
            response_json = response.json()
            runtime_status = response_json["runtimeStatus"]
            if runtime_status == "Completed":
                is_completed = True
                break
            time.sleep(retry_interval_sec)

        # Verify that the workflow completed execution
        assert is_completed is True
        output = response_json["output"]

        # Verify that there was only one Step execution
        assert len(output) == 1

        # Verify the response content and workflow execution result
        step_output = output[0]
        stdout = step_output["result"]["stdout"]
        status = step_output["result"]["status"]
        assert stdout == "SAME OUTPUT\n"
        assert status == "success"

    @pytest.mark.skip("Skipping until we mock or create Azure Functions account")
    def test_multi_step_execution_with_output(self):
        # Setup test parameters
        notebook_path = "test/backends/testdata/sample_notebooks/multi_step_code_with_data_flow.ipynb"
        connect_timeout_sec = 10
        read_timeout_sec = 60
        status_query_timeout_sec = 10
        retry_interval_sec = 1
        user = str(uuid.uuid4())

        # Read inputs
        notebook_dict = notebook_processing.read_notebook(notebook_path)
        steps = notebook_processing.get_sorted_list_of_steps(notebook_dict)

        # Serialize input Steps into JSON to send over HTTP to the Azure Function application instance
        steps_serialized = Step.to_json_array(steps)

        # For this test, we expect the input notebook to have three Steps
        assert len(steps_serialized) == 3

        # Prepare HTTP request payload
        params = {
            "steps": steps_serialized,
            "user": user,
        }
        params_json = json.dumps(params)

        # Send the HTTP request
        response = self.session.post(
            self.workflow_url,
            data=params_json,
            timeout=(connect_timeout_sec, read_timeout_sec))

        # Verify that the HTTP request has been accepted
        assert response.status_code == 202

        # Parse the endpoint to query for workflow progress and result
        response_json = response.json()
        status_query_url = response_json["statusQueryGetUri"]

        # Query for the progress, keep trying until we timeout or get the completion status
        is_completed = False
        iterations = read_timeout_sec // retry_interval_sec
        for _ in range(iterations):
            response = self.session.get(status_query_url, timeout=(connect_timeout_sec, status_query_timeout_sec))
            response_json = response.json()
            runtime_status = response_json["runtimeStatus"]
            if runtime_status == "Completed":
                is_completed = True
                break
            time.sleep(retry_interval_sec)

        # Verify that the workflow completed execution
        assert is_completed is True
        output = response_json["output"]

        # Verify that there were three Step executions
        assert len(output) == 3

        # Verify the response content and workflow execution result
        step_output = output[2]
        stdout = step_output["result"]["stdout"]
        status = step_output["result"]["status"]
        assert stdout == "3\n"
        assert status == "success"
