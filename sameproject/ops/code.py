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


def get_installable_packages(code: str) -> List[str]:
    """
    Parses a block of python code for import statements that require the
    installation of a package from PyPI.
    """

    # Parse fully-qualified module names from every import statement.
    raw_imports = set()
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for subnode in node.names:
                    raw_imports.add(subnode.name)
            elif isinstance(node, ast.ImportFrom):
                raw_imports.add(node.module)
    except Exception as err:
        logging.error("Failed to parse import statements in code block.")
        raise err

    # Parse the base module for each import, i.e. "pkg.thing" -> "pkg".
    base_imports = set()
    for name in [n for n in raw_imports if n]:
        base, _, _ = name.partition(".")
        base_imports.add(base)

    stdlib = {x.strip() for x in stdlibs.splitlines()}
    installable_imports = list(base_imports - stdlib)

    # Sorted for determinism.
    return sorted(
        map(get_pypi_name, installable_imports),
        key=lambda x: x.lower(),
    )


def get_pypi_name(pkg: str) -> str:
    """Returns the name of the PyPI package containing the given module."""
    return pypi_mapping.get(pkg, pkg)
