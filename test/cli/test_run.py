from sameproject.ops.backends import render as template_render
from sameproject.ops import notebooks
from sameproject.ops.backends import deploy
from sameproject.data.config import SameConfig
from click.testing import CliRunner
from sameproject.cli import run
from pathlib import Path
import sameproject.ops.helpers
import tempfile
import logging
import pytest
import dotenv
import sys


same_config_file_path = "test/ops/testdata/same_notebooks/generic/same.yaml"


@pytest.fixture
def same_config():
    with open(same_config_file_path, "r") as f:
        return SameConfig.from_yaml(f.read())


@pytest.fixture(autouse=True)
def reset_modules():
    """
    KFP modifies sys.modules by importing component modules, which we'd like
    to reset after each test to simulate a clean environment.
    """
    modules_bkup = sys.modules.copy()
    yield
    sys.modules.clear()
    sys.modules.update(modules_bkup)


@pytest.mark.kubeflow
def test_live_test_kubeflow(mocker, tmpdir, same_config):
    temp_dir_mock = mocker.patch.object(tempfile, "mkdtemp")
    temp_dir_mock.return_value = tmpdir

    mocker.patch.object(sameproject.ops.helpers, "recursively_remove_dir")

    dotenv.load_dotenv("./.env.sh")
    same_file_path = Path(same_config_file_path)
    assert same_file_path.exists()

    same_file_path_as_string = str(same_file_path.absolute())
    runner = CliRunner()

    result = runner.invoke(
        run,
        [
            "-f",
            same_file_path_as_string,
            "-t",
            "kubeflow",
        ],
    )
    assert result.exit_code == 0


@pytest.mark.aml
def test_live_test_aml(mocker, tmpdir, same_config):
    temp_dir_mock = mocker.patch.object(tempfile, "mkdtemp")
    temp_dir_mock.return_value = tmpdir

    mocker.patch.object(sameproject.ops.helpers, "recursively_remove_dir")

    dotenv.load_dotenv("./.env.sh")
    same_file_path = Path(same_config_file_path)
    assert same_file_path.exists()

    same_file_path_as_string = str(same_file_path.absolute())
    runner = CliRunner()

    result = runner.invoke(
        run,
        [
            "-f",
            same_file_path_as_string,
            "-t",
            "aml",
        ],
    )
    assert result.exit_code == 0


@pytest.mark.kubeflow
def test_kubeflow_same_program_run_with_secrets_e2e():
    multi_env_same_config_file_path = "test/ops/testdata/same_notebooks/multienv/same.yaml"
    same_file_path = Path(multi_env_same_config_file_path)
    assert same_file_path.exists()

    same_file_path_as_string = str(same_file_path.absolute())
    runner = CliRunner()

    result = runner.invoke(
        run,
        [
            "-f",
            same_file_path_as_string,
            "-t",
            "kubeflow",
            "--image-pull-secret-name",
            "IMAGE_PULL_SECRET_NAME",
            "--image-pull-secret-registry-uri",
            "IMAGE_PULL_SECRET_REGISTRY_URI",
            "--image-pull-secret-username",
            "IMAGE_PULL_SECRET_USERNAME",
            "--image-pull-secret-password",
            "IMAGE_PULL_SECRET_PASSWORD",
            "--image-pull-secret-email",
            "IMAGE_PULL_SECRET_EMAIL",
        ],
    )
    assert result.exit_code == 0
