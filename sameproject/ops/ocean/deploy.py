from sameproject.data.config import SameConfig
from sameproject.ops import helpers
from pathlib import Path
import importlib
import kubernetes

def create_job(logger, body, job):
    try:
        logger.debug(f"Creating job {job}")
        batch_client = kubernetes.client.BatchV1Api()
        obj = batch_client.create_namespaced_job(body["metadata"]["namespace"], job)
        logger.info(f"{obj.kind} {obj.metadata.name} created")
    except ApiException as e:
        logger.debug(f"Exception when calling BatchV1Api->create_namespaced_job: {e}\n")

def deploy(base_path: Path, root_file: str, config: SameConfig):
    return
    # with helpers.add_path(str(base_path)):
    #     root_module = importlib.import_module(root_file)  # python module

    #     client = boto3.client('ec2')
    #     return client.create_run_from_pipeline_func(
    #         root_module.root,
    #         arguments={},
    #     )
