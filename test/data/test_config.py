from pathlib import Path
from sameproject.data.config import SameConfig, SameValidator
import pytest

test_data_dir = Path(__file__).parent.joinpath("testdata")
# An example of a well-formed, complete SAME config file.
good_config = test_data_dir.joinpath("same_configs", "good_same.yaml")
good_notebook = test_data_dir.joinpath("same_configs", "good_notebook.ipynb")

# List of SAME config files that are broken in various ways:
#   name, path
bad_configs = [
    ("no api version", test_data_dir.joinpath("same_configs", "no_apiVersion.yaml")),
    ("no default environment", test_data_dir.joinpath("same_configs", "no_default_for_environments.yaml")),
]

bad_notebooks = [
    ("no api version", test_data_dir.joinpath("same_configs", "no_apiVersion.ipynb")),
    ("no config", test_data_dir.joinpath("same_configs", "notebook_no_config.ipynb")),
]


def test_schema():
    assert SameValidator.get_validator() is not None


def test_good_config():
    config = None
    with open(good_config, "r") as f:
        config = SameConfig.from_yaml(f.read())

    assert config is not None
    assert config.notebook.path == "sample_notebook.ipynb"
    assert config.metadata.name == "SampleComplicatedNotebook"
    assert len(config.datasets.USER_HISTORY.environments) == 3
    assert isinstance(config.run.parameters, dict)


@pytest.mark.parametrize("name, path", bad_configs, ids=[x[0] for x in bad_configs])
def test_bad_configs(name, path):
    with pytest.raises(SyntaxError):
        with open(path, "r") as f:
            SameConfig.from_yaml(f.read())


def test_good_notebook_config():
    config = SameConfig.from_ipynb(good_notebook.read_text(), good_notebook, False)

    assert config is not None
    assert config.notebook.path == good_notebook.name
    assert config.metadata.name == "NotebookConfig"
    assert len(config.datasets.USER_HISTORY.environments) == 3
    assert isinstance(config.run.parameters, dict)


@pytest.mark.parametrize("name, path", bad_notebooks, ids=[x[0] for x in bad_notebooks])
def test_bad_notebook_configs(name, path):
    with pytest.raises(SyntaxError):
        with open(path, "r") as f:
            SameConfig.from_yaml(f.read())
