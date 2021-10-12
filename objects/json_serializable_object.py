from __future__ import annotations
from typing import Any
from abc import ABC

import json


class JSONSerializableObject(ABC):
    """Abstract class that provides a mechanism to convert to/from JSON format.
    This must only be used for classes where all the fields are JSON serializable.
    Ref: https://medium.com/python-pandemonium/json-the-python-way-91aac95d4041
    """
    @classmethod
    def to_dict(cls, obj: Any) -> dict:
        """Takes in a custom object and returns a dictionary representation of the object.
        This dict representation includes metadata such as the object's module and class names.
        """
        # Populate the dictionary with object metadata
        obj_dict = {
            "__class__": obj.__class__.__name__,
            "__module__": obj.__module__
        }
        # Populate the dictionary with object properties
        obj_dict.update(obj.__dict__)
        return obj_dict

    @classmethod
    def from_dict(cls, obj_dict: dict) -> Any:
        """Takes in a dict and returns a custom object associated with the dict.
        This function makes use of the "__module__" and "__class__" metadata in the dictionary to verify if the correct
        dictionary is being provided.
        """
        if "__class__" in obj_dict:
            # Pop ensures we remove metadata from the dict to leave only the instance arguments
            class_name = obj_dict.pop("__class__")
            # Get the module name from the dict and import it
            module_name = obj_dict.pop("__module__")
            # We use the built in __import__ function since the module name is not yet known at runtime
            module = __import__(module_name, fromlist=[None])
            # Get the class from the module
            class_ = getattr(module, class_name)
            obj = class_()
            for attribute_name, attribute_value in obj_dict.items():
                setattr(obj, attribute_name, attribute_value)
            return obj
        else:
            # Input is not of the appropriate type to be converted into a Step object
            raise TypeError(f"Object cannot be converted to an object of type: {cls.__name__}")

    @classmethod
    def to_json(cls, obj):
        json_obj = json.dumps(obj, default=cls.to_dict)
        return json_obj

    @classmethod
    def from_json(cls, json_obj):
        obj = json.loads(json_obj, object_hook=cls.from_dict)
        return obj
