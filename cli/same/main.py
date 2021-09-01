import click
from .program import commands as program_group


@click.group()
def main():
    """Project SAME CLI"""


@main.group()
def program():
    """Work with a SAME program"""


@program.command("run")
def program_run():
    """Run a SAME program"""


if __name__ == "__main__":
    main()
