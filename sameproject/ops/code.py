from pipreqs.pipreqs import get_all_imports
from sameproject.mapping import mapping
from sameproject.stdlib import stdlibs
from tempfile import mkdtemp
from pathlib import Path
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


def remove_magic_lines(code: str) -> str:
    """Removes all magic lines from the given python source code."""
    res = []

    # Parse out all non-magic lines in the cell:
    parser = jupytext.magics.StringParser("python")
    for i, line in enumerate(code.split("\n")):
        is_magic = not parser.is_quoted() and jupytext.magics.is_magic(line, "python")

        parser.read_line(line)
        if not is_magic:
            res.append(line)

    return "\n".join(res)


def get_imported_modules(code: str) -> List[str]:
    """Returns a list of all non-standard imports in the given code."""
    code_dir = Path(mkdtemp())
    with (code_dir / "code.py").open("w") as writer:
        writer.write(code)

    return get_all_imports(code_dir)


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
