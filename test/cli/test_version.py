from click.testing import CliRunner
from cli.same.version.commands import version


def test_version():
    # just testing that version works - should never fail
    runner = CliRunner()
    result = runner.invoke(version)
    assert result.exit_code == 0
