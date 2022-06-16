from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from typing import Tuple
from uuid import uuid4
from base64 import urlsafe_b64encode
import logging
import os
import time

from sameproject.data.step import Step
from sameproject.ops import helpers
import sameproject.ops.explode

ocean_step_template = "step.jinja"


def render(compile_path: str, steps: list, same_config: dict) -> Tuple[Path, str]:
    """Renders the notebook into a root file and a series of step files according to the target requirements. Returns an absolute path to the root file for deployment."""
    templateDir = os.path.dirname(os.path.abspath(__file__))
    templateLoader = FileSystemLoader(templateDir)
    print(f"Template dir {templateDir}")
    env = Environment(trim_blocks=True, loader=templateLoader)

    root_file_string = _build_step_file(env, next(iter(steps.values())), same_config)
    root_pipeline_name = f"root_pipeline_{uuid4().hex.lower()}"
    root_path = Path(compile_path) / f"{root_pipeline_name}.py"
    helpers.write_file(root_path, root_file_string)

    return (compile_path, root_pipeline_name)


def _build_step_file(env: Environment, step: Step, same_config) -> str:
    with open(sameproject.ops.explode.__file__, "r") as f:
        explode_code = f.read()

    requirements_file = None
    if "requirements_file" in step:
        requirements_file = urlsafe_b64encode(bytes(step.requirements_file, "utf-8")).decode()

    memory_limit = same_config.runtime_options.get(
        "serialisation_memory_limit",
        512 * 1024 * 1024,  # 512MB
    )

    same_env = same_config.runtime_options.get(
        "same_env",
        "default",
    )

    step_contract = {
        "name": step.name,
        "same_env": same_env,
        "memory_limit": memory_limit,
        "unique_name": step.unique_name,
        "requirements_file": requirements_file,
        "user_code": urlsafe_b64encode(bytes(step.code, "utf-8")).decode(),
        "explode_code": urlsafe_b64encode(bytes(explode_code, "utf-8")).decode(),
        "same_yaml": urlsafe_b64encode(bytes(same_config.to_yaml(), "utf-8")).decode(),
    }

    return env.get_template(ocean_step_template).render(step_contract)