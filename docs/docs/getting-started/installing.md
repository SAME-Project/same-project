---
type: docs
title: "Installing SAME"
linkTitle: "Installing SAME"
description: "How to install the SAME project"
---

## Installing SAME

### System Requirements

- Python 3.8+
- Docker (optional, used by `same verify` command)

### Install [`sameproject` from PyPI](https://pypi.org/project/sameproject/)

For example, with `pip`

```bash
pip3 install --upgrade sameproject
```

### Verify installation

Validate successful installation by running `same version`. Output should look similar to below

```bash
same version
```

```
0.2.2
```

## Connecting to a Workflow Engine

To run SAME, you will need a workflow engine to connect to.
We support Kubeflow Pipelines.

### Option A: Test Drive

Use a test drive Kubernetes cluster with Kubeflow Pipelines preinstalled.
This test drive cluster will expire 1 hour after starting it.
You can run `testctl get` again to get a new one at any time.

1. Register for a [Testfaster account](https://testfaster.ci/access_token).

2. Copy and run the `testctl` install instructions at [Access Token](https://testfaster.ci/access_token).
   **Make sure to include the `testctl login` command**.

3. Clone this Kubeflow Combinator repo and get a cluster:
   ```bash
   git clone https://github.com/combinator-ml/terraform-k8s-stack-kubeflow-mlflow
   cd terraform-k8s-stack-kubeflow-mlflow
   cd examples/testfaster
   ```
   ```bash
   testctl get
   ```
   ```bash
   export KUBECONFIG=$(pwd)/kubeconfig
   ```
   (If you use a non-`bash` shell, you may need to spell the command to set an environment variable differently.)
4. To launch the Kubeflow Pipelines UI, from the `terraform-k8s-kubeflow/testfaster` directory, run:
   ```bash
   testctl ip
   ```
   And copy the final URL into your browser. Log in with `admin@kubeflow.org` and `12341234`. Go to `Pipelines` -> `Experiments` -> `Default` in the Kubeflow UI.
5. Now in the same shell you ran the `export` command, you can run `same run` (see next section) and it will be able to find and deploy to Kubeflow pipelines in the configured cluster.

### Option B: Use Existing Kubeflow Pipelines Install

Ensure your active `kubectl` context is pointing to the Kubernetes cluster with Kubeflow Pipelines installed:

```bash
kubectl config current-context
```

If so, you are ready to run `same run` (see next page for example).

After running `same run`, look in `Pipelines` -> `Experiments` -> `Default` in the Kubeflow UI.

### Option C: Install Kubeflow Pipelines on Kubernetes

Follow the [Kubeflow installation instructions](https://www.kubeflow.org/docs/started/installing-kubeflow/), and then follow the [existing Kubeflow Pipelines](#option-b-use-existing-kubeflow-pipelines) section.

Or, try the [Test Drive](#option-a-test-drive) if this is too much hard work.


## Next

You're done setting up SAME and are now ready to execute!
The default execution uses Kubeflow (either locally or in the cloud). Use the `-t` flag to set another target.

To try out an example, check out the roadsigns example from [Example Notebook](./example-notebook.md).