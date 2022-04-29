from sameproject.mapping import mapping
from sameproject.stdlib import stdlibs
from typing import List
import traceback
import jupytext
import logging
import ast


# Mapping of module names to the names of the PyPI package containing them.
pypi_mapping = dict(
    x.strip().split(":") for x in [s for s in mapping.splitlines() if s]
)


def get_magic_lines(code: str) -> List[str]:
    """Parses a block of python code for Jupyter notebook magic lines."""

    magic_lines = []
    parser = jupytext.magics.StringParser("python")
    for i, line in enumerate(code.split("\n")):
        if not parser.is_quoted() and jupytext.magics.is_magic(line, "python"):
            magic_lines.append(f"line {i}: {line}")
        parser.read_line(line)

    return magic_lines


def get_imported_modules(code: str) -> List[str]:
    """Returns a list of all imported modules in the given code."""
    raw_imports = set()
    for node in ast.walk(ast.parse(code)):
        if isinstance(node, ast.Import):
            for subnode in node.names:
                raw_imports.add(subnode.name)
        elif isinstance(node, ast.ImportFrom):
            raw_imports.add(node.module)
    raw_imports = [expr for expr in raw_imports if expr]  # remove any None

    # Parse the base module for each import, i.e. "pkg.thing" -> "pkg".
    base_modules = set()
    for expr in raw_imports:
        base, _, _ = expr.partition(".")
        base_modules.add(base)

    return list(base_modules)


def get_installable_packages(code: str) -> List[str]:
    """
    Parses a block of python code for import statements that require the
    installation of a package from PyPI.
    """
    base_modules = set(get_imported_modules(code))
    stdlib = {x.strip() for x in stdlibs.splitlines()}
    installable_imports = list(base_modules - stdlib)

    # Sorted for determinism.
    return sorted(
        map(get_pypi_name, installable_imports),
        key=lambda x: x.lower(),
    )


def get_pypi_name(pkg: str) -> str:
    """Returns the name of the PyPI package containing the given module."""
    return pypi_mapping.get(pkg, pkg)
