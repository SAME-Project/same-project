from typing import Any, Callable, List, Optional
from cerberus import Validator
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
    schema = {
        "type": "dict",
        "schema": {},
    }

    for opt in list_options():
        opt_schema = _registry[opt].schema
        if opt_schema is None:
            opt_schema = {
                "nullable": True,
                "type": _get_cerberus_type(
                    _registry[opt].name,
                    _registry[opt].type
                )
            }
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


def validate_options(backend: str):
    """
    Raises if the runtime options are set incorrectly for the given backend.
    Doing it with 'validator' functions allows us to have options that are
    conditionally dependent on each other for a particular backend.
    """
    opts = {}
    for name in list_options():
        opts[name] = get_option_value(name)

    validator = Validator({"values": runtime_schema()})
    if not validator.validate({"values": opts}):
        raise SyntaxError(f"One or more runtime options is invalid: {validator.errors}")

    for name in list_options():
        if _registry[name].validator is not None:
            _registry[name].validator(backend, name, opts)


def _compose_decorators(fn: Callable, decorators: List[Callable]) -> Callable:
    for decorator in decorators:
        fn = decorator(fn)
    return fn


def _register_option(
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
        "schema": schema,
        "validator": validator,
        "callback": lambda ctx, param, value: setattr(_registry[name], "value", value),
    })


def _get_cerberus_type(name: str, type: Any) -> str:
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
