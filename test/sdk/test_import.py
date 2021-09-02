# pylint: disable=protected-access,missing-function-docstring, missing-class-docstring
# pylint: disable=missing-module-docstring, missing-class-docstring
# -*- coding: utf-8 -*-
import unittest
from pathlib import Path
import mock
import sdk.same as same
import subprocess
import sys

import pytest
import pytest_virtualenv as venv
import shutil

from distutils.dir_util import copy_tree


@pytest.fixture
def init_env():
    v = venv.VirtualEnv()
    yield v
    v.teardown()


def test_install_package(init_env):
    reqs = init_env.installed_packages()
    six_package_name = "six"
    assert reqs.get(six_package_name) is None, "Package 'six' is already installed."
    same.import_packages([six_package_name], str(init_env.python))
    reqs = init_env.installed_packages()
    assert (reqs.get(six_package_name) is not None) or (
        six_package_name in sys.modules
    ), "Package 'six' was not installed."


def test_install_two_packages_output(init_env):
    reqs = init_env.installed_packages()

    # Testing two different types of modules - one that's a system module (regex) and one that needs installing from pypi (minimal)
    urllib3_package_name = "urllib3"
    regex_package_name = "regex"
    assert (reqs.get(urllib3_package_name) is None) and (
        urllib3_package_name not in sys.modules
    ), "Package 'urllib3' is already installed."

    assert reqs.get(regex_package_name) is None, "Package 'regex' is already installed."

    same.import_packages(
        [urllib3_package_name, regex_package_name], str(init_env.python)
    )

    reqs = init_env.installed_packages()
    assert (reqs.get(urllib3_package_name) is not None) or (
        urllib3_package_name in sys.modules
    ), "Package 'urllib3' not installed"
    assert (reqs.get(regex_package_name) is not None) or (
        regex_package_name in sys.modules
    ), "Package 'regex' not installed"
