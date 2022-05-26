from azure.mgmt.applicationinsights import ApplicationInsightsManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.web import WebSiteManagementClient
from azure.identity import DefaultAzureCredential
from zipfile import ZipFile
from tempfile import mktemp
from pathlib import Path
import requests
import json


# TODO configure application insights
# TODO pin api versions for all of the clients
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
    aim_client = ApplicationInsightsManagementClient(creds)

    # A hack to fix a bug in azure.mgmt.applicationinsights.
    #   see: https://github.com/Azure/azure-sdk-for-python/issues/24606
    setattr(aim_client._config, "subscription_id", subscription_id)

    # Create a resource group to house everything we"re going to provision:
    print("Provisioning resource group 'same-resource_group'...")
    rm_client.resource_groups.create_or_update(
        "same-resource-group",
        {
            "location": "West US",
        },
    )

    # Provisions a storage account for the functionapp:
    print("Provisioning storage account 'samestorageaccount'...")
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

    # Provisions an application insights component for logging:
    print("Provisioning application insights component 'same-app-insights'...")
    ai = aim_client.components.create_or_update(
        "same-resource-group",
        "same-app-insights",
        {
            "kind": "web",
            "location": "West US",
            "application_type": "web",
        }
    )

    # Provisions an app service plan for the functionapp:
    print("Provisioning app service plan 'same-app-service-plan'...")
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
    print("Provisioning function app 'same-site'...")
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
                    {
                        "name": "APPINSIGHTS_INSTRUMENTATIONKEY",
                        "value": ai.instrumentation_key,
                    },
                    {
                        "name": "APPLICATIONINSIGHTS_CONNECTION_STRING",
                        "value": f"InstrumentationKey=${ai.instrumentation_key}",
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
    print("Creating zip archive of orchestrator functions...")
    zip = create_function_archive()
    print(f"Archive saved to: {zip.absolute()}")

    # Deploys the zipped function to the functionapp using zip deployment:
    #  https://docs.microsoft.com/en-us/azure/azure-functions/deployment-zip-push
    username = pcs.result().publishing_user_name
    password = pcs.result().publishing_password
    with zip.open("rb") as file:
        zip_data = file.read()

    print("Deploying zip archive to: https://same-site.scm.azurewebsites.net/api/zipdeploy")
    res = requests.post(
        "https://same-site.scm.azurewebsites.net/api/zipdeploy",
        data=zip_data,
        auth=(username, password),
    )

    if res.status_code == 200:
        print("Successful deployment!")
    else:
        raise Exception(f"Deployment was unsuccessful, with status code: {res.status_code}")


def create_function_archive():
    """Creates a temporary zip archive of the 'functions/' directory."""
    zip = Path(mktemp(suffix=".zip"))
    with ZipFile(zip, "w") as archive:
        root = Path(__file__).parent / "functions"
        for file in root.rglob("*"):
            archive.write(file, file.relative_to(root))

    return zip
