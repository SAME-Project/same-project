"""Execute code from SAME on an Azure Functions backend.
"""


from .context import code_executor
from .context import exception_utils
from .context import http_utils
from .context import Step
import azure.functions as func
import logging
import time


# Constants
HTTP_PARAM_STEP = 'step'


def execute_step(req: func.HttpRequest) -> func.HttpResponse:
    """Execute code (step) from the incoming HTTP request and respond back with the result and appropriate outputs.
    In case of any exceptions in code execution or handling of code/state will be returned in the response.
    """
    start_time = time.time()
    logging.info("Executing request")
    status_code = 200

    try:
        try:
            # Fetch the step
            body = req.get_json()
            serialized_steps = body['steps']
            sorted_steps = Step.from_json_list(serialized_steps)
            num_steps = len(sorted_steps)

            # A single function execution is expected to execute a single Step, at least for now
            assert num_steps == 1, f"Expected a single Step object, received: {num_steps}"

            # Extract the Step to execute
            step = sorted_steps[0]
            logging.info(f"Executing Step: {step.name}")

            # TODO fetch namespaces from state
            global_namespace = {}
            local_namespace = {}

            # Execute the code from the given Step
            exec_result, stdout, stderr = code_executor.exec_with_output(step.code, global_namespace, local_namespace)

            result = {
                "status": "success",
                "exec_result": exec_result,
                "step_index": step.index,
                "stdout": stdout,
                "stderr": stderr
            }
        except Exception as ex:
            status_code = 400
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

            # TODO handle updated states
            state_size_bytes = 0

            # Prepare execution stats
            stats = {
                "start_time": start_time,
                "end_time": end_time,
                "time_taken_ms": time_taken_ms,
                "state_size_bytes": state_size_bytes
            }

        response_payload = {
            "result": result,
            "stats": stats
        }

        return http_utils.generate_response(response_payload, status_code)
    finally:
        logging.info("Total time taken: %.2f ms", 1000 * (time.time() - start_time))
