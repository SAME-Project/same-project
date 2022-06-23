---
type: docs
title: "Hello World Notebook"
linkTitle: "Hello World"
description: "Deploying An Example Notebook"
---
## Clone the Sample Repo

To get started, first you'll need to clone our sample repo. To do so, execute the following command:

```bash
git clone https://github.com/SAME-Project/SAME-samples.git
```

Next, change into the `03-road-signs` directory:

```bash
cd SAME-samples
cd 03-road-signs
```

This is a complete data fetching, data engineering and model training example in three steps.

### Check the Requirements Work With the Container and the Notebook

This step is optional, and requires that you have Docker running locally.
If you don't, you can skip straight to deploying the pipeline to your Workflow Engine.

```bash
same verify
```

Note: this step can fail spuriously when run on a different architecture versus the workflow engine (e.g. M1 Mac).

### Deploy Pipeline to Workflow Engine

Finally, deploy your notebook to your environment. If you are using Kubeflow, you would execute the following command:

```bash
same run
```

This command converts the notebook into a multi-stage pipeline, and deploys it to your [previously configured](installing.md) Kubeflow.

In the Kubeflow UI, click on **Pipelines -> Experiments** to see your runs!

<img width="830" alt="multi-step-execution" src="/images/multi-step-pipeline.png">

## Try Your Own Notebook

Try running
```bash
same init
```

And then
```bash
same verify
```

And finally
```bash
same run
```

In an empty folder with your own notebook in it!

If you have any issues, please [report a GitHub issue](https://github.com/SAME-Project/same-project/issues/new) or [come tell us on Slack](https://join.slack.com/t/thesameproject/shared_invite/zt-lq9rk2g6-Jyfv3AXu_qnX9LqWCmV7HA)!