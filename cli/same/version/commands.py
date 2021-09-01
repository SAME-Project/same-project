import click


@click.command("version")
def version():
    """Prints the versions for the CLI"""
    click.echo("0.0.1")
