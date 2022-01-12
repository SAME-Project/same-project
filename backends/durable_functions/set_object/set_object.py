from __future__ import annotations
from .context import exception_utils
from .context import http_utils
import azure.functions as func
import logging
import time


def set_object(
    req: func.HttpRequest,
    obj #: func.Out
) -> func.HttpResponse:
    """
    Sets the given object (in the HTTP request) to an output binding.
    """
    start_time = time.time()
    obj_name = req.params.get("obj_name")
    obj_content = req.get_body()

    try:
        logging.info(f"SET: {obj_name}, {type(obj)}")

        obj_size_bytes = len(obj_content)

        if obj_content is not None:
            obj.set(obj_content)

        # Prepare the result
        result = {
            "status": "success",
            "size": obj_size_bytes
        }
    except Exception as ex:
        exception_info = exception_utils.get_exception_info()
        result = {
            "status": "fail",
            "reason": "exception",
            "exception": str(ex),
            "info": exception_info
        }
    finally:
        # Measure execution time
        end_time = time.time()
        time_taken_ms = 1000 * (end_time - start_time)

        # Prepare execution stats
        stats = {
            "start_time": start_time,
            "end_time": end_time,
            "time_taken_ms": time_taken_ms,
        }

        response_payload = {
            "result": result,
            "stats": stats
        }

        http_status = 200
        http_response = http_utils.generate_json_response(response_payload, http_status)
        return http_response
