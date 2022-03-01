---
type: docs
title: "Installing SAME"
linkTitle: "Installing SAME"
description: "How to install the SAME project"
weight: 10
---

## Installing SAME

### System Requirements

- Python >=3.8, <3.11

### Install SAME using pip

Before installing the pip package, using a [virtual environment](https://docs.python.org/3/tutorial/venv.html) is highly recommended to isolate package installation from the system.

SAME project is available through [PyPI](https://pypi.org/project/sameproject/):

```shell
pip install sameproject
```

### Verify installation

Validate successful installation by running `same version`. Output should look similar to below

```shell
$ same version
0.0.1
```

## Connecting to a Workflow engine

To run SAME, you will need a workflow engine to connect to. We support a variety of workflow engines, but recommend that, for now, you connect to one that is dedicated to SAME exclusively.

### Prerequisites

- Kubernetes cluster running locally or in a cloud environment
- [`kubectl`](https://kubernetes.io/docs/tasks/tools/#kubectl) installed

### Install Kubeflow

1. Verify that correct Kubernetes cluster has been configured with the desired `kubectl` context set as the default.
   ```shell
   kubectl config current-context
   ```
2. Set `KUBECONFIG` environment variable. While SAME can operate without setting the environment variable, some tools
   may expect this to be set.
   ```shell
   export KUBECONFIG="~/.kube/config"
   ```
   If you use a non-`bash` shell, you may need to spell this command to set an environment variable differently.
3. Install Kubeflow on Kubernetes
    - We recommend using a [Terrachain from Combinator.ml](https://combinator.ml/stacks/kubeflow-mlflow/).

## Next

You're done setting up SAME and are now ready to execute! The default execution uses Kubeflow (either locally or in the cloud). Use the `-t` flag to set another target.

To try out an example, check out the hello-world example from [First Notebook](./first-notebook.md).
