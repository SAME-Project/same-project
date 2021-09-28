from click.testing import CliRunner
import pytest
from pathlib import Path
from cli.same.same_config import SameConfig
from cli.same.program.commands import compile
from cli.same.program.compile import notebook_processing
import logging
from backends.executor import render as template_render
from backends.executor import deploy

same_config_file_path = "test/testdata/generic_notebook/same.yaml"


@pytest.fixture
def same_config():
    with open(same_config_file_path, "rb") as f:
        return SameConfig(buffered_reader=f)


def test_live_test_kubeflow(mocker, tmpdir, same_config):
    notebook_path = "test/testdata/generic_notebook/sample_notebook.ipynb"
    notebook_dict = notebook_processing.read_notebook(notebook_path)
    steps = notebook_processing.get_steps(notebook_dict)
    complied_path = template_render("kubeflow", steps, same_config, compile_path=tmpdir)
    deploy("kubeflow", complied_path)

    assert True  # Deployed to Kubeflow without raising an error


@pytest.mark.skip
def test_kubeflow_secrets():
    assert False
    # TODO: Unit test for secrets being created
    # No secrets
    # One secret
    # Two+ secrets
    # Partially complete secrets
