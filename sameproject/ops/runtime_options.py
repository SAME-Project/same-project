from box import Box
import click

# Registry of runtime options, which are backend-specific data passed to
# SAME via command line flags, environment variables or the SAME config file.
# These options are injected into the SAME config object before it is passed
# to a backend.
_registry = {}


def runtime_options(fn):
    """Returns a click decorator composing all registered runtime options."""
    return _compose_decorators(
        fn,
        map(get_option_decorator, list_options()),
    )


def runtime_schema():
    """Returns a cerberus schema for validating runtime options."""
    schema = {
        "type": "dict",
        "schema": {},
    }

    for opt in list_options():
        schema["schema"][opt] = {"type": "string"}  # TODO: other types?

    return schema


def list_options():
    """Returns the list of registered options."""
    return _registry.keys()


def get_option_value(name):
    """Returns the current value of the option with the given name."""
    if name not in _registry:
        raise Exception(f"Option registry does not contain name '{name}'.")

    return _registry[name].value


def get_option_decorator(name):
    """Returns a click decorator for setting an option via the command-line."""
    if name not in _registry:
        raise Exception(f"Option registry does not contain name '{name}'.")

    return click.option(
        _registry[name].flag,
        help=_registry[name].desc,
        envvar=_registry[name].env,
        callback=_registry[name].callback,
        expose_value=False,  # don't affect click method signatures
        required=False,  # TODO: support required runtime options?
        is_eager=True,  # handle runtime options before other options
    )


def _compose_decorators(fn, decorators):
    for decorator in decorators:
        fn = decorator(fn)
    return fn


def _register_option(name: str, desc: str, flag=None, env=None):
    """
    Registers an option with the given internal name, command-line flag and
    environment variable.
    """
    if flag is None:
        flag = "--" + name.replace("_", "-")

    if env is None:
        env = name.upper()

    _registry[name] = Box({
        "name": name,
        "desc": desc,
        "flag": flag,
        "env": env,
        "value": None,
        "callback": lambda ctx, param, value: setattr(_registry[name], "value", value),
    })


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

# Options for AML backend:
# TODO: write help lines for each of these options
_register_option("aml_compute_name", "")
_register_option("aml_sp_password_value", "")
_register_option("aml_sp_tenant_id", "")
_register_option("aml_sp_app_id", "")
_register_option("workspace_subscription_id", "")
_register_option("workspace_resource_group", "")
_register_option("workspace_name", "")
