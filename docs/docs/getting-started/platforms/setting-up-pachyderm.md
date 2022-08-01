---
type: docs
title: "Pachyderm"
description: "How to use SAME to deploy a notebook to Pachyderm."
---

Assuming you have a [Pachyderm cluster](https://docs.pachyderm.com/2.0.x/deploy-manage/deploy/) and `pachctl list repo` is working for you, deploying a notebook against SAME is as simple as:

```
same run --target pachyderm --input-repo test
```

Update the input repo to refer to a repo that exists on your cluster.

You can also specify `--input-glob` to specify a glob pattern, or `--input` to specify a raw [input specification](https://docs.pachyderm.com/latest/reference/pipeline-spec/) in JSON format, to specify more advanced input formats.

Your notebook should read data from `/pfs`, and write any output data to `/pfs/out`. You might want to use the [Pachyderm JupyterLab Mount Extension](https://docs.pachyderm.com/latest/how-tos/jupyterlab-extension/) to develop your notebook, then it will run the same way with the mount extension as when you run it in Pachyderm with SAME.