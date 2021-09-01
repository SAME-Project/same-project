import click


@click.group()
def main():
    """Project SAME CLI"""


@main.group()
def program():
    """Work with a SAME program"""


@program.command("compile")
def program_compile():
    """Compile a SAME program without running"""


@program.command("run")
def program_run():
    """Run a SAME program"""


if __name__ == "__main__":
    main()
