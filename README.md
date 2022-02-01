# SAME Project

This is the central repository for continuing development of the SAME project.

## Getting Started

Refer to the [SAME Project docs](https://github.com/SAME-Project/same-project/blob/main/docs/docs/getting-started/dev-build.md) for building and running this repo. 

**SUBMODULES** If you are getting this error `E ModuleNotFoundError: No module named 'vendor.conda.conda_env`, it's because you haven't updated your submodules (usually after an initial clone). Do this:

```bash
git submodule update --init --recursive
```

## Project Structure

`same-project` includes several extensions:

- **[/backends](backends/README.md):** Python module used by SAME CLI to compile & deploy SAME configurations on different workflow execution backends.
- **[/cli](cli/README.md):** Python implmentation of the SAME CLI for converting Jupyter notebooks to SAME configurations and running them against a target environment.
- **[/docs](docs/README.md):** Documentation mkdocs github pages website
- **/objects:** Helper library for a JSON serialization object shared by other Python modules.
- **/scripts:** Helper shell scripts for testing and test environment setup.
- **[/sdk](sdk/README.md):** Experimental Python module for functions to be used in Jupyter notebooks making them easier to integrate into DevOps.
- **/templates:** Jinja templates used by the AML and Kubeflow backends for code generation. Current implementation detail for those backends.
- **[/test](test/README.md):** Unit and functional tests for each of the major Python modules.
- **/vendor:** Folder for 3rd party submodules imported by `same-mono-repo`, such as https://github.com/conda/conda.

## Releasing

To release to PyPI run:

```
poetry publish --build
```

The version number is defined in `pyproject.toml`.
