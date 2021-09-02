from email.policy import default
from pydoc import describe
from unicodedata import name
import click
from .compile import notebook_processing as nbproc
from .. import helpers


@click.group()
def program():
    pass


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
def compile(same_file, persist_temp_files, target):
    """Compile a SAME program without running"""
    click.echo(f"File is: {same_file}")

    same_config = helpers.load_same_config_file(same_file)

    notebook_path = nbproc.get_pipeline_path(same_config)  # noqa: F841

    # compileProgramCmd.Flags().String("image-pull-secret-server", "", "Image pull server for any private repos (only one server currently supported for all private repos)")
    # compileProgramCmd.Flags().String("image-pull-secret-username", "", "Image pull username for any private repos (only one username currently supported for all private repos)")
    # compileProgramCmd.Flags().String("image-pull-secret-password", "", "Image pull password for any private repos (only one password currently supported for all private repos)")
    # compileProgramCmd.Flags().String("image-pull-secret-email", "", "Image pull email for any private repos (only one email currently supported for all private repos)")
