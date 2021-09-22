# ------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the Apache License 2.0.
# ------------------------------------------------------------
ARG VARIANT=3-bullseye
FROM mcr.microsoft.com/vscode/devcontainers/python:${VARIANT}

# This Dockerfile adds a non-root 'vscode' user with sudo access. However, for Linux,
# this user's GID/UID must match your local user UID/GID to avoid permission issues
# with bind mounts. Update USER_UID / USER_GID if yours is not 1000. See
# https://aka.ms/vscode-remote/containers/non-root-user for details.
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID  

# Install Poetry as user for package building and dependency management
USER ${USERNAME}
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -

# Other useful dependencies:
# Azure CLI
# Kubeflow
# Docker, Kubernetes, Helm
