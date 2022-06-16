---
type: docs
title: "Setting Up a Development Environment"
description: "How to set up your environment for running tests and building SAME."
---

## Prerequisites

- [Python 3.8+](https://www.python.org/downloads/)
- [Poetry 1.1.7](https://python-poetry.org/docs/#installation) or higher

1. Clone the repo to your local machine and initialize the submodules:

    ```bash
    git clone https://github.com/SAME-Project/same-project.git
    cd same-project
    git submodule update --init --recursive
    ```

2. Download and install Poetry, which is used to manage dependencies and virtual environments for the SAME project. You will need to install the project's Python dependencies using Poetry as well after installing it:

    ```bash
    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python3 -
    poetry install
    ```

    To install AML dependencies, now optional, use `poetry install --extras azureml`

## Using the repo

Use of the SAME python project assumes executing in a virtual environment managed by Poetry. Before running any commands, the virtual environment should be started:

```bash
poetry shell
```

> **NOTE:** From this point forward, all functions require executing inside that virtual environment. If you see an error like `zsh: command not found`, it could be because you're not executing inside the venv. You can check this by executing:
>
> ```bash
> which python3
> ```
>
> This should result in a response like: `.../pypoetry/virtualenvs/same-project-88mixeKa-py3.8/bin/python3`. If it reports something like `/usr/bin/python` or `/usr/local/bin/python`, you are using the system python, and things will not work as expected.

## How to execute against a notebook from source code

From the root of project, execute:

```bash
same <cli-arguments>
```

## Running tests
To run all the tests against the CLI and SDK:

```bash
pytest
```

To run a subset of tests for a single file:

```bash
pytest test/cli/test_<file>.py -k "test_<name>"
```

## How to setup private test environments

### Local Kubeflow cluster on Minikube

You can set up a local Kubeflow cluster to run the CLI pytests against if you wish:

1. Start a minikube cluster in the devcontainer:

    > **Note:** Kubeflow currently defines its Custom Resource Definitions (CRD) under `apiextensions.k8s.io/v1beta` which is deprecated in Kubernetes v1.22, so minikube must start the cluster with a version <1.22. See [kubeflow/kfctl issue #500](https://github.com/kubeflow/kfctl/issues/500).

    ```bash
    minikube start --kubernetes-version=v1.21.5
    ```

    Starting minikube will also change the default kubeconfig context to the minikube cluster. You can check this with:

    ```bash
    kubectl config get-contexts
    ```

2. Deploy Kubeflow to the minikube cluster:

    ```bash
    export PIPELINE_VERSION=1.7.0
    kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/cluster-scoped-resources?ref=$PIPELINE_VERSION"
    kubectl wait --for condition=established --timeout=60s crd/applications.app.k8s.io
    kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/env/platform-agnostic-pns?ref=$PIPELINE_VERSION"
    ```

### Kubeflow cluster on Azure Kubernetes Services (AKS)

From any Azure subscription where you are at least a Contributor, you can create and provision a new AKS cluster with Kubeflow:

1. Create a new AKS cluster either using the [Azure CLI](https://docs.microsoft.com/en-us/azure/aks/kubernetes-walkthrough) or [Azure Portal](https://docs.microsoft.com/en-us/azure/aks/kubernetes-walkthrough-portal).

   The linked instructions will also update your kubeconfig to use the new cluster as the context when you run `az aks get-credentials`, but you can also manually do so with:

   ```bash
   kubectl config set-context <context name>
   ```

2. [Deploy Kubeflow](https://www.kubeflow.org/docs/distributions/azure/deploy/install-kubeflow/#kubeflow-installation) to the cluster.

    > **Note:** The document references a non-existent v1.3.0 release, you can simply use the [v1.2.0 release](https://github.com/kubeflow/kfctl/releases/tag/v1.2.0) instead. See [kubeflow/kfctl issue #495](https://github.com/kubeflow/kfctl/issues/495).

### Azure Machine Learning (AML) workspace and compute

1. [Create a new Service Principal](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-setup-authentication#configure-a-service-principal) for running tests against your private AML instance.

    As mentioned in the instructions, make sure to take note of the output of the command as you will need the `clientId`, `clientSecret`, and `tenantId` values to configure the `.env.sh` file to run the AML tests.

2. [Create a new Azure Machine Learning Workspace](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-configure-cli#set-up).

    You will need the `--resource-group` and `--workspace-name` values you specified during workspace creation to configure the `.env.sh` file to run the AML tests.

    You will also need the subscription `id` that you created the AML workspace in. You can check this by running:

    ```bash
    az account show --query id
    ```

3. Create an [AML Compute cluster](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-create-attach-compute-cluster?tabs=azure-cli#create) or [AML Compute Instance](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-create-manage-compute-instance?tabs=azure-cli#create).

    You will need the `--name` that you specified during compute cluster/instance creation to configure the `.env.sh` file to run the AML tests.
