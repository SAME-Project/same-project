from cerberus import Validator
from uuid import uuid4
from box import Box


schema = {
    "name": {"type": "string", "required": True},
    "code": {"type": "string", "required": True},
    "index": {"type": "integer", "required": True},
    "cache_value": {"type": "string", "required": True},
    "environment_name": {"type": "string", "required": True},
    "requirements_file": {"type": "string"},
    "tags": {
        "type": "list",
        "required": True,
        "schema": {"type": "string"},
    },
    "parameters": {
        "type": "list",
        "required": True,
        "schema": {"type": "string"},
    },
    "packages_to_install": {
        "type": "list",
        "required": True,
        "schema": {"type": "string"},
    },

    # For preserving unique names when serialising step objects.
    "unique_name": {"type": "string"},
}


def _get_validator():
    return Validator(schema)


def _generate_unique_variant_of(name):
    return f"{name}_{uuid4().hex.lower()}"


class Step(Box):
    """
    Contains an individual code unit along with its associated metadata. Each
    step conceptually represents an individual component within a pipeline,
    # and is executed by dispatching the code unit to an execution backend.
    """

    def __init__(self, *args, frozen_box=True, **kwargs):
        data = Box(*args, **kwargs)
        validator = _get_validator()
        if not validator.validate(data):
            raise SyntaxError(f"Step data is invalid: {validator.errors}")

        # We generate unique names for steps if they don't already have them:
        if "unique_name" not in kwargs:
            kwargs["unique_name"] = _generate_unique_variant_of(kwargs["name"])

        # Uses Box as the child box_class so we don't recursively validate:
        super().__init__(*args, frozen_box=frozen_box, box_class=Box, **kwargs)

    @staticmethod
    def from_json_list(json_steps):
        steps = []
        for json_step in json_steps:
            steps.append(Step.from_json(json_step))
        return steps

    @staticmethod
    def to_json_array(steps_list):
        serialized_steps = []
        for step in steps_list:
            serialized_steps.append(step.to_json())
        return serialized_steps
