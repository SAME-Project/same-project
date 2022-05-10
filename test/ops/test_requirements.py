from sameproject.ops.requirements import get_package_info, render_package_info
import pytest


def test_get_package_info():
    modules = ["does-not-exist", "tensorflow", "numpy", "pytorch", "Globals"]
    pkg_info = get_package_info(modules)

    assert len(pkg_info) > 0
    for pkg in pkg_info.keys():
        assert "version" in pkg_info[pkg]
        assert pkg_info[pkg].version != ""

    # Should not return info for non-existing package.
    assert "does-not-exist" not in pkg_info

    # Should recognise "Globals" as coming from "Zope2".
    assert pkg_info.Globals.name == "Zope2"


def test_render_package_info():
    modules = ["tensorflow", "numpy", "Globals"]
    pkg_info = get_package_info(modules)
    req = render_package_info(pkg_info)

    assert req != ""
    assert "tensorflow==" in req
    assert "numpy==" in req
    assert "Zope2==" in req
