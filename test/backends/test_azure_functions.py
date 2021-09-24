from .context import notebook_processing
from .context import Step
import json
import logging
import os
import requests


# Environment variable that can be optionally set to specify a host where Azure Functions backend is running.
# If none is specified, the one deployed on Azure Functions is used.
AZURE_FUNCTIONS_BACKEND_TEST_HOST_ENV_VAR = "AZURE_FUNCTIONS_BACKEND_TEST_HOST"

# Name of the app deployed on Azure Functions running the backend.
AZURE_FUNCTIONS_APP_NAME_AZURE = "azure-functions-backend-001"

# Azure Functions host URL where the backend is running.
AZURE_FUNCTIONS_BACKEND_URL_AZURE = f"https://{AZURE_FUNCTIONS_APP_NAME_AZURE}.azurewebsites.net"

# Name of the HTTP endpoint that kicks off the step execution workflow in the backend.
EXECUTE_STEP_FUNCTION_NAME = "execute_step"


class TestAzureFunctions():
    def setup_class(self):
        # Check if a user specified host is specified for the backend, otherwise use the Azure Functions URL.
        test_host = os.environ.get(AZURE_FUNCTIONS_BACKEND_TEST_HOST_ENV_VAR, AZURE_FUNCTIONS_BACKEND_URL_AZURE)
        self.exec_url = f"{test_host}/api/{EXECUTE_STEP_FUNCTION_NAME}"
        logging.info(f"Exec URL being used: {self.exec_url}")

    def test_single_step_execution_with_output(self):
        # Setup test parameters
        notebook_path = "test/backends/testdata/sample_notebooks/single_cell_code_with_output.ipynb"
        connect_timeout_sec = 10
        read_timeout_sec = 60

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
        }
        params_json = json.dumps(params)

        # Send the HTTP request
        with requests.Session() as session:
            response = session.post(
                self.exec_url,
                data=params_json,
                timeout=(connect_timeout_sec, read_timeout_sec))

        # Verify that the HTTP request succeeded
        assert response.status_code == 200

        # Verify the response content and execution result
        response_json = response.json()
        stdout = response_json["result"]["stdout"]
        status = response_json["result"]["status"]
        assert stdout == "SAME OUTPUT\n"
        assert status == "success"
