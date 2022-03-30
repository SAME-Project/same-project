from multiprocessing.sharedctypes import Value
from sameproject.same_config import SameConfig
from urllib.parse import urlparse
import pandas as pd
import yaml
import os


def dataset(name, same_file="same.yaml"):
    """
    Imports the dataset with the given name using the configured same
    environment. Currently tested for json, csv and ipfs datasets.
    """
    with open(same_file, "rb+") as file:
        same_config = SameConfig(file)

    if name not in same_config.datasets:
        raise ValueError(f"'{name}' is not a dataset in the same file at '{same_file}'.")

    env = os.environ["SAME_ENV"] or "default"
    if env not in same_config.datasets[name].environments:
        raise ValueError(f"'{env}' is not an environment in the '{name}' dataset in the same file at '{same_file}'.")

    url = urlparse(same_config.datasets[name].environments[env])
    if url.scheme == "ipfs":
        url = "https://gateway.ipfs.io/ipfs/" + url.netloc + url.path
    else:
        url = same_config.datasets[name].environments[env]

    reader = _get_pandas_reader_for(url)
    return reader(url)


def _get_pandas_reader_for(url):
    extensions = {
        ".csv": "read_csv",
        ".dta": "read_stata",
        ".feather": "read_feather",
        ".html": "read_html",
        ".json": "read_json",
        ".orc": "read_orc",
        ".parquet": "read_parquet",
        ".pickle": "read_pickle",
        ".sas": "read_sas",
        ".sav": "read_spss",
        ".sql": "read_sql",
        ".txt": "read_fwf",
        ".xml": "read_xml",
        (".hdf", ".h4", ".hdf4", ".he2", ".h5", ".hdf5", ".he5"): "read_hdf",
        (".xlsx", ".ods"): "read_excel",
    }

    for key, value in list(extensions.items()):
        if type(key) == tuple:
            for ext in key:
                extensions[ext] = value
            extensions.pop(key)

    _, extension = os.path.splitext(url)
    return getattr(pd, extensions[extension])
