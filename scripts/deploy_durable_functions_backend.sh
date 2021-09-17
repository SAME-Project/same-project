#!/bin/bash
# usage: ./deploy_durable_functions_backend.sh <optional: --install-az-cli>

dir="durable-functions-deployment"

echo "Checking if Azure CLI is installed..."
az_cli_check="$(az help > /dev/null 2>&1)"
if [[ $? -ne 0 ]] ; then
    echo "Installing and setting up Azure CLI..."
    curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
    az login
else
    echo "Azure CLI is already installed and set up..."
fi

bash ./generate_durable_functions_app_package.sh $dir

echo "Publishing to Azure..."
func azure functionapp publish $appname
cd ..

echo "Cleaning up..."
rm -rf $dir

echo "Done!"