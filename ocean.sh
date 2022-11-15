#!/bin/bash

cd /data/transformations/

mv 0 hello.ipynb

same init

same run --persist-temp-files -t ocean

python3.8 hello.py
