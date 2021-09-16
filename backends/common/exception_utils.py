"""Utilities for capturing information about raised exceptions.
"""

from . import serialization_utils as su
import sys


def get_exception_info() -> str:
    """Get information about the currently raised exception.
    """
    exc_info = sys.exc_info()
    exception_msg = str(exc_info[1])
    exception_serialized = su.serialize_obj(exc_info)

    info = {
        "exception_msg": exception_msg,
        "exception": exception_serialized
    }
    return info
