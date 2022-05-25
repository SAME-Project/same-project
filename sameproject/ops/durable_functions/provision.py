# from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.web import WebSiteManagementClient
from azure.identity import DefaultAzureCredential
from zipfile import ZipFile
from tempfile import mktemp
from pathlib import Path
import requests
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

    # Provisions a storage account for the functionapp:
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

    # To use the storage account we need an access key:
    sak = sm_client.storage_accounts.list_keys(
        "same-resource-group",
        "samestorageaccount",
    )

    # Provisions an app service plan for the functionapp:
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

    # Provisions the actual functionapp and configures it for python:
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
                        "value": f"DefaultEndpointsProtocol=https;AccountName=samestorageaccount;EndpointSuffix=core.windows.net;AccountKey={sak.keys[0].value}",
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

    # To deploy a function to the functionapp we need credentials:
    pcs = wm_client.web_apps.begin_list_publishing_credentials(
        "same-resource-group",
        "same-site",
    )
    pcs.wait()

    # Zips the relevant files for the orchestrator function:
    root = Path(__file__).parent
    zip = Path(mktemp(suffix=".zip"))
    with ZipFile(zip, "w") as archive:
        archive.write(root / "host.json", "host.json")
        archive.write(root / "requirements.txt", "requirements.txt")
        archive.write(root / "orchestrator" / "__init__.py", "orchestrator/__init__.py")
        archive.write(root / "orchestrator" / "function.json", "orchestrator/function.json")

    # Deploys the zipped function to the functionapp using zip deployment:
    #  https://docs.microsoft.com/en-us/azure/azure-functions/deployment-zip-push
    username = pcs.result().publishing_user_name
    password = pcs.result().publishing_password
    with zip.open("rb") as file:
        zip_data = file.read()

    res = requests.post(
        "https://same-site.scm.azurewebsites.net/api/zipdeploy",
        data=zip_data,
        auth=(username, password),
    )

    print(f"Deployment status code: {res.status_code}")
