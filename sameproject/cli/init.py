from sameproject.ops.files import find_same_config, find_notebook
from sameproject.data.config import SameValidator
from pathlib import Path
from box import Box
import pkg_resources
import click


@click.command()
def init():
    """Creates a new SAME config file."""

    # Start by looking for an existing same config in the current directory.
    cfg = find_same_config(recurse=False)
    if cfg is not None:
        click.echo("An existing SAME config file was found at the following path:")
        click.echo(f"\t{cfg}")
        if not click.confirm("Do you want to replace it?"):
            exit(0)

    # Ask user for notebook info:
    nb_name = click.prompt("Notebook name", type=str)
    nb_path = click.prompt("Notebook path", default=find_notebook(recurse=True), type=Path)
    if not nb_path.exists():
        click.echo(f"No such file found: {nb_path}", err=True)
        exit(1)

    # Ask user for metadata:
    pipe_name = click.prompt("Pipeline name", type=str)
    pipe_labels = _process_labels(click.prompt("Pipeline labels", type=str))

    # Ask user for runtime info:
    run_name = click.prompt("Default run name", type=str)

    # Ask user for environment info:
    image = click.prompt("Default docker image", default="library/python:3.9-slim-buster", type=str)

    # Construct, validate and save the SAME config file!
    same_config = Box({
        "apiVersion": _get_api_version(),
        "metadata": {
            "name": pipe_name,
            "labels": pipe_labels,
            "version": "0.0.0",
        },
        "environments": {
            "default": {
                "image_tag": image,
            },
        },
        "notebook": {
            "name": nb_name,
            "path": str(nb_path),
        },
        "run": {
            "name": run_name,
        },
    })

    validator = SameValidator.get_validator()
    if not validator.validate(same_config):
        click.echo(f"One or more of the provided parameters was invalid: {validator.errors}", err=True)
        exit(1)

    pwd = Path(".").resolve() / "same.yaml"
    click.echo(f"About to write to {pwd}:")
    click.echo()
    click.echo(same_config.to_yaml())
    click.echo()
    if click.confirm("Is this okay?", default=True):
        pwd.write_text(same_config.to_yaml())


def _process_labels(labelstr):
    return list(map(lambda x: x.strip(), labelstr.split(",")))


def _get_api_version():
    try:
        return pkg_resources.get_distribution("sameproject").version
    except Exception:
        return "unknown"  # TODO: better fallback
