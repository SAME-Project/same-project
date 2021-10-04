# ------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the Apache License 2.0.
# ------------------------------------------------------------
ARG VARIANT=3-bullseye
FROM mcr.microsoft.com/vscode/devcontainers/python:${VARIANT}

# Reuse existing username configured as part of base image. See:
# https://github.com/microsoft/vscode-dev-containers/blob/main/containers/python-3/.devcontainer/base.Dockerfile
ARG USERNAME=vscode

ARG KUBECTL_VERSION="latest"
ARG HELM_VERSION="latest"
ARG MINIKUBE_VERSION="latest"

COPY library-scripts/* custom-scripts/* first-run-notice.txt /tmp/staging/

RUN apt-get update \
    # Additional custom configurations for non-root user.
    && bash /tmp/staging/setup-user.sh "${USERNAME}" "${PATH}" \
    #
    # Install Docker CE CLI and Engine for Docker-in-Docker.
    && bash /tmp/staging/docker-in-docker-debian.sh "true" "${USERNAME}" "false" \
    #
    # Install Kubectl, Helm and Minkikube.
    && bash /tmp/staging/kubectl-helm-debian.sh "${KUBECTL_VERSION}" "${HELM_VERSION}" "${MINIKUBE_VERSION}" \
    #
    # Copy devcontainer init, Docker bind-mount and GOPATH setup scripts
    && mv -f -t /usr/local/share/ /tmp/staging/docker-bind-mount.sh /tmp/staging/devcontainer-init.sh \
    && chmod +x /usr/local/share/docker-bind-mount.sh /usr/local/share/devcontainer-init.sh \
    && chown ${USERNAME}:root /usr/local/share/docker-bind-mount.sh /usr/local/share/devcontainer-init.sh \
    #
    # Move the first run notice to the correct location for Codespaces.
    && mkdir -p /usr/local/etc/vscode-dev-containers/ \
    && mv -f /tmp/staging/first-run-notice.txt /usr/local/etc/vscode-dev-containers/ \
    #
    # Clean up packages and the staging folder.
    && apt-get autoremove -y && apt-get clean -y && rm -rf /tmp/staging

# Install the Azure CLI
RUN apt-get update \
    && apt-get install ca-certificates curl apt-transport-https lsb-release gnupg \
    && curl -sL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | tee /etc/apt/trusted.gpg.d/microsoft.gpg > /dev/null \
    && AZ_REPO=$(lsb_release -cs) \
    && echo "deb [arch=amd64] https://packages.microsoft.com/repos/azure-cli/ $AZ_REPO main" | tee /etc/apt/sources.list.d/azure-cli.list \
    && apt-get update \
    && apt-get install azure-cli

# Install Poetry as user for package building and dependency management
USER ${USERNAME}
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -

# Mount for docker-in-docker
VOLUME [ "/var/lib/docker" ]

# Initialize Dapr devcontainer script
ENTRYPOINT [ "/usr/local/share/devcontainer-init.sh" ]
CMD [ "sleep", "infinity" ]
