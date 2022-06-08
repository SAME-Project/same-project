from sameproject.data.config import SameConfig
from sameproject.data.step import Step
from pathlib import Path
from typing import Tuple
import sameproject.ops.functions as functions
import sameproject.ops.kubeflow as kubeflow
import sameproject.ops.kubeflowv1 as kubeflowv1
import sameproject.ops.aml as aml
import sameproject.ops.vertex as vertex
import sameproject.ops.helpers
import tempfile
import click


def render(execution_target: str, steps: list, same_run_config: SameConfig, compile_path: str = None) -> Tuple[Path, str]:
    target_renderers = {
        "aml": aml.render,
        "kubeflow": kubeflow.render,
        "functions": functions.render,
        "vertex": vertex.render,
        "kubeflowv1": kubeflowv1.render,
    }

    render_function = target_renderers.get(execution_target, None)
    if render_function is None:
        raise ValueError(f"Unknown backend: {execution_target}")

    if compile_path is None:
        compile_path = str(tempfile.mkdtemp())

    compile_path, root_module_name = render_function(compile_path, steps, same_run_config)
    return (compile_path, root_module_name)


def deploy(execution_target: str, base_path: Path, root_file: str, same_run_config: SameConfig):
    target_deployers = {
        "aml": aml.deploy,
        "kubeflow": kubeflow.deploy,
        "functions": functions.deploy,
        "vertex": vertex.deploy,
        "kubeflowv1": kubeflowv1.deploy,
    }

    deploy_function = target_deployers.get(execution_target, None)
    if deploy_function is None:
        raise ValueError(f"Unknown backend: {execution_target}")

    click.echo(f"Files persisted in: {base_path}")
    deploy_return = deploy_function(base_path, root_file, same_run_config)

    return deploy_return
