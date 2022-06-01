from sameproject.ops.runtime_options import register_option, required_for_backend

register_option(
    "image_pull_secret_name",
    "The name of the kubernetes secret to create for docker secrets.",
)

register_option(
    "image_pull_secret_registry_uri",
    "URI of private docker registry for private image pulls.",
)

register_option(
    "image_pull_secret_username",
    "Username for private docker registry for private image pulls.",
)

register_option(
    "image_pull_secret_password",
    "Password for private docker registry for private image pulls.",
)

register_option(
    "image_pull_secret_email",
    "Email address for private docker registry for private image pulls.",
)
