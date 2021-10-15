from .context import notebook_processing
from .context import Step
from .context import EXECUTE_WORKFLOW_ACTIVITY_NAME
from typing import List
import json
import logging
import time
import requests


class DurableFunctionsClient:
    """
    Client for interacting with the DurableFunctionsBackend.
    # TODO: Add unit tests:
    #       - non-zero start state
    """
    def __init__(
        self,
        backend_host: str,
        user: str,
        start_state_id: int = 0
    ):
        if backend_host.endswith('/'):
            backend_host = backend_host[-1]
        self.backend_host = backend_host
        self.user = user
        self.next_state_id = start_state_id
        self.connect_timeout_sec = 10
        self.read_timeout_sec = 60
        self.status_query_timeout_sec = 10
        self.retry_interval_sec = 1
        self.session = requests.Session()
        self.workflow_url = f"{self.backend_host}/api/orchestrators/{EXECUTE_WORKFLOW_ACTIVITY_NAME}"

    def __del__(self):
        self.session.close()

    def execute_notebook(self, notebook_path: str) -> List[dict]:
        """
        Execute a given notebook and return the output of each Step.
        """
        # Read the notebook and convert it into a sorted list of Steps
        notebook_dict = notebook_processing.read_notebook(notebook_path)
        steps = notebook_processing.get_sorted_list_of_steps(notebook_dict)
        # Execute the steps
        output = self.execute_steps(steps)
        return output

    def execute_steps(self, steps: List[Step]) -> List[dict]:
        """
        Execute a given list of Steps and return the output of each Step.
        """
        # Serialize input Steps into JSON to send over HTTP to the Azure Function application instance
        steps_serialized = Step.to_json_array(steps)

        # Prepare HTTP request payload
        params = {
            "steps": steps_serialized,
            "user": self.user,
            "idin": self.next_state_id,
        }
        params_json = json.dumps(params)

        # Send the HTTP request
        response = self.session.post(
            self.workflow_url,
            data=params_json,
            timeout=(self.connect_timeout_sec, self.read_timeout_sec))

        # Verify that the HTTP request has been accepted
        if response.status_code != 202:
            logging.error(f"Failed to start orchestration. HTTP response: {response}")
            return

        # Parse the endpoint to query for workflow progress and result
        response_json = response.json()
        status_query_url = response_json["statusQueryGetUri"]

        # Query for the progress, keep trying until we timeout or get the completion status
        is_completed = False
        iterations = self.read_timeout_sec // self.retry_interval_sec
        for _ in range(iterations):
            response = self.session.get(
                status_query_url,
                timeout=(self.connect_timeout_sec, self.status_query_timeout_sec))
            response_json = response.json()
            runtime_status = response_json["runtimeStatus"]
            if runtime_status == "Completed":
                is_completed = True
                break
            time.sleep(self.retry_interval_sec)

        # Verify that the workflow completed execution
        if not is_completed:
            logging.error(f"Failed to complete orchestration in given time ({self.read_timeout_sec}s)")
            return

        # Increment the state ID for next invocations
        self.next_state_id += 1

        # Return a list where each ith element is a dictionary corresponding to the output of the ith Step
        output = response_json["output"]
        return output
