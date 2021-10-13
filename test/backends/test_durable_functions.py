from .context import notebook_processing
from .context import Step
import json
import logging
import os
import time
import requests
import uuid


# Environment variable that can be optionally set to specify a host where Durable Functions backend is running.
# If none is specified, the one deployed on Azure Functions is used.
DURABLE_FUNCTIONS_BACKEND_TEST_HOST_ENV_VAR = "DURABLE_FUNCTIONS_BACKEND_TEST_HOST"

# Name of the app deployed on Azure Functions running the backend.
DURABLE_FUNCTIONS_APP_NAME_AZURE = "durable-functions-backend-001"

# Azure Functions host URL where the backend is running.
DURABLE_FUNCTIONS_BACKEND_URL_AZURE = f"https://{DURABLE_FUNCTIONS_APP_NAME_AZURE}.azurewebsites.net"

# Name of the HTTP endpoint that kicks off the step execution workflow in the backend.
EXECUTE_WORKFLOW_ACTIVITY_NAME = "execute_steps_workflow"


class TestDurableFunctions():
    def setup_class(self):
        # Check if a user specified host is specified for the backend, otherwise use the Azure Functions URL.
        test_host = os.environ.get(DURABLE_FUNCTIONS_BACKEND_TEST_HOST_ENV_VAR, DURABLE_FUNCTIONS_BACKEND_URL_AZURE)
        if test_host.endswith('/'):
            test_host = test_host[-1]
        self.workflow_url = f"{test_host}/api/orchestrators/{EXECUTE_WORKFLOW_ACTIVITY_NAME}"
        logging.info(f"Workflow URL being used: {self.workflow_url}")

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
        with requests.Session() as session:
            response = session.post(
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
            response = session.get(status_query_url, timeout=(connect_timeout_sec, status_query_timeout_sec))
            response_json = response.json()
            runtime_status = response_json["runtimeStatus"]
            if runtime_status == "Completed":
                is_completed = True
                break
            time.sleep(retry_interval_sec)

        # Verify that the workflow completed execution
        assert is_completed is True
        output = response_json["output"]

        # Verify that there was only one step execution
        assert len(output) == 1

        # Verify the response content and workflow execution result
        step_output = output[0]
        stdout = step_output["result"]["stdout"]
        status = step_output["result"]["status"]
        assert stdout == "SAME OUTPUT\n"
        assert status == "success"

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
        with requests.Session() as session:
            response = session.post(
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
            response = session.get(status_query_url, timeout=(connect_timeout_sec, status_query_timeout_sec))
            response_json = response.json()
            runtime_status = response_json["runtimeStatus"]
            if runtime_status == "Completed":
                is_completed = True
                break
            time.sleep(retry_interval_sec)

        # Verify that the workflow completed execution
        assert is_completed is True
        output = response_json["output"]

        # Verify that there was only one step execution
        assert len(output) == 3

        # Verify the response content and workflow execution result
        step_output = output[2]
        stdout = step_output["result"]["stdout"]
        status = step_output["result"]["status"]
        assert stdout == "3\n"
        assert status == "success"
