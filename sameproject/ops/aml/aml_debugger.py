from azureml.core.compute import ComputeTarget, AmlCompute
from azureml.core.compute_target import ComputeTargetException
import os
from azureml.core import Workspace
from azureml.core.authentication import ServicePrincipalAuthentication
from azureml.core.compute import ComputeTarget, AmlCompute
from azureml.core.runconfig import RunConfiguration
from azureml.core.conda_dependencies import CondaDependencies
from azureml.core import Environment
from azureml.pipeline.core import Pipeline, PipelineData, PipelineParameter
from azureml.pipeline.steps import PythonScriptStep
from azureml.core import Run, Experiment, Datastore


def get_aml_workspace(aml_workspace_credentials):
	svc_pr_password = aml_workspace_credentials.get("AML_SP_PASSWORD_VALUE")

	svc_pr = ServicePrincipalAuthentication(
		tenant_id=aml_workspace_credentials.get("AML_SP_TENANT_ID"),
		service_principal_id=aml_workspace_credentials.get("AML_SP_APP_ID"),
		service_principal_password=svc_pr_password,
	)

	return Workspace(
		subscription_id=aml_workspace_credentials.get("WORKSPACE_SUBSCRIPTION_ID"),
		resource_group=aml_workspace_credentials.get("WORKSPACE_RESOURCE_GROUP"),
		workspace_name=aml_workspace_credentials.get("WORKSPACE_NAME"),
		auth=svc_pr,
	)

credentials_dict = {
    "AML_SP_PASSWORD_VALUE": os.environ.get("AML_SP_PASSWORD_VALUE"),
    "AML_SP_TENANT_ID": os.environ.get("AML_SP_TENANT_ID"),
    "AML_SP_APP_ID": os.environ.get("AML_SP_APP_ID"),
    "WORKSPACE_SUBSCRIPTION_ID": os.environ.get("WORKSPACE_SUBSCRIPTION_ID"),
    "WORKSPACE_RESOURCE_GROUP": os.environ.get("WORKSPACE_RESOURCE_GROUP"),
    "WORKSPACE_NAME": os.environ.get("WORKSPACE_NAME"),
    "AML_COMPUTE_NAME": os.environ.get("AML_COMPUTE_NAME"),
}

ws=get_aml_workspace(aml_workspace_credentials=credentials_dict)
# Choose a name for your CPU cluster
cpu_cluster_name = "same-compute"

# # Verify that cluster does not exist already
# try:
#     cpu_cluster = ComputeTarget(workspace=ws, name=cpu_cluster_name)
#     print('Found existing cluster, use it.')
# except ComputeTargetException:
#     # To use a different region for the compute, add a location='<region>' parameter
#     compute_config = AmlCompute.provisioning_configuration(vm_size='STANDARD_D2_V2',
#                                                            max_nodes=4)
#     cpu_cluster = ComputeTarget.create(ws, cpu_cluster_name, compute_config)

cpu_cluster = ComputeTarget(workspace=ws, name=cpu_cluster_name)
print('Found existing cluster, use it.')

cpu_cluster.wait_for_completion(show_output=True)
identity_id=f'/subscriptions/{credentials_dict["WORKSPACE_SUBSCRIPTION_ID"]}/resourcegroups/{credentials_dict["WORKSPACE_RESOURCE_GROUP"]}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{credentials_dict["AML_SP_APP_ID"]}'
print(f"IdentityID: {identity_id}")
cpu_cluster.add_identity(identity_type="UserAssigned", identity_id=[identity_id])