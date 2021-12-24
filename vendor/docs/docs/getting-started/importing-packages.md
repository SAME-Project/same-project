---
type: docs
title: "Importing Packages"
description: "Using the SAME SDK to import packages and update your environment file."
weight: 40
---

### Background around Python Packages in Notebooks

The SAME SDK helps data scientists avoid one of the most common problems in the development, forgetting to include their dependencies as part of their deployments. For example, it is very common to do something like the following when running a notebook:

```python
import foo
import bar.qaz
from qux import moo
!pip install baz
```

All of the above work well when run locally, but if a data scientist is not diligent, and update their requirements.txt file (and commit that update to the code base), when run in prodcution, the code will not work (normally showing an error like "module not found"). Apart from just being annoying, this could also take a long time to detect, due to the length of time before pipeline jobs are executed.

To aleviate this, the `same-sdk` enables both local import (using caching and cleaner outputs) and keeps the environment file in sync.

### Importing Packages via SAME
To use `same` in a notebook, first one has to install it:

```bash
pip install same-sdk
```

Then, inside the notebook, instead of doing `import same`, a data scientist would execute:

```python3
same.import("package_name")
```

This will load the module into python's `sys.modules`. Later, when `same program run` is executed, it updates the `environment.yaml` file to the latest for all system modules for the entire notebook, and uses that file as the record for injecting requirements to the back end system.
