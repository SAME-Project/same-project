from io import BufferedReader
import click

from cli.same.program.compile import notebook_processing as nbproc

import backends.executor
import cli.same.helpers

import os


@click.group()
def program():
    pass


@program.command(
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
    )
)
@click.option(
    "--no-deploy",
    "no_deploy",
    default=False,
    is_flag=True,
    type=bool,
    help="Only run through the compilation but do not deploy.",
)
@click.option(
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
    help="Configuration file (same.yaml) for this project. We currently only support notebooks/python files describing pipelines in the same directory as the same configuration file.",
    show_default=True,
)
@click.option(
    "-t",
    "--target",
    type=click.Choice(["kubeflow", "aml"]),
)
@click.option(
    "--image-pull-secret-name",
    "image_pull_secret_name",
    type=str,
    help="The name of the secret to create (only relevant for Kubernetes based deployments such as Kubeflow).",
)
@click.option(
    "--image-pull-secret-registry-uri",
    "image_pull_secret_registry_uri",
    type=str,
    help="The private registry URI - required as an argument during Docker pull.",
)
@click.option(
    "--image-pull-secret-username",
    "image_pull_secret_username",
    type=str,
    help="The username for pulling the Docker image from the private registry.",
)
@click.option(
    "--image-pull-secret-password",
    "image_pull_secret_password",
    type=str,
    help="The password for pulling the Docker image from the private registry.",
)
@click.option(
    "--image-pull-secret-email",
    "image_pull_secret_email",
    type=str,
    help="The email for pulling the Docker image from the private registry (required for Docker pulls from private registries).",
)
def run(
    same_file: BufferedReader,
    target: str,
    image_pull_secret_name: str,
    image_pull_secret_registry_uri: str,
    image_pull_secret_username: str,
    image_pull_secret_password: str,
    image_pull_secret_email: str,
    persist_temp_files: bool = False,
    no_deploy: bool = False,
):
    secret_dict = cli.same.helpers.create_secret_dict(
        image_pull_secret_name, image_pull_secret_registry_uri, image_pull_secret_username, image_pull_secret_password, image_pull_secret_email
    )

    aml_required_values = [
        "AML_SP_PASSWORD_VALUE",
        "AML_SP_TENANT_ID",
        "AML_SP_APP_ID",
        "WORKSPACE_SUBSCRIPTION_ID",
        "WORKSPACE_RESOURCE_GROUP",
        "WORKSPACE_NAME",
        "AML_COMPUTE_NAME",
    ]

    aml_dict = {}
    if target == "aml":
        for aml_var in aml_required_values:
            missing_values = []
            val = os.environ.get(aml_var, None)
            if val is not None:
                aml_dict[aml_var] = val
            else:
                missing_values.append(aml_var)
        if len(missing_values) > 0:
            click.echo(f"You selected AML as a target, but are missing the following environment variables: {', '.join(missing_values)}")
            raise ValueError("Missing values.")

    click.echo(f"File is: {same_file.name}")
    compiled_same_file, root_module_name = nbproc.compile(same_file, target, secret_dict, aml_dict)
    if not no_deploy:
        backends.executor.deploy(target, compiled_same_file, root_module_name, persist_temp_files)
