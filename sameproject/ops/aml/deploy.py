from sameproject.data.config import SameConfig
from sameproject.ops import helpers
import importlib


def deploy(base_path: str, root_name: str, config: SameConfig):
    with helpers.add_path(str(base_path)):
        root_module = importlib.import_module(root_name)
        root_module.root()
