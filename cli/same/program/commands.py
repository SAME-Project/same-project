from io import BufferedReader
import click
from cli.same.program.compile import notebook_processing as nbproc
from cli.same.same_config import SameConfig

import backends


@click.group()
def program():
    pass


@program.command()
@click.option(
    "-f",
    "--same-file",
    "same_file",
    type=click.File("rb"),
    default="same.yaml",
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

    same_config = SameConfig(same_file)

    notebook_path = nbproc.get_notebook_path(same_file.name, same_config)  # noqa: F841

    notebook_dict = nbproc.read_notebook(notebook_path)

    all_steps = nbproc.get_steps(notebook_dict)

    backends.executor.render(target=target, steps=all_steps, same_config=same_config)

    # compileProgramCmd.Flags().String("image-pull-secret-server", "", "Image pull server for any private repos (only one server currently supported for all private repos)")
    # compileProgramCmd.Flags().String("image-pull-secret-username", "", "Image pull username for any private repos (only one username currently supported for all private repos)")
    # compileProgramCmd.Flags().String("image-pull-secret-password", "", "Image pull password for any private repos (only one password currently supported for all private repos)")
    # compileProgramCmd.Flags().String("image-pull-secret-email", "", "Image pull email for any private repos (only one email currently supported for all private repos)")


@program.command()
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
    default="same.yaml",
    help="Configuration file (same.yaml) for this project. We currently only support notebooks/python files describing pipelines in the same directory as the same configuration file.",
    show_default=True,
)
@click.option(
    "-t",
    "--target",
    type=click.Choice(["kubeflow", "aml"]),
)
def run(same_file: BufferedReader, target: str, persist_temp_files: bool = False):
    compiled_same_file = compile(same_file, target)
    backends.executor.deploy(compiled_same_file, persist_temp_files)
