from sameproject.data.config import SameConfig
from sameproject.data.step import Step
from pathlib import Path
from typing import Tuple
import sameproject.ops.kubeflow as kubeflow
import sameproject.ops.kubeflowv1 as kubeflowv1
import sameproject.ops.aml as aml
import sameproject.ops.vertex as vertex
import sameproject.ops.helpers
import tempfile
import click


def render(same_run_config: dict, execution_target: str, steps: list, compile_path: str = None) -> Tuple[Path, str]:
    target_renderers = {"kubeflow": kubeflow.render, "aml": aml.render, "vertex": vertex.render, "kubeflowv1": kubeflowv1.render}
    render_function = target_renderers.get(execution_target, None)
    if render_function is None:
        raise ValueError(f"Unknown backend: {execution_target}")

    if compile_path is None:
        compile_path = str(tempfile.mkdtemp())

    compile_path, root_module_name = render_function(compile_path, steps, same_run_config)
    return (compile_path, root_module_name)


def deploy(target: str, root_file_absolute_path: str, root_module_name: str, persist_temp_files: bool = False):
    target_deployers = {"kubeflow": kubeflow.deploy, "aml": aml.deploy, "vertex": vertex.deploy, "kubeflowv1": kubeflowv1.deploy}
    deploy_function = target_deployers.get(target, None)
    if deploy_function is None:
        raise ValueError(f"Unknown backend: {target}")

    deploy_return = deploy_function(root_file_absolute_path, root_module_name)
    if not persist_temp_files:
        pass  # TODO: removing temp files breaks things as the deployer runs async
        # sameproject.helpers.recursively_remove_dir(Path(root_file_absolute_path))
    else:
        click.echo(f"Files persisted in: {root_file_absolute_path}")

    return deploy_return
