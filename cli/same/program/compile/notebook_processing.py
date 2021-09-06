import logging
from pathlib import Path
import jupytext
from typing import List
import re


def get_pipeline_path(same_config_path, same_config_file_contents) -> str:
    """Returns absolute value of the pipeline path relative to current file execution"""
    return str(Path.joinpath(Path(same_config_path), same_config_file_contents["pipeline"]["package"]))


def convert_notebook_to_text(notebook_path) -> str:
    logging.info(f"Using notebook from here: {notebook_path}")
    notebook_raw_text = ""
    try:
        notebook_file_handle = Path(notebook_path)
        notebook_raw_text = notebook_file_handle.read_text(encoding="ascii")
    except FileNotFoundError:
        logging.fatal(f"No notebook found at {notebook_path}")
        exit(1)

    ntbk_object = jupytext.reads(notebook_raw_text)
    return jupytext.writes(ntbk_object, fmt="py:percent")


def match_steps(notebook_text) -> List:
    # # Need to enable multiline for beginning of the line checking - (?m)
    # Looking for something of the format:
    # # - ...
    # or
    # # + tags=[...]
    return re.findall(r"(?m)^\s*# (?:\+|\-) ?(.*?)$", notebook_text)


def find_all_steps(notebook_text) -> List:
    # raw_step_tags_found = match_steps(notebook_text)

    # tagsFound := make([][]string, len(stepsFound))
    # namedStepsFound := false
    # for i, thisStep := range stepsFound {
    # 	tagsFound[i] = ParseTagsForStep(thisStep[1])
    # 	for _, tag := range tagsFound[i] {
    # 		if strings.HasPrefix(tag, "same_step_") {
    # 			namedStepsFound = true
    # 		}
    # 	}
    # }

    # if !namedStepsFound {
    # 	log.Tracef("no steps found in the file - treating the entire file as a single step.")
    # 	foundStep := FoundStep{}
    # 	foundStep.CodeSlice = convertedText
    # 	foundStep.Index = 0
    # 	foundStep.StepName = "same_step_0"
    # 	foundStep.Tags = nil

    # 	return []FoundStep{foundStep}, nil
    # }

    # log.Trace("Found at least one step with a 'same_step_#' format, breaking up the file")

    # code_blocks_slices := re_steps.Split(convertedText, -1)
    # foundSteps = make([]FoundStep, 0)
    # current_step_name := "same_step_0"
    # current_index := 0
    # log.Tracef("Raw steps found: %v", len(stepsFound))
    # log.Tracef("Code slices found: %v", len(code_blocks_slices))
    # log.Tracef("Raw tag blocks found: %v", len(tagsFound))
    # for i := range stepsFound {

    # 	if (i == 0) && (code_blocks_slices[0] == "") {
    # 		// When splitting cells, you can often have a zero cell
    # 		// at the start, so skipping it
    # 		code_blocks_slices = code_blocks_slices[1:]
    # 	}

    # 	cacheValue := ""
    # 	environmentName := ""
    # 	genericTags := make([]string, 0)

    # 	// Drop tags into one  of three categories (should be more extensible in the future)
    # 	for _, tag := range tagsFound[i] {
    # 		if strings.HasPrefix(tag, "same_step_") {
    # 			current_step_name = tag
    # 			current_index, _ = strconv.Atoi(strings.Split(tag, "_")[2])
    # 		} else if strings.HasPrefix(tag, "cache=") {
    # 			cacheValue = strings.Split(tag, "=")[1]
    # 		} else if strings.HasPrefix(tag, "environment=") {
    # 			environmentName = strings.Split(tag, "=")[1]
    # 		} else {
    # 			genericTags = append(genericTags, tag)
    # 		}
    # 	}
    # 	thisFoundStep := FoundStep{}
    # 	thisFoundStep.StepName = current_step_name
    # 	thisFoundStep.CacheValue = cacheValue
    # 	thisFoundStep.EnvironmentName = environmentName
    # 	thisFoundStep.Tags = genericTags
    # 	thisFoundStep.Index = current_index
    # 	thisFoundStep.CodeSlice = code_blocks_slices[i]
    # 	foundSteps = append(foundSteps, thisFoundStep)

    # }

    # return foundSteps, nil
    return []
