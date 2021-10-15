from __future__ import annotations
from .json_serializable_object import JSONSerializableObject
from uuid import uuid4


class Step(JSONSerializableObject):
    """Object describing an individual code execution step and its associated metadata.
    This is the unit of execution and is dispatched to a code execution backend.
    """

    def __init__(
        self,
        name: str = "same_step_unset",
        cache_value: str = "P0D",
        environment_name: str = "default",
        tags: list = [],
        index: int = -1,
        code: str = "",
        parameters: list = [],
        packages_to_install: list = []
    ):
        self.name = name
        self.cache_value = cache_value
        self.environment_name = environment_name
        self.tags = tags
        self.index = index
        self.code = code
        self.parameters = parameters
        self.packages_to_install = packages_to_install

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name
        self.unique_step_name = self.__generate_unique_name(name)

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
        """Takes as input a list of Step objects and produces an array of JSON serialized Steps in the same order."""
        steps_serialized = []
        for step in steps_list:
            step_serialized = Step.to_json(step)
            steps_serialized.append(step_serialized)
        return steps_serialized

    # Need a unique name so that libraries don't conflict in sys.modules.
    # This is MOSTLY a test issue, but could be the case generally.
    def __generate_unique_name(self, name) -> str:
        return f"{name}_{uuid4().hex.lower()}"
