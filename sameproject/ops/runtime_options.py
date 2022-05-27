from traceback import print_last
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


def runtime_schema() -> dict:
    """Returns a cerberus schema for validating runtime options."""

    # TODO: #161 Not sure if this is correct (allowing unknown) - SHOULD work, since we validate elsewhere, but seems silly not to reuse the same validation rules. The reason I had to do this was in SameConfig, runtime_options does not get the same rules as we inject in options.py - it's just a dict.
    schema = {"type": "dict", "schema": {}, "allow_unknown": True}

    for opt in list_options():
        schema["schema"][opt] = {
            "type": _get_cerberus_type(
                _registry[opt].name,
                _registry[opt].type
            )
        }

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


def _register_option(name: str, desc: str, type=str, flag=None, env=None):
    """
    Raises if the runtime options are set incorrectly for the given backend.
    Doing it with 'validator' functions allows us to have options that are
    conditionally dependent on each other for a particular backend.
    """
    opts = {}
    for name in list_options():
        opts[name] = get_option_value(name)

    validator = Validator({"values": runtime_schema()}, error_handler=UserFriendlyMessagesErrorHandler)
    if not validator.validate({"values": opts}):
        print("The following environment variables had errors:")
        error_values = validator.errors["values"][0]

        left_col_width = len(max(error_values.keys())) + 5

        for error_field_name, error_field_message_array in error_values.items():
            lcol = error_field_name.upper()
            val = f"'{opts[error_field_name] or ''}'"
            for error_field_message in error_field_message_array:
                print(f"  {lcol:<{left_col_width}}\t{val}\t{error_field_message.capitalize()}")
                lcol = ""  # Empty lcol label if there's more than one error
                val = ""

        raise SyntaxError(f"One or more runtime options is invalid: {validator.errors}")

    for name in list_options():
        if _registry[name].validator is not None:
            _registry[name].validator(backend, name, opts)


def required_for_backend(backend: str) -> Callable:
    """Validator that marks an option as required for a given backend."""

    def _inner(_backend, name, opts):
        if _backend == backend:
            if opts[name] is None:
                raise Exception(f"Option '{name}' must be set for backend '{backend}'.")

    return _inner


def register_option(
    name: str,
    desc: str,
    type: Any = str,
    flag: Optional[str] = None,
    env: Optional[str] = None,
    schema: Optional[dict] = None,
    validator: Callable[[str, str, dict], None] = None,
):
    """
    Registers a runtime option with the given metadata.

    :param name: The internal name used to refer to the option.
    :param desc: A description of what the option is configuring.
    :param type: The Python type of the option, e.g. 'str' or 'bool'.
    :param flag: Command line flag used to set the option. Defaults to a kebab-case translation of 'name', e.g. 'my_opt' ==> '--my-opt'.
    :param env: Environment variable used to set the option. Defaults to an upper-case translation of 'name', e.g. 'my_opt' ==> 'MY_OPT'.
    :param schema: Cerberus schema used to validate the option once it's been set. Defaults to checking that the input matches 'type'.
    :param validator: Function that receives the current backend, option name and bag of options and raises if the option has been set incorrectly.
    """
    if flag is None:
        flag = "--" + name.replace("_", "-")

    if env is None:
        env = name.upper()

    value = None
    if env in os.environ:
        value = type(os.environ[env])

    _registry[name] = Box({
        "name": name,
        "desc": desc,
        "flag": flag,
        "env": env,
        "type": type,
        "value": value,
        "callback": lambda ctx, param, value: setattr(_registry[name], "value", value),
    })


def _get_cerberus_type(name, type):
    if type == str:
        return "string"

    if type == int:
        return "integer"

    if type == bool:
        return "boolean"

    raise TypeError(f"Runtime option '{name}' has unsupported type '{type}'.")


# General SAME configuration:
_register_option(
    "serialisation_memory_limit",
    "Maximum size in bytes allowed for variables being serialised between steps.",
    type=int,
)
_register_option(
    "same_env",
    "Environment to compile and deploy notebooks against.",
)

# Options for Kubeflow backend:
_register_option(
    "image_pull_secret_name",
    "The name of the kubernetes secret to create for docker secrets.",
)
_register_option(
    "image_pull_secret_registry_uri",
    "URI of private docker registry for private image pulls.",
)
_register_option(
    "image_pull_secret_username",
    "Username for private docker registry for private image pulls.",
)
_register_option(
    "image_pull_secret_password",
    "Password for private docker registry for private image pulls.",
)
_register_option(
    "image_pull_secret_email",
    "Email address for private docker registry for private image pulls.",
)

# Options for Azure durable functions backend:
_register_option(
    "functions_subscription_id",
    "Azure subscription ID in which to provision backend functions.",
)
_register_option(
    "functions_skip_provisioning",
    "Skip provisioning of azure functions resources, to be used only if they already exist.",
    type=bool,
)

# Options for AML backend:
# TODO: write help lines for each of these options
_register_option("aml_compute_name", "")
_register_option("aml_sp_password_value", "")
_register_option("aml_sp_tenant_id", "")
_register_option("aml_sp_app_id", "")
_register_option("workspace_subscription_id", "")
_register_option("workspace_resource_group", "")
_register_option("workspace_name", "")
