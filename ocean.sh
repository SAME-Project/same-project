#!/bin/bash

cd /data/transformations/

mv algorithm hello.ipynb

same init

same run

jupyter nbconvert hello.ipynb --to python

python3.8 hello.py
