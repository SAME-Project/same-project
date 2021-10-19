# SAME Mono Private

This is the central repository for continuing development of the SAME project.

> ⚠ This repo supersedes https://github.com/azure-octo/same-cli and extends its functionality.

## Getting Started

Refer to the [SAME Project docs](https://samedocs.azurewebsites.net/getting-started/dev-build/) for building and running this repo. They can also be referenced directly from the [SAME-Docs repo](https://github.com/SAME-Project/SAME-Docs/blob/main/content/getting-started/dev-build.md) if the docs site is down.

## Project Structure

`same-mono-private` supersedes the old https://github.com/azure-octo/same-cli repository and includes several extensions:

- **[/backends](backends/README.md):** Python module used by SAME CLI to compile & deploy SAME configurations on different workflow execution backends.
- **[/cli](cli/README.md):** Python implmentation of the SAME CLI for converting Jupyter notebooks to SAME configurations and running them against a target environment.
- **/objects:** Helper library for a JSON serialization object shared by other Python modules.
- **/scripts:** Helper shell scripts for testing and test environment setup.
- **[/sdk](sdk/README.md):** Experimental Python module for functions to be used in Jupyter notebooks making them easier to integrate into DevOps.
- **/templates:** Jinja templates used by the AML and Kubeflow backends for code generation. Current implementation detail for those backends.
- **[/test](test/README.md):** Unit and functional tests for each of the major Python modules.
- **/vendor:** Folder for 3rd party submodules imported by `same-mono-repo`, such as https://github.com/conda/conda.

## Releases

This repo does not currently publish redistributables.

> ⚠ The [latest SAME CLI release](https://github.com/SAME-Project/SAMPLE-CLI-TESTER/releases/tag/0.0.65) is still based off the old Go-based implementation from https://github.com/azure-octo/same-cli. When issue [#21](https://github.com/SAME-Project/same-mono-private/issues/21) is resolved, new binary releases from this repo can be published to https://github.com/SAME-Project/SAMPLE-CLI-TESTER as well, although it would be preferred to only publish releases from this repo when it is made public.
