from sameproject.data.example import Example
import pytest


@pytest.fixture
def example():
    return Example({"example": "test"})


def test_data_example_immutable(example):
    # Example boxes should be immutable by default.
    with pytest.raises(Exception):
        example.field = "value"


def test_data_example_json(example):
    # Example boxes should support json serialisation.
    example_p = Example.from_json(example.to_json())
    assert example_p.example == example.example


def test_data_example_yaml(example):
    # Example boxes should support yaml serialisation.
    example_p = Example.from_yaml(example.to_yaml())
    assert example_p.example == example.example
