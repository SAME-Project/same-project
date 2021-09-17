"""Utilities for handling HTTP requests and responses.
"""

from . import serialization_utils
import json
import azure.functions as func


def generate_response(body: dict, status_code: int) -> func.HttpResponse:
    """
    """
    body_json_str = json.dumps(body)
    response = func.HttpResponse(
        body=body_json_str,
        mimetype="application/json",
        status_code=status_code,
    )
    return response


def get_deserialized_obj_from_request(param: str, req: func.HttpRequest) -> str:
    """Get the given parameter from the HTTP request and deserialize it.
    Returns the deserialized object.
    """
    if param not in req.params:
        raise Exception("Required parameter is missing: %s" % param)
    try:
        code_serialized = req.params.get(param)
        code = serialization_utils.deserialize_obj(code_serialized)
        return code
    except Exception as ex:
        raise Exception("Cannot get and deserialize parameter: %s - Exception: %s" % (param, ex))
