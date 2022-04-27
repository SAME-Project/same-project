from .json_serializable_object import JSONSerializableObject
from uuid import uuid4
from box import Box


class Step(Box):
    """
    Contains an individual code unit along with its associated metadata. Each
    step conceptually represents an individual component within a pipeline, and
    is executed by dispatching the code unit to an execution backend.
    """

    def __init__(
        self,
        name: str,
        cache_value: str,
        environment_name: str,
        tags: list,
        index: int,
        code: str,
        parameters: list,
        packages_to_install: list
    ):
        data = {
            "name": name,
            "cache_value": cache_value,
            "environment_name": environment_name,
            "tags": tags,
            "index": index,
            "code": code,
            "parameters": parameters,
            "packages_to_install": packages_to_install,
        }

        super(Box, self).__init__(
            data,
            frozen_box=True,
        )

    @staticmethod
    def from_json_list(json_serialized_steps):
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
    def to_json_array(steps_list):
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
