import click
import pkg_resources


@click.command()
def version():
    """Prints the versions for the CLI"""
    click.echo(pkg_resources.get_distribution("sameproject").version)
