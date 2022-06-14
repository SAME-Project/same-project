from sameproject.ops.runtime_options import register_option

register_option(
    "functions_subscription_id",
    "Azure subscription ID in which to provision backend functions.",
    backend="functions",
    schema={
        "nullable": True,
        "type": "string",
        "regex": r"^[\d\w-]+",
    },
)

register_option(
    "functions_skip_provisioning",
    "Skip provisioning of azure functions resources, to be used only if they already exist.",
    backend="functions",
    type=bool,
)
