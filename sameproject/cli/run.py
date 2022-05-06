from sameproject.ops.runtime_options import runtime_options, get_option_value
from sameproject.data.config import SameConfig
from io import BufferedReader
from pathlib import Path
import sameproject.ops.notebooks as notebooks
import sameproject.ops.backends as backends
import click


@click.command(
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
    )
)
@click.option(
    "-f",
    "--same-file",
    "same_file",
    default="same.yaml",
    show_default=True,
    type=click.File("r"),
    help="Path to SAME configuration file.",
)
@click.option(
    "-t",
    "--target",
    default="kubeflow",
    type=click.Choice(["kubeflow", "aml", "vertex"]),
)
@click.option(
    "--persist-temp-files",
    "persist_temp_files",
    default=False,
    is_flag=True,
    type=bool,
    help="Persist compilation artifacts.",
)
@click.option(
    "--no-deploy",
    "no_deploy",
    default=False,
    is_flag=True,
    type=bool,
    help="Do not deploy compiled pipelines.",
)
@runtime_options
def run(
    target: str,
    same_file: BufferedReader,
    no_deploy: bool = False,
    persist_temp_files: bool = False,
):
    """Compiles and deploys a pipeline from a SAME config file."""
    # TODO: Make SAME config object immutable (frozen_box=True).
    same_run_config = SameConfig.from_yaml(same_file.read(), frozen_box=False)
    same_run_config = same_run_config.resolve(Path(same_file.name).parent)
    same_run_config = same_run_config.inject_runtime_options()

    click.echo(f"File is: {same_file.name}")
    artifact_path, root_module = notebooks.compile(same_run_config=same_run_config, execution_target=target)
    if persist_temp_files:
        click.echo(f"Compile artifacts persisted at: {artifact_path}")
    if not no_deploy:
        backends.deploy(target, artifact_path, root_module, persist_temp_files)
