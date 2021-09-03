from click.testing import CliRunner
import pytest
from pathlib import Path
import cli.same.helpers as helpers
from cli.same.program.commands import compile
from cli.same.program.compile import notebook_processing
import logging
from io import BufferedReader

same_config_file_path = "test/cli/testdata/generic_notebook/same.yaml"


@pytest.fixture
def same_config():
    with open(same_config_file_path, "rb") as f:
        return helpers.load_same_config_file(f)


def test_compile_verb():
    # just testing that we can test the compile verb

    same_file_path = Path(same_config_file_path)
    assert same_file_path.exists()

    same_file_path_as_string = str(same_file_path.absolute())
    runner = CliRunner()
    result = runner.invoke(
        compile,
        ["-f", same_file_path_as_string],
    )
    assert result.exit_code == 0


def test_get_pipeline_path(same_config):
    assert "sample_notebook.ipynb" in notebook_processing.get_pipeline_path(Path(same_config_file_path).parent, same_config)


def test_bad_notebook_path(caplog):
    bad_path_string = "BAD_PATH"
    with pytest.raises(SystemExit) as e:
        with caplog.at_level(logging.FATAL):
            notebook_processing.convert_notebook_to_text(bad_path_string)
            assert bad_path_string in caplog.text
    assert e.type == SystemExit
    assert e.value.code == 1


def test_read_notebook_as_string(caplog, same_config):
    notebook_path = notebook_processing.get_pipeline_path(Path(same_config_file_path).parent, same_config)
    notebook_as_py = ""
    with caplog.at_level(logging.FATAL):
        notebook_as_py = notebook_processing.convert_notebook_to_text(notebook_path)
        assert caplog.text == ""

    assert "jupytext:\n#     text_representation:\n#       extension: .py\n#       format_name: percent" in notebook_as_py
