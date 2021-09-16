"""
"""


from __future__ import annotations
from typing import Any
from abc import ABC
import json


class JSONSerializableObject(ABC):
    """Abstract class that provides a mechanism to convert to/from JSON format.
    This must only be used for classes where all the fields are JSON serializable.
    Ref: https://medium.com/python-pandemonium/json-the-python-way-91aac95d4041
    """
    @staticmethod
    def to_dict(obj: Any) -> dict:
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


    @staticmethod
    def from_dict(obj_dict: dict) -> Any:
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
            # Use dictionary unpacking to initialize the object
            obj = class_(**obj_dict)
            return obj
        else:
            # Input is not of the appropriate type to be converted into a Step object
            raise TypeError(f"Object cannot be converted to an object of type: {Step.__name__}")


    @staticmethod
    def to_json(obj):
        json_obj = json.dumps(obj, default=JSONSerializableObject.to_dict)
        return json_obj


    @staticmethod
    def from_json(json_obj):
        obj = json.loads(json_obj, object_hook=JSONSerializableObject.from_dict)
        return obj


class Step(JSONSerializableObject):
    """
    """
    def __init__(self,
                 name = "same_step_unset",
                 cache_value = "P0D",
                 environment_name = "default",
                 tags = [],
                 index = -1,
                 code = "",
                 parameters = [],
                 packages_to_install = {}):
        self.name = name
        self.cache_value = cache_value
        self.environment_name = environment_name
        self.tags = tags
        self.index = index
        self.code = code
        self.parameters = parameters
        self.packages_to_install = packages_to_install


    @staticmethod
    def from_json_list(json_serialized_steps: str) -> list[Step]:
        """Takes as input a list of JSON serialized Step objects.
        Each of them is deserialized into a Python Step object and a list of them is returned, sorted by the Step index.
        Note: If any of the deserialization operations fails, an exception will be thrown.
        """
        # List of Step objects to return
        steps = []
        # For each JSON serialized Step object, deserialize it into a Python Step object
        for json_step in json_serialized_steps:
            step = Step.from_json(json_step)
            steps.append(step)
        # Sort the steps in ascending order of their index
        steps_sorted_by_index = sorted(steps, key=lambda x: x.index, reverse=True)
        return steps_sorted_by_index
