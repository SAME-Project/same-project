# SAME Codebase

Contains the SAME project's python codebase.


## Vendored Dependencies

The SDK relies on the `conda` package to support Conda environments. Conda's `setup.py` is incompatible with python ^3.10, however, so we have vendored the package directly in the `vendor` directory.

The `pipreqs` tool is used to automatically suggest missing dependencies to the user if they have unresolved imports in their notebook. `pipreqs` doesn't have an importable library, however, so we have also directly vendored the code.

Do *not* make changes to vendored code, unless you are pulling in upstream commits from the `conda` or `pipreqs` repositories.


## Backend Features

The most extensively developed backend right now is `kubeflow`, which supports the following set of features: 

1. Notebooks containing multiple steps.
2. Configuration with a specified docker image to run against.
3. Configuration with a `requirements.txt` of dependencies to install.
4. Integration of `datasets` configuration and the `same.datasets(...)` SDK.

Other backends support the following subset of these features:

|                     |**1**|**2**|**3**|**4**|
|--------------------:|:---:|:---:|:---:|:----|
|**kubeflow**         |  x  |  x  |  x  |  x  |
|**durable functions**|     |     |     |     |
|**aml**              |     |     |     |     |
|**vertex**           |     |     |     |     |
