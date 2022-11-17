#!/bin/bash

cd /data/transformations/

mv algorithm hello.ipynb

same init

export KF_PIPELINES_ENDPOINT_ENV='ml_pipeline.kubeflow.svc.cluster.local'

echo KF_PIPELINES_ENDPOINT_ENV

same run

jupyter nbconvert hello.ipynb --to python

python3.8 hello.py
