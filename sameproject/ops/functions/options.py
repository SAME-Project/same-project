from sameproject.ops.runtime_options import register_option

register_option(
    "functions_subscription_id",
    "Azure subscription ID containing the deployed 'functions' backend.",
    backend="functions",
    schema={
        "type": "string",
        "regex": r"^[\d\w-]+",
    },
)

register_option(
    "functions_host_name",
    "Hostname of the deployed 'functions' backend.",
    backend="functions",
    schema={
        "type": "string",
    },
)
