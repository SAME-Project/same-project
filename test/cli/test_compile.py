from click.testing import CliRunner
from cli.same.program.commands import compile


def test_compile():
    # just testing that we can test.
    runner = CliRunner()
    result = runner.invoke(compile)
    assert result.exit_code == 0
