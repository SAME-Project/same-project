import click


@click.command("compile")
def program_compile():
    """Compile a SAME program without running"""
    click.echo("foobaz")
