from sameproject import backends
from sameproject.objects.step import Step
from pathlib import Path
import tempfile
import sameproject.backends.kubeflow.render
import sameproject.backends.kubeflow.deploy
import sameproject.backends.aml.render
import sameproject.backends.aml.deploy

from typing import Tuple

import sameproject.helpers

import click


def render(target: str, steps: list, same_config: dict, compile_path: str = None) -> Tuple[Path, str]:
    target_renderers = {"kubeflow": backends.kubeflow.render.render_function, "aml": backends.aml.render.render_function}
    render_function = target_renderers.get(target, None)
    if render_function is None:
        raise ValueError(f"Unknown backend: {target}")

    if compile_path is None:
        compile_path = str(tempfile.mkdtemp())

    compile_path, root_module_name = render_function(compile_path, steps, same_config)
    return (compile_path, root_module_name)


def deploy(target: str, root_file_absolute_path: str, root_module_name: str, persist_temp_files: bool = False):
    target_deployers = {"kubeflow": backends.kubeflow.deploy.deploy_function, "aml": backends.aml.deploy.deploy_function}
    deploy_function = target_deployers.get(target, None)
    if deploy_function is None:
        raise ValueError(f"Unknown backend: {target}")

    deploy_return = deploy_function(root_file_absolute_path, root_module_name)
    if not persist_temp_files:
        sameproject.helpers.recursively_remove_dir(Path(root_file_absolute_path))
    else:
        click.echo(f"Files persisted in: {root_file_absolute_path}")

    return deploy_return
