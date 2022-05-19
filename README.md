# SAME Project

This is the central repository for the development of the SAME project.


## Getting Started

For instructions on how to install a standalone version of SAME, see the [getting started guide](https://github.com/SAME-Project/same-project/blob/main/docs/docs/getting-started/installing.md). If you're a developer, see the [developer documentation](https://github.com/SAME-Project/same-project/blob/main/docs/docs/getting-started/dev-build.md) for instructions on how to build, run and test the codebase.


## Project Structure

The project is laid out as follows:

- **[/docs](docs/README.md):** Documentation website for the SAME project.
- **[/sameproject](sameproject/README.md):** Python codebase containing the implementation of the SAME project.
- **[/cli](sameproject/cli):** Python implmentation of the `same` CLI tool for compiling Jupyter notebooks against target DevOps backends.
- **[/sdk](sameproject/sdk/README.md):** Experimental python module for making Jupyter notebooks easier to integrate into DevOps backends.
- **[/test](test/README.md):** Unit tests and integration tests for the python codebase.
- **[/scripts](scripts):** Useful scripts for development and testing.


## Releasing

To publish a release to PyPI, run:

```
poetry publish --build
```

The version number of the release is defined in `pyproject.toml`.
