---
type: docs
title: "Changing Environment"
description: "Requiring that certain steps use different base images."
---

Often times, a specific step will require a particular base container image to execute inside of. This may be because the image was pre-built with particular dependencies (packages, libraries, drivers, etc) which Jupyter does not need to execute, but may be necessary on the back end. This feature allows to specify the base image required to execute a given step.

### Adding an Environment Specifier

Editing cell tags in the same way you did for [adding steps](adding-steps.md), you can add alternate base images with the following tag structure:

```bash
environment=environment_name
```

For example:

```bash
environment=default
```

![Default Environment Tag](../images/environment-default.jpg)

or:

```bash
environment=private-training-env
```

![Private Environment Tag](../images/environment-private-training-env.jpg)

### Update SAME Config

Then in your `same.yaml` config file, you'll add a section that maps to the specific image you'll need.

![SAME config file contents](../images/private-environment-same-file.jpg)
