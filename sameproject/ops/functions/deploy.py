from sameproject.data.config import SameConfig
from pathlib import Path
import requests
import json


def deploy(base_path: Path, root_file: str, config: SameConfig):
    subscription_id = config.runtime_options.get("functions_subscription_id", None)
    if subscription_id is None:
        raise ValueError("The 'functions' backend requires the 'functions_subscription_id' runtime option to be set.")

    host_name = config.runtime_options.get("functions_host_name", None)
    if host_name is None:
        raise ValueError("The 'functions' backend requires the 'functions_host_name' option to be set.")

    # The 'initiator' function expects a JSON blob encoding notebook steps:
    with (base_path / root_file).open("r") as reader:
        body = json.load(reader)

    # Initiate execution against the backend functionapp:
    backend_uri = f"https://{host_name}/api/initiate"
    res = requests.post(backend_uri, json=body)
    if res.status_code != 202:  # HTTP 'accepted' status
        raise RuntimeError(f"The 'functions' backend returned status code {res.status_code}: {res.text}")

    # Result is a JSON blob describing the 'orchestrator' execution context:
    data = json.loads(res.text)
    print(f"Successfully started an execution of notebook '{config.notebook.name}', visit the following link for results:\n\t{data['statusQueryGetUri']}")

    return data
