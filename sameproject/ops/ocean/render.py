from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from typing import Tuple
from uuid import uuid4
import os

from sameproject.ops import helpers

ocean_root_template = "root.jinja"


def render(compile_path: str, same_config: dict) -> Tuple[Path, str]:
    """Renders the notebook into a root file and a series of step files according to the target requirements. Returns an absolute path to the root file for deployment."""
    templateDir = os.path.dirname(os.path.abspath(__file__))
    templateLoader = FileSystemLoader(templateDir)
    print(f"Template dir {templateDir}")
    env = Environment(trim_blocks=True, loader=templateLoader)

    root_file_string = _build_root_file(env, same_config)
    root_pipeline_name = f"root_pipeline_{uuid4().hex.lower()}"
    root_path = Path(compile_path) / f"{root_pipeline_name}.py"
    helpers.write_file(root_path, root_file_string)

    return (compile_path, root_pipeline_name)