from sameproject.ops import notebooks as nbproc
from .options import k8s_registry_secrets
from io import BufferedReader
import sameproject.ops.backends
import sameproject.ops.helpers
import click
import os


@click.command(
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
    )
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
    default="kubeflow",
    type=click.Choice(["kubeflow", "aml", "vertex"]),
)
@k8s_registry_secrets
@click.option(
    "--persist-temp-files",
    "persist_temp_files",
    default=False,
    is_flag=True,
    type=bool,
    help="Persist compilation artifacts.",
)
@click.option(
    "--no-deploy",
    "no_deploy",
    default=False,
    is_flag=True,
    type=bool,
    help="Do not deploy compiled pipelines.",
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
    """Compiles and deploys a pipeline from a SAME config file."""

    secret_dict = sameproject.ops.helpers.create_secret_dict(
        image_pull_secret_name,
        image_pull_secret_registry_uri,
        image_pull_secret_username,
        image_pull_secret_password,
        image_pull_secret_email,
    )

    aml_required_values = [
        "AML_COMPUTE_NAME",
        "AML_SP_PASSWORD_VALUE",
        "AML_SP_TENANT_ID",
        "AML_SP_APP_ID",
        "WORKSPACE_SUBSCRIPTION_ID",
        "WORKSPACE_RESOURCE_GROUP",
        "WORKSPACE_NAME",
    ]

    aml_dict = {}
    if target == "aml":
        missing_values = []
        for aml_var in aml_required_values:
            val = os.environ.get(aml_var, None)
            if val is not None:
                aml_dict[aml_var] = val
            else:
                missing_values.append(aml_var)
        if len(missing_values) > 0:
            missing_values_string = ", ".join(missing_values)
            click.echo(
                f"You selected AML as a target, but are missing the following environment variables: {missing_values_string}"
            )
            raise ValueError(f"Missing values: {missing_values_string}")

    click.echo(f"File is: {same_file.name}")
    compiled_same_file, root_module_name = nbproc.compile(same_file, target, secret_dict, aml_dict)
    if persist_temp_files:
        click.echo(f"Compiled files persisted to: {compiled_same_file}")

    if not no_deploy:
        sameproject.ops.backends.deploy(target, compiled_same_file, root_module_name, persist_temp_files)
