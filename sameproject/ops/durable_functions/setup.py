# from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.web import WebSiteManagementClient
from azure.identity import DefaultAzureCredential
from pathlib import Path
import json


# TODO: deploy a storage account for the functionapp.
# TODO: make idempotent - seems to be by default though!.
def provision_orchestrator(
    subscription_id: str,
):
    """
    Idempotently provisions the orchestrator function app. Once the
    orchestrator is provisioned, SAME can deploy notebooks to the orchestrator
    for execution.

    Provisioning is based on the following bicep template:
    https://github.com/Azure/azure-quickstart-templates/blob/master/quickstarts/microsoft.web/function-app-create-dynamic/main.bicep
    """
    creds = DefaultAzureCredential()
    rm_client = ResourceManagementClient(creds, subscription_id)
    wm_client = WebSiteManagementClient(creds, subscription_id)
    sm_client = StorageManagementClient(creds, subscription_id)

    # Create a resource group to house everything we"re going to provision:
    rm_client.resource_groups.create_or_update(
        "same-resource-group",
        {
            "location": "West US",
        },
    )

    sa = sm_client.storage_accounts.begin_create(
        "same-resource-group",
        "samestorageaccount",
        {
            "kind": "Storage",
            "location": "West US",
            "sku": {
                "name": "Standard_LRS",
            },
        }
    )
    sa.wait()
    print(sa.result())

    sak = sm_client.storage_accounts.list_keys(
        "same-resource-group",
        "samestorageaccount",
    )
    storage_string = f"DefaultEndpointsProtocol=https;AccountName=samestorageaccount;EndpointSuffix=core.windows.net;AccountKey={sak.keys[0].value}"
    print(storage_string)

    asp = wm_client.app_service_plans.begin_create_or_update(
        "same-resource-group",
        "same-app-service-plan",
        {
            "kind": "functionapp",
            "location": "West US",
            "reserved": False,
            "sku": {
                "name": "Y1",
                "tier": "Dynamic",
                "size": "Y1",
                "family": "Y",
                "capacity": 0
            },
        }
    )
    asp.wait()
    print("HERE")
    print(asp.result())

    wa = wm_client.web_apps.begin_create_or_update(
        "same-resource-group",
        "same-site",
        {
            'location': "West US",
            'server_farm_id': asp.result().id,
            'reserved': False,
            'enabled': True,
            'kind': 'functionapp',
            'site_config': {
                "python_version": "3.9",
                "app_settings": [
                    {
                        "name": "AzureWebJobsStorage",
                        "value": storage_string,
                    },
                    {
                        "name": "FUNCTIONS_EXTENSION_VERSION",
                        "value": "~4",
                    },
                    {
                        "name": "FUNCTIONS_WORKER_RUNTIME",
                        "value": "python",
                    },
                ],
            }
        }
    )
    wa.wait()
    print("HERE")
    print(wa.result())

    # So we can actually hit a host name like this!

    root_path = Path(__file__).parent / "orchestrator"
    config_path = root_path / "function.json"
    script_path = root_path / "__init__.py"
    print(config_path.as_uri())
    with config_path.open("r") as file:
        config = json.loads(file.read())
