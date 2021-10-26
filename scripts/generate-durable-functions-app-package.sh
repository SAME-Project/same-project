#!/bin/bash
# usage: ./generate-durable-functions-app-package.sh <output_path>

if [ $# -eq 0 ]
  then
    echo "Error: Output path not specified."
    echo "usage: ./generate-durable-functions-app-package.sh <output_path>"
    exit 1
fi

dir=$1

echo "Preparing application..."
rm -rf $dir
mkdir -p $dir
cp -r ../objects/ $dir
cp -r ../backends/common/ $dir
cp -r ../backends/durable_functions/* $dir
cd $dir

echo "Listing application contents..."
ls -lh