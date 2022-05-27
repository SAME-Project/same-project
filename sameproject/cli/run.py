from sameproject.ops.runtime_options import validate_options, runtime_options, get_option_value
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
    type=click.Choice(["aml", "kubeflow", "functions"]),
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
    persist_temp_files: bool = False,  # TODO: remove this
):
    """Compiles and deploys a pipeline from a SAME config file."""
    # Validate runtime options against the configured backend:

    click.echo(f"File is: {same_file.name}")
    base_path, root_file = notebooks.compile(config, target)
    if not no_deploy:
        backends.deploy(target, base_path, root_file, config)
