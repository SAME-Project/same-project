#!/usr/bin/env bash
#-------------------------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See https://go.microsoft.com/fwlink/?linkid=2090316 for license information.
#-------------------------------------------------------------------------------------------------------------
#
# Initializes the devcontainer tasks each time the container starts.
# Users can edit this copy under /usr/local/share in the container to
# customize this as needed for their custom localhost bindings.

set -e
echo "Running devcontainer-init.sh ..."

# Invoke /usr/local/share/docker-bind-mount.sh or docker-init.sh as appropriate
set +e
if [[ "${BIND_LOCALHOST_DOCKER,,}" == "true" ]]; then
    echo "Invoking docker-bind-mount.sh ..."
    exec /usr/local/share/docker-bind-mount.sh "$@"
else
    echo "Invoking docker-init.sh ..."
    exec /usr/local/share/docker-init.sh "$@"
fi
