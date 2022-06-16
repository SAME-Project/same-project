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

        project_id = config.runtime_options.project_id
        service_account_credentials_file = config.runtime_options.service_account_credentials_file
        location = config.runtime_options.location

        credentials = service_account.Credentials.from_service_account_file(service_account_credentials_file)

        # aiplatform.init(project=project_id, location=location, credentials=credentials)
        TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        display_name = helpers.lowerAlphaNumericOnly(config.metadata.name)
        job_id = f"{display_name}-{TIMESTAMP}"

        BUCKET_NAME = config.runtime_options.bucket_name
        BUCKET_URI = f"gs://{BUCKET_NAME}"
        PIPELINE_ROOT = f"{BUCKET_URI}/{job_id}/"

        job = aiplatform.PipelineJob(
            display_name=display_name,
            template_path=str(package_json_path),
            project=project_id,
            credentials=credentials,
            location=location,
            pipeline_root=f"{PIPELINE_ROOT}",
            job_id=job_id,
            parameter_values={
                "job_id": job_id,
            },
        )

        print("\n"*3)
        import pprint
        pprint.pprint(f"PIPELINE JOB: {job.project}")
        print("\n"*3)

        job.submit(service_account=credentials.service_account_email)

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
