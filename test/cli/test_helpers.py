from cli.same.same_config import schema, SAMEValidator
from cerberus import SchemaError, DocumentError
from cli.same import helpers
import pytest
from pathlib import Path
from ruamel.yaml import YAML

same_config_file_path = "test/cli/testdata/generic_notebook/same.yaml"


def test_load_same_config():
    # just testing that we can test the compile verb

    same_file_path = Path(same_config_file_path)
    assert same_file_path.exists()

    with open(same_config_file_path, "rb") as f:
        same_config_file_contents = helpers.load_same_config_file(f)

    assert same_config_file_contents != ""


def test_must_have_default():
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

    v = SAMEValidator()
    assert v._check_with_must_have_default("environments", has_default, DocumentError) is None
    assert isinstance(v._check_with_must_have_default("environments", no_default, DocumentError), DocumentError)


def test_same_config_schema_compiles():
    try:
        v = SAMEValidator(schema)
    except SchemaError as e:
        pytest.fail(f"Schema failed to validate: {e}")

    assert v is not None
