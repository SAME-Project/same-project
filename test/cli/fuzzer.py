from random import random, sample
from typing import Mapping
import pytest

# A simple parameter mapping that mostly generates alphanums, but occasionally
# includes some special characters of different kinds.
std = {
    "abcdeABCDE1234": 16,
    "_-": 8,
    "\\/": 2,
    "@#$%^&": 2,
    "'`\"": 1,
    "(){}<>": 1,
}

# A parameter mapping for generating file names.
file = {
    "abcdeABCDE1234": 16,
    "_-": 8,
    "@#$%^&": 2,
    "(){}<>": 1,
}


def genstr(params: Mapping[str, int], dp: float = 0.05, minlen: int = 0) -> str:
    """
    Generates a random string where each char is generated with probability
    corresponding to its weight in the `params` mapping.
        :param params: maps strings to their char's weights
        :param p:      tunes the average length of the results
        :param minlen: minimum length of a string to generate
    """
    p = 0.1
    res = ""
    while len(res) < minlen or random() > p:
        res += _genchar(params)
        p += dp

    return res


def _genchar(params: Mapping[str, int]) -> str:
    return sample(sample(params.keys(), 1)[0], 1)[0]
