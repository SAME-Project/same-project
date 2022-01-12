from __future__ import annotations
from .context import serialization_utils
from .lazy_loading_namespace import LazyLoadingNamespace


class LazyExecutionEnvironment:
    """
    Environment for executing code in.
    This includes the namespaces, imports etc.
    Loading of objects from the namespace is done lazily from the backing store upon accesses.
    """
    def __init__(
        self,
        username: str,
        global_namespace : LazyLoadingNamespace = None,
        local_namespace : LazyLoadingNamespace = None,
    ):
        self.username = username
        self.temporary_entries = set()
        if global_namespace is not None:
            self.global_namespace = global_namespace
        else:
            self.global_namespace = LazyLoadingNamespace(self.username, "global")
        if local_namespace is not None:
            self.local_namespace = local_namespace
        else:
            self.local_namespace = LazyLoadingNamespace(self.username, "local")

    @property
    def global_namespace(self) -> LazyLoadingNamespace:
        return self._global_namespace

    @global_namespace.setter
    def global_namespace(self, global_namespace: LazyLoadingNamespace):
        self._global_namespace = global_namespace

    @property
    def local_namespace(self) -> LazyLoadingNamespace:
        return self._local_namespace

    @local_namespace.setter
    def local_namespace(self, local_namespace: LazyLoadingNamespace):
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
    def deserialize(env_serialized: str) -> LazyExecutionEnvironment:
        env = serialization_utils.deserialize_obj(env_serialized)
        return env

    def serialize(self) -> str:
        """
        Note:
        This operation will remove the temporary entries that might have been added into the
        environment earlier.
        """
        self.remove_temporary_entries()
        env_serialized = serialization_utils.serialize_obj(self)
        return env_serialized

    @property
    def access_stats(self) -> dict:
        access_stats = {
            "global_namespace": self.global_namespace.get_access_stats(),
            "local_namespace": self.local_namespace.get_access_stats(),
        }
        return access_stats
