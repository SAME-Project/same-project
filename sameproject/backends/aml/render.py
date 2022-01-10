from sameproject.objects.step import Step
from pathlib import Path
from sameproject import helpers
from jinja2 import Environment, FileSystemLoader, select_autoescape

from typing import Tuple

import logging

from uuid import uuid4


kubeflow_root_template = "aml/root.jinja"
kubeflow_step_template = "aml/step.jinja"


def render_function(compile_path: str, steps: list, same_config: dict) -> Tuple[Path, str]:
    """Renders the notebook into a root file and a series of step files according to the target requirements. Returns an absolute path to the root file for deployment."""
    templateLoader = FileSystemLoader(searchpath="./templates")
    env = Environment(loader=templateLoader)
    same_config["compile_path"] = compile_path
    root_file_string = _build_root_file(env, steps, same_config)

    root_pipeline_name = f"root_pipeline_{uuid4().hex.lower()}"
    root_path = Path(compile_path) / f"{root_pipeline_name}.py"
    helpers.write_file(root_path, root_file_string)

    for step_name in steps:
        # Need a unique name so that libraries don't conflict in sys.modules. This is MOSTLY a test issue, but could be the case generally.
        step_file_string = _build_step_file(env, steps[step_name], steps[step_name].unique_step_name)
        (Path(compile_path) / steps[step_name].unique_step_name).mkdir()
        helpers.write_file(Path(compile_path) / steps[step_name].unique_step_name / f"{steps[step_name].unique_step_name}.py", step_file_string)

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
        "aml_workspace_credentials": {},
        "compile_dir": "",
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

            # This is starting to have quite a lot of code smell - root_contract requires a bit of massaging (instead of
            # just passing through same_config to the jinja template nakedly) but i'm starting to dislike everything here.
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

    if same_config.get("aml"):
        root_contract["aml_workspace_credentials"] = {
            "AML_SP_PASSWORD_VALUE": same_config.aml.AML_SP_PASSWORD_VALUE,
            "AML_SP_TENANT_ID": same_config.aml.AML_SP_TENANT_ID,
            "AML_SP_APP_ID": same_config.aml.AML_SP_APP_ID,
            "WORKSPACE_SUBSCRIPTION_ID": same_config.aml.WORKSPACE_SUBSCRIPTION_ID,
            "WORKSPACE_RESOURCE_GROUP": same_config.aml.WORKSPACE_RESOURCE_GROUP,
            "WORKSPACE_NAME": same_config.aml.WORKSPACE_NAME,
            "AML_COMPUTE_NAME": same_config.aml.AML_COMPUTE_NAME,
        }

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

    # For AML, each "step" needs to have '_step' attached (this may be historical)
    # and not necessary - look at it when we combine all these step rendering functions into one
    root_contract["comma_delim_list_of_step_names_as_str"] = ", ".join([f"{all_steps[this_step_name].unique_step_name}_step" for this_step_name in all_steps])

    root_contract["compile_path"] = same_config["compile_path"]

    return template.render(root_contract)


def _build_step_file(env: Environment, step: Step, step_name: str) -> str:
    template = env.get_template(kubeflow_step_template)

    # Create a parameter_string for putting in each step function
    # default is to be a serialized empty dict. We should probably
    # handle this a different way (allowing custom params to be passed in)
    # but haven't found this requirement from a customer yet.
    parameter_string = '__context="gAR9lC4=", __run_info="gAR9lC4=", __metadata_url=""'
    step_contract = {"name": step_name, "inner_code": step.code, "parameter_string": parameter_string}
    return template.render(step_contract)
