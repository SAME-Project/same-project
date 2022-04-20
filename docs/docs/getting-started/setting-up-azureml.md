---
type: docs
title: "Setting up Azure ML"
description: "How to set up Azure ML for SAME."
weight: 30
---

In order to use AzureML, you need to have environment variables named the following:

```bash
export AML_SP_PASSWORD_VALUE= 
export AML_SP_TENANT_ID= 
export AML_SP_APP_ID= 
export WORKSPACE_SUBSCRIPTION_ID= 
export WORKSPACE_RESOURCE_GROUP=
export WORKSPACE_NAME=
export AML_COMPUTE_NAME=
```

To set the workspace variables, follow this instruction:
https://docs.microsoft.com/en-us/azure/machine-learning/how-to-configure-environment#workspace


Create a service principal account: 
https://docs.microsoft.com/en-us/azure/machine-learning/how-to-setup-authentication

```bash
az ad sp create-for-rbac --sdk-auth --name same-project-aml-auth --role Contributor --scopes /subscriptions/72ac7288-fb92-4ad6-83bc-5cfd361f47ef
```
AML_SP_APP_ID => clientId
AML_SP_PASSWORD_VALUE => clientSecret
AML_SP_TENANT_ID => tenantId

Create a compute cluster

```bash
az extension add -n azure-cli-ml
az ml computetarget create amlcompute -n cpu --min-nodes 2 --max-nodes 3 -s STANDARD_D3_V2 --location koreacentral
```
