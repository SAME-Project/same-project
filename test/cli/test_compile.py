from click.testing import CliRunner
import pytest
from pathlib import Path
import cli.same.helpers as helpers
from cli.same.program.commands import compile
from cli.same.program.compile import notebook_processing
import logging
from test.cli.testdata.fake_notebooks_in_python import py_zero_steps, py_zero_steps_with_params, py_one_step, py_one_step_with_cache

same_config_file_path = "test/cli/testdata/generic_notebook/same.yaml"
# Notebook Name, Notebook Text, Found Slices, Resulting Steps
test_converted_notebooks = [
    ("Zero Step Notebook", py_zero_steps, 0, 1),
    ("Zero Step Notebook With Params", py_zero_steps_with_params, 0, 1),
    ("One Step Notebook", py_one_step, 2, 2),
    ("One Step Notebook With Params", py_one_step_with_cache, 3, 4),
]

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
    ("Code", "test/cli/testdata/sample_notebooks/code.ipynb", 1, 3),
    ("Code Tag", "test/cli/testdata/sample_notebooks/code_tag.ipynb", 2, 2),
    ("Code Tag Code", "test/cli/testdata/sample_notebooks/code_tag_code.ipynb", 2, 2),
    ("Tag", "test/cli/testdata/sample_notebooks/tag.ipynb", 2, 2),
    ("Tag Code", "test/cli/testdata/sample_notebooks/tag_code.ipynb", 1, 1),
    ("Tag Code Tag", "test/cli/testdata/sample_notebooks/tag_code_tag.ipynb", 2, 2),
    ("Tag Code Tag Code", "test/cli/testdata/sample_notebooks/tag_code_tag_code.ipynb", 2, 2),
    ("Tag Tag", "test/cli/testdata/sample_notebooks/tag_tag.ipynb", 2, 2),
    ("Tag Tag Code", "test/cli/testdata/sample_notebooks/tag_tag_code.ipynb", 2, 2),
    ("Code Tag Code Tag Code", "test/cli/testdata/sample_notebooks/code_tag_code_tag_code.ipynb", 3, 3),
    ("Code Code Tag Code Code Tag Code Code", "test/cli/testdata/sample_notebooks/code_code_tag_code_code_tag_code_code.ipynb", 3, 6),
]


@pytest.fixture
def same_config():
    with open(same_config_file_path, "rb") as f:
        return helpers.load_same_config_file(f)


def test_compile_verb():
    # just testing that we can test the compile verb

    same_file_path = Path(same_config_file_path)
    assert same_file_path.exists()

    same_file_path_as_string = str(same_file_path.absolute())
    runner = CliRunner()
    result = runner.invoke(
        compile,
        ["-f", same_file_path_as_string],
    )
    assert result.exit_code == 0


def test_get_pipeline_path(same_config):
    assert "sample_notebook.ipynb" in notebook_processing.get_pipeline_path(Path(same_config_file_path).parent, same_config)


def test_bad_notebook_path(caplog):
    bad_path_string = "BAD_PATH"
    with pytest.raises(SystemExit) as e:
        with caplog.at_level(logging.FATAL):
            notebook_processing.convert_notebook_to_text(bad_path_string)
            assert bad_path_string in caplog.text
    assert e.type == SystemExit
    assert e.value.code == 1


def test_read_notebook_as_string(caplog, same_config):
    notebook_path = notebook_processing.get_pipeline_path(Path(same_config_file_path).parent, same_config)
    notebook_as_py = ""
    with caplog.at_level(logging.FATAL):
        notebook_as_py = notebook_processing.convert_notebook_to_text(notebook_path)
        assert caplog.text == ""

    assert "jupytext:\n#     text_representation:\n#       extension: .py\n#       format_name: percent" in notebook_as_py


@pytest.mark.parametrize("test_name, notebook_path, number_of_steps, number_of_total_cells", test_notebooks, ids=[p[0] for p in test_notebooks])
def test_parse_notebook(test_name, notebook_path, number_of_steps, number_of_total_cells):
    notebook_dict = notebook_processing.read_notebook(notebook_path)
    assert notebook_dict.get("cells", None) is not None
    assert (
        len(notebook_dict["cells"]) == number_of_total_cells
    ), f"{test_name} did not get number of expected cells - expected: {number_of_total_cells}, actual: {len(notebook_dict['cells'])}"

    steps = notebook_processing.get_steps(notebook_dict)
    assert len(steps) == number_of_steps, f"{test_name} did not get number of expected steps - expected: {number_of_steps}, actual: {len(steps)}"


# @pytest.mark.parametrize("test_name, notebook_text, expected_slices, expected_steps", test_converted_notebooks, ids=[p[0] for p in test_converted_notebooks])
# def test_find_steps_in_notebook(test_name, notebook_text, expected_slices, expected_steps):
#     found_steps = notebook_processing.find_all_steps(notebook_text)
#     assert len(found_steps) == expected_steps, f"{test_name} did not match - expected: {expected_steps}, actual: {len(found_steps)}"


# @pytest.mark.parametrize("test_name, notebook_text, expected_slices, expected_steps", test_converted_notebooks, ids=[p[0] for p in test_converted_notebooks])
# def test_parse_notebooks(test_name, notebook_text, expected_slices, expected_steps):
#     foundSteps = []
#     with does_not_raise() as e:
#         foundSteps = notebook_processing.find_all_steps(notebook_text)

#     assert len(foundSteps) == expected_steps, f"Expected: {expected_steps} steps. Actual steps: {len(foundSteps)}"
#     assert e is None, f"Unexpected error: {str(e)}"

#     # codeBlocks, err := c.CombineCodeSlicesToSteps(foundSteps)
#     # assert.Equal(T, len(codeBlocks), expectedNumberCombined, "%v did not result in %v code slices. Actual code slices: %v", testStringName, expectedNumberCombined, len(codeBlocks))
#     # assert.NoError(T, err, "%v resulted in an error building code blocks: %v", testStringName, err)
#     # assert False


# func (suite *ProgramCompileSuite) Test_ParseOneStep() {
# 	testStep(suite.T(), 4, 2, ONE_STEP, "ONE_STEP")
# }

# func (suite *ProgramCompileSuite) Test_ParseOneStepWithCache() {
# 	testStep(suite.T(), 4, 2, ONE_STEP_WITH_CACHE, "ONE_STEP_WITH_CACHE")
# }

# func (suite *ProgramCompileSuite) Test_ParseTwoSteps() {
# 	testStep(suite.T(), 6, 3, TWO_STEPS, "TWO_STEPS")
# }

# func (suite *ProgramCompileSuite) Test_ParseTwoStepsCombine() {
# 	testStep(suite.T(), 8, 3, TWO_STEPS_COMBINE, "TWO_STEPS_COMBINE")
# }

# func (suite *ProgramCompileSuite) Test_ParseTwoStepsCombineNoParams() {
# 	testStep(suite.T(), 6, 3, TWO_STEPS_COMBINE_NO_PARAMS, "TWO_STEPS_COMBINE_NO_PARAMS")
# }

# func (suite *ProgramCompileSuite) Test_SettingCacheValue_NoCache() {
# 	os.Setenv("TEST_PASS", "1")
# 	c := utils.GetCompileFunctions()

# 	foundSteps, _ := c.FindAllSteps(ONE_STEP)
# 	codeBlocks, _ := c.CombineCodeSlicesToSteps(foundSteps)
# 	cb := codeBlocks["same_step_1"]
# 	assert.Equal(suite.T(), cb.CacheValue, "P0D", "Expected to set a missing cache value to P0D. Actual: %v", cb.CacheValue)

# }

# func (suite *ProgramCompileSuite) Test_SettingCacheValue_WithCache() {
# 	os.Setenv("TEST_PASS", "1")
# 	c := utils.GetCompileFunctions()

# 	foundSteps, _ := c.FindAllSteps(ONE_STEP_WITH_CACHE)
# 	codeBlocks, _ := c.CombineCodeSlicesToSteps(foundSteps)
# 	cb := codeBlocks["same_step_1"]
# 	assert.Equal(suite.T(), cb.CacheValue, "P20D", "Expected to set a missing cache value to P20D. Actual: %v", cb.CacheValue)

# }

# func (suite *ProgramCompileSuite) Test_ImportsWorkingProperly() {
# 	os.Setenv("TEST_PASS", "1")
# 	c := utils.GetCompileFunctions()

# 	foundSteps, _ := c.FindAllSteps(NOTEBOOKS_WITH_IMPORT)
# 	codeBlocks, _ := c.CombineCodeSlicesToSteps(foundSteps)
# 	packagesToMerge, _ := c.WriteStepFiles("kubeflow", suite.tmpDirectory, codeBlocks)
# 	containsKey := ""
# 	for key := range packagesToMerge["same_step_0"] {
# 		containsKey += key
# 	}
# 	assert.Contains(suite.T(), containsKey, "tensorflow", "Expected to contain 'tensorflow'. Actual: %v", packagesToMerge["same_step_0"])
# }

# func (suite *ProgramCompileSuite) Test_FullNotebookExperience() {
# 	os.Setenv("TEST_PASS", "1")
# 	c := utils.GetCompileFunctions()
# 	jupytextExecutable, err := exec.LookPath("jupytext")
# 	if err != nil {
# 		assert.Fail(suite.T(), "Jupytext not installed")
# 	}

# 	notebookPath := "../testdata/notebook/sample_notebook.ipynb"
# 	if _, exists := os.Stat(notebookPath); exists != nil {
# 		assert.Fail(suite.T(), "Notebook not found at: %v", notebookPath)
# 	}
# 	convertedText, _ := c.ConvertNotebook(jupytextExecutable, notebookPath)
# 	foundSteps, _ := c.FindAllSteps(convertedText)
# 	codeBlocks, _ := c.CombineCodeSlicesToSteps(foundSteps)
# 	packagesToMerge, _ := c.WriteStepFiles("kubeflow", suite.tmpDirectory, codeBlocks)
# 	containsKey := ""
# 	for key := range packagesToMerge["same_step_0"] {
# 		containsKey += key
# 	}
# 	assert.Contains(suite.T(), containsKey, "tensorflow", "Expected to contain 'tensorflow'. Actual: %v", packagesToMerge["same_step_0"])
# }
