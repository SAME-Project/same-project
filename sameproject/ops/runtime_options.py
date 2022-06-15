from typing import Any, Callable, List, Optional
from cerberus import Validator, errors
from box import Box
import click
import os

# Registry of runtime options, which are backend-specific data passed to
# SAME via command line flags, environment variables or the SAME config file.
# These options are injected into the SAME config object before it is passed
# to a backend.
_registry = {}


def runtime_options(fn) -> Callable:
    """Returns a click decorator composing all registered runtime options."""
    return _compose_decorators(
        fn,
        map(get_option_decorator, list_options()),
    )


def runtime_schema(backend: str) -> dict:
    """
    Returns a cerberus schema for validating runtime options for a
    specific backend.
    """
    schema = {"type": "dict", "schema": {}}
    for opt in list_options():
        if _registry[opt].backend is None or _registry[opt].backend == backend:
            opt_schema = _registry[opt].schema
            if opt_schema is None:
                opt_schema = {"nullable": True, "type": _get_cerberus_type(_registry[opt].name, _registry[opt].type)}
            schema["schema"][opt] = opt_schema

    return schema


def list_options() -> List[str]:
    """Returns the list of registered options."""
    return _registry.keys()


def get_option_value(name: str) -> Any:
    """Returns the current value of the option with the given name."""
    if name not in _registry:
        raise Exception(f"Option registry does not contain name '{name}'.")

    return _registry[name].value


def get_option_decorator(name: str) -> Callable:
    """Returns a click decorator for setting an option via the command-line."""
    if name not in _registry:
        raise Exception(f"Option registry does not contain name '{name}'.")

    return click.option(
        _registry[name].flag,
        type=_registry[name].type,
        help=_registry[name].desc,
        envvar=_registry[name].env,
        callback=_registry[name].callback,
        is_flag=_registry[name].type == bool,
        expose_value=False,  # don't affect click method signatures
        is_eager=True,  # handle runtime options before other options
    )


class UserFriendlyMessagesErrorHandler(errors.BasicErrorHandler):
    messages = errors.BasicErrorHandler.messages.copy()
    messages[errors.NOT_NULLABLE.code] = "Value of variable is missing or empty."


def validate_options(backend: str):
    """
    Raises if the runtime options are set incorrectly for the given backend.
    """
    opts = {}
    for opt in list_options():
        if _registry[opt].backend is None or _registry[opt].backend == backend:
            opts[opt] = get_option_value(opt)

    validator = Validator(
        {"values": runtime_schema(backend)},
        error_handler=UserFriendlyMessagesErrorHandler,
    )
    if not validator.validate({"values": opts}):
        print("The following runtime options had errors:")
        error_values = validator.errors["values"][0]

        left_col_width = len(max(error_values.keys())) + 5
        for error_field_name, error_field_message_array in error_values.items():
            lcol = error_field_name
            val = f"'{opts[error_field_name] or ''}'"
            for error_field_message in error_field_message_array:
                print(f"  {lcol:<{left_col_width}}\t{val}\t{error_field_message.capitalize()}")
                lcol = ""  # Empty lcol label if there's more than one error
                val = ""

        # TODO: point to docs on setting runtime options
        # print("\nSee https://sameproject.ml/?")

        raise SyntaxError(f"One or more runtime options is invalid: {validator.errors}")


def register_option(
    name: str,
    desc: str,
    type: Any = str,
    flag: Optional[str] = None,
    env: Optional[str] = None,
    schema: Optional[dict] = None,
    backend: Optional[str] = None,
):
    """
    Registers a runtime option with the given metadata.

    :param name: The internal name used to refer to the option.
    :param desc: A description of what the option is configuring.
    :param type: The Python type of the option, e.g. 'str' or 'bool'.
    :param flag: Command line flag used to set the option. Defaults to a kebab-case translation of 'name', e.g. 'my_opt' ==> '--my-opt'.
    :param env: Environment variable used to set the option. Defaults to an upper-case translation of 'name', e.g. 'my_opt' ==> 'MY_OPT'.
    :param schema: Cerberus schema used to validate the option once it's been set. Defaults to checking that the input matches 'type'.
    :param backend: The backend this option is for - "None" signifies it is for all backends.
    """
    if flag is None:
        flag = "--" + name.replace("_", "-")

    if env is None:
        env = name.upper()

    value = None
    if env in os.environ:
        value = type(os.environ[env])

    _registry[name] = Box(
        {
            "name": name,
            "desc": desc,
            "flag": flag,
            "env": env,
            "type": type,
            "value": value,
            "schema": schema,
            "backend": backend,
            "callback": lambda ctx, param, value: setattr(_registry[name], "value", value),
        }
    )


def _get_cerberus_type(name: str, type: Any) -> str:
    if type == str:
        return "string"

    if type == int:
        return "integer"

    if type == bool:
        return "boolean"

    raise TypeError(f"Runtime option '{name}' has unsupported type '{type}'.")


def _compose_decorators(fn: Callable, decorators: List[Callable]) -> Callable:
    for decorator in decorators:
        fn = decorator(fn)
    return fn


# General SAME configuration:
register_option(
    "serialisation_memory_limit",
    "Maximum size in bytes allowed for variables being serialised between steps.",
    type=int,
)

register_option(
    "same_env",
    "Environment to compile and deploy notebooks against.",
)
