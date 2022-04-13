"""Code execution utilities.
"""

from io import StringIO
from typing import Any
import contextlib
import sys


@contextlib.contextmanager
def capture_outputs(stdout=None, stderr=None):
    """
    Capture the outputs of stdout and stderr.
    Return type (which cannot be set as type annotation with Python <= 3.9):
    Generator[tuple[str, str], None, None]:
    """
    oldstdout = sys.stdout
    oldstderr = sys.stderr
    if stdout is None:
        stdout = StringIO()
    if stderr is None:
        stderr = StringIO()
    sys.stdout = stdout
    sys.stderr = stderr
    yield stdout, stderr
    sys.stdout = oldstdout
    sys.stderr = oldstderr


def exec_with_output(code: str, user_global_ns: dict, user_ns: dict):
    """
    It executes code statements and returns the execution result, the stdout, and the stderr.
    Return type (which cannot be set as type annotation with Python <= 3.9):
    tuple[Any, str, str]:
    """
    with capture_outputs() as (stdout, stderr):
        exec_result = exec(code, user_global_ns, user_ns)
        out = stdout.getvalue()
        err = stderr.getvalue()

        # We need to merge the user_ns into the user_global_ns for nested functions.
        # TODO verify if this is needed or not.
        user_global_ns["__builtins__"].update(user_ns)
        return exec_result, out, err
