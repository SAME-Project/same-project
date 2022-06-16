from base64 import urlsafe_b64encode, urlsafe_b64decode
import azure.functions.blob as blob
import azure.functions as fn
import logging
import time
import dill


# Encodes a session
empty_context = urlsafe_b64encode(dill.dumps({})).decode("utf-8")


def info(msg: str):
    logging.info(f"executor: {msg}")


def executor(
    input: dict,
) -> str:
    """Executes a single SAME step in a pipeline."""
    start_secs = time.time()

    try:
        # Executes the step's code in a new execution frame, with a single
        # local/global session_context to simulate top-level execution.
        code = input["code"]
        session_context_enc = input.get("session_context", empty_context)
        session_context = dill.loads(urlsafe_b64decode(session_context_enc))
        exec(code, session_context, session_context)

        # Prune out anything that can't be serialised in the user's session_context:
        keys = list(session_context.keys())
        for key in keys:
            try:
                dill.dumps(session_context[key])
            except TypeError:
                del session_context[key]
        pickle = dill.dumps(session_context)

        return {
            "session_context": urlsafe_b64encode(pickle).decode("utf-8"),
        }
    finally:
        info(f"total time taken: {1000 * (time.time() - start_secs)}ms")
