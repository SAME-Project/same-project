"""Utilities for handling HTTP requests and responses.
"""

import azure.functions as func
import json
import sys
from .context import serialization_utils as su


def create_error_response(msg: str, status_code=400, exception=False):
    """Create an HTTP response indicating failure with information about the exception in the body.
    """
    response_payload = {
        "msg": msg,
    }
    if exception:
        exc_info = sys.exc_info()
        response_payload["exception_msg"] = str(exc_info[1])
        response_payload["exception"] = su.serialize_obj(exc_info)
    body = json.dumps(response_payload)
    return func.HttpResponse(
        body=body,
        mimetype="application/json",
        status_code=status_code,
    )


def create_success_response(params: dict, pretty=False) -> func.HttpResponse:
    """Create an HTTP response indicating success with the given parameters in the body.
    """
    if pretty:
        body = json.dumps(params, indent=2)
    else:
        body = json.dumps(params)
    return func.HttpResponse(
        body=body,
        mimetype="application/json",
        status_code=200,
    )


def get_code_from_request(req: func.HttpRequest) -> str:
    """Get the code to execute from the given HTTP request.
    It is expected to be base64 encoded in the request and will be decoded before being returned.
    """
    if 'code' not in req.params:
        raise Exception("Required parameter is missing: code")
    try:
        code_serialized = req.params.get("code")
        code = su.deserialize_obj(code_serialized)
        return code
    except Exception as ex:
        raise Exception("Cannot parse 'code_obj' parameter: %s" % ex)
