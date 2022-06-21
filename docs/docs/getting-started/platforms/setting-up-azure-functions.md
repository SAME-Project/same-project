---
type: docs
title: "Setting up Azure Functions"
description: "How to set up Azure Functions for SAME."
---

The `functions` backend is an [Azure Durable Functions](https://docs.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-overview) app that can execute SAME runs. In order to use it, you will first need to deploy the app to an Azure subscription that you own, and then configure SAME to send requests to it.


## Prerequisites

You will need the following tools to deploy the `functions` backend:

1. [`az`](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli), the Azure CLI tool.
2. [`func`](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=v4%2Clinux%2Ccsharp%2Cportal%2Cbash#install-the-azure-functions-core-tools), the Azure Functions CLI tool.
3. [`terraform`](https://learn.hashicorp.com/tutorials/terraform/install-cli), the Terraform CLI tool.

## Initial Setup

First, clone the [`same-project`](https://github.com/SAME-Project/same-project) git repository:

```bash
git clone https://github.com/SAME-Project/same-project.git
cd same-project
```

Next, you will need to authorise `terraform` to deploy resources to your Azure account. This can either be done using your personal [_user account_](https://registry.terraform.io/providers/hashicorp/azuread/latest/docs/guides/azure_cli), or by using a [_service principal_](https://registry.terraform.io/providers/hashicorp/azuread/latest/docs/guides/service_principal_client_secret) you have created for this purpose.


## Apply the Terraform

The `functions` backend provides Terraform scripts for provisioning the Azure resources it needs:

```bash
cd sameproject/ops/functions/terraform
terraform init
terraform apply
```

Once `terraform` has finished provisioning the resources, take note of the name and hostname of the function app that was created:

```bash
export FUNCTIONS_APP_NAME=$(terraform output -raw app_name)
export FUNCTIONS_HOST_NAME=$(terraform output -raw host_name)
```


## Deploy the Functions App

Next, you will need to deploy the SAME `functions` backend to your newly provisioned resources:

```bash
cd - && cd sameproject/ops/functions/functions
func azure functionapp publish $FUNCTIONS_APP_NAME
```

Once the deployment has finished you should be able to see the functions in the [Azure Functions portal](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.Web%2Fsites/kind/functionapp):

<div style="text-align: center;">
  <img src="/images/functions-root-portal.png" width="600px" />
</div>

The portal allows you to see which functions are active in the function app:

<div style="text-align: center;">
  <img src="/images/functions-function-list.png" width="600px" />
</div>

Clicking on one of these functions will bring up some useful tools for debugging and monitoring the app:

<div style="text-align: center;">
  <img src="/images/functions-monitoring.png" width="600px" />
</div>


## Test the Deployment

You are now ready to execute SAME runs on Azure Functions!

To test your deployment, you can run one of the test suite notebooks in the `same-project` repository:

```bash
cd - && cd test/testdata/features/singlestep
same run -t functions -f same.yaml \
  --functions-host-name "${FUNCTIONS_HOST_NAME}"
```

## Limitations

The Azure Functions backend does not support custom Docker images in SAME config files. All python dependencies must be specified using a `requirements.txt`, and non-python dependencies are not currently supported.
