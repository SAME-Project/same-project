#!/usr/bin/env bash

echo 'Removing old resources'

# Cleanup repos.
for repo in edges images montage
do
  pachctl delete repo --force $repo
done

# Cleanup pipelines.
for pipeline in edges montage
do
  pachctl delete pipeline --force $pipeline
done

echo 'Creating new resources'
pachctl create repo images
for specification in edges.json montage.json
do
  pachctl create pipeline --file $specification
done


echo 'Committing images'
pachctl start commit images@master >> /dev/null
pachctl put file -r images@master:/ -f images
pachctl finish commit images@master

echo ''
echo 'Waiting for montage pipeline to complete...'
pachctl wait commit montage@master

pachctl get file montage@master:/montage.png --output montage.png
