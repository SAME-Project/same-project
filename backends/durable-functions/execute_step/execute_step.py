from .context import code_executor
from .context import exception_utils
from .context import Step
import logging
import time


def execute_step(step: Step) -> str:
    """Executes a given Step and returns the produced result and output in stderr, stdout.
    """
    start_time = time.time()
    logging.info(f"Executing Step: {step.name}")

    try:
        try:
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

        return response_payload
    finally:
        logging.info("Total time taken: %.2f ms", 1000 * (time.time() - start_time))
