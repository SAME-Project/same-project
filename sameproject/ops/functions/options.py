from sameproject.ops.runtime_options import register_option

register_option(
    "functions_host_name",
    "Hostname of the deployed 'functions' backend.",
    backend="functions",
    schema={
        "type": "string",
    },
)

register_option(
    "functions_use_http",
    "Use http instead of https for communicating with 'functions' backend.",
    type=bool,
    backend="functions",
    default_value=False,
    schema={
        "type": "boolean",
    },
)
