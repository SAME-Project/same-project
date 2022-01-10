import click
from sameproject.program import commands as program_group
from sameproject.version import commands as version


@click.group()
def main():
    """Project SAME CLI"""


@main.group()
def program():
    """Work with a SAME program"""


main.add_command(program_group.program)
main.add_command(version.version)

if __name__ == "__main__":
    main(auto_envvar_prefix="SAME")
