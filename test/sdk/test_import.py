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


@pytest.fixture(scope="session")
def init_env():
    v = venv.VirtualEnv()
    yield v
    shutil.rmtree(v.workspace)


def test_placeholder(init_env):
    """Obvious placeholder, remove when tests actually work"""
    assert True is True


# def test_install_package(init_env):
#     reqs = init_env.installed_packages()
#     minimum_package_name = "minimal"
#     assert (
#         reqs.get(minimum_package_name) is None
#     ), "Package 'minimal' is already installed."
#     same.import_packages([minimum_package_name], str(init_env.python))
#     reqs = init_env.installed_packages()
#     assert (
#         reqs.get(minimum_package_name) is not None
#     ), "Package 'minimal' was not installed."


# def test_install_two_packages_output(init_env):
#     reqs = init_env.installed_packages()
#     minimum_package_name = "minimal"
#     assert (
#         reqs.get(minimum_package_name) is None
#     ), "Package 'minimal' is already installed."

#     reqs = init_env.installed_packages()
#     assert (
#         reqs.get(minimum_package_name) is not None
#     ), "Package 'minimal' was not installed."
#     assert reqs.get("regex") is None, "Package 'regex' not installed"
#     same.import_packages([minimum_package_name, "regex"], str(init_env.python))
