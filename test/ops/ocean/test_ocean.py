from sameproject.ops.backends import deploy
import test.testdata
import pytest
import yaml


@pytest.mark.ocean
@test.testdata.notebooks("oceandata")
def test_ocean_deploy(config, notebook, requirements, validation_fn):
    deployment = deploy("ocean", "", "", config)
    assert deployment == b''