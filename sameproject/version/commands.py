import click
import pkg_resources


@click.command()
def version():
    """Prints the versions for the CLI"""
    try:
        click.echo(pkg_resources.get_distribution("sameproject").version)
    except Exception as e:
        click.echo(f"Unknown version (error getting version: {e})")
