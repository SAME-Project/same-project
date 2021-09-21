from .context import http_utils
from .context import Step
import azure.functions as func
import azure.durable_functions as df
import logging


HTTP_PARAM_CODE_STEPS = "steps"


async def start_steps_workflow(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    """Starts the orchestration that will execute a given list of Steps.
    """
    client = df.DurableOrchestrationClient(starter)

    try:
        # Fetch the steps
        body = req.get_json()
        serialized_steps = body['steps']
        sorted_steps = Step.from_json_list(serialized_steps)
        num_steps = len(sorted_steps)
        logging.info(f"Number of steps to orchestrate: {num_steps}")

        # Start workflow orchestrator
        instance_id = await client.start_new(req.route_params["functionName"], None, sorted_steps)
        logging.info(f"Started orchestration with ID = '{instance_id}'.")
    except Exception as ex:
        status_code = 400
        result = {
            "status": "fail",
            "exception": str(ex)
        }
        stats = {

        }
        response_payload = {
            "result": result,
            "stats": stats
        }
        return http_utils.generate_response(response_payload, status_code)

    return client.create_check_status_response(req, instance_id)
