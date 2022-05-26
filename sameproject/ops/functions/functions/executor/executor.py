from base64 import urlsafe_b64encode
import azure.functions.blob as blob
import azure.functions as fn
import logging
import time
import dill


def info(msg: str):
    logging.info(f"executor: {msg}")


def executor(
    input: dict,
    inputCtx: blob.InputStream,  # TODO: load pickle into user namespace.
    outputCtx: fn.Out[bytes]  # TODO: dump pickle into output context.
) -> str:
    """Executes a single SAME step in a pipeline."""
    start_secs = time.time()

    try:
        # Executes the step's code in a new execution frame, with a single
        # local/global namespace to simulate top-level execution.
        namespace = {}
        code = input["code"]
        exec(code, namespace, namespace) 

        # Prune out anything that can't be serialised in the user's namespace:
        keys = list(namespace.keys())
        for key in keys:
            try:
                dill.dumps(namespace[key])
            except TypeError:
                del namespace[key]
        pickle = dill.dumps(namespace)

        return {
            "context": urlsafe_b64encode(pickle).decode("utf-8"),
        }
    finally:
        info(f"total time taken: {1000 * (time.time() - start_secs)}ms")
