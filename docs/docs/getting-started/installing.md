---
type: docs
title: "Installing SAME"
linkTitle: "Installing SAME"
description: "How to install the SAME project"
weight: 10
---

## Installing SAME

### Test drive

If you want to try SAME without a Kubernetes cluster with Kubeflow installed, click the following Combinator.ml link, open the Kubeflow UI, then run through the rest of the Tutorial in the "SSH" tab, following the Ubuntu instructions.

<a href="https://testfaster.ci/launch?embedded=true&amp;repo=https://github.com/combinator-ml/terraform-k8s-stack-kubeflow-mlflow&amp;file=examples/testfaster/.testfaster.yml" target="\_blank">:computer: Launch Test Drive :computer:</a>


### System Requirements

- Python >=3.8, <3.11, with pip
  - Ubuntu/Debian: `sudo apt update && sudo apt install -y python3-pip`

### Install SAME using pip

Before installing the pip package, using a [virtual environment](https://docs.python.org/3/tutorial/venv.html) is highly recommended to isolate package installation from the system. (You can skip this step in the test drive, since the test drive VM is already isolated.)

SAME project is available through [PyPI](https://pypi.org/project/sameproject/):

```shell
pip3 install sameproject
```

### Verify installation

Validate successful installation by running `same version`. Output should look similar to below

```shell
same version
```

```shell
0.1.4
```

## Connecting to a Workflow engine

To run SAME, you will need a workflow engine to connect to. We support a variety of workflow engines, but recommend that, for now, you connect to one that is dedicated to SAME exclusively.

_If you are using the [Combinator.ml test drive](#test-drive), you can skip this section as Kubernetes and Kubeflow is already configured in your test drive VM._

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
    - Follow the [Kubeflow installation instructions](https://www.kubeflow.org/docs/started/installing-kubeflow/), or try the [test drive](#test-drive) if this is too much hard work.

## Next

You're done setting up SAME and are now ready to execute! The default execution uses Kubeflow (either locally or in the cloud). Use the `-t` flag to set another target.

To try out an example, check out the hello-world example from [First Notebook](./first-notebook.md).
