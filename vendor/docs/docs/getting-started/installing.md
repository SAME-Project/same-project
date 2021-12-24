---
type: docs
title: "Installing SAME"
linkTitle: "Installing SAME"
description: "How to install the SAME binary"
weight: 10
---

> ## ⚠ Warning
>
> The instructions for installing SAME CLI binary tool will use the version generated from the archived https://github.com/azure-octo/same-cli private repo.
>
> To use the updated same-mono-private version of the tool, you will need to run it from source code as described in [How to set up your environment for running tests and building SAME]({{< ref dev-build.md >}}).

## Installing SAME

In order to use the SAME CLI to build and deploy your code, you first need to install the SAME binary. This is a no-dependency binary that runs on various operating systems, with pre-built binaries for recent versions of Windows, MacOS and Linux.

{{< tabs From-Source Linux MacOS Windows Binaries >}}
{{% codetab %}}

It is currently recommended to clone the repo and run SAME CLI directly from the Python virtual environment.

For details, refer to [How to set up your environment for running tests and building SAME]({{< ref dev-build.md >}}).

{{% /codetab %}}

{{% codetab %}}

Execute the following command to install SAME on Linux.

```bash
curl -L0 https://get.sameproject.org/ | bash -
```

{{% /codetab %}}

{{% codetab %}}

Execute the following command to install SAME on MacOS.

```bash
curl -L0 https://get.sameproject.org/ | bash -
```

{{% /codetab %}}

{{% codetab %}}

```powershell
# Not supported
```

{{% /codetab %}}

{{% codetab %}}

1. Download the `same` CLI from the pre-built packages and signatures:

   - <https://github.com/SAME-Project/SAMPLE-CLI-TESTER/releases>

1. Ensure the user has permission to execute the binary and place it somewhere on your PATH so it can be invoked easily.

{{% /codetab %}}
{{< /tabs >}}

## Connecting to a Workflow engine

To run SAME, you will need a workflow engine to connect to. We support a variety of workflow engines, but recommend that, for now, you connect to one that is dedicated to SAME exclusively. Below are installation and configuration instructions for each.

{{< tabs Kubernetes-Kubeflow Azure-Machine-Learning Sagemaker Airflow >}}

{{% codetab %}}

1. Verify that you have a Kubernetes cluster configured with a local `kubectl` context set as the default.
   To verify this, run `kubectl config current-context` and verify that it returns the name of your cluster.

1. Install Kubeflow on Kubernetes. We recommend using a Terrachain from Combinator.ml. <https://combinator.ml/stacks/kubeflow-mlflow/>

**Note: We support Kubernetes in Docker as well, though this can be quite resource intensive. You may wait up to 10 minutes for the service to become available after the first installation.**

1. Ensure your $KUBECONFIG is set. SAME can operate without this, but some tools may expect this to be set.

```sh
set KUBECONFIG="~/.kube/config"
```

{{% /codetab %}}

{{% codetab %}}

In order to use Azure Machine Learning as a target, you will need to:

1. Authorize with Azure
1. Set a series of environment variables that describe your workspace
1. Provision the necessary compute ahead of time.

We will walk through all of these now.

### Authorizing with Azure

First, you should download and install the Azure CLI - <https://docs.microsoft.com/en-us/cli/azure/install-azure-cli>

You will also need to create a service principal for accessing the AML workspace. You can follow the instructions for doing that here. <https://docs.microsoft.com/en-us/azure/machine-learning/how-to-manage-workspace-cli?tabs=createnewresources%2Cvnetpleconfigurationsv1cli>

### Setting Your Environment Variables

After executing this, you will get a JSON blob output that you will need to set as environment variables.  You will need to set all of the following:

```sh
export AML_SP_NAME="xxxx"
export AML_SP_APP_ID="<UID>"
export AML_SP_OBJECT_ID="<UID>"
export AML_SP_TENANT_ID="<UID>"
export AML_SP_PASSWORD_VALUE="**PASSWORD**"
export AML_SP_PASSWORD_ID="<UID>"

export WORKSPACE_SUBSCRIPTION_ID="<UID>"
export WORKSPACE_RESOURCE_GROUP="Resource_Group_Name"
export WORKSPACE_NAME="WORKSPACE_NAME"
```

### Setting Up Compute cluster

Finally, you will need to setup your compute cluster(s) to target with SAME. The instructions to do that are here: <https://docs.microsoft.com/en-us/azure/machine-learning/how-to-create-attach-compute-cluster?tabs=azure-cli>

{{% /codetab %}}

{{% codetab %}}

-- Not Implemented --

{{% /codetab %}}

{{% codetab %}}

-- Not Implemented --

{{% /codetab %}}

{{< /tabs >}}

## Next

You're done setting up SAME and are now ready to execute! The default execution uses Kubeflow (either locally or in the cloud). Use the `-t` flag to set another target.
