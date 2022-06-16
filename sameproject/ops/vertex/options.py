from sameproject.ops.runtime_options import register_option

register_option(
    "bucket_name",
    "Google Cloud Bucket necessary for running the pipeline.",
    backend="vertex",
    schema={"nullable": False, "type": "string", "regex": r"^[\d\w][\d\w-]*[\d\w]", "maxlength": 63, "minlength": 3},
)

register_option(
    "project_id",
    "Google Cloud Bucket necessary for running the pipeline.",
    backend="vertex",
    schema={"nullable": False, "type": "string", "regex": r"^[\d\w][\d\w-]*[\d\w]", "maxlength": 63, "minlength": 3},
)

register_option(
    "service_account_credentials_file",
    "Exported json file for the service principal credentials - read more about creating this service principal with the correct credentials here - https://cloud.google.com/vertex-ai/docs/pipelines/configure-project.",
    backend="vertex",
    schema={"nullable": False, "type": "string"},
)

register_option(
    "location",
    "Google Cloud region and zone - should be of the form '<region>-<zone>' e.g. 'northamerica-northeast1' (with the dash).",
    backend="vertex",
    schema={"nullable": False, "type": "string", "regex": r"^[\d\w][\d\w-]*[\d\w]", "maxlength": 128},
)
