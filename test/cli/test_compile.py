from click.testing import CliRunner
import pytest
from pathlib import Path
from cli.same.same_config import SameConfig
from cli.same.program.commands import compile
from cli.same.program.compile import notebook_processing
import logging
from backends.executor import render as template_render
from backends.executor import deploy

same_config_file_path = "test/testdata/generic_notebook/same.yaml"

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
    ("Code", "test/testdata/sample_notebooks/code.ipynb", 1, 3),
    ("Code Tag", "test/testdata/sample_notebooks/code_tag.ipynb", 2, 2),
    ("Code Tag Code", "test/testdata/sample_notebooks/code_tag_code.ipynb", 2, 2),
    ("Tag", "test/testdata/sample_notebooks/tag.ipynb", 2, 2),
    ("Tag Code", "test/testdata/sample_notebooks/tag_code.ipynb", 1, 1),
    ("Tag Code Tag", "test/testdata/sample_notebooks/tag_code_tag.ipynb", 2, 2),
    ("Tag Code Tag Code", "test/testdata/sample_notebooks/tag_code_tag_code.ipynb", 2, 2),
    ("Tag Tag", "test/testdata/sample_notebooks/tag_tag.ipynb", 2, 2),
    ("Tag Tag Code", "test/testdata/sample_notebooks/tag_tag_code.ipynb", 2, 2),
    ("Code Tag Code Tag Code", "test/testdata/sample_notebooks/code_tag_code_tag_code.ipynb", 3, 3),
    ("Code Code Tag Code Code Tag Code Code", "test/testdata/sample_notebooks/code_code_tag_code_code_tag_code_code.ipynb", 3, 6),
]

# Test Name, String to detect
magic_strings_to_detect = [
    ("Bang pip with no space", "!pip install six"),
    ("Bang pip with space", "! pip install six"),
    ("Bang pip space and version", "! pip install minimal==0.1.0"),
]


@pytest.fixture
def same_config():
    with open(same_config_file_path, "rb") as f:
        return SameConfig(buffered_reader=f)


def test_compile_verb():
    runner = CliRunner()
    result = runner.invoke(compile)

    assert result.exit_code == 2  # From missing file flag
    assert "Invalid value for" in result.output  # Missing file flag error string


def test_same_program_compile_e2e():
    same_file_path = Path(same_config_file_path)
    assert same_file_path.exists()

    same_file_path_as_string = str(same_file_path.absolute())
    runner = CliRunner()
    result = runner.invoke(compile, ["-f", same_file_path_as_string, "-t", "kubeflow"])
    assert result.exit_code == 0


def test_get_notebook_path(same_config):
    assert "sample_notebook.ipynb" in notebook_processing.get_notebook_path(Path(same_config_file_path).parent, same_config)


def test_bad_notebook_path(caplog):
    bad_path_string = "BAD_PATH"
    with pytest.raises(SystemExit) as e:
        with caplog.at_level(logging.FATAL):
            notebook_processing.read_notebook(bad_path_string)
            assert bad_path_string in caplog.text
    assert e.type == SystemExit
    assert e.value.code == 1


@pytest.mark.parametrize("test_name, notebook_path, number_of_steps, number_of_total_cells", test_notebooks, ids=[p[0] for p in test_notebooks])
def test_parse_notebook(test_name, notebook_path, number_of_steps, number_of_total_cells):
    notebook_dict = notebook_processing.read_notebook(notebook_path)
    assert notebook_dict.get("cells", None) is not None
    assert (
        len(notebook_dict["cells"]) == number_of_total_cells
    ), f"{test_name} did not get number of expected cells - expected: {number_of_total_cells}, actual: {len(notebook_dict['cells'])}"

    steps = notebook_processing.get_steps(notebook_dict)
    assert len(steps) == number_of_steps, f"{test_name} did not get number of expected steps - expected: {number_of_steps}, actual: {len(steps)}"


@pytest.mark.parametrize("test_name, error_string", magic_strings_to_detect, ids=[p[0] for p in magic_strings_to_detect])
def test_detect_bad_python_strings(caplog, test_name, error_string):
    notebook_path = "test/testdata/notebook_edge_cases/bad_python_lines.ipynb"
    notebook_dict = notebook_processing.read_notebook(notebook_path)
    with pytest.raises(SyntaxError) as e:
        with caplog.at_level(logging.INFO):
            notebook_processing.get_steps(notebook_dict)
            assert error_string in caplog.text
    assert e.type == SyntaxError


def test_e2e_full_notebook():
    notebook_path = "test/testdata/generic_notebook/sample_notebook.ipynb"
    number_of_steps = 3
    number_of_total_cells = 13
    test_name = "E2E 'sample_notebook'"

    notebook_dict = notebook_processing.read_notebook(notebook_path)
    assert notebook_dict.get("cells", None) is not None
    assert (
        len(notebook_dict["cells"]) == number_of_total_cells
    ), f"{test_name} did not get number of expected cells - expected: {number_of_total_cells}, actual: {len(notebook_dict['cells'])}"

    steps = notebook_processing.get_steps(notebook_dict)
    assert len(steps) == number_of_steps, f"{test_name} did not get number of expected steps - expected: {number_of_steps}, actual: {len(steps)}"

    assert "tensorflow" in steps["same_step_000"].packages_to_install, f"Packages to install expected to contain 'tensorflow'. Actual: {steps['same_step_000'].packages_to_install}"

    # Below tests to make sure the packages for the first step are the same as the last one (because we're doing this globally)
    assert steps["same_step_000"].packages_to_install == steps["same_step_002"].packages_to_install

    # Check to make sure the 'IPython' package has been correctly mapped to 'ipython' (lower case)
    assert "ipython" in steps["same_step_000"].packages_to_install
    assert "IPython" not in steps["same_step_000"].packages_to_install


def test_kubeflow_template(mocker, tmpdir, same_config):
    mocker.patch.object(Path, "write_text")

    notebook_path = "test/testdata/generic_notebook/sample_notebook.ipynb"
    notebook_dict = notebook_processing.read_notebook(notebook_path)
    steps = notebook_processing.get_steps(notebook_dict)
    template_render("kubeflow", steps, same_config, compile_path=tmpdir)

    root_file_content = Path.write_text.call_args_list[0][0][0]

    # Checking that initial imports are there
    assert "import kfp" in root_file_content

    # Checking that root parameters were filled in correctly
    assert "def root(sample_parameter='0.841'" in root_file_content

    # Confirm that dict is ignored
    assert "sample_complicated_parameter" not in root_file_content

    # Confirm that packages have been attached
    assert "'Requests', 'scipy', 'tensorflow'" in root_file_content

    # Confirm that three steps are written (only way we could get this line is if the two previous steps were also written)
    assert "same_step_002_task.after(same_step_001_task)" in root_file_content

    # Confirm that four files were written (root and three steps)
    assert len(Path.write_text.call_args_list) == 4
