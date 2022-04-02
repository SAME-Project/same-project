# SAME Python SDK

> ⚠ This module is experimental and incomplete.

## Overview

Experimental SDK module for use in Jupyter notebooks to help integration with ML DevOps. Refer to the [initial roadmap scenarios](https://github.com/SAME-Project/same-mono-private/issues/7) for more information.

## Vendored Dependencies

The SDK relies on the `conda` package to support Conda environments. Conda's `setup.py` is incompatible with python ^3.10, however, so we have vendored the package directly in the `vendor` directory. Do *not* make changes to the vendored code, unless you are pulling in upstream commits from the `conda` repo.
