from sameproject.data.config import SameConfig
from sameproject.data.step import Step
from base64 import urlsafe_b64encode
from typing import Mapping, Tuple
from pathlib import Path
import json


def render(path: str, steps: Mapping[str, Step], config: SameConfig) -> Tuple[Path, str]:
    path = Path(path)
    body_path = path / "body.json"
    codes = [step.code.encode("utf-8") for step in steps.values()]
    with body_path.open("w") as writer:
        json.dump({
            "steps": [
                urlsafe_b64encode(code).decode("utf-8")
                for code in codes
            ],
        }, writer)

    return (path, "body.json")
