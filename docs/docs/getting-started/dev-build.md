---
type: docs
title: "Setting up dev"
description: "How to set up your environment for running tests and building SAME."
weight: 02
---

If you are using the same-mono-private repo, it does not currently produce a binary that can be installed from https://get.sameproject.org/. You will need to clone the repo and run the CLI from the main branch:

## Prerequisites

- [Python 3.8](https://www.python.org/downloads/). _Note that 3.9 is not currently supported due to Azure Machine Learning dependencies.
- [Poetry 1.1.7](https://python-poetry.org/docs/#installation) or higher.
- [Azure CLI 2.27](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-linux?pivots=script) or higher.
- [Azure Functions Work Tools v3.x](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=v3%2Clinux%2Ccsharp%2Cportal%2Cbash%2Ckeda) or higher (Optional).

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

## Using the devcontainer with Visual Studio Code

If you are using [Visual Studio Code (VSCode)](https://code.visualstudio.com) to work with the same-mono-private repo, VSCode supports development in a containerized environment through its [Remote - Container extension](https://code.visualstudio.com/docs/remote/containers), so you don't need to manually install all of the tools and frameworks yourself.

### Prerequisites

1. [Docker](https://docs.docker.com/get-docker/)
   > For Windows users, we recommend enabling [WSL2 back-end integration with Docker](https://docs.docker.com/docker-for-windows/wsl/).
2. [Visual Studio Code](https://code.visualstudio.com/Download)
3. [Visual Studio Code Remote - Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

### Opening same-project in a devcontainer

1. After you have cloned the dapr repo locally, open the dapr folder in VSCode. For example:

    ```bash
    git clone https://github.com/SAME-Project/same-project.git
    cd same-project
    git submodule update --init --recursive
    code .
    ```

   VSCode will detect the presence of a dev container definition in the repo and will prompt you to reopen the project in a container.

   Alternatively, you can open the command palette and use the `Remote-Containers: Reopen in Container` command.

2. Once the container is loaded, open an [integrated terminal](https://code.visualstudio.com/docs/editor/integrated-terminal) in VSCode and you're ready to use the repo. You will still need to install the project Python dependencies using the preinstalled Poetry tool:

    ```bash
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
python3 cli/same/main.py <cli-arguments>
```

> **TODO:** Enable building the CLI into a redistributable binary via something like [PyOxidiser](https://pyoxidizer.readthedocs.io/en/stable/index.html) in same-project.

When we get to binary builds of the CLI that can be run locally, you can execute the local build with:

```bash
bin/same <cli-arguments> 
```

After we start publishing builds, you can install and execute with the following:

```bash
curl -L0 https://get.sameproject.ml/ | bash -
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

### Local Kubeflow cluster on Minikube in devcontainer

The devcontainer image for same-project comes with [minikube](https://minikube.sigs.k8s.io/docs/) preinstalled, so you can set up a local Kubeflow cluster to run the CLI pytests against if you wish:

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
