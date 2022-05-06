from sameproject.ops.notebooks import read_notebook, get_steps
from sameproject.data.config import SameConfig
from pathlib import Path
import pytest


def _relpath(path):
    return Path(__file__).parent / path


config_path = _relpath("../testdata/generic_notebook/same.yaml")
notebook_path = _relpath("../testdata/generic_notebook/sample_notebook.ipynb")
requirements_path = _relpath("../testdata/generic_notebook/requirements.txt")


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
