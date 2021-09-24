from io import BufferedReader
import click
from cli.same.program.compile import notebook_processing as nbproc
from cli.same.same_config import SameConfig

import backends


@click.group()
def program():
    pass


@program.command()
@click.option(
    "-p",
    "--persist-temp-files",
    "persist_temp_files",
    default=False,
    is_flag=True,
    type=bool,
    help="Persist the temporary compilation files.",
)
@click.option(
    "-f",
    "--same-file",
    "same_file",
    type=click.File("rb"),
    default="same.yaml",
    help="Configuration file (same.yaml) for this project. We currently only support notebooks/python files describing pipelines in the same directory as the same configuration file.",
    show_default=True,
)
@click.option(
    "-t",
    "--target",
    type=click.Choice(["kubeflow", "aml"]),
)
def compile(same_file: BufferedReader, target, persist_temp_files):
    """Compile a SAME program without running"""
    click.echo(f"File is: {same_file.name}")

    same_config = SameConfig(same_file)

    notebook_path = nbproc.get_notebook_path(same_file.name, same_config)  # noqa: F841

    notebook_dict = nbproc.read_notebook(notebook_path)

    all_steps = nbproc.get_steps(notebook_dict)

    backends.executor.render(target=target, steps=all_steps, same_config=same_config)

    # compileProgramCmd.Flags().String("image-pull-secret-server", "", "Image pull server for any private repos (only one server currently supported for all private repos)")
    # compileProgramCmd.Flags().String("image-pull-secret-username", "", "Image pull username for any private repos (only one username currently supported for all private repos)")
    # compileProgramCmd.Flags().String("image-pull-secret-password", "", "Image pull password for any private repos (only one password currently supported for all private repos)")
    # compileProgramCmd.Flags().String("image-pull-secret-email", "", "Image pull email for any private repos (only one email currently supported for all private repos)")


# func (c *CompileLive) WriteStepFiles(target string, compiledDir string, aggregatedSteps map[string]CodeBlock) (map[string]map[string]string, error) {

# 	tempStepHolderDir, err := ioutil.TempDir(os.TempDir(), "SAME-compile-*")
# 	defer os.Remove(tempStepHolderDir)

# 	returnedPackages := make(map[string]map[string]string)

# 	if err != nil {
# 		return nil, fmt.Errorf("error creating temporary directory to write steps to: %v", err)
# 	}

# 	for i := range aggregatedSteps {
# 		returnedPackages[aggregatedSteps[i].StepIdentifier] = make(map[string]string)
# 		parameterString, _ := JoinMapKeysValues(aggregatedSteps[i].Parameters)
# 		if parameterString != "" {
# 			parameterString = "," + parameterString
# 		}

# 		// Prepend an empty locals as the default
# 		parameterString = `__context="gAR9lC4=", __run_info="gAR9lC4=", __metadata_url=""` + parameterString

# 		stepToWrite := ""
# 		var step_file_bytes []byte
# 		switch target {
# 		case "kubeflow":
# 			stepToWrite = filepath.Join(compiledDir, fmt.Sprintf("%v.py", aggregatedSteps[i].StepIdentifier))
# 			step_file_bytes = box.Get("/kfp/step.tmpl")
# 		case "aml":
# 			// AML requires each step to be in its own directory, with the same name as the python file
# 			stepDirectoryName := filepath.Join(compiledDir, aggregatedSteps[i].StepIdentifier)
# 			_, err := os.Stat(stepDirectoryName)
# 			if os.IsNotExist(err) {
# 				errDir := os.MkdirAll(stepDirectoryName, 0700)
# 				if errDir != nil {
# 					return nil, fmt.Errorf("error creating step directory for %v: %v", stepDirectoryName, err)
# 				}

# 			}

# 			stepToWrite = filepath.Join(stepDirectoryName, fmt.Sprintf("%v.py", aggregatedSteps[i].StepIdentifier))
# 			step_file_bytes = box.Get("/aml/step.tmpl")
# 		default:
# 			return nil, fmt.Errorf("unknown target: %v", target)
# 		}

# 		innerCodeToExecute := ""
# 		scanner := bufio.NewScanner(strings.NewReader(aggregatedSteps[i].Code))
# 		for scanner.Scan() {
# 			innerCodeToExecute += fmt.Sprintln(scanner.Text())
# 		}

# 		stepFileContext := pongo2.Context{
# 			"Name":             aggregatedSteps[i].StepIdentifier,
# 			"Parameter_String": parameterString,
# 			"Inner_Code":       innerCodeToExecute,
# 		}

# 		tmpl := pongo2.Must(pongo2.FromBytes(step_file_bytes))
# 		stepFileString, err := tmpl.Execute(stepFileContext)
# 		if err != nil {
# 			return nil, fmt.Errorf("error writing step %v: %v", aggregatedSteps[i].StepIdentifier, err.Error())
# 		}

# 		err = os.WriteFile(stepToWrite, []byte(stepFileString), 0400)
# 		if err != nil {
# 			return nil, fmt.Errorf("Error writing step %v: %v", stepToWrite, err.Error())
# 		}

# 		tempStepFile, err := ioutil.TempFile(tempStepHolderDir, fmt.Sprintf("SAME-inner-code-file-*-%v", fmt.Sprintf("%v.py", aggregatedSteps[i].StepIdentifier)))
# 		if err != nil {
# 			return nil, fmt.Errorf("error creating tempfile for step %v: %v", aggregatedSteps[i].StepIdentifier, err.Error())
# 		}

# 		err = ioutil.WriteFile(tempStepFile.Name(), []byte(innerCodeToExecute), 0400)
# 		if err != nil {
# 			return nil, fmt.Errorf("Error writing temporary step file %v: %v", tempStepFile, err.Error())
# 		}

# 		log.Tracef("Freezing python packages")
# 		pipCommand := fmt.Sprintf(`
# #!/bin/bash
# set -e
# pipreqs %v --print
# 	`, tempStepHolderDir)

# 		cmdReturn, err := ExecuteInlineBashScript(&cobra.Command{}, pipCommand, "Pipreqs output failed", false)

# 		if err != nil {
# 			log.Tracef("Error executing: %v\n CmdReturn: %v", err.Error(), cmdReturn)
# 			return nil, err
# 		}
# 		allPackages := strings.Split(cmdReturn, "\n")

# 		for _, packageString := range allPackages {
# 			if packageString != "" && !strings.HasPrefix(packageString, "INFO: ") {
# 				returnedPackages[aggregatedSteps[i].StepIdentifier][packageString] = ""
# 			}
# 		}

# 	}

# 	return returnedPackages, nil
# }

# func (c *CompileLive) ConvertNotebook(jupytextExecutablePath string, notebookFilePath string) (string, error) {
# 	log.Infof("Using notebook from here: %v\n", notebookFilePath)
# 	notebookFile, err := os.Open(notebookFilePath)
# 	if err != nil {
# 		return "", fmt.Errorf("program_compile.go: error reading from notebook file: %v", notebookFilePath)
# 	}

# 	scriptCmd := exec.Command("/bin/sh", "-c", fmt.Sprintf("%v --to py", jupytextExecutablePath))
# 	scriptStdin, err := scriptCmd.StdinPipe()

# 	if err != nil {
# 		return "", fmt.Errorf("Error building Stdin pipe for notebook file: %v", err.Error())
# 	}

# 	b, _ := ioutil.ReadAll(notebookFile)

# 	go func() {
# 		defer scriptStdin.Close()
# 		_, _ = io.WriteString(scriptStdin, string(b))
# 	}()

# 	out, err := scriptCmd.CombinedOutput()
# 	if err != nil {
# 		return "", fmt.Errorf("Error executing notebook conversion: %v", err.Error())
# 	}

# 	if err != nil {
# 		return "", fmt.Errorf(`
# could not convert the file: %v
# full error message: %v`, notebookFilePath, string(out))
# 	}

# 	return string(out), nil
# }

# func (c CompileLive) WriteSupportFiles(workingDirectory string, directoriesToWriteTo []string) error {
# 	// Inspired by Kubeflwo - TODO: Make sure to have copyright and license here
# 	// https://github.com/kubeflow/pipelines/blob/cc83e1089b573256e781ed2e4ac90f604129e769/sdk/python/kfp/containers/_build_image_api.py#L68

# 	// This function recursively scans the working directory and captures the following files in the container image context:
# 	// * :code:`requirements.txt` files
# 	// * All python files

# 	// Copying all *.py and requirements.txt files

# 	for _, destDir := range directoriesToWriteTo {
# 		opt := recurseCopy.Options{
# 			Skip: func(src string) (bool, error) {
# 				fi, err := os.Stat(src)
# 				if err != nil {
# 					return true, err
# 				}
# 				if fi.IsDir() {
# 					return false, nil
# 				}
# 				return !strings.HasSuffix(src, ".py"), nil
# 			},
# 			OnDirExists: func(src string, dst string) recurseCopy.DirExistsAction {
# 				return recurseCopy.Merge
# 			},
# 			Sync: true,
# 		}
# 		err := recurseCopy.Copy(workingDirectory, destDir, opt)
# 		if err != nil {
# 			return fmt.Errorf("Error copying support python files from %s to %s: %v", workingDirectory, destDir, err)
# 		}

# 	}
# 	return nil
# }
