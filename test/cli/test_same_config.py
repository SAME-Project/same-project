from sameproject.same_config import SameConfig, SameValidator
from cerberus import SchemaError
import pytest
from pathlib import Path
from ruamel.yaml import YAML
from io import StringIO

from sameproject import helpers

same_config_file_path = "test/testdata/sample_same_configs/good_same.yaml"

# Test name, Same File Path, Valid, Error Phrase
sample_same_file_paths = [
    ("Good SAME Config", "test/testdata/sample_same_configs/good_same.yaml", True, ""),
    ("No API Version", "test/testdata/sample_same_configs/no_apiVersion.yaml", False, "'apiVersion': ['required field']"),
    ("No Default Environment", "test/testdata/sample_same_configs/no_default_for_environments.yaml", False, "environments does not contain"),
]


@pytest.fixture
def same_config():
    with open(same_config_file_path, "rb") as f:
        return SameConfig(buffered_reader=f)


def test_load_same_config_both_set():
    with pytest.raises(ValueError) as e:
        # Setting both values should raise error (values don't matter)
        SameConfig(buffered_reader=StringIO(), content="NON_EMPTY_STRING")

    assert "SameConfig accepts either" in str(e.value)


def test_set_setting_path(caplog, same_config):
    invalid_path = "/INVALID_DIR/INVALID_PATH"
    with pytest.raises(FileNotFoundError) as e:
        same_config.path = invalid_path
    assert invalid_path in str(e.value)

    valid_path = same_config_file_path
    same_config.path = valid_path
    assert valid_path == same_config.path


def test_bad_config_from_file_buffer(caplog):
    _, bad_config_file, _, _ = sample_same_file_paths[2]
    with pytest.raises(SyntaxError) as e:
        with open(bad_config_file, "rb") as f:
            SameConfig(buffered_reader=f)

    assert "environments does not contain a" in str(e.value)


def test_load_same_from_string():
    with pytest.raises(ValueError) as e:
        SameConfig(content="")

    assert "Content is empty." in str(e.value)

    _, bad_config_file, _, _ = sample_same_file_paths[2]

    with pytest.raises(SyntaxError) as e:
        with open(bad_config_file, "rb") as f:
            bad_file_content = "".join(map(bytes.decode, f.readlines()))

        SameConfig(content=bad_file_content)

    assert "environments does not contain a" in str(e.value)


def test_load_same_config():
    same_file_path = Path(same_config_file_path)
    assert same_file_path.exists()

    with open(same_config_file_path, "rb") as f:
        same_config_file_contents = SameConfig(buffered_reader=f)

    assert same_config_file_contents is not None


def test_must_have_default():

    with open(same_config_file_path, "rb") as f:
        good_same_config_file_contents = SameConfig(buffered_reader=f)

    has_default_yaml = """
environments:
    default:
        image_tag: library/python:3.9-slim-buster
    private_environment:
        image_tag: sameprivateregistry.azurecr.io/sample-private-org/sample-private-image:latest
        private_registry: true
"""

    no_default_yaml = """
environments:
    private_environment:
        image_tag: sameprivateregistry.azurecr.io/sample-private-org/sample-private-image:latest
        private_registry: true
"""
    yaml = YAML(typ="safe")
    has_default = yaml.load(has_default_yaml)
    no_default = yaml.load(no_default_yaml)

    has_default_full = {**good_same_config_file_contents.to_dict(), **has_default}
    no_default_full = {**good_same_config_file_contents.to_dict(), **no_default}

    try:
        SameConfig(content=helpers.dict_to_yaml(has_default_full))
    except SyntaxError as e:
        assert False, e

    with pytest.raises(SyntaxError) as e:
        SameConfig(content=helpers.dict_to_yaml(no_default_full))

    assert "environments does not contain a" in str(e.value)


def test_same_config_schema_compiles():
    try:
        v = SameValidator.get_validator()
    except SchemaError as e:
        pytest.fail(f"Schema failed to validate: {e}")

    assert v is not None


@pytest.mark.parametrize("test_name, same_config_file_path, valid, error_phrase", sample_same_file_paths, ids=[p[0] for p in sample_same_file_paths])
def test_load_sample_same_configs(caplog, test_name, same_config_file_path, valid, error_phrase):
    v = SameValidator.get_validator()
    try:
        with open(same_config_file_path, "rb") as f:
            same_config_file_contents = SameConfig(f)  # noqa
        assert valid, print(f"Unable to validate same config: {v.errors}")
    except SyntaxError as e:
        assert not valid, print(f"SameConfig is invalid, but not detected: {str(e.msg)}")
        assert error_phrase in str(e.msg)


def test_e2e_load_same_object(caplog):
    with open(same_config_file_path, "rb") as f:
        same_config_object = SameConfig(f)  # noqa

    assert same_config_object.notebook.path == "sample_notebook.ipynb"
    assert same_config_object.metadata.name == "SampleComplicatedNotebook"
    assert len(same_config_object.datasets.USER_HISTORY.environments) == 3
    assert isinstance(same_config_object.run.parameters, dict)
