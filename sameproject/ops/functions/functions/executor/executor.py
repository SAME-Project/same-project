from base64 import urlsafe_b64encode, urlsafe_b64decode
from sameproject.ops.execution import execute
from typing import Optional
from tempfile import mktemp
import logging
import time
import dill
import os


def info(msg: str):
    logging.info(f"executor: {msg}")


def decode_str(data: Optional[str]) -> Optional[str]:
    if data is None:
        return None

    return urlsafe_b64decode(data).decode("utf-8")


def decode_bytes(data: Optional[str]) -> Optional[bytes]:
    if data is None:
        return None

    return urlsafe_b64decode(data)


def executor(
    input: dict,
) -> str:
    """Executes a single SAME step in a pipeline."""
    start_secs = time.time()

    # Write sources from input into local directory:
    for name, source in input["step"]["sources"].items():
        with open(name, "w") as file:
            file.write(decode_str(source))

    # Install requirements, if necessary:
    if "requirements.txt" in input["step"]["sources"]:
        os.system("pip install -r requirements.txt")

    # Execute the step's code in a fresh execution frame:
    try:
        code = decode_str(input["step"]["code"])
        input_context = decode_bytes(input["session_context"])
        output_context = execute(code, input_context)

        return {
            "session_context": urlsafe_b64encode(
                output_context
            ).decode("utf-8"),
        }
    finally:
        info(f"total time taken: {1000 * (time.time() - start_secs)}ms")
