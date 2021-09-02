from click.testing import CliRunner
import pytest
from pathlib import Path
import cli.same.helpers as helpers
from cli.same.program.commands import compile
from cli.same.program.compile import notebook_processing

same_config_file_path = "test/cli/testdata/generic_notebook/same.yaml"


@pytest.fixture
def same_config():
    return helpers.load_same_config_file(same_config_file_path)


def test_compile_verb():
    # just testing that we can test the compile verb

    same_file_path = Path(same_config_file_path)
    assert same_file_path.exists()

    runner = CliRunner()
    result = runner.invoke(
        compile,
        ["-f", str(same_file_path.absolute())],
    )
    assert result.exit_code == 0


def test_get_pipeline_path(same_config):
    assert "sample_notebook.ipynb" == notebook_processing.get_pipeline_path(same_config)
