import subprocess
import sys
from johnnydep.lib import JohnnyDist


def import_packages(packages_to_import, python_executable=None):
    if python_executable is None:
        python_executable = sys.executable
    pip_list_proc = subprocess.run(
        [
            python_executable,
            "-m",
            "pip",
            "list",
            "--format=freeze",
            "--disable-pip-version-check",
        ],
        capture_output=True,
    )
    installed_packages_blob = pip_list_proc.stdout
    all_installed_packages = {}
    for installed_package in installed_packages_blob.split():
        try:
            package_name, package_version = installed_package.decode("ascii").split(
                "=="
            )
        except ValueError:
            # not enough values
            package_name, package_version = installed_package.decode("ascii"), None
        all_installed_packages[package_name] = package_version

    new_packages = {}
    already_installed_packages = {}
    for package in packages_to_import:
        try:
            package_name, package_version = package.split("==")
        except ValueError:
            # not enough values
            package_name, package_version = package, ""

        # minimal
        # - package name, if version is '', then get the latest version and compare what's already installed. Results in:
        # -- skip installing
        # -- or install
        # minimal=='0.1.0'
        # - package name and version - hand the whole thing to pip to figure out
        # minimal=='0.1.8'
        # - package name and version with a package that doesn't exist

        installed_package_dist = JohnnyDist(package_name)
        if package_version == "":
            if (
                installed_package_dist.version_latest
                == installed_package_dist.version_installed
            ):
                already_installed_packages[
                    package_name
                ] = installed_package_dist.version_latest
            else:
                new_packages[package_name] = installed_package_dist.version_latest

    already_installed_string = ""
    already_installed_list = []

    for package_name, package_version in already_installed_packages.items():
        if package_version != "":
            already_installed_list.append(f"{package_name}=={package_version}")
        else:
            already_installed_list.append(f"{package_name}")

    already_installed_string = ", ".join(already_installed_list)

    if already_installed_string != "":
        print(
            f"Packages skipped because they are already installed: {already_installed_string}"
        )

    new_packages_string = ""
    for package_name, package_version in new_packages.items():
        new_packages_list = []
        if package_version != "":
            new_packages_list.append(f"{package_name}=={package_version}")
        else:
            new_packages_list.append(f"{package_name}")

    new_packages_string = ", ".join(new_packages_list)

    if new_packages_string != "":
        print(f"Packages installed: {new_packages_string}")


def _install_package(python_executable, package):
    subprocess.check_call(
        [python_executable, "-m", "pip", "install", package],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )


class Importer:
    def __init__(self):
        pass
