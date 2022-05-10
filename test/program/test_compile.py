from sameproject.ops import notebooks as nbproc
from sameproject.data.config import SameConfig
from pathlib import Path
import pytest


config_path = Path("test/ops/testdata/same_notebooks/generic/same.yaml")


magic_line_testcases = [
    ("bad_python_lines", "test/ops/testdata/edgecase_notebooks/bad_python_lines.ipynb", True),
    ("multiline_strings", "test/ops/testdata/edgecase_notebooks/multiline_strings.ipynb", False),
]


@pytest.fixture
def config():
    with config_path.open("r") as file:
        return SameConfig.from_yaml(file.read()).resolve(config_path.parent)


@pytest.mark.parametrize("name, path, expect_err", magic_line_testcases)
def test_magic_line_parsing(name, path, expect_err, config):
    """
    Tests magic line parsing in notebooks, with edge-cases like
    multiline strings containing what appear to be multiline strings.
    """
    notebook_dict = nbproc.read_notebook(path)

    if expect_err:
        with pytest.raises(SyntaxError):
            assert nbproc.get_steps(notebook_dict, config)
    else:
        assert nbproc.get_steps(notebook_dict, config)
