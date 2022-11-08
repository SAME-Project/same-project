#!/bin/bash

cd /data/transformations/

<<<<<<< HEAD
mv 0 hello.ipynb

jupyter nbconvert hello.ipynb --to python

python3.8 hello.py
=======
same init

same run -t ocean --no-deploy --persist-temp-files
>>>>>>> 40799268c81881cc8354cdd847d8435b72a3f44b
