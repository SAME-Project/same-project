from sameproject.ops.functions.provision import provision_orchestrator
from sameproject.data.config import SameConfig
from pathlib import Path
import requests
import json


# TODO: fetch this URI using the azure SDK, may be different in some cases:
backend_uri = "https://same-site.azurewebsites.net/api/initiate"


def deploy(base_path: Path, root_file: str, config: SameConfig):
    subscription_id = config.runtime_options.get("functions_subscription_id", None)
    if subscription_id is None:
        raise ValueError("The 'functions' backend requires the '--functions-subscription-id' flag to be provided.")

    # Ensure that the 'functions' backend has been deployed to azure:
    # TODO: make this more efficient by checking if it already exists
    if not config.runtime_options.get("functions_skip_provisioning", False):
        provision_orchestrator(subscription_id)

    # The 'initiator' function expects a JSON blob encoding notebook steps:
    with (base_path / root_file).open("r") as reader:
        body = json.load(reader)

    # Initiate execution against the backend functionapp:
    res = requests.post(backend_uri, json=body)
    if res.status_code != 202:  # HTTP 'accepted' status
        raise RuntimeError(f"The 'functions' backend returned status code {res.status_code}: {res.text}")

    # Result is a JSON blob describing the 'orchestrator' execution context:
    data = json.loads(res.text)
    print(f"Successfully started an execution of notebook '{config.notebook.name}', cURL the following URI for status updates:\n\t{data['statusQueryGetUri']}")
