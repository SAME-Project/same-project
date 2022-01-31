# pylint: disable=protected-access,missing-function-docstring, missing-class-docstring
# pylint: disable=missing-module-docstring, missing-class-docstring
# -*- coding: utf-8 -*-
import sdk.same as same
import subprocess
import sys
import csv
import os
import pytest
import pytest_virtualenv as venv
from urllib.parse import urlparse
import yaml
import importlib
import pandas as pd

@pytest.fixture(scope="module")
def return_yaml(same_file='../data/same.yaml'):
    with open(same_file, 'r') as file:
        same_variables = yaml.safe_load(file)
    
    return same_variables

@pytest.fixture(scope="module")
def return_env(envar):
    os.environ["SAME_ENV"] = envar
    try:
      env_var=os.environ['SAME_ENV'] if os.environ['SAME_ENV']!="" else "default"
    except:
      env_var="default"
    return_dataset(env_var)

@pytest.fixture(scope="module")
def return_name(name):
    return "USER_HISTORY"

@pytest.fixture(scope="module")
def return_dataset(return_env):

    urlpar = urlparse(return_yaml['datasets'][return_name][return_env])
    
    url = 'https://gateway.ipfs.io/ipfs/'+urlpar.netloc+urlpar.path if urlpar.scheme=='ipfs' else same_variables['datasets'][name][env_var]
    filename, file_extension = os.path.splitext(url)
    
    extensions = {
      '.csv': 'read_csv',
      '.dta': 'read_stata',
      '.feather': 'read_feather',
      '.html': 'read_html',
      '.json': 'read_json',
      '.orc': 'read_orc',
      '.parquet': 'read_parquet',
      '.pickle': 'read_pickle',
      '.sas': 'read_sas',
      '.sav': 'read_spss',
      '.sql': 'read_sql',
      '.txt': 'read_fwf',
      '.xml': 'read_xml',
      ('.hdf', '.h4', '.hdf4', '.he2', '.h5', '.hdf5', '.he5'): 'read_hdf',
      ('.xlsx', '.ods'): 'read_excel',
    }
    
    for key,value in list(extensions.items()):
      if type(key)==tuple:
        for ext in key:
          extensions[ext]=value
        extensions.pop(key)
    ds=eval("pd."+extensions[file_extension])(url)
    return ds

def test_dataset_csv():
    return_env("")
    assert return_dataset == same.dataset(name="USER_HISTORY")


def test_dataset_ipfs():
    return_env("IPFS")
    assert return_dataset == same.dataset(name="USER_HISTORY")