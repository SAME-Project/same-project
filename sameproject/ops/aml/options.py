from sameproject.ops.runtime_options import register_option

register_option(
    "aml_compute_name",
    "Azure compute name for the pre-provisioned compute cluster.",
    backend="aml",
    schema={"nullable": False, "type": "string", "regex": r"^[\d\w-]+", "maxlength": 24, "minlength": 3},
)

register_option(
    "aml_sp_password_value",
    "Password for the service principal necessary for running this AML job. Read more here: https://docs.microsoft.com/en-us/cli/azure/create-an-azure-service-principal-azure-cli",
    backend="aml",
    schema={
        "nullable": False,
        "type": "string",
    },
)

register_option(
    "aml_sp_tenant_id",
    "Tenant for the service principal necessary for running this AML job. Read more here: https://docs.microsoft.com/en-us/cli/azure/create-an-azure-service-principal-azure-cli",
    backend="aml",
    schema={
        "nullable": False,
        "type": "string",
        "regex": r"^[\d\w-]+",
    },
)

register_option(
    "aml_sp_app_id",
    "Service Principal App ID for the service principal necessary for running this AML job. Read more here: https://docs.microsoft.com/en-us/cli/azure/create-an-azure-service-principal-azure-cli",
    backend="aml",
    schema={
        "nullable": False,
        "type": "string",
        "regex": r"^[\d\w-]+",
    },
)

register_option(
    "workspace_subscription_id",
    "Workspace ID for your AML backend. Read more here: https://docs.microsoft.com/en-us/azure/machine-learning/how-to-configure-environment#workspace",
    backend="aml",
    schema={
        "nullable": False,
        "type": "string",
        "regex": r"^[\d\w-]+",
    },
)

register_option(
    "workspace_resource_group",
    "Workspace resource group for your AML backend. Read more here: https://docs.microsoft.com/en-us/azure/machine-learning/how-to-configure-environment#workspace",
    backend="aml",
    schema={
        "nullable": False,
        "type": "string",
        "regex": r"^[\d\w-]+",
    },
)

register_option(
    "workspace_name",
    "Workspace name for your AML backend. Read more here: https://docs.microsoft.com/en-us/azure/machine-learning/how-to-configure-environment#workspace",
    backend="aml",
    schema={
        "nullable": False,
        "type": "string",
        "regex": r"^[\d\w-]+",
    },
)
