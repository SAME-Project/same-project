from sameproject.ops.notebooks import compile
from sameproject.ops.backends import deploy
from sameproject.ops.execution import load
from base64 import urlsafe_b64decode
import test.testdata
import requests
import pytest
import json
import time
import dill


@pytest.mark.functions
@test.testdata.notebooks("features")
def test_functions_features(config, notebook, requirements, validation_fn):
    """
    Tests the Azure Functions backend against the feature test suite. This
    requires the following enviroment variables to be set:
      FUNCTIONS_SUBSCRIPTION_ID = "<azure subscription id>"
    """
    base_path, root_file = compile(config, "functions")
    data = deploy("functions", base_path, root_file, config)

    # Query the status URI until the execution is completed:
    #   see: https://docs.microsoft.com/en-us/javascript/api/durable-functions/orchestrationruntimestatus?view=azure-node-latest
    start_secs = time.time()
    while True:
        res = json.loads(requests.get(data["statusQueryGetUri"]).text)

        if res["runtimeStatus"] == "Completed":
            break

        if res["runtimeStatus"] == "Failed":
            raise RuntimeError(f"Notebook execution failed: {res}")

        if time.time() - start_secs > 600:  # 10 minutes
            raise RuntimeError(f"Notebook execution took too long to complete: {res}")

    # Decode the output namespace and validate the results:
    module = load(urlsafe_b64decode(res["output"]["session_context"]))
    attrs = dict(map(lambda k: (k, getattr(module, k)), dir(module)))
    if validation_fn is not None:
        assert validation_fn(attrs)
