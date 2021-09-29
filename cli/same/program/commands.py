from io import BufferedReader
import click
from program.compile import notebook_processing as nbproc

import backends.executor


@click.group()
def program():
    pass


@program.command(
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
    )
)
@click.option(
    "-f",
    "--same-file",
    "same_file",
    type=click.File("rb"),
    help="Configuration file (same.yaml) for this project. We currently only support notebooks/python files describing pipelines in the same directory as the same configuration file.",
    show_default=True,
)
@click.option(
    "-t",
    "--target",
    type=click.Choice(["kubeflow", "aml"]),
)
def compile(same_file: BufferedReader, target: str):
    """Compile a SAME program without running - this is an internal function only."""
    click.echo(f"File is: {same_file.name}")
    nbproc.compile(same_file, target)


@program.command(
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
    )
)
@click.option(
    "-p",
    "--persist-temp-files",
    "persist_temp_files",
    default=False,
    is_flag=True,
    type=bool,
    help="Persist the temporary compilation files.",
)
@click.option(
    "-f",
    "--same-file",
    "same_file",
    type=click.File("rb"),
    help="Configuration file (same.yaml) for this project. We currently only support notebooks/python files describing pipelines in the same directory as the same configuration file.",
    show_default=True,
)
@click.option(
    "-t",
    "--target",
    type=click.Choice(["kubeflow", "aml"]),
)
def run(same_file: BufferedReader, target: str, persist_temp_files: bool = False):
    click.echo(f"File is: {same_file.name}")
    compiled_same_file = nbproc.compile(same_file, target)
    backends.executor.deploy(target, compiled_same_file, persist_temp_files)
