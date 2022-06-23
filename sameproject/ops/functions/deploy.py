from sameproject.data.config import SameConfig
from pathlib import Path
import requests
import json


def deploy(base_path: Path, root_file: str, config: SameConfig):
    # The 'initiator' function expects a JSON blob encoding notebook steps:
    with (base_path / root_file).open("r") as reader:
        body = json.load(reader)

    # Initiate execution against the backend functionapp:
    url = get_backends_url(config)
    try:
        res = requests.post(url, json=body)
    except Exception as err:
        raise RuntimeError(f"The 'functions' backend could not communicate with '{url}': {err}")
    if res.status_code != 202:  # HTTP 'accepted' status
        raise RuntimeError(f"The 'functions' backend returned status code {res.status_code}: {res.text}")

    # Result is a JSON blob describing the 'orchestrator' execution context:
    data = json.loads(res.text)
    print(f"Successfully started an execution of notebook '{config.notebook.name}', visit the following link for results:\n\t{data['statusQueryGetUri']}")

    return data


def get_backends_url(config: SameConfig) -> str:
    protocol = "https"
    if config.runtime_options.get("functions_use_http"):
        protocol = "http"
    host = config.runtime_options.get("functions_host_name")

    return f"{protocol}://{host}/api/initiate"
