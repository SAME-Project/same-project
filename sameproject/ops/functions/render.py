from sameproject.data.config import SameConfig
from sameproject.data.step import Step
from base64 import urlsafe_b64encode
from typing import Mapping, Tuple
from pathlib import Path
import json


def render(path: str, steps: Mapping[str, Step], config: SameConfig) -> Tuple[Path, str]:
    if len(steps) > 1:  # TODO: support multistep notebooks
        raise NotImplementedError("The 'functions' backend does not support multi-step notebooks.")

    path = Path(path)
    body_path = path / "body.json"
    code = list(steps.values())[0].code.encode("utf-8")
    with body_path.open("w") as writer:
        json.dump({
            "code": urlsafe_b64encode(code).decode("utf-8"),
        }, writer)

    return (path, "body.json")
