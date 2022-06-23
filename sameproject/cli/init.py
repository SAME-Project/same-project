from sameproject.ops.files import find_same_config, find_notebook, find_requirements
from sameproject.ops.requirements import get_package_info, render_package_info
from sameproject.ops.notebooks import get_code, read_notebook
from sameproject.ops.code import get_imported_modules, remove_magic_lines
from sameproject.data.config import SameValidator, name_schema, image_schema
from cerberus import Validator
from pathlib import Path
from box import Box
import pkg_resources
import click


def _click_type(name, schema):
    """Returns a click ParamType subclass that validates input."""
    class ParamType(click.ParamType):
        name = "name"
        schema = "schema"

        def __call__(self, value, param=None, ctx=None):
            if value is not None:
                validator = Validator({"value": schema})
                if not validator.validate({"value": value}):
                    regex = schema["regex"]
                    self.fail(f"input is invalid, should satisfy regex '{regex}'")
                return value

    return ParamType()


# Click types for prompts that perform validation:
name_type = _click_type("name", name_schema)
image_type = _click_type("docker_image", image_schema)
file_type = click.Path(
    exists=True,
    file_okay=True,
    dir_okay=False,
    readable=True,
    resolve_path=True,
    path_type=Path,
)


@click.command()
def init():
    """Creates a new SAME config file."""

    # Start by looking for an existing same config in the current directory.
    cfg = find_same_config(recurse=False)
    if cfg is not None:
        click.echo("An existing SAME config file was found at the following path:")
        click.echo(f"\t{cfg}")
        if not click.confirm("Do you want to replace it?", default=False):
            exit(0)
    else:
        cfg = Path("./same.yaml")

    # Name of the pipeline:
    pl_name = click.prompt(
        "Name of this config:",
        default="default_config",
        type=name_type
    )

    # Notebook data:
    nb_path = click.prompt(
        "Notebook path",
        default=find_notebook(recurse=True),
        type=file_type,
    )
    if not nb_path.exists():
        click.echo(f"No such file found: {nb_path}", err=True)
        exit(1)
    nb_dict = read_notebook(nb_path)
    nb_name = click.prompt("Notebook name", default=nb_name, type=str)

    # Docker image data:
    image = click.prompt(
        "Default docker image",
        default="combinatorml/jupyterlab-tensorflow-opencv:0.9",
        type=image_type
    )

    # Requirements.txt data:
    req = find_requirements(recurse=False)
    if req is None:
        if click.confirm("No requirements.txt found in current directory - would you like to create one?", default=True):
            req_contents = f"# Dependencies for {nb_path.resolve()}:\n"

            writing_reqs = False
            if click.confirm("Would you like SAME to fill in the requirements.txt for you?", default=True):
                code = remove_magic_lines(get_code(nb_dict))
                modules = get_imported_modules(code)
                pkg_info = get_package_info(modules)

                if len(pkg_info) > 0:
                    writing_reqs = True
                    click.echo("Found the following requirements for the notebook:")
                    for pkg in pkg_info:
                        click.echo(f"\t{pkg_info[pkg].name}=={pkg_info[pkg].version}")
                else:
                    click.echo("No requirements found for the notebook.")
                req_contents += render_package_info(pkg_info) + "\n"

            req = Path("requirements.txt")
            with req.open("w") as file:
                file.write(req_contents)

            if writing_reqs:
                click.echo(f"Wrote requirements to {req.resolve()}.")
            else:
                click.echo(f"Wrote empty requirements file to {req.resolve()}.")
    else:
        req = click.prompt(
            "Requirements.txt",
            default=req,
            type=file_type,
        )
        if req == "":
            req = None

    # Construct, validate and save the SAME config file!
    same_config = Box({
        "apiVersion": _get_api_version(),
        "metadata": {
            "name": f"{pl_name}",
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
            "name": f"{pl_name} run",
        },
    })

    # Add requirements if the user has configured one:
    if req is not None:
        same_config.notebook.requirements = str(req)

    click.echo(f"About to write to {cfg.absolute()}:")
    click.echo()
    click.echo(same_config.to_yaml())
    if click.confirm("Is this okay?", default=True):
        cfg.write_text(same_config.to_yaml())
        click.echo(f"Wrote config file to {cfg.absolute()}.")
        click.echo()
        click.echo("""You can now run 'same verify' to check that everything is configured correctly
(requires docker locally), or you can run 'same run' to deploy the pipeline to a
configured backend (e.g. Kubeflow Pipelines in a Kubernetes cluster file pointed
to by ~/.kube/config or set in the KUBECONFIG environment variable).
""")


def _prompt(msg, default=None, type=None, validation_fn=None):
    """Wraps a `click.prompt` call with retries and validation."""
    res = None
    while True:
        res = click.prompt(msg, default=default, type=type)
        if validation_fn is not None:
            is_valid, errors = validation_fn(res)
            if not is_valid:
                click.echo(f"invalid input: {errors}")
                continue
        break
    return res


def _get_api_version():
    return "sameproject.ml/v1alpha1"
