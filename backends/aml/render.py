from cli import same
from objects.step import Step
from pathlib import Path
from cli.same import helpers
from jinja2 import Environment, FileSystemLoader, select_autoescape

import logging

aml_root_template = "aml/root.jinja"
aml_step_template = "aml/step.jinja"


def render_function(compile_path: Path, steps: list[Step], same_config: dict):
    templateLoader = FileSystemLoader(searchpath="./templates")
    env = Environment(loader=templateLoader)
    root_file_string = _build_root_file(env, steps, same_config)

    helpers.write_file(compile_path, root_file_string)

    for step in steps:
        step_file_string = _build_step_file(env, step, same_config)
        helpers.write_file(compile_path, step_file_string)

    # 		stepToWrite := ""
    # 		var step_file_bytes []byte
    # 		switch target {
    # 		case "aml":
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
    return


def _build_root_file(env: Environment, all_steps: list[Step], same_config: dict) -> str:
    template = env.get_template(aml_root_template)

    root_contract = {
        "root_parameters_as_string": "",
        "comma_delim_list_of_packages_as_string": "",
        "list_of_steps": [],
        "comma_delim_list_of_step_names_as_str": "",
        "secrets_to_create_as_dict": {},
        "experiment_name": "",
        "experiment_name_safe": "",
        "list_of_environments": {},
        "image_pull_secrets": {},
    }

    params_to_merge = []

    # Do i need to check if run and run.parameters are required fields?
    try:
        run_parameters = same_config.run.parameters
    except Exception:
        run_parameters = {}

    for k in run_parameters:
        # Is this necessary? Could we support complex datatypes as parameters?
        # Probably - but we'll need to serialize to pass as a param and then deserialize in the template
        if isinstance(run_parameters[k], (int, float, str)):
            params_to_merge.append(f"{k}='{run_parameters[k]}'")
        else:
            logging.warning(f"We only support numeric, bool and strings as default parameters (no dicts or lists). We're setting the default value for '{k}' to ''.")

    root_contract["root_parameters_as_string"] = ", ".join(params_to_merge)

    root_contract["list_of_environments"]["default"] = {}
    root_contract["list_of_environments"]["default"]["image_tag"] = "library/python:3.9-slim-buster"
    root_contract["list_of_environments"]["default"]["private_registry"] = False

    for name in same_config.environments:
        root_contract["list_of_environments"][name] = {}
        root_contract["list_of_environments"][name]["image_tag"] = same_config.environments[name].image_tag

        # Need to convert to string here because yaml parsing automatically converts (so we need to normalize)
        # to string, in case the user didn't write True/False in a compliant way (e.g. 'true' lowercase)
        private_registry_bool = str(same_config.environments[name].get("private_registry", False))
        root_contract["list_of_environments"][name]["private_registry"] = private_registry_bool.lower() == "true"
        root_contract["list_of_environments"][name]["secret_name"] = ""

        if root_contract["list_of_environments"][name]["private_registry"]:

            if "credentials" in same_config.environments[name]:
                # Someone COULD set this to be a 'private_registry' but did not set credentials. This may be ok!
                # They could have already mounted the secret in the cluster, so we should let it go ahead.
                # However, because jinja doesn't like it when we parse through a struct without anything being set (even empty)
                # We're going to go ahead and set it up now, and populate it only if there are values

                # TODO:  # same_config.environments[name].get("credentials", {}) <- would something like this work?
                # It COULD autopopulate the entire dict, but not sure because if it's empty, then do all the fields
                # get created?
                these_credentials = same_config.environments[name].get("credentials", {})
                these_credentials["secret_name"] = these_credentials.get("secret_name", "")
                these_credentials["server"] = these_credentials.get("server", "")
                these_credentials["username"] = these_credentials.get("username", "")
                these_credentials["password"] = these_credentials.get("password", "")
                these_credentials["email"] = these_credentials.get("email", "")
                root_contract["secrets_to_create_as_dict"] = these_credentials
                root_contract["list_of_environments"][name]["secret_name"] = these_credentials["secret_name"]

    # Until we get smarter, we're just going to combine inject EVERY package into every step.
    # This is not IDEAL, but it's not as bad as it sounds because it'll allow systems to cache
    # containers more readily, even between steps, and package downloads are pretty small.
    # Using a dict so that we it'll remove dupes.
    # Also, we should probably swap this out for conda_environment.yaml (somehow).
    global_package_list = {}
    for step in all_steps:
        for package in all_steps[step].packages_to_install:
            global_package_list[package] = ""

    if global_package_list:
        # First merge all the packages together and delimit with ' and ,
        joined_string = "', '".join(list(global_package_list.keys()))

        # Then bound it with one more single quote on each side
        root_contract["comma_delim_list_of_packages_as_string"] = f"'{joined_string}'"

    # If someone does something hinky, like name their steps out of alpha order, we're just not
    # going to care, and parse them in the order they gave them to us.
    previous_step_name = ""
    for step_name in all_steps:

        step_content = all_steps[step_name]
        env_name = step_content.environment_name

        step_to_append = {}
        step_to_append["name"] = step_content.name
        step_to_append["package_string"] = root_contract["comma_delim_list_of_packages_as_string"]
        step_to_append["cache_value"] = step_content.cache_value
        step_to_append["previous_step"] = previous_step_name
        step_to_append["environment_name"] = env_name
        step_to_append["image_tag"] = root_contract["list_of_environments"][env_name]["image_tag"]
        step_to_append["private_registry"] = root_contract["list_of_environments"][env_name]["private_registry"]
        step_to_append["secret_name"] = root_contract["list_of_environments"][env_name]["secret_name"]

        if previous_step_name != "":
            step_to_append["previous_step_name"] = previous_step_name
        root_contract["list_of_steps"].append(step_to_append)

        previous_step_name = step_content.name

    # Text manipulation in jinja is pretty weak, we'll do both of these cleanings in python.

    # experiment_name is often displayed to the user, so try to keep it as close to the original as possible
    root_contract["experiment_name"] = helpers.removeIllegalExperimentNameCharacters(same_config.metadata.name)

    # However, often there's a backup, internal only name that needs much stricter character restrictions
    # We'll create that here.
    root_contract["safe_experiment_name"] = helpers.alphaNumericOnly(same_config.metadata.name)

    # List manipulation is also pretty weak in jinja (plus I like views being very non-functional). We'll
    # create the comma delim list of steps (which we need for DAG description) in python as well.
    root_contract["comma_delim_list_of_step_names_as_str"] = ", ".join([name for name in all_steps])

    return template.render(root_contract)


def _build_step_file(env: Environment, step: Step) -> str:
    template = env.get_template(aml_step_template)
    step_contract = {"name": step.name, "inner_code": step.code}
    return template.render(step_contract)