from sameproject.ops.notebooks import read_notebook, get_steps, get_code
from sameproject.ops.code import get_imported_modules
from sameproject.data.config import SameConfig
from pathlib import Path
import test.testdata
import logging
import logging
import pytest


config_path = Path("test/ops/testdata/same_notebooks/generic/same.yaml")
notebook_path = Path("test/ops/testdata/same_notebooks/generic/sample_notebook.ipynb")
requirements_path = Path("test/ops/testdata/same_notebooks/generic/requirements.txt")

tagged_notebooks = [
    ("Code", "test/ops/testdata/tagged_notebooks/code.ipynb", 1, 3),
    ("Code Tag", "test/ops/testdata/tagged_notebooks/code_tag.ipynb", 2, 2),
    ("Code Tag Code", "test/ops/testdata/tagged_notebooks/code_tag_code.ipynb", 2, 2),
    ("Tag", "test/ops/testdata/tagged_notebooks/tag.ipynb", 2, 2),
    ("Tag Code", "test/ops/testdata/tagged_notebooks/tag_code.ipynb", 1, 1),
    ("Tag Code Tag", "test/ops/testdata/tagged_notebooks/tag_code_tag.ipynb", 2, 2),
    ("Tag Code Tag Code", "test/ops/testdata/tagged_notebooks/tag_code_tag_code.ipynb", 2, 2),
    ("Tag Tag", "test/ops/testdata/tagged_notebooks/tag_tag.ipynb", 2, 2),
    ("Tag Tag Code", "test/ops/testdata/tagged_notebooks/tag_tag_code.ipynb", 2, 2),
    ("Code Tag Code Tag Code", "test/ops/testdata/tagged_notebooks/code_tag_code_tag_code.ipynb", 3, 3),
    ("Code Code Tag Code Code Tag Code Code", "test/ops/testdata/tagged_notebooks/code_code_tag_code_code_tag_code_code.ipynb", 3, 6),
]

magic_line_testcases = [
    ("bad_python_lines", "test/ops/testdata/edgecase_notebooks/bad_python_lines.ipynb", True),
    ("multiline_strings", "test/ops/testdata/edgecase_notebooks/multiline_strings.ipynb", False),
]


@pytest.fixture
def config():
    with config_path.open("r") as file:
        return SameConfig.from_yaml(file.read()).resolve(config_path.parent)


@pytest.fixture
def notebook():
    return read_notebook(notebook_path)


@pytest.fixture
def requirements():
    with requirements_path.open("r") as file:
        return file.read()


def test_notebooks_inject_requirements(config, notebook, requirements):
    steps = get_steps(notebook, config)
    for name in steps:
        assert "requirements_file" in steps[name]
        assert steps[name].requirements_file == requirements


def test_notebooks_get_code(notebook):
    code = get_code(notebook)

    # Code should not break when parsed:
    modules = get_imported_modules(code)
    assert len(modules) > 0


def test_read_notebooks_nonexistent():
    with pytest.raises(SystemExit):
        read_notebook("BAD_PATH")


@test.testdata.notebooks("tagged")
def test_read_notebooks_tagged(
    config,
    notebook,
    requirements,
    validation_fn,
):
    assert "cells" in notebook
    steps = get_steps(notebook, config)

    assert validation_fn({
        "cells": len(notebook["cells"]),
        "steps": len(steps),
    })


@pytest.mark.parametrize("name, path, expect_err", magic_line_testcases)
def test_read_notebooks_magic_lines(name, path, expect_err, config):
    """
    Tests magic line parsing in notebooks, with edge-cases like
    multiline strings containing what appear to be multiline strings.
    """
    notebook_dict = read_notebook(path)

    if expect_err:
        with pytest.raises(SyntaxError):
            assert get_steps(notebook_dict, config)
    else:
        assert get_steps(notebook_dict, config)
