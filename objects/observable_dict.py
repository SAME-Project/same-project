from itertools import chain
from datetime import datetime


str_base = str, bytes, bytearray
items = 'items'
_RaiseKeyError = object() # singleton for no-default behavior


GET = "get"
SET = "set"
DEL = "del"


class ObservableDict(dict):
    """
    Source: https://stackoverflow.com/a/39375731/3132415
    TODO: Add unit tests.
    """
    __slots__ = () # no __dict__ - that would be redundant
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

    def __init__(self, mapping=(), **kwargs):
        super(ObservableDict, self).__init__(self._process_args(mapping, **kwargs))

    def __getitem__(self, k):
        self.__record_access(GET, k)
        return super(ObservableDict, self).__getitem__(k)

    def __setitem__(self, k, v):
        self.__record_access(SET, k)
        return super(ObservableDict, self).__setitem__(k, v)

    def __delitem__(self, k):
        self.__record_access(DEL, k)
        return super(ObservableDict, self).__delitem__(k)

    def get(self, k, default=None):
        self.__record_access(GET, k)
        return super(ObservableDict, self).get(k, default)

    def setdefault(self, k, default=None):
        self.__record_access(SET, k)
        return super(ObservableDict, self).setdefault(k, default)

    def pop(self, k, v=_RaiseKeyError):
        if v is _RaiseKeyError:
            return super(ObservableDict, self).pop(k)
        self.__record_access(DEL, k)
        return super(ObservableDict, self).pop(k, v)

    def update(self, mapping=(), **kwargs):
        super(ObservableDict, self).update(self._process_args(mapping, **kwargs))

    def __contains__(self, k):
        return super(ObservableDict, self).__contains__(k)

    def copy(self): # don't delegate w/ super - dict.copy() -> dict :(
        return type(self)(self)

    @classmethod
    def fromkeys(cls, keys, v=None):
        return super(ObservableDict, cls).fromkeys((k for k in keys), v)

    def __repr__(self):
        return '{0}({1})'.format(type(self).__name__, super(ObservableDict, self).__repr__())

    def get_access_stats(self):
        return self._access_stats
