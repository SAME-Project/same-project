import click
from program import commands as program_group
from version import commands as version


@click.group()
def main():
    """Project SAME CLI"""


@main.group()
def program():
    """Work with a SAME program"""


@program.command("run")
def program_run():
    """Run a SAME program"""


main.add_command(program_group.command_group)
main.add_command(version.version)

if __name__ == "__main__":
    main()
