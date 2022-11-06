#!/bin/bash

cd /data/transformations/

cli_execute_transform_command  algorithm converted_script.py

python3.8 converted_script.py

same init

same run -t ocean --no-deploy --persist-temp-files