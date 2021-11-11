from __future__ import annotations
from .context import serialization_utils


class ExecutionEnvironment:
    """
    Environment for executing code in.
    This includes the namespaces, imports etc.
    TODO: Add imports.
    TODO: Add ability to update namespaces and serialize only diffs.
    """
    def __init__(self, global_namespace : dict = {}, local_namespace : dict = {}):
        self.global_namespace = global_namespace
        self.local_namespace = local_namespace
        self.temporary_entries = set()

    @property
    def global_namespace(self) -> dict:
        return self._global_namespace

    @global_namespace.setter
    def global_namespace(self, global_namespace: dict):
        self._global_namespace = global_namespace

    @property
    def local_namespace(self) -> dict:
        return self._local_namespace

    @local_namespace.setter
    def local_namespace(self, local_namespace: dict):
        self._local_namespace = local_namespace

    def add_to_temporary_global_namespace(self, key, value):
        if key in self.global_namespace:
            raise Exception(f"Key already exists in global namespace: {key}")
        self.temporary_entries.add(key)
        self.global_namespace[key] = value

    def remove_temporary_entries(self):
        for key in self.temporary_entries:
            del self.global_namespace[key]
        self.temporary_entries.clear()

    @staticmethod
    def deserialize(env_serialized: str) -> ExecutionEnvironment:
        env = serialization_utils.deserialize_obj(env_serialized)
        return env

    @staticmethod
    def serialize(env: ExecutionEnvironment) -> str:
        env.remove_temporary_entries()
        env_serialized = serialization_utils.serialize_obj(env)
        return env_serialized
