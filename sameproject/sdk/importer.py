from johnnydep.lib import JohnnyDist
from .conda_env import CondaEnv
from typing import Tuple
from pathlib import Path
import pkg_resources
import sameproject
import subprocess
import importlib
import logging
import sys

default_conda = """
name: NULL_NAME
dependencies:
  - NULL_PACKAGE
"""


def import_packages(packages_to_import, update_conda_env=False, conda_env_path="environment.yml", python_executable=None):
    if python_executable is None:
        python_executable = sys.executable

    if isinstance(packages_to_import, str):
        packages_to_import = [packages_to_import]

    new_packages, already_installed_packages = get_packages_to_install(packages_to_import)

    already_installed_list = build_already_installed_package_notice(already_installed_packages)

    new_packages_list = build_new_packages_notice(python_executable, new_packages)

    for package in already_installed_list + new_packages_list:
        package_name = ""
        try:
            package_name, package_version = package.split("==")
        except ValueError:
            # not enough values
            package_name, package_version = package, ""  # noqa F841 - package version unused
        importlib.import_module(package_name)

    if update_conda_env:
        _update_conda_env(conda_env_path)


def build_new_packages_notice(python_executable, new_packages) -> list:
    new_packages_list = []
    for package_name, package_version in new_packages.items():
        new_package_string = ""
        if package_version != "":
            new_package_string = f"{package_name}=={package_version}"
        else:
            new_package_string = f"{package_name}"
        _install_package(python_executable, new_package_string)
        new_packages_list.append(new_package_string)

    if len(new_packages_list) > 0:
        print("Packages installed: %v", ", ".join(new_packages_list))

    return new_packages_list


def build_already_installed_package_notice(already_installed_packages) -> list:
    already_installed_list = []

    for package_name, package_version in already_installed_packages.items():
        if package_version != "":
            already_installed_list.append(f"{package_name}=={package_version}")
        else:
            already_installed_list.append(f"{package_name}")

    print(f'Packages skipped because they are already installed: {", ".join(already_installed_list)}')

    return already_installed_list


def get_packages_to_install(packages_to_import) -> Tuple[dict, dict]:
    new_packages = {}
    already_installed_packages = {}

    for package in packages_to_import:
        try:
            package_name, package_version = package.split("==")
        except ValueError:
            # not enough values
            package_name, package_version = package, ""

        installed_package_dist = JohnnyDist(package_name)
        if package_version == "":
            if installed_package_dist.version_latest == installed_package_dist.version_installed:
                already_installed_packages[package_name] = installed_package_dist.version_latest
            else:
                new_packages[package_name] = installed_package_dist.version_latest

    return (new_packages, already_installed_packages)


def _install_package(python_executable, package):
    subprocess.check_call(
        [python_executable, "-m", "pip", "install", package],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )


def _update_conda_env(file_path):
    try:
        with open(file_path, "rb") as f:
            conda_env = CondaEnv(buffered_reader=f)
    except FileNotFoundError:
        conda_env_path = "environment.yaml"
        conda_env_path_object = Path(conda_env_path).absolute
        logging.info(f"No file found at '{conda_env_path_object}', creating one.")
        conda_env = CondaEnv(content=default_conda)
        conda_env.name = sameproject.sdk.helpers.ipy_nb_name()
        conda_env.dependencies = []

    conda_dependencies = {}
    for dependency_line in conda_env.dependencies:
        package_name = dependency_line.split(r"=+")
        conda_dependencies[package_name] = dependency_line

    installed_packages = pkg_resources.working_set
    installed_packages_list = ["%s=%s" % (i.key, i.version) for i in installed_packages]

    for package in installed_packages_list:
        print(package)

    # # This is pretty hacky, but not sure what to do in the alternative.
    # # The problem is that I want there to be a same.yaml file if we write a conda file
    # # But since this is the SDK, it shouldn't (?) be necessary to have one (yet).
    # # So commenting out... for now.
    # # try:
    # #     same_config_file_path = Path("same.yaml")
    # #     if not same_config_file_path.exists():
    # #         raise FileNotFoundError()

    # #     with open(same_config_file_path.absolute, "rb") as f:
    # #         same_config = SameConfig(buffered_reader=f)
    # # except FileNotFoundError:
    # #     logging.fatal("No SAME file found at 'same.yaml', please create one.")
