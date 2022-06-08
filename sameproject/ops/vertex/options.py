from sameproject.ops.runtime_options import register_option, required_for_backend

register_option(
    "bucket_name",
    "Google Cloud Bucket necessary for running the pipeline.",
    validator=required_for_backend("vertex"),
    schema={"nullable": False, "type": "string", "regex": r"^[\d\w][\d\w]*[\d\w]", "maxlength": 63, "minlength": 3},
)
