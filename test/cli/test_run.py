from click.testing import CliRunner
import pytest
from pathlib import Path
from sameproject.same_config import SameConfig
from sameproject.program.commands import run
from sameproject.program.compile import notebook_processing
import sameproject.helpers
import logging
from sameproject.backends.executor import render as template_render
from sameproject.backends.executor import deploy

import tempfile
import dotenv

same_config_file_path = "test/testdata/generic_notebook/same.yaml"


@pytest.fixture
def same_config():
    with open(same_config_file_path, "rb") as f:
        return SameConfig(buffered_reader=f)


@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    """Fixture to execute asserts before and after a test is run"""
    import sys

    # We need to do this fixture because the pipeline modifies sys.modules (through imports) and therefore we need to clear it before/after each test.
    # This is unlikely to be a problem when actually running.
    original_sys_modules = sys.modules.copy()

    yield

    sys.modules.clear()
    sys.modules.update(original_sys_modules)

@pytest.mark.skip("Skipping until we mock or create a live Kubeflow cluster")
def test_live_test_kubeflow(mocker, tmpdir, same_config):
    temp_dir_mock = mocker.patch.object(tempfile, "mkdtemp")
    temp_dir_mock.return_value = tmpdir

    mocker.patch.object(sameproject.helpers, "recursively_remove_dir")

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

@pytest.mark.skip("Skipping until we mock or create AML account")
def test_live_test_aml(mocker, tmpdir, same_config):
    temp_dir_mock = mocker.patch.object(tempfile, "mkdtemp")
    temp_dir_mock.return_value = tmpdir

    mocker.patch.object(sameproject.helpers, "recursively_remove_dir")

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

@pytest.mark.skip("Skipping until we mock or create a live Kubeflow cluster")
def test_kubeflow_same_program_run_with_secrets_e2e():
    multi_env_same_config_file_path = "test/testdata/multienv_notebook/same.yaml"
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

    multi_env_same_config_file_path = "test/testdata/multienv_notebook/same.yaml"
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
