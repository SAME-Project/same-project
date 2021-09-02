import click


@click.command()
def version():
    """Prints the versions for the CLI"""
    click.echo("0.0.1")
