import logging

import azure.functions as func
import azure.durable_functions as df
from .context import Step


# Constants
HTTP_PARAM_CODE_STEPS = "steps"


async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    client = df.DurableOrchestrationClient(starter)

    # Fetch the steps
    body = req.get_json()
    serialized_steps = body['steps']
    sorted_steps = Step.from_json_list(serialized_steps)
    num_steps = len(sorted_steps)
    logging.info(f"Number of steps to orchestrate: {num_steps}")


    instance_id = await client.start_new(req.route_params["functionName"], None, sorted_steps)
    logging.info(f"Started orchestration with ID = '{instance_id}'.")

    return client.create_check_status_response(req, instance_id)
