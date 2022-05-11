# SAME Notebooks Test Suite

This folder contains a suite of different kinds of fully-configured SAME
configs and notebooks. The idea is to capture a selection of common frameworks
like `pytorch`, `tensorflow` and `sklearn`, so that we can run full integration
tests periodically and ensure that SAME is working correctly on each of our
backends.


## Structure

Each of the child folders contains a number of notebooks and as well as a
number of folders. The notebooks are candidates for being added to the suite,
but have not yet been given a SAME config and `requirements.txt` file. The child
folders contain fully-configured notebooks that have both.


## Process

To add a notebook to the test suite, create a folder for it in the relevant
child directory, i.e. `pytorch` if it's a pytorch notebook. Add the notebook
to the directory, create a SAME config file and `requirements.txt` for it and
register the notebook in: (TODO write a registry)

Try to ensure that the notebook:
* has more than one configured SAME step
* has been pared down to reduce memory and cpu requirements

The commands `same init` and `same verify` are useful for configuring a new
notebook, as they automatically generate and check the config/requirements 
files.
