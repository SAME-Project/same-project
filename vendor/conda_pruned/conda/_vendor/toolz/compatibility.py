import operator
import sys

PY3 = sys.version_info[0] > 2
PY33 = sys.version_info[0] == 3 and sys.version_info[1] == 3
PY34 = sys.version_info[0] == 3 and sys.version_info[1] == 4
PYPY = hasattr(sys, "pypy_version_info")

__all__ = ("map", "filter", "range", "zip", "reduce", "zip_longest", "iteritems", "iterkeys", "itervalues", "filterfalse", "PY3", "PY34", "PYPY", "import_module")


map = map
filter = filter
range = range
zip = zip
from functools import reduce
from itertools import zip_longest
from itertools import filterfalse

iteritems = operator.methodcaller("items")
iterkeys = operator.methodcaller("keys")
itervalues = operator.methodcaller("values")

try:
    from importlib import import_module
except ImportError:

    def import_module(name):
        __import__(name)
        return sys.modules[name]
