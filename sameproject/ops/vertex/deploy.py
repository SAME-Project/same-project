from sameproject.ops import helpers
from pathlib import Path
import importlib
import kfp
from pathlib import Path
from kfp.v2 import compiler
import importlib
import kfp
from kfp.v2 import dsl
from kfp.v2.dsl import component, Output, HTML
from google.cloud import aiplatform
import dotenv
import datetime
import logging
import os
from google.oauth2 import service_account
from sameproject.data.config import SameConfig


def deploy(base_path: str, root_name: str, config: SameConfig):

    with helpers.add_path(str(base_path)):
        root_module = importlib.import_module(root_name)

        compiled_path = Path(base_path)

        file_suffix = ".json"

        package_json_path = compiled_path / f"root{file_suffix}"

        logging.debug(f"Package path: {package_json_path}")

        compiler.Compiler().compile(pipeline_func=root_module.root, package_path=str(package_json_path))

        project_id = os.environ.get("PROJECT_ID", project_id)
        service_account_credentials_file = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", service_account_credentials_file)
        location = "northamerica-northeast1"

        credentials = service_account.Credentials.from_service_account_file(service_account_credentials_file)

        # aiplatform.init(project=project_id, location=location, credentials=credentials)

        BUCKET_NAME = os.environ.get("BUCKET_NAME")
        BUCKET_URI = f"gs://{BUCKET_NAME}"
        PIPELINE_ROOT = f"{BUCKET_URI}/{config['runtime_options']}/pipeline_root"

        TIMESTAMP = datetime.now().strftime("%Y%m%d%H%M%S")

        job = aiplatform.PipelineJob(
            display_name="MY_DISPLAY_JOB",
            template_path=compiled_path,
            project=project_id,
            credentials=credentials,
            location=location,
            pipeline_root=f"{PIPELINE_ROOT}",
            job_id="MY_DISPLAY_JOB-{0}".format(TIMESTAMP),
        )

        # job = aiplatform.PipelineJob(
        #     display_name="MY_DISPLAY_JOB",
        #     template_path=compiled_pipeline_path,
        #     job_id=JOB_ID,
        #     pipeline_root=PIPELINE_ROOT_PATH,
        #     parameter_values=PIPELINE_PARAMETERS,
        #     enable_caching=ENABLE_CACHING,
        #     encryption_spec_key_name=CMEK,
        #     labels=LABELS,
        #     credentials=CREDENTIALS,
        #     project=PROJECT_ID,
        #     location=LOCATION,
        # )

        job.submit(service_account=credentials.service_account_email)
