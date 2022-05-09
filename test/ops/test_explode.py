from sameproject.ops.explode import ExplodingVariable
import pytest
import dill


class ExplodingException(Exception):
    pass


@pytest.fixture
def exploder():
    return ExplodingVariable(ExplodingException())


def test_explode_can_detect(exploder):
    assert exploder.__is_exploding_variable__()

    # Should still be possible after serialisation.
    pickled_exploder = dill.dumps(exploder)
    exploder = dill.loads(pickled_exploder)
    assert exploder.__is_exploding_variable__()


def test_explode_can_pickle(exploder):
    pickled_exploder = dill.dumps(exploder)
    exploder = dill.loads(pickled_exploder)

    # Should contain the same error after deserialising:
    with pytest.raises(ExplodingException):
        print(exploder)


def test_explode_string(exploder):
    with pytest.raises(ExplodingException):
        f"{exploder}"

    with pytest.raises(ExplodingException):
        print(exploder)

    with pytest.raises(ExplodingException):
        repr(exploder)


def test_explode_numeric(exploder):
    with pytest.raises(ExplodingException):
        exploder + 1

    with pytest.raises(ExplodingException):
        exploder += 1

    with pytest.raises(ExplodingException):
        -exploder

    with pytest.raises(ExplodingException):
        abs(exploder)


def test_explode_bool(exploder):
    with pytest.raises(ExplodingException):
        exploder >> 4

    with pytest.raises(ExplodingException):
        exploder & exploder

    with pytest.raises(ExplodingException):
        exploder | exploder

    with pytest.raises(ExplodingException):
        exploder ^ exploder


def test_explode_context(exploder):
    with pytest.raises(ExplodingException):
        with exploder:
            True


def test_explode_class(exploder):
    with pytest.raises(ExplodingException):
        exploder.random()


def test_explode_list(exploder):
    with pytest.raises(ExplodingException):
        exploder[0]

    with pytest.raises(ExplodingException):
        0 in exploder

    with pytest.raises(ExplodingException):
        [0 for x in exploder]

    with pytest.raises(ExplodingException):
        sorted(exploder)

    with pytest.raises(ExplodingException):
        reversed(exploder)

    with pytest.raises(ExplodingException):
        len(exploder)


def test_explode_function(exploder):
    with pytest.raises(ExplodingException):
        exploder()
