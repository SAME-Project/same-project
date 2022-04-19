import click


def k8s_registry_secrets(fn):
    """Click decorator for kubernetes docker registry secrets."""

    return _compose(
        fn,
        [
            click.option(
                "--image-pull-secret-name",
                "image_pull_secret_name",
                type=str,
                help="The name of the secret to create (only relevant for Kubernetes based deployments such as Kubeflow).",
            ),
            click.option(
                "--image-pull-secret-registry-uri",
                "image_pull_secret_registry_uri",
                type=str,
                help="The private registry URI - required as an argument during Docker pull.",
            ),
            click.option(
                "--image-pull-secret-username",
                "image_pull_secret_username",
                type=str,
                help="The username for pulling the Docker image from the private registry.",
            ),
            click.option(
                "--image-pull-secret-password",
                "image_pull_secret_password",
                type=str,
                help="The password for pulling the Docker image from the private registry.",
            ),
            click.option(
                "--image-pull-secret-email",
                "image_pull_secret_email",
                type=str,
                help="The email for pulling the Docker image from the private registry (required for Docker pulls from private registries).",
            ),
        ]
    )


def _compose(fn, decorators):
    for decorator in decorators:
        fn = decorator(fn)
    return fn
