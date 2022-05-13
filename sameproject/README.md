# SAME Codebase

## Vendored Dependencies

The SDK relies on the `conda` package to support Conda environments. Conda's `setup.py` is incompatible with python ^3.10, however, so we have vendored the package directly in the `vendor` directory.

The `pipreqs` tool is used to automatically suggest missing dependencies to the user if they have unresolved imports in their notebook. `pipreqs` doesn't have an importable library, however, so we have also directly vendored the code.

Do *not* make changes to the vendored code, unless you are pulling in upstream commits from the `conda` or `pipreqs` repos.
