#cython: embedsignature=True
from cpython.dict cimport (PyDict_Check, PyDict_GetItem, PyDict_Merge,
                           PyDict_New, PyDict_Next, PyDict_SetItem,
                           PyDict_Update, PyDict_DelItem)
from cpython.exc cimport PyErr_Clear, PyErr_GivenExceptionMatches, PyErr_Occurred
from cpython.list cimport PyList_Append, PyList_New
from cpython.ref cimport PyObject

# Locally defined bindings that differ from `cython.cpython` bindings
from .cpython cimport PtrObject_GetItem


__all__ = ['merge', 'merge_with', 'valmap', 'keymap', 'valfilter', 'keyfilter',
           'assoc', 'dissoc', 'get_in', 'update_in']


cdef dict c_merge(object dicts):
    cdef dict rv
    rv = PyDict_New()
    for d in dicts:
        PyDict_Update(rv, d)
    return rv


def merge(*dicts):
    """
    Merge a collection of dictionaries

    >>> merge({1: 'one'}, {2: 'two'})
    {1: 'one', 2: 'two'}

    Later dictionaries have precedence

    >>> merge({1: 2, 3: 4}, {3: 3, 4: 4})
    {1: 2, 3: 3, 4: 4}

    See Also:
        merge_with
    """
    if len(dicts) == 1 and not PyDict_Check(dicts[0]):
        dicts = dicts[0]
    return c_merge(dicts)


cdef dict c_merge_with(object func, object dicts):
    cdef dict result, rv, d
    cdef object k, v
    cdef PyObject *values
    result = PyDict_New()
    rv = PyDict_New()
    for d in dicts:
        for k, v in d.iteritems():
            values = PyDict_GetItem(result, k)
            if values is NULL:
                PyDict_SetItem(result, k, [v])
            else:
                PyList_Append(<object>values, v)
    for k, v in result.iteritems():
        PyDict_SetItem(rv, k, func(v))
    return rv


def merge_with(func, *dicts):
    """
    Merge dictionaries and apply function to combined values

    A key may occur in more than one dict, and all values mapped from the key
    will be passed to the function as a list, such as func([val1, val2, ...]).

    >>> merge_with(sum, {1: 1, 2: 2}, {1: 10, 2: 20})
    {1: 11, 2: 22}

    >>> merge_with(first, {1: 1, 2: 2}, {2: 20, 3: 30})  # doctest: +SKIP
    {1: 1, 2: 2, 3: 30}

    See Also:
        merge
    """
    if len(dicts) == 1 and not PyDict_Check(dicts[0]):
        dicts = dicts[0]
    return c_merge_with(func, dicts)


cpdef dict valmap(object func, dict d):
    """
    Apply function to values of dictionary

    >>> bills = {"Alice": [20, 15, 30], "Bob": [10, 35]}
    >>> valmap(sum, bills)  # doctest: +SKIP
    {'Alice': 65, 'Bob': 45}

    See Also:
        keymap
    """
    cdef:
        dict rv
        Py_ssize_t pos
        PyObject *k
        PyObject *v

    if d is None:
        raise TypeError("expected dict, got None")

    rv = PyDict_New()
    pos = 0
    while PyDict_Next(d, &pos, &k, &v):
       PyDict_SetItem(rv, <object>k, func(<object>v))
    return rv


cpdef dict keymap(object func, dict d):
    """
    Apply function to keys of dictionary

    >>> bills = {"Alice": [20, 15, 30], "Bob": [10, 35]}
    >>> keymap(str.lower, bills)  # doctest: +SKIP
    {'alice': [20, 15, 30], 'bob': [10, 35]}

    See Also:
        valmap
    """
    cdef:
        dict rv
        Py_ssize_t pos
        PyObject *k
        PyObject *v

    if d is None:
        raise TypeError("expected dict, got None")

    rv = PyDict_New()
    pos = 0
    while PyDict_Next(d, &pos, &k, &v):
       PyDict_SetItem(rv, func(<object>k), <object>v)
    return rv


cpdef dict valfilter(object predicate, dict d):
    """
    Filter items in dictionary by value

    >>> iseven = lambda x: x % 2 == 0
    >>> d = {1: 2, 2: 3, 3: 4, 4: 5}
    >>> valfilter(iseven, d)
    {1: 2, 3: 4}

    See Also:
        keyfilter
        valmap
    """
    cdef:
        dict rv
        Py_ssize_t pos
        PyObject *k
        PyObject *v

    if d is None:
        raise TypeError("expected dict, got None")

    rv = PyDict_New()
    pos = 0
    while PyDict_Next(d, &pos, &k, &v):
        if predicate(<object>v):
            PyDict_SetItem(rv, <object>k, <object>v)
    return rv


cpdef dict keyfilter(object predicate, dict d):
    """
    Filter items in dictionary by key

    >>> iseven = lambda x: x % 2 == 0
    >>> d = {1: 2, 2: 3, 3: 4, 4: 5}
    >>> keyfilter(iseven, d)
    {2: 3, 4: 5}

    See Also:
        valfilter
        keymap
    """
    cdef:
        dict rv
        Py_ssize_t pos
        PyObject *k
        PyObject *v

    if d is None:
        raise TypeError("expected dict, got None")

    rv = PyDict_New()
    pos = 0
    while PyDict_Next(d, &pos, &k, &v):
        if predicate(<object>k):
            PyDict_SetItem(rv, <object>k, <object>v)
    return rv


cpdef dict assoc(dict d, object key, object value):
    """
    Return a new dict with new key value pair

    New dict has d[key] set to value. Does not modify the initial dictionary.

    >>> assoc({'x': 1}, 'x', 2)
    {'x': 2}
    >>> assoc({'x': 1}, 'y', 3)   # doctest: +SKIP
    {'x': 1, 'y': 3}
    """
    cdef dict rv
    rv = d.copy()
    PyDict_SetItem(rv, key, value)
    return rv


cpdef dict dissoc(dict d, object key):
    """
    Return a new dict with the given key removed.

    New dict has d[key] deleted.
    Does not modify the initial dictionary.

    >>> dissoc({'x': 1, 'y': 2}, 'y')
    {'x': 1}
    """
    cdef dict rv
    rv = d.copy()
    PyDict_DelItem(rv, key)
    return rv


cpdef dict update_in(dict d, object keys, object func, object default=None):
    """
    Update value in a (potentially) nested dictionary

    inputs:
    d - dictionary on which to operate
    keys - list or tuple giving the location of the value to be changed in d
    func - function to operate on that value

    If keys == [k0,..,kX] and d[k0]..[kX] == v, update_in returns a copy of the
    original dictionary with v replaced by func(v), but does not mutate the
    original dictionary.

    If k0 is not a key in d, update_in creates nested dictionaries to the depth
    specified by the keys, with the innermost value set to func(default).

    >>> inc = lambda x: x + 1
    >>> update_in({'a': 0}, ['a'], inc)
    {'a': 1}

    >>> transaction = {'name': 'Alice',
    ...                'purchase': {'items': ['Apple', 'Orange'],
    ...                             'costs': [0.50, 1.25]},
    ...                'credit card': '5555-1234-1234-1234'}
    >>> update_in(transaction, ['purchase', 'costs'], sum) # doctest: +SKIP
    {'credit card': '5555-1234-1234-1234',
     'name': 'Alice',
     'purchase': {'costs': 1.75, 'items': ['Apple', 'Orange']}}

    >>> # updating a value when k0 is not in d
    >>> update_in({}, [1, 2, 3], str, default="bar")
    {1: {2: {3: 'bar'}}}
    >>> update_in({1: 'foo'}, [2, 3, 4], inc, 0)
    {1: 'foo', 2: {3: {4: 1}}}
    """
    cdef object prevkey, key
    cdef dict rv, inner, dtemp
    cdef PyObject *obj
    prevkey, keys = keys[0], keys[1:]
    rv = d.copy()
    inner = rv

    for key in keys:
        obj = PyDict_GetItem(d, prevkey)
        if obj is NULL:
            d = PyDict_New()
            dtemp = d
        else:
            d = <object>obj
            dtemp = d.copy()
        PyDict_SetItem(inner, prevkey, dtemp)
        prevkey = key
        inner = dtemp

    obj = PyDict_GetItem(d, prevkey)
    if obj is NULL:
        key = func(default)
    else:
        key = func(<object>obj)
    PyDict_SetItem(inner, prevkey, key)
    return rv


cdef tuple _get_in_exceptions = (KeyError, IndexError, TypeError)


cpdef object get_in(object keys, object coll, object default=None, object no_default=False):
    """
    Returns coll[i0][i1]...[iX] where [i0, i1, ..., iX]==keys.

    If coll[i0][i1]...[iX] cannot be found, returns ``default``, unless
    ``no_default`` is specified, then it raises KeyError or IndexError.

    ``get_in`` is a generalization of ``operator.getitem`` for nested data
    structures such as dictionaries and lists.

    >>> transaction = {'name': 'Alice',
    ...                'purchase': {'items': ['Apple', 'Orange'],
    ...                             'costs': [0.50, 1.25]},
    ...                'credit card': '5555-1234-1234-1234'}
    >>> get_in(['purchase', 'items', 0], transaction)
    'Apple'
    >>> get_in(['name'], transaction)
    'Alice'
    >>> get_in(['purchase', 'total'], transaction)
    >>> get_in(['purchase', 'items', 'apple'], transaction)
    >>> get_in(['purchase', 'items', 10], transaction)
    >>> get_in(['purchase', 'total'], transaction, 0)
    0
    >>> get_in(['y'], {}, no_default=True)  # doctest: +SKIP
    Traceback (most recent call last):
        ...
    KeyError: 'y'

    See Also:
        itertoolz.get
        operator.getitem
    """
    cdef object item
    cdef PyObject *obj
    for item in keys:
        obj = PtrObject_GetItem(coll, item)
        if obj is NULL:
            item = <object>PyErr_Occurred()
            if no_default or not PyErr_GivenExceptionMatches(item, _get_in_exceptions):
                raise item
            PyErr_Clear()
            return default
        coll = <object>obj
    return coll
