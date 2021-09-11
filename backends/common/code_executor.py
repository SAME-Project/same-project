"""Code execution utilities.
"""

import contextlib
import sys
from io import StringIO
from typing import Any, Generator


@contextlib.contextmanager
def capture_outputs(stdout=None, stderr=None) -> Generator[tuple[str, str], None, None]:
    """Capture the outputs of stdout and stderr.
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


def exec_with_output(code: str, user_global_ns: dict, user_ns: dict) -> tuple[Any, str, str]:
    """It executes code statements and returns the execution result, the stdout, and the stderr.
    """
    with capture_outputs() as (stdout, stderr):
        exec_result = exec(code, user_global_ns, user_ns)
        out = stdout.getvalue()
        err = stderr.getvalue()
        return exec_result, out, err
