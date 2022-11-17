#!/bin/bash

cd /data/transformations/

mv algorithm hello.ipynb

jupyter nbconvert hello.ipynb --to python

python3.8 hello.py
