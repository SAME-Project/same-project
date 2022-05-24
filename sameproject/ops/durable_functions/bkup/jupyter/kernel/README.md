**SAME Python Kernel** is a Jupyter kernel for running the notebook cells on SAME backends.

## Install

First, you need to install the same_kernel library and dependencies:

```shell
pip install -e . --upgrade
```

Then, you need to install the SAME kernel spec:

```shell
python -m same_kernel install --user
```

## Running

You can then run the SAME kernel as a console, notebook, etc.:

```shell
jupyter console --kernel=same_kernel
```

## Dependencies

1. IPython 3
2. SAME Kernel (installed with pip)
