from sameproject.ops.runtime_options import register_option, required_for_backend

register_option(
    "functions_subscription_id",
    "Azure subscription ID in which to provision backend functions.",
    validator=required_for_backend("functions"),
    schema={
        "nullable": True,
        "type": "string",
        "regex": r"^[\d\w-]+",
    },
)

register_option(
    "functions_skip_provisioning",
    "Skip provisioning of azure functions resources, to be used only if they already exist.",
    type=bool,
)
