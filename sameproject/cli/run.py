from sameproject.ops.runtime_options import runtime_options, get_option_value
from sameproject.ops import notebooks as nbproc
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
    type=click.File("r"),
    default="same.yaml",
    help="Configuration file (same.yaml) for this project. We currently only support notebooks/python files describing pipelines in the same directory as the same configuration file.",
    show_default=True,
)
@click.option(
    "-t",
    "--target",
    default="kubeflow",
    type=click.Choice(["kubeflow", "aml"]),
)
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
@runtime_options
def run(
    target: str,
    same_file: BufferedReader,
    no_deploy: bool = False,
    persist_temp_files: bool = False,
):
    """Compiles and deploys a pipeline from a SAME config file."""

    secret_dict = sameproject.ops.helpers.create_secret_dict(
        get_option_value("image_pull_secret_name"),
        get_option_value("image_pull_secret_registry_uri"),
        get_option_value("image_pull_secret_username"),
        get_option_value("image_pull_secret_password"),
        get_option_value("image_pull_secret_email"),
    )

    aml_required_values = [
        "aml_compute_name",
        "aml_sp_password_value",
        "aml_sp_tenant_id",
        "aml_sp_app_id",
        "workspace_subscription_id",
        "workspace_resource_group",
        "workspace_name",
    ]

    aml_dict = {}
    if target == "aml":
        missing_values = []
        for aml_var in aml_required_values:
            val = get_option_value(aml_var)
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
    compile_dir, root_module_name = nbproc.compile(same_file, target, secret_dict, aml_dict)
    if persist_temp_files:
        click.echo(f"Compile artifacts persisted at: {compile_dir}")
    if not no_deploy:
        sameproject.ops.backends.deploy(target, compile_dir, root_module_name, persist_temp_files)
