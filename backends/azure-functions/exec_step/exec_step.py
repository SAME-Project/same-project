"""Execute code from SAME on an Azure Functions backend.
"""

import azure.functions as func
import logging
import time
from .context import code_executor as ce
from ..utils import http_utils as hu

def exec_code(req: func.HttpRequest) -> func.HttpResponse:
    """Execute code from the incoming HTTP request and respond back with the result and appropriate outputs.
    In case of any exceptions in code execution or handling of code/state will be returned in the response.
    """
    t_0 = time.time()
    logging.info("Executing code")

    try:
        try:
            # Fetch the code.
            code = hu.get_code_from_request(req)

            exec_result = None
            stdout = None
            stderr = None

            # TODO fetch namespaces from state.
            global_namespace = {}
            local_namespace = {}

            # Execute the code
            exec_result, stdout, stderr = ce.exec_with_output(code, global_namespace, local_namespace)

            # We need to merge the user_ns into the user_global_ns for nested functions.
            # TODO verify that this is needed or not.
            global_namespace["__builtins__"].update(local_namespace)
        except Exception as ex:
            return hu.create_error_response(f"Exception executing the code: {ex}", exception=True)
        finally:
            # TODO output updated states.
            pass

        # Success reply to Jupyter
        response_payload = {
            "exec_result": exec_result,
            "stdout": stdout,
            "stderr": stderr,
            "state_size": 0, # TODO update with the size of serialized states
        }

        return hu.create_success_response(response_payload)
    finally:
        logging.info("Time to execute code: %.2f ms", 1000 * (time.time() - t_0))
