# An example of an easy way to create data objects that can be validated and
# serialised to/from json, yaml and dictionary objects. Standard Box functions
# like from_json, to_json, from_yaml etc work with validation.

from cerberus import Validator
from box import Box


schema = {
    "string": {"type": "string", "required": True},
    "dict": {"type": "dict", "required": True},
}


def _get_validator():
    return Validator(schema)


class Example(Box):
    def __init__(self, *args, frozen_box=True, **kwargs):
        data = Box(*args, **kwargs)
        validator = _get_validator()
        if not validator.validate(data):
            raise SyntaxError(f"Example data is invalid: {validator.errors}")

        # Uses Box as the child box_class so we don't recursively validate:
        super().__init__(*args, frozen_box=frozen_box, box_class=Box, **kwargs)
