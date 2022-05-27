import azure.durable_functions as df
import azure.functions as fn
import logging
import json


def info(msg: str):
    logging.info(f"initiator: {msg}")


async def initiator(req: fn.HttpRequest, client: str) -> fn.HttpResponse:
    """Initiates the orchestration of a SAME pipeline."""
    client = df.DurableOrchestrationClient(client)

    try:
        json_data = req.get_json()
    except ValueError:
        return fn.HttpResponse(
            status_code=400,
            body="error: a json request body is required"
        )

    info(f"body of request: {json_data}")

    try:
        instance_id = await client.start_new("orchestrator", None, json_data)
    except Exception as err:
        return fn.HttpResponse(
            status_code=400,
            body=f"error: failed to orchestrate workflow: {err}",
        )

    info(f"started orchestration with id: {instance_id}")
    return client.create_check_status_response(req, instance_id)
