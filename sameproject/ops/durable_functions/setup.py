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

    sak = sm_client.storage_accounts.list_keys(
        "same-resource-group",
        "samestorageaccount",
    )
    storage_string = f"DefaultEndpointsProtocol=https;AccountName=samestorageaccount;EndpointSuffix=core.windows.net;AccountKey={sak.keys[0].value}"

    asp = wm_client.app_service_plans.begin_create_or_update(
        "same-resource-group",
        "same-app-service-plan",
        {
            "kind": "linux",
            "reserved": "true",
            "location": "West US",
            "sku": {
                "name": "Y1",
            },
        }
    )
    asp.wait()

    wa = wm_client.web_apps.begin_create_or_update(
        "same-resource-group",
        "same-site",
        {
            "kind": "functionapp,linux",
            "location": "West US",
            "reserved": True,
            "server_farm_id": asp.result().id,
            "site_config": {
                "linux_fx_version": "PYTHON|3.9",
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
