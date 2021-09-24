from re import S
import backends
from objects.step import Step
from pathlib import Path
import tempfile
import backends.kubeflow.render
import backends.kubeflow.deploy
import backends.aml.render
import backends.aml.deploy


def render(target: str, steps: list[Step], same_config: dict, compile_path:str = None) -> Path:
    target_renderers = {"kubeflow": backends.kubeflow.render.render_function, "aml": backends.aml.render.render_function}
    render_function = target_renderers.get(target, None)
    if render_function is None:
        raise ValueError(f"Unknown backend: {target}")

    if compile_path is None:
        compile_path = str(tempfile.mkdtemp())

    render_function(compile_path, steps, same_config)
    return compile_path


def deploy(target: str, root_file_absolute_path: str):
    target_deployers = {"kubeflow": backends.kubeflow.deploy.deploy_function, "aml": backends.aml.deploy.deploy_function}
    deploy_function = target_deployers.get(target, None)
    if deploy_function is None:
        raise ValueError(f"Unknown backend: {target}")

    return deploy_function(root_file_absolute_path)
