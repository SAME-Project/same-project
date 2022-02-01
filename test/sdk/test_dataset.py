# pylint: disable=protected-access,missing-function-docstring, missing-class-docstring
# pylint: disable=missing-module-docstring, missing-class-docstring
# -*- coding: utf-8 -*-
import sameproject as same
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
csv={
    'longitude': [
        -114.31,
        -114.47,
        -114.56,
        -114.57,
        -114.57,
        -114.58,
        -114.58,
        -114.59,
        -114.59,
        -114.6,
        ],
    'latitude': [
        34.19,
        34.4,
        33.69,
        33.64,
        33.57,
        33.63,
        33.61,
        34.83,
        33.61,
        34.83,
        ],
    'housing_median_age': [
        15,
        19,
        17,
        14,
        20,
        29,
        25,
        41,
        34,
        46,
        ],
    'total_rooms': [
        5612,
        7650,
        720,
        1501,
        1454,
        1387,
        2907,
        812,
        4789,
        1497,
        ],
    'total_bedrooms': [
        1283,
        1901,
        174,
        337,
        326,
        236,
        680,
        168,
        1175,
        309,
        ],
    'population': [
        1015,
        1129,
        333,
        515,
        624,
        671,
        1841,
        375,
        3134,
        787,
        ],
    'households': [
        472,
        463,
        117,
        226,
        262,
        239,
        633,
        158,
        1056,
        271,
        ],
    'median_income': [
        1.4936,
        1.82,
        1.6509,
        3.1917,
        1.925,
        3.3438,
        2.6768,
        1.7083,
        2.1782,
        2.1908,
        ],
    'median_house_value': [
        66900,
        80100,
        85700,
        73400,
        65500,
        74000,
        82400,
        48500,
        58400,
        48100,
        ],
    }
json={
	"owl" : [
	    {"item" : "<span class='item'><h1>1</h1></span>"},
	    {"item" : "<span class='item'><h1>2</h1></span>"},
	    {"item" : "<span class='item'><h1>3</h1></span>"},
	    {"item" : "<span class='item'><h1>4</h1></span>"},
	    {"item" : "<span class='item'><h1>5</h1></span>"},
	    {"item" : "<span class='item'><h1>6</h1></span>"},
	    {"item" : "<span class='item'><h1>7</h1></span>"},
	    {"item" : "<span class='item'><h1>8</h1></span>"},
	    {"item" : "<span class='item'><h1>9</h1></span>"},
	    {"item" : "<span class='item'><h1>10</h1></span>"},
	    {"item" : "<span class='item'><h1>11</h1></span>"},
	    {"item" : "<span class='item'><h1>12</h1></span>"},
	    {"item" : "<span class='item'><h1>13</h1></span>"},
	    {"item" : "<span class='item'><h1>14</h1></span>"}
	]
}
def test_dataset_csv():
    os.environ["SAME_ENV"] = ""
    assert list(csv) == list(same.dataset(name="USER_HISTORY"))


def test_dataset_ipfs():
    os.environ["SAME_ENV"] = "IPFS"
    assert list(json) == list(same.dataset(name="USER_HISTORY"))