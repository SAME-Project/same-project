import click


@click.group()
def program():
    pass


@program.command()
def compile():
    """Compile a SAME program without running"""
    click.echo("foobaz")
