from builtins import filter as filter, map as map, range as range, zip as zip
from functools import reduce as reduce
from itertools import filterfalse as filterfalse, zip_longest as zip_longest
import collections.abc
import typing

__all__ = (
    "map",
    "filter",
    "range",
    "zip",
    "reduce",
    "zip_longest",
    "iteritems",
    "iterkeys",
    "itervalues",
    "filterfalse",
    "PY3",
    "PY34",
    "PYPY",
)

PY3: bool
PY34: bool
PYPY: bool


def iteritems[K, V](mapping: collections.abc.Mapping[K, V]) -> collections.abc.ItemsView[K, V]: ...

def iterkeys[K, V](mapping: collections.abc.Mapping[K, V]) -> collections.abc.KeysView[K]: ...

def itervalues[K, V](mapping: collections.abc.Mapping[K, V]) -> collections.abc.ValuesView[V]: ...
