import pytest
from sameproject.ops import notebooks as nbproc


magic_line_testcases = [
    ("bad_python_lines", "test/testdata/notebook_edge_cases/bad_python_lines.ipynb", True),
    ("multiline_strings", "test/testdata/notebook_edge_cases/multiline_strings.ipynb", False),
]


@pytest.mark.parametrize("name, path, expect_err", magic_line_testcases)
def test_magic_line_parsing(name, path, expect_err):
    """
    Tests magic line parsing in notebooks, with edge-cases like
    multiline strings containing what appear to be multiline strings.
    """
    notebook_dict = nbproc.read_notebook(path)

    if expect_err:
        with pytest.raises(SyntaxError):
            assert nbproc.get_steps(notebook_dict)
    else:
        assert nbproc.get_steps(notebook_dict)
