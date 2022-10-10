from sameproject.data.config import SameConfig
from sameproject.ops import helpers
from pathlib import Path
import importlib
import os

def deploy(base_path: Path,
           root_file: str, # root function with notebook code (string)
           config: SameConfig):
    return