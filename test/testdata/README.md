# SAME Notebooks Test Suite

This folder contains a suite of different kinds of fully-configured SAME
configs and notebooks. The idea is to capture a selection of common frameworks
like `pytorch`, `tensorflow` and `sklearn`, so that we can run full integration
tests periodically and ensure that SAME is working correctly on each of our
backends.


## Structure

Each of the child folders contains a number of notebooks and as well as a
number of folders. The notebooks are candidates for being added to the suite,
but have not yet been given a SAME config and `requirements.txt` file. The 
folders contain fully-configured notebooks that have been registered with
the testdata suite - see below.


## Process

To add a notebook to the test suite, create a folder for it in the relevant
child directory, i.e. `pytorch` if it's a pytorch notebook. Add the notebook
to the directory, create a SAME config file and `requirements.txt` for it and
register the notebook in `__init__.py`:

```python
_register_notebook(
  "notebook_name",
  "notebook_desc",
  "test_group",
  Path("notebook/same.yaml"),
  
  # Validation function that returns True if the notebook executed correctly.
  lambda res: res["x"] == 1,
)
```

Try to ensure that the notebook:
* has more than one configured SAME step
* has had all outputs cleared to avoid a messy notebook file
* has been pared down if possible to reduce cpu and memory requirements

The commands `same init` and `same verify` are useful for configuring a new
notebook, as they automatically generate and check the config/requirements 
files.
