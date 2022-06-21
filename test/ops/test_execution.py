from sameproject.ops.execution import execute, load
import pytest


steps = [
    "a = 0",
    "b = a + 1",
    "c = 2*b",
    """def poly(x):
    return 2*x + 1""",
    "d = poly(c)",
]


def test_execution():
    session_context = None
    for step in steps:
        session_context = execute(step, session_context)

    module = load(session_context)
    assert module.a == 0
    assert module.b == 1
    assert module.c == 2
    assert module.d == 5
