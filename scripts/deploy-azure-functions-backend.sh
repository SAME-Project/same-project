#!/bin/bash
# usage: ./deploy-azure-functions-backend.sh <optional: --install-az-cli>

dir="azure-functions-deployment"
appname="azure-functions-backend-001"

echo "Checking if Azure CLI is installed..."
az_cli_check="$(az help > /dev/null 2>&1)"
if [[ $? -ne 0 ]] ; then
    echo "Installing and setting up Azure CLI..."
    curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
    az login
else
    echo "Azure CLI is already installed and set up..."
fi

bash ./generate-azure-functions-app-package.sh $dir

echo "Publishing to Azure..."
pushd $dir
func azure functionapp publish $appname
popd

echo "Cleaning up..."
rm -rf $dir

echo "Done!"