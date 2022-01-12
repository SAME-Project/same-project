from itertools import chain
from datetime import datetime
from .context import serialization_utils
import hashlib
import logging
import requests


str_base = str, bytes, bytearray
items = 'items'
_RaiseKeyError = object() # singleton for no-default behavior


GET = "get"
SET = "set"
DEL = "del"


class LazyLoadingNamespace(dict):
    """
    Source: https://stackoverflow.com/a/39375731/3132415
    TODO: Add unit tests.
    """
    __slots__ = (
        'username',
        'tag',
        'connect_timeout_sec',
        'read_timeout_sec',
        'status_query_timeout_sec',
        'retry_interval_sec',
        'get_object_url_base',
        'set_object_url_base',
        'session'
    )
    _access_stats = {
        GET: {},
        SET: {},
        DEL: {},
    }

    def __record_access(self, category: str, k):
        self._access_stats[category][k] = str(datetime.now())

    @staticmethod # because this doesn't make sense as a global function.
    def _process_args(mapping=(), **kwargs):
        if hasattr(mapping, items):
            mapping = getattr(mapping, items)()
        return ((k, v) for k, v in chain(mapping, getattr(kwargs, items)()))

    def __init__(self, username, tag=None, mapping=(), **kwargs):
        super(LazyLoadingNamespace, self).__init__(self._process_args(mapping, **kwargs))
        self.username = username
        self.tag = tag
        self.connect_timeout_sec = 10
        self.read_timeout_sec = 20 * 60
        self.status_query_timeout_sec = 20 * 60
        self.retry_interval_sec = 1
        self.get_object_url_base = "http://localhost:7071/api/get_object"
        self.set_object_url_base = "http://localhost:7071/api/set_object"
        self.session = requests.Session()

    def __get_remote_obj_name(self, k):
        key_hash_int : int = k.__hash__()
        key_hash_bytes = key_hash_int.to_bytes(8, 'big', signed=True)
        obj_name = hashlib.md5(key_hash_bytes).hexdigest()
        if self.tag is not None:
            obj_name = f"{obj_name}_{self.tag}"
        return obj_name

    def __get_from_remote_endpoint(self, k):
        obj_name = self.__get_remote_obj_name(k)
        params = {
            "user": self.username,
            "obj_name": obj_name,
        }
        response = self.session.post(
            self.get_object_url_base,
            params=params,
            timeout=(self.connect_timeout_sec, self.read_timeout_sec))
        if response.status_code != 200:
            raise FileNotFoundError(f"Failed to get object. HTTP response: {response}")
        content_bytes = response.content
        obj = serialization_utils.deserialize_obj(content_bytes)
        return obj

    def __set_at_remote_endpoint(self, k, v):
        obj_name = self.__get_remote_obj_name(k)
        params = {
            "user": self.username,
            "obj_name": obj_name,
        }
        body_bytes = serialization_utils.serialize_obj(v)
        response = self.session.post(
            self.set_object_url_base,
            params=params,
            data=body_bytes,
            timeout=(self.connect_timeout_sec, self.read_timeout_sec))
        if response.status_code != 200:
            raise Exception(f"Failed to set object. HTTP response: {response}")

    def __getitem__(self, k):
        self.__record_access(GET, k)
        if not self.__contains__(k):
            try:
                v = self.__get_from_remote_endpoint(k)
                self.__setitem__(k, v)
                return v
            except FileNotFoundError as e:
                logging.debug(f"Cannot retrieve object from remote endpoint: {k} ({e}), trying locally...")
        return super(LazyLoadingNamespace, self).__getitem__(k)

    def __setitem__(self, k, v):
        self.__record_access(SET, k)
        self.__set_at_remote_endpoint(k, v)
        return super(LazyLoadingNamespace, self).__setitem__(k, v)

    def __delitem__(self, k):
        self.__record_access(DEL, k)
        return super(LazyLoadingNamespace, self).__delitem__(k)

    def get(self, k, default=None):
        self.__record_access(GET, k)
        return super(LazyLoadingNamespace, self).get(k, default)

    def setdefault(self, k, default=None):
        self.__record_access(SET, k)
        return super(LazyLoadingNamespace, self).setdefault(k, default)

    def pop(self, k, v=_RaiseKeyError):
        if v is _RaiseKeyError:
            return super(LazyLoadingNamespace, self).pop(k)
        self.__record_access(DEL, k)
        return super(LazyLoadingNamespace, self).pop(k, v)

    def update(self, mapping=(), **kwargs):
        super(LazyLoadingNamespace, self).update(self._process_args(mapping, **kwargs))

    def __contains__(self, k):
        return super(LazyLoadingNamespace, self).__contains__(k)

    def copy(self): # don't delegate w/ super - dict.copy() -> dict :(
        return type(self)(self)

    @classmethod
    def fromkeys(cls, keys, v=None):
        return super(LazyLoadingNamespace, cls).fromkeys((k for k in keys), v)

    def __repr__(self):
        return '{0}({1})'.format(type(self).__name__, super(LazyLoadingNamespace, self).__repr__())

    def get_access_stats(self):
        return self._access_stats
