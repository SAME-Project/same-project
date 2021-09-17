#!/bin/bash
# usage: ./deploy_durable_functions_backend.sh <optional: --install-az-cli>

dir="durable-functions-backend-deployment"
appname="durable-functions-backend-001"

echo "Checking if Azure CLI is installed..."
az_cli_check="$(az help > /dev/null 2>&1)"
if [[ $? -ne 0 ]] ; then
    echo "Installing and setting up Azure CLI..."
    curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
    az login
else
    echo "Azure CLI is already installed and set up..."
fi

echo "Preparing application..."
rm -rf $dir
mkdir -p $dir
cp -r ../objects $dir
cp -r ../backends/common/ $dir
cp -r ../backends/durable-functions/* $dir
cd $dir

echo "Listing application contents..."
ls -lh

echo "Publishing to Azure..."
func azure functionapp publish $appname
cd ..

echo "Cleaning up..."
rm -rf $dir

echo "Done!"