---
type: docs
title: "Hello World Notebook"
linkTitle: "Hello World"
description: "Deploying Your First Notebook"
weight: 20
---
## Clone the Sample Repo

To get started, first you'll need to clone our sample repo. To do so, execute the following command:

```bash
git clone https://github.com/SAME-Project/SAME-samples.git
```

Next, change into the hello-world directory:

```bash
cd SAME-samples
cd 01-hello-world
```

Finally, deploy your notebook to your environment. If you are using kubeflow, you would execute the following command:

```bash
same program run
```

This command converts the notebook into a single python script, and deploys it to your [previously configured](installing.md) Kubeflow.

In the Kubeflow UI, click on **Pipelines -> Experiments** to see your runs!

<img width="830" alt="one-step-execution" src="https://user-images.githubusercontent.com/264658/157191116-42bc92eb-2814-4622-81ba-0a2e048c59c4.png">

