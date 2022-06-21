from sameproject.data.config import SameConfig
from sameproject.data.step import Step
from base64 import urlsafe_b64encode
from typing import Mapping, Tuple
from pathlib import Path
import json


def render(path: str, steps: Mapping[str, Step], config: SameConfig) -> Tuple[Path, str]:
    path = Path(path)
    body_path = path / "body.json"

    step_data = []
    for name, step in steps.items():
        sources = {}
        sources["same.yaml"] = _encode(config.to_yaml())
        if "requirements_file" in step:
            sources["requirements.txt"] = _encode(step.requirements_file)

        step_data.append({
            "name": name,
            "code": _encode(step.code),
            "sources": sources,
        })

    with body_path.open("w") as writer:
        json.dump({"steps": step_data}, writer)

    return (path, "body.json")


def _encode(data: str) -> str:
    """Encodes the given data as an urlsafe base64 string."""
    return urlsafe_b64encode(
        data.encode("utf-8")
    ).decode("utf-8")
