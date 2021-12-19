# ------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the Apache License 2.0.
# ------------------------------------------------------------

# Using buster instead of bullseye as Azure Functions Core Tools do not yet support Debian 11, see:
# https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=v3%2Clinux%2Ccsharp%2Cportal%2Cbash%2Ckeda#install-the-azure-functions-core-tools
ARG VARIANT=3.10
FROM python:${VARIANT}

# Reuse existing username configured as part of base image. See:
# https://github.com/microsoft/vscode-dev-containers/blob/main/containers/python-3/.devcontainer/base.Dockerfile
ARG USERNAME=vscode

ARG KUBECTL_VERSION="latest"
ARG HELM_VERSION="latest"
ARG MINIKUBE_VERSION="latest"

COPY library-scripts/* custom-scripts/* first-run-notice.txt /tmp/staging/

COPY py.sh /usr/local/bin/py.sh

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

# Install the Azure CLI and Azure Functions Core Tools
RUN apt-get update \
    && apt-get install ca-certificates curl apt-transport-https lsb-release gnupg \
    && curl -sL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | tee /etc/apt/trusted.gpg.d/microsoft.gpg > /dev/null \
    && TARGET_ARCH=$(dpkg-architecture -q DEB_BUILD_ARCH) \
    && TARGET_CODENAME=$(lsb_release -cs) \
    && TARGET_RELEASE=$(lsb_release -rs | cut -d'.' -f 1) \
    && echo "deb [arch=${TARGET_ARCH}] https://packages.microsoft.com/repos/azure-cli/ ${TARGET_CODENAME} main" | tee /etc/apt/sources.list.d/azure-cli.list \
    && echo "deb [arch=${TARGET_ARCH}] https://packages.microsoft.com/debian/${TARGET_RELEASE}/prod ${TARGET_CODENAME} main" | tee /etc/apt/sources.list.d/dotnetdev.list \
    && apt-get update \
    && apt-get install azure-cli azure-functions-core-tools-3

# Install Poetry as user for package building and dependency management
USER ${USERNAME}
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -

# Install Azure ML v2 extension as user
RUN az extension add --name ml -y

# Mount for docker-in-docker
VOLUME [ "/var/lib/docker" ]

# Initialize Dapr devcontainer script
ENTRYPOINT [ "/usr/local/share/devcontainer-init.sh" ]
CMD [ "sleep", "infinity" ]
