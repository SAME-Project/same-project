#!/bin/bash
# usage: ./deploy-durable-functions-backend.sh <app_name>

dir="durable-functions-deployment"

if [ $# -eq 0 ]
  then
    echo "Error: App name not specified."
    echo "usage: ./deploy-durable-functions-backend.sh <app_name>"
    exit 1
fi

appname=$1

echo "Checking if Azure CLI is installed..."
az_cli_check="$(az help > /dev/null 2>&1)"
if [[ $? -ne 0 ]] ; then
    echo "Installing and setting up Azure CLI..."
    curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
    az login
else
    echo "Azure CLI is already installed and set up..."
fi

bash ./generate-durable-functions-app-package.sh $dir

echo "Publishing to Azure..."
pushd $dir
func azure functionapp publish $appname
popd

echo "Cleaning up..."
rm -rf $dir

echo "Done!"