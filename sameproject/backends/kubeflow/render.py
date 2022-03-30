from jinja2 import Environment, FileSystemLoader, select_autoescape
from kubernetes import client, config
from base64 import urlsafe_b64encode
from pathlib import Path
from typing import Tuple
from uuid import uuid4
import logging
import dill
import os

from sameproject.objects.step import Step
from sameproject import helpers


kubeflow_root_template = "kubeflow/root.jinja"
kubeflow_step_template = "kubeflow/step.jinja"


def render_function(compile_path: str, steps: list, same_config: dict) -> Tuple[Path, str]:
    """Renders the notebook into a root file and a series of step files according to the target requirements. Returns an absolute path to the root file for deployment."""
    sourceDir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    print(f"In sourceDir {sourceDir}")
    templateDir = os.path.join(sourceDir, "templates")
    templateLoader = FileSystemLoader(templateDir)
    print(f"Template dir {templateDir}")
    env = Environment(loader=templateLoader)

    # Write the steps first so that if we need to make any changes while writing (such as adding a unique name), it's reflected in the root filepath
    for step_name in steps:
        step_file_string = _build_step_file(env, steps[step_name])
        helpers.write_file(Path(compile_path) / f"{steps[step_name].unique_step_name }.py", step_file_string)

    root_file_string = _build_root_file(env, steps, same_config)

    root_pipeline_name = f"root_pipeline_{uuid4().hex.lower()}"
    root_path = Path(compile_path) / f"{root_pipeline_name}.py"
    helpers.write_file(root_path, root_file_string)

    return (compile_path, root_pipeline_name)


def _build_root_file(env: Environment, all_steps: list, same_config: dict) -> str:
    template = env.get_template(kubeflow_root_template)

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
                these_credentials = {}
                these_credentials["image_pull_secret_name"] = same_config.environments[name].credentials.get("image_pull_secret_name", "")
                these_credentials["image_pull_secret_registry_uri"] = same_config.environments[name].credentials.get("image_pull_secret_registry_uri", "")
                these_credentials["image_pull_secret_username"] = same_config.environments[name].credentials.get("image_pull_secret_username", "")
                these_credentials["image_pull_secret_password"] = same_config.environments[name].credentials.get("image_pull_secret_password", "")
                these_credentials["image_pull_secret_email"] = same_config.environments[name].credentials.get("image_pull_secret_email", "")
                root_contract["secrets_to_create_as_dict"][name] = these_credentials

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
        step_to_append["unique_step_name"] = step_content.unique_step_name
        step_to_append["package_string"] = root_contract["comma_delim_list_of_packages_as_string"]
        step_to_append["cache_value"] = step_content.cache_value
        step_to_append["previous_step"] = previous_step_name

        if root_contract["list_of_environments"].get(env_name, None) is None:
            error_message = f"'{env_name}'' was listed as an environment in the notebook, but no such environment is listed in your SAME configuration file."
            logging.fatal(error_message)
            raise ValueError(error_message)

        step_to_append["environment_name"] = env_name
        step_to_append["image_tag"] = root_contract["list_of_environments"][env_name]["image_tag"]
        step_to_append["private_registry"] = root_contract["list_of_environments"][env_name]["private_registry"]
        step_to_append["secret_name"] = root_contract["list_of_environments"][env_name]["secret_name"]

        if previous_step_name != "":
            step_to_append["previous_step_name"] = previous_step_name
        root_contract["list_of_steps"].append(step_to_append)

        previous_step_name = step_content.unique_step_name

    # Text manipulation in jinja is pretty weak, we'll do both of these cleanings in python.

    # experiment_name is often displayed to the user, so try to keep it as close to the original as possible
    root_contract["experiment_name"] = helpers.removeIllegalExperimentNameCharacters(same_config.metadata.name)

    # However, often there's a backup, internal only name that needs much stricter character restrictions
    # We'll create that here.
    root_contract["experiment_name_safe"] = helpers.lowerAlphaNumericOnly(same_config.metadata.name)

    # List manipulation is also pretty weak in jinja (plus I like views being very non-functional). We'll
    # create the comma delim list of steps (which we need for DAG description) in python as well.
    root_contract["comma_delim_list_of_step_names_as_str"] = ", ".join([name for name in all_steps])

    return template.render(root_contract)


def _build_step_file(env: Environment, step: Step) -> str:
    step_contract = {
        "name": step.name,
        "unique_step_name": step.unique_step_name,
        "inner_code": urlsafe_b64encode(dill.dumps(step.code)).decode()
    }

    return env.get_template(kubeflow_step_template).render(step_contract)
