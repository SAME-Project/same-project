import sameproject.ops.runtime_options as opts
import pytest


# Cerberus schemas for testing validation:
alphanum = {
    "nullable": True,
    "type": "string",
    "regex": r"^[\d\w ]+",
}
dockertag = {
    "nullable": True,
    "type": "string",
    "regex": ".*/.*"
}


# Validator functions for testing validation:
def required_for_one(backend, name, opts):
    if backend == "one":
        if name not in opts or opts[name] is None:
            raise Exception(f"Option '{name}' must be set for backend '{backend}'.")


# Runtime options for testing schemas and validation:
opts._register_option(
    "test_one_alphanum", "",
    type=str,
    schema=alphanum,
    validator=required_for_one,
)
opts._register_option(
    "test_one_dockertag", "",
    type=str,
    schema=dockertag,
)


def test_runtime_validation():
    # If we validate for backend 'two', then everything should be fine:
    opts.validate_options("two")

    # Validating for backend 'one' should raise, as we haven't set test_one_alphanum:
    with pytest.raises(Exception):
        opts.validate_options("one")

    # Validating with an invalid value should raise a different exception:
    opts._registry["test_one_alphanum"].value = "invalid$string"
    with pytest.raises(SyntaxError):
        opts.validate_options("one")

    # Validating with an valid value should be fine:
    opts._registry["test_one_alphanum"].value = "valid1234"
    opts.validate_options("one")
