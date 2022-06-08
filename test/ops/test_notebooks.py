from sameproject.ops.notebooks import read_notebook, get_steps, get_code
from sameproject.ops.code import get_imported_modules
from sameproject.data.config import SameConfig
from pathlib import Path
import test.testdata
import logging
import pytest


config_path = Path("test/ops/testdata/same_notebooks/generic/same.yaml")
notebook_path = Path("test/ops/testdata/same_notebooks/generic/sample_notebook.ipynb")
requirements_path = Path("test/ops/testdata/same_notebooks/generic/requirements.txt")

magic_line_testcases = [
    ("bad_python_lines", "test/ops/testdata/edgecase_notebooks/bad_python_lines.ipynb", False),
    ("multiline_strings", "test/ops/testdata/edgecase_notebooks/multiline_strings.ipynb", False),
]


@pytest.fixture
def config():
    with config_path.open("r") as file:
        return SameConfig.from_yaml(file.read()).resolve(config_path.parent)


@pytest.fixture
def notebook():
    return read_notebook(notebook_path)


@pytest.fixture
def requirements():
    with requirements_path.open("r") as file:
        return file.read()


def test_notebooks_inject_requirements(config, notebook, requirements):
    steps = get_steps(notebook, config)
    for name in steps:
        assert "requirements_file" in steps[name]
        assert steps[name].requirements_file == requirements


def test_notebooks_get_code(notebook):
    code = get_code(notebook)

    # Code should not break when parsed:
    modules = get_imported_modules(code)
    assert len(modules) > 0
