from random import random, sample
from typing import Mapping
import pytest

example_params = {
    "abcdeABCDE": 16,
    "_-": 8,
    "'`\"": 2,
    "(){}<>": 1,
    "@#$%^&": 1,
}


# An example of how to use genstr(...):
def test_genstr():
    for _ in range(10):
        print(genstr(example_params))


def genstr(params: Mapping[str, int], dp: float = 0.05) -> str:
    """
    Generates a random string where each char is generated with probability
    corresponding to its weight in the `params` mapping.
        :param params: maps strings to their char's weights
        :param p:      tunes the average length of the results
    """
    p = 0.1
    res = ""
    while random() > p:
        res += _genchar(params)
        p += dp

    return res


def _genchar(params: Mapping[str, int]) -> str:
    return sample(sample(params.keys(), 1)[0], 1)[0]
