from sameproject.cli import run, version, init, verify
import click


@click.group()
def main():
    """
Command-line interface for the SAME project, a tool for easily converting
Jupyter notebooks into pipelines and deploying them to your favourite backend.
    """


# For backwards-compatibility with older versions of same.
@click.group()
def program():
    """Historical alias for the `run` command."""


main.add_command(run)
main.add_command(init)
main.add_command(verify)
main.add_command(version)

# For backwards-compatibility with older versions of same.
main.add_command(program)
program.add_command(run)


# https://click.palletsprojects.com/en/8.1.x/options/#values-from-environment-variables
if __name__ == "__main__":
    main(auto_envvar_prefix="SAME")
