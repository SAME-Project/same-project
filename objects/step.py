from __future__ import annotations
from .json_serializable_object import JSONSerializableObject


class Step(JSONSerializableObject):
    """Object describing an individual code execution step and its associated metadata.
    This is the unit of execution and is dispatched to a code execution backend.
    """
    def __init__(self,
                 name="same_step_unset",
                 cache_value="P0D",
                 environment_name="default",
                 tags=[],
                 index=-1,
                 code="",
                 parameters=[],
                 packages_to_install={}):
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
        steps = []
        for json_step in json_serialized_steps:
            step = Step.from_json(json_step)
            steps.append(step)
        return steps

    @staticmethod
    def to_json_array(steps_list: list[Step]):
        """Takes as input a list of Step objects and produces an array of JSON serialized Steps in the same order.
        """
        steps_serialized = []
        for step in steps_list:
            step_serialized = Step.to_json(step)
            steps_serialized.append(step_serialized)
        return steps_serialized
