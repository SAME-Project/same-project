from .context import http_utils
import azure.functions as func
import azure.durable_functions as df
import logging


async def start_steps_workflow(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    """
    Starts the orchestration that will execute a given list of Steps.
    """
    client = df.DurableOrchestrationClient(starter)

    try:
        # Fetch the steps
        body = req.get_json()

        # Start workflow orchestrator
        instance_id = await client.start_new(req.route_params["functionName"], None, body)
        logging.info(f"Started orchestration with ID = '{instance_id}'.")
    except Exception as ex:
        status_code = 400
        result = {
            "status": "fail",
            "exception": str(ex)
        }
        stats = {}
        response_payload = {
            "result": result,
            "stats": stats
        }
        return http_utils.generate_response(response_payload, status_code)

    return client.create_check_status_response(req, instance_id)
