from sameproject.ops.files import find_same_config, find_notebook, find_requirements
from sameproject.ops.notebooks import read_notebook, get_name
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
    else:
        cfg = Path("./same.yaml")

    # Notebook data:
    nb_path = click.prompt("Notebook path", default=find_notebook(recurse=True), type=Path)
    if not nb_path.exists():
        click.echo(f"No such file found: {nb_path}", err=True)
        exit(1)

    nb_name = get_name(read_notebook(nb_path))
    if nb_name == "":
        nb_name = "notebook"
    nb_name = click.prompt("Notebook name", default=nb_name, type=str)

    # Docker image data:
    image = click.prompt("Default docker image", default="library/python:3.9-slim-buster", type=str)

    # Requirements.txt data:
    req = find_requirements(recurse=False)
    if req is None:
        if click.confirm("No requirements.txt found in current directory - would you like to create one?", default=True):
            req = Path("requirements.txt")
            with req.open("w") as file:
                file.write(f"# Dependencies for {nb_path}:\n")
            click.echo(f"Wrote to {req.resolve()}.")
    else:
        req = click.prompt("Requirements.txt", default=req, type=Path)
        if req == "":
            req = None  # TODO: handle optional with click

    # Construct, validate and save the SAME config file!
    same_config = Box({
        "apiVersion": _get_api_version(),
        "metadata": {
            "name": f"{nb_name} pipeline",
            "labels": [],
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
            "name": f"{nb_name} run",
        },
    })

    # Add requirements if the user has configured one:
    if req is not None:
        same_config.notebook.requirements = str(req)

    validator = SameValidator.get_validator()
    if not validator.validate(same_config):
        click.echo(f"One or more of the provided parameters was invalid: {validator.errors}", err=True)
        exit(1)

    click.echo(f"About to write to {cfg.absolute()}:")
    click.echo()
    click.echo(same_config.to_yaml())
    click.echo()
    if click.confirm("Is this okay?", default=True):
        cfg.write_text(same_config.to_yaml())


def _get_api_version():
    try:
        return pkg_resources.get_distribution("sameproject").version
    except Exception:
        return "unknown"  # TODO: better fallback
