from __future__ import annotations
from typing import List
from .context import code_executor
from .context import exception_utils
from .context import Step
from .context import NumpyToNumsTransformer
from .context import PandasToDaskTransformer
from .context import Transformer
from .context import ExecutionEnvironment
import azure.functions as func
import azure.functions.blob as blob
import logging
import time


def execute_step(
    input: dict,
    envin: blob.InputStream,
    envout: func.Out[bytes]
) -> str:
    """
    Executes a given Step and returns the produced result and output in stderr, stdout.
    """
    start_time = time.time()
    output_env_size_bytes = 0

    try:
        step : Step = input["step"]
        logging.info(f"Executing Step: {step.name}")

        # Get the execution environment from input
        if envin is not None:
            envin_serialized = envin.read()
            env : ExecutionEnvironment = ExecutionEnvironment.deserialize(envin_serialized)
        else:
            env : ExecutionEnvironment = ExecutionEnvironment()

        try:
            # Perform code transformations
            transformers : List[Transformer] = [
                PandasToDaskTransformer(env),
                NumpyToNumsTransformer(env)
            ]
            for transformer in transformers:
                transformer.transform_step(step)

            # Execute the code from the given Step
            exec_result, stdout, stderr = code_executor.exec_with_output(
                step.code,
                env.global_namespace,
                env.local_namespace)

            # Post-process for each transformer
            for transformer in transformers:
                transformer.post_process()

            # Serialize the execution environment and set the output
            env_serialized = env.serialize()
            envout.set(env_serialized)
            output_env_size_bytes = len(env_serialized)

            # Prepare the result
            result = {
                "status": "success",
                "exec_result": exec_result,
                "step_index": step.index,
                "executed_code": step.code,
                "env_access_stats": env.access_stats,
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

            # Prepare execution stats
            stats = {
                "start_time": start_time,
                "end_time": end_time,
                "time_taken_ms": time_taken_ms,
                "output_env_size_bytes": output_env_size_bytes,
            }

        response_payload = {
            "result": result,
            "stats": stats
        }

        return response_payload
    finally:
        logging.info("Total time taken: %.2f ms", 1000 * (time.time() - start_time))
