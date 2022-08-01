---
type: docs
title: "Pachyderm"
description: "How to use SAME to deploy a notebook as a pipeline to Pachyderm."
---

Assuming you have a [Pachyderm installation](https://docs.pachyderm.com/2.0.x/deploy-manage/deploy/) and `pachctl list repo` is working for you, deploying a notebook as a pipeline to Pachyderm is as simple as:

Install SAME:
```
pip3 install --upgrade sameproject
```

Set up a same.yaml and requirements.txt in a folder alongside your .ipynb file:
```
same init
```

Test the suggested container image against the requirements.txt and your notebook's imports (optional, requires Docker):
```
same verify
```

Deploy the notebook as a pipeline to Pachyderm:
```
same run --target pachyderm --input-repo test
```

Update the input repo to refer to a repo that exists on your Pachyderm installation.

You can also specify `--input-glob` to specify a glob pattern, or `--input` to specify a raw [input specification](https://docs.pachyderm.com/latest/reference/pipeline-spec/) in JSON format, to specify more advanced input formats.

Your notebook should read data from `/pfs`, and write any output data to `/pfs/out`. You might want to use the [Pachyderm JupyterLab Mount Extension](https://docs.pachyderm.com/latest/how-tos/jupyterlab-extension/) to develop your notebook, then it will run the same way with the mount extension as when you run it in Pachyderm with SAME.