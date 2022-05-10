from sameproject.ops.backends import render as template_render
from sameproject.ops import notebooks
from sameproject.ops.backends import deploy
from sameproject.data.config import SameConfig
from click.testing import CliRunner
from sameproject.cli import run
from pathlib import Path
import logging
import pytest

same_config_file_path = Path("test/ops/testdata/same_notebooks/generic/same.yaml")

# Permutations of notebooks
# | Code | Tag | Code | Tag | Code |
# |------|-----|------|-----|------|
# | X    | 0   | 0    | 0   | 0    |
# | X    | X   | 0    | 0   | 0    |
# | X    | X   | X    | 0   | 0    |
# | 0    | X   | 0    | 0   | 0    |
# | 0    | X   | X    | 0   | 0    |
# | 0    | X   | X    | X   | 0    |
# | 0    | X   | X    | X   | X    |
# | 0    | X   | 0    | X   | 0    |
# | 0    | X   | 0    | X   | X    |
# | X    | X   | X    | X   | X    |
# Test Name, Notebook Path, number of steps, number of total cells
test_notebooks = [
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

# Test Name, String to detect
magic_strings_to_detect = [
    ("Bang pip with no space", "!pip install six"),
    ("Bang pip with space", "! pip install six"),
    ("Bang pip space and version", "! pip install minimal==0.1.0"),
]


@pytest.fixture
def same_config():
    with same_config_file_path.open("r") as file:
        return SameConfig.from_yaml(file.read()).resolve(same_config_file_path.parent)


def test_same_program_compile_e2e():
    same_file_path = Path(same_config_file_path)
    assert same_file_path.exists()

    same_file_path_as_string = str(same_file_path.absolute())
    runner = CliRunner()
    result = runner.invoke(run, ["-f", same_file_path_as_string, "-t", "kubeflow", "-t", "kubeflow", "--persist-temp-files", "--no-deploy"])
    assert result.exit_code == 0


def test_bad_notebook_path(caplog):
    bad_path_string = "BAD_PATH"
    with pytest.raises(SystemExit) as e:
        with caplog.at_level(logging.FATAL):
            notebooks.read_notebook(bad_path_string)
            assert bad_path_string in caplog.text
    assert e.type == SystemExit
    assert e.value.code == 1


@pytest.mark.parametrize("test_name, notebook_path, number_of_steps, number_of_total_cells", test_notebooks, ids=[p[0] for p in test_notebooks])
def test_parse_notebook(same_config, test_name, notebook_path, number_of_steps, number_of_total_cells):
    notebook_dict = notebooks.read_notebook(notebook_path)
    assert notebook_dict.get("cells", None) is not None
    assert (
        len(notebook_dict["cells"]) == number_of_total_cells
    ), f"{test_name} did not get number of expected cells - expected: {number_of_total_cells}, actual: {len(notebook_dict['cells'])}"

    steps = notebooks.get_steps(notebook_dict, same_config)
    assert len(steps) == number_of_steps, f"{test_name} did not get number of expected steps - expected: {number_of_steps}, actual: {len(steps)}"


@pytest.mark.parametrize("test_name, error_string", magic_strings_to_detect, ids=[p[0] for p in magic_strings_to_detect])
def test_detect_bad_python_strings(same_config, caplog, test_name, error_string):
    notebook_path = "test/ops/testdata/edgecase_notebooks/bad_python_lines.ipynb"
    notebook_dict = notebooks.read_notebook(notebook_path)
    with pytest.raises(SyntaxError) as e:
        with caplog.at_level(logging.INFO):
            notebooks.get_steps(notebook_dict, same_config)
            assert error_string in caplog.text
    assert e.type == SyntaxError


def test_e2e_full_notebook(same_config):
    notebook_path = "test/ops/testdata/same_notebooks/generic/sample_notebook.ipynb"
    number_of_steps = 3
    number_of_total_cells = 13
    test_name = "E2E 'sample_notebook'"

    notebook_dict = notebooks.read_notebook(notebook_path)
    assert notebook_dict.get("cells", None) is not None
    assert (
        len(notebook_dict["cells"]) == number_of_total_cells
    ), f"{test_name} did not get number of expected cells - expected: {number_of_total_cells}, actual: {len(notebook_dict['cells'])}"

    steps = notebooks.get_steps(notebook_dict, same_config)
    assert len(steps) == number_of_steps, f"{test_name} did not get number of expected steps - expected: {number_of_steps}, actual: {len(steps)}"

    assert "tensorflow" in steps["same_step_000"].packages_to_install, f"Packages to install expected to contain 'tensorflow'. Actual: {steps['same_step_000'].packages_to_install}"

    # Below tests to make sure the packages for the first step are the same as the last one (because we're doing this globally)
    assert steps["same_step_000"].packages_to_install == steps["same_step_002"].packages_to_install

    # Check to make sure the 'IPython' package has been correctly mapped to 'ipython' (lower case)
    assert "ipython" in steps["same_step_000"].packages_to_install
    assert "IPython" not in steps["same_step_000"].packages_to_install
