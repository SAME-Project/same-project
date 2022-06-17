from sameproject.data.config import SameConfig
from sameproject.ops import helpers
from pathlib import Path
import importlib


def deploy(base_path: Path, root_file: str, config: SameConfig):
    with helpers.add_path(str(base_path)):
        root_module = importlib.import_module(root_file)  # python module
        print(f"Root module is {root_module}")
    return