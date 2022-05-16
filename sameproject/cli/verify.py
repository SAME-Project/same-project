from sameproject.ops.notebooks import read_notebook, get_code
from sameproject.ops.code import get_imported_modules, remove_magic_lines
from sameproject.data.config import SameConfig
from io import BufferedReader
from tempfile import mkdtemp
from pathlib import Path
from typing import List, Dict
import docker
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
    help="Path to SAME config file.",
)
def verify(same_file: BufferedReader):
    """
    Verifies that your notebook's dependencies are satisfied by the docker
    image and requirements file specified in your SAME config file. Requires
    a configured docker installation.
    """
    try:
        config = SameConfig.from_yaml(same_file.read())
        config = config.resolve(Path(same_file.name).parent)

        notebook = read_notebook(config.notebook.path)
        code = remove_magic_lines(get_code(notebook))
        modules = get_imported_modules(code)

    except Exception as err:
        click.echo(f"Error during 'same verify' initialisation: {err}", err=True)
        exit(1)

    for i, env in enumerate(config.environments.keys()):
        try:
            if not _verify(config, env, modules):
                exit(1)

            if i > 0:
                click.echo()  # space between environment checks
        except docker.errors.APIError as err:
            click.echo(f"An exception was raised by the docker API: {err}", err=True)
            exit(1)
        except Exception as err:
            click.echo(f"One or more 'same verify' steps failed to execute correctly: {err}", err=True)
            exit(1)


def _verify(config: SameConfig, env: str, modules: List[str]) -> bool:
    click.echo(f"Verifying dependencies for environment '{env}':")

    # First step is to connect to docker.
    click.echo("\t* connecting to docker...")
    client = docker.from_env()
    image = config.environments[env].image_tag

    # Next we generate a bound volume with the SAME config's requirements.txt:
    volumes = {}
    if "requirements" in config.notebook:
        click.echo("\t* binding requirements to docker volume...")
        volumes = _create_requirements_volume(config)

    # Spins up a container with the configured docker image:
    click.echo(f"\t* spinning up container with image '{image}'...")
    container = client.containers.run(
        image,
        tty=True,
        detach=True,
        volumes=volumes
    )

    # Installs the requirements if any have been configured:
    if "requirements" in config.notebook:
        click.echo("\t* installing requirements inside container...")
        res = container.exec_run(
            ["pip", "install", "-r", "/mnt/requirements/requirements.txt"]
        )

        if res.exit_code != 0:
            raise Exception(f"'pip install' returned non-zero exit code '{res.exit_code}' when installing requirements:\n{res.output.decode('utf-8')}\n\nTry updating ./requirements.txt to fix the above error and run 'same verify' again.")

    # Check the user's module imports to see which ones succeed:
    click.echo("\t* checking notebook imports to see whether they resolve...")
    failed_modules = []
    for module in modules:
        res = container.exec_run(["python", "-c", f"import {module}"])
        if res.exit_code != 0:
            failed_modules.append(module)

    # Shutdown container and return dependency results:
    click.echo("\t* killing container...")
    container.kill()

    # Report back to the user:
    if len(failed_modules) == 0:
        click.echo(f"Done - all modules for environment '{env}' successfully resolve!")
        return True
    else:
        click.echo("Done - the following modules failed to resolve:")
        for module in failed_modules:
            click.echo(f"\t* {module}")

        if "requirements" in config.notebook:
            click.echo(f"Consider adding dependencies to '{config.notebook.requirements}' for these modules.")
        else:
            click.echo("Consider configuring a 'requirements.txt' in your SAME config file for these modules.")
        return False


def _create_requirements_volume(config: SameConfig) -> Dict:
    with Path(config.notebook.requirements).open("r") as file:
        requirements = file.read()

    vdir = Path(mkdtemp())
    with (vdir / "requirements.txt").open("w") as file:
        file.write(requirements)

    return {
        str(vdir): {
            "bind": "/mnt/requirements",
            "mode": "ro",
        }
    }
