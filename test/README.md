# SAME Project - Tests

Contains a repository of unit tests and integration tests for the SAME project. The module structure mimics the module structure in the [python codebase](../sameproject/README.md), with the exception of the [testdata](/testdata) module, which contains notebooks and configuration we can test against.


## Running Tests

For detailed instructions on how to run tests, refer to the [developer documentation](https://github.com/SAME-Project/same-project/blob/main/docs/docs/getting-started/dev-build.md#running-tests). If you have problems, make sure your submodules are updated and that you are running commands from a `poetry shell`.

```bash
pytest
```

Integration tests for specific backends are disabled by default, as they require a running instnance of the backend to test against. If you want to enable integrations for a particular backend, such as `kubeflow`, you will need to set its respective `pytest` flag:

```bash
pytest --kubeflow           # enables the kubeflow integration tests
pytest --durable_functions  # enables the durable functions integration tests
...
```

We also have a repository of "from-the-wild" notebooks that we have collected from various sources online. These notebooks are contained and registered in the [testdata](/testdata) module. To test a particular backend against "from-the-wild" notebooks, you will need to set the `--external` flag as well:

```bash
pytest --kubeflow --external  # tests "from-the-wild" notebooks against a kubeflow backend
```

Finally, our tests have support for parallelisation, which speeds up integration tests considerably. To run tests on multiple threads, specify the `-n` option when running `pytest`:

```bash
pytest --durable_functions -n 4  # tests a durable function backend using 4 threads
```
