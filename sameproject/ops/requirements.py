from pipreqs.pipreqs import get_pkg_names, get_import_local, get_imports_info
from box import Box


def get_package_info(modules):
    """Looks up package information from PyPI for each of the given modules."""
    pkg_names = get_pkg_names(modules)

    imports_info = {}
    for im in get_imports_info(pkg_names):
        imports_info[im["name"]] = im

    pkg_info = {}
    for pkg, mod in zip(pkg_names, modules):
        if pkg in imports_info and "version" in imports_info[pkg]:
            pkg_info[mod] = Box(imports_info[pkg])
    return Box(pkg_info)


def render_package_info(pkg_info):
    """Renders package info as a requirements.txt file."""
    return "\n".join([f"{pkg.name}=={pkg.version}" for pkg in pkg_info.values()])
