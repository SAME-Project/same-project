from __future__ import annotations
from .context import exception_utils
from .context import http_utils
import azure.functions as func
import azure.functions.blob as blob
import logging
import time


def get_object(
    req: func.HttpRequest,
    obj: blob.InputStream
) -> func.HttpResponse:
    """
    Returns the given object (retrieved as an input binding) in the HTTP response.
    """
    start_time = time.time()
    obj_name = req.params.get("obj_name")
    obj_content_bytes = None
    http_status = 404

    try:
        logging.info(f"GET: {obj_name}")

        if obj is not None:
            obj_content_bytes = obj.read()
            http_status = 200
        else:
            result = {
                "status": "fail",
                "reason": "Not found"
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
        end_time = time.time()
        time_taken_ms = 1000 * (end_time - start_time)
        logging.debug(f"Time taken to GET {obj_name}: {time_taken_ms}")

        http_response = http_utils.generate_binary_response(obj_content_bytes, http_status)
        return http_response
