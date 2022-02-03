# pylint: disable=protected-access,missing-function-docstring, missing-class-docstring
# pylint: disable=missing-module-docstring, missing-class-docstring
# -*- coding: utf-8 -*-
import sys
print(sys.path)
from pathlib import Path
sys.path.append(Path(__file__).parent.parent.absolute().name)
import sameproject.sdk.same as same
import subprocess
import sys

import pytest
import pytest_virtualenv as venv

import importlib


@pytest.fixture
def init_env(mocker):
    v = venv.VirtualEnv()

    yield v
    v.teardown()


def test_install_package(init_env, mocker):
    mocker.patch("sameproject.sdk.same.helpers.ipy_nb_name", return_value="TEST_NOTEBOOK_NAME")

    reqs = init_env.installed_packages()
    six_package_name = "six"
    assert reqs.get(six_package_name) is None, "Package 'six' is already installed."
    same.import_packages([six_package_name], str(init_env.python))
    reqs = init_env.installed_packages()
    assert (reqs.get(six_package_name) is not None) or (six_package_name in sys.modules), "Package 'six' was not installed."


def test_install_two_packages_output(init_env, mocker):
    mocker.patch("sameproject.sdk.same.helpers.ipy_nb_name", return_value="TEST_NOTEBOOK_NAME")
    reqs = init_env.installed_packages()

    # Need to add virtual env manually because it doesn't play well with importlib - https://stackoverflow.com/questions/36103169/how-to-import-packages-in-virtualenv-in-python-shell
    # Need to capture site packages (_should_ be for testing only)
    venv_site_packages = eval(
        subprocess.check_output(
            [str(init_env.python), "-c", "import site; print(site.getsitepackages());"],
        )
    )

    sys.path.append(venv_site_packages[0])
    importlib.invalidate_caches()

    # Testing two different types of modules - one that's a system module (regex) and one that needs installing from pypi (nose)
    nose_package_name = "nose"
    regex_package_name = "regex"
    assert (reqs.get(nose_package_name) is None) and (nose_package_name not in sys.modules), "Package 'nose' is already installed."

    assert reqs.get(regex_package_name) is None, "Package 'regex' is already installed."

    same.import_packages([nose_package_name, regex_package_name], str(init_env.python))

    reqs = init_env.installed_packages()
    assert (reqs.get(nose_package_name) is not None) or (nose_package_name in sys.modules), "Package 'nose' not installed"
    assert (reqs.get(regex_package_name) is not None) or (regex_package_name in sys.modules), "Package 'regex' not installed"
