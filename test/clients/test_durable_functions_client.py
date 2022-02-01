from .context import DURABLE_FUNCTIONS_BACKEND_TEST_HOST_ENV_VAR
from .context import DURABLE_FUNCTIONS_BACKEND_URL_AZURE
from .context import DurableFunctionsClient
import os
import uuid
import pytest

@pytest.mark.skip("not using durable functions right now")
class TestDurableFunctionsClient():
    def setup_class(self):
        # Check if a user specified host is specified for the backend, otherwise use the Azure Functions URL.
        test_host = os.environ.get(DURABLE_FUNCTIONS_BACKEND_TEST_HOST_ENV_VAR, DURABLE_FUNCTIONS_BACKEND_URL_AZURE)
        if test_host.endswith('/'):
            test_host = test_host[-1]
        self.test_host = test_host

    def test_single_step_execution_with_output(self):
        # Setup test parameters
        notebook_path = "test/backends/testdata/sample_notebooks/single_cell_code_with_output.ipynb"
        user = str(uuid.uuid4())
        start_state_id = 0

        # Create client and execute notebook
        client = DurableFunctionsClient(self.test_host, user, start_state_id)
        output = client.execute_notebook(notebook_path)

        # Verify that there was only one Step execution
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
        user = str(uuid.uuid4())
        start_state_id = 0

        # Create client and execute notebook
        client = DurableFunctionsClient(self.test_host, user, start_state_id)
        output = client.execute_notebook(notebook_path)

        # Verify that there were three Step executions
        assert len(output) == 3

        # Verify the response content and workflow execution result
        step_output = output[2]
        stdout = step_output["result"]["stdout"]
        status = step_output["result"]["status"]
        assert stdout == "3\n"
        assert status == "success"
