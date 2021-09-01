from click.testing import CliRunner
from cli.same.program.commands import program_compile


def test_compile():
    # just testing that we can test.
    runner = CliRunner()
    result = runner.invoke(program_compile)
    assert result.exit_code == 0
