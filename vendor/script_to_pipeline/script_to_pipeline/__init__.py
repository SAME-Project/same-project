from functools import partial, wraps
from typing import Callable, List, Optional

from .constants import DEPENDENCIES_ATTR, ENTRYPOINT_ATTR, PIPELINE_NAME_ATTR
from .utils import in_container


def pipeline(
    pipeline_function: Optional[Callable] = None,
    *,
    name: Optional[str] = None,
    dependencies: Optional[List[str]] = None
):
    def set_attributes(func):
        setattr(func, ENTRYPOINT_ATTR, True)
        setattr(func, PIPELINE_NAME_ATTR, name)
        setattr(func, DEPENDENCIES_ATTR, dependencies)

    if not in_container():
        # If we aren't running in the container, pass through
        if not pipeline_function:
            return partial(pipeline, name=name, dependencies=dependencies)
        set_attributes(pipeline_function)
        return pipeline_function

    def pipeline_decorator(pipeline_function_inner):
        @wraps(pipeline_function_inner)
        def wrapped_function(*args, **kwargs):
            return pipeline_function_inner(*args, **kwargs)
        set_attributes(wrapped_function)
        return wrapped_function

    if pipeline_function:
        return pipeline_decorator(pipeline_function)
    return pipeline_decorator




