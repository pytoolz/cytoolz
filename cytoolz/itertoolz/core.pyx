from cpython.dict cimport PyDict_Contains, PyDict_GetItem, PyDict_New, PyDict_SetItem
from cpython.exc cimport PyErr_Clear, PyErr_GivenExceptionMatches, PyErr_Occurred
from cpython.list cimport PyList_Append, PyList_Check, PyList_GET_SIZE, PyList_New
from cpython.ref cimport PyObject, Py_INCREF
from cpython.sequence cimport PySequence_Check
from cpython.set cimport PySet_Add, PySet_Contains
from cpython.tuple cimport PyTuple_New, PyTuple_SET_ITEM

from itertools import chain, islice, izip_longest

from cytoolz.cpython cimport PyObject_GetItem


concatv = chain
concat = chain.from_iterable


cpdef inline object identity(object x):
    return x


# XXX currently unused
cdef class _empty_iterator:
    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration


cdef class remove:
    """ Return those items of collection for which predicate(item) is true.

    >>> def iseven(x):
    ...     return x % 2 == 0
    >>> list(remove(iseven, [1, 2, 3, 4]))
    [1, 3]
    """
    def __cinit__(self, object predicate, object seq):
        self.predicate = predicate
        self.iter_seq = iter(seq)

    def __iter__(self):
        return self

    def __next__(self):
        cdef object val
        val = next(self.iter_seq)
        while self.predicate(val):
            val = next(self.iter_seq)
        return val


cdef class accumulate:
    """ Repeatedly apply binary function to a sequence, accumulating results

    >>> from operator import add, mul
    >>> list(accumulate(add, [1, 2, 3, 4, 5]))
    [1, 3, 6, 10, 15]
    >>> list(accumulate(mul, [1, 2, 3, 4, 5]))
    [1, 2, 6, 24, 120]

    Accumulate is similar to ``reduce`` and is good for making functions like
    cumulative sum:

    >>> from functools import partial, reduce
    >>> sum    = partial(reduce, add)
    >>> cumsum = partial(accumulate, add)

    See Also:
        itertools.accumulate :  In standard itertools for Python 3.2+
    """
    def __cinit__(self, object binop, object seq):
        self.binop = binop
        self.iter_seq = iter(seq)
        self.result = self  # sentinel

    def __iter__(self):
        return self

    def __next__(self):
        cdef object val
        val = next(self.iter_seq)
        if self.result is self:
            self.result = val
        else:
            self.result = self.binop(self.result, val)
        return self.result


cpdef dict groupby(object func, object seq):
    """ Group a collection by a key function

    >>> names = ['Alice', 'Bob', 'Charlie', 'Dan', 'Edith', 'Frank']
    >>> groupby(len, names)
    {3: ['Bob', 'Dan'], 5: ['Alice', 'Edith', 'Frank'], 7: ['Charlie']}

    >>> iseven = lambda x: x % 2 == 0
    >>> groupby(iseven, [1, 2, 3, 4, 5, 6, 7, 8])
    {False: [1, 3, 5, 7], True: [2, 4, 6, 8]}

    See Also:
        ``countby``
    """
    cdef dict d
    cdef list vals
    cdef object item, key
    d = PyDict_New()
    for item in seq:
        key = func(item)
        if PyDict_Contains(d, key):
            PyList_Append(d[key], item)
        else:
            vals = PyList_New(0)
            PyList_Append(vals, item)
            PyDict_SetItem(d, key, vals)
    return d


'''  Alternative implementation of `groupby`
cpdef dict groupby(object func, object seq):
    cdef dict d
    cdef list vals
    cdef object item, key
    cdef PyObject *obj
    d = PyDict_New()
    for item in seq:
        key = func(item)
        obj = PyDict_GetItem(d, key)
        if obj is NULL:
            vals = PyList_New(0)
            PyList_Append(vals, item)
            PyDict_SetItem(d, key, vals)
        else:
            vals = <list>obj
            PyList_Append(vals, item)
    return d
'''


cdef class _unique_key:
    def __cinit__(self, object seq, object key):
        self.iter_seq = iter(seq)
        self.key = key
        self.seen = set()

    def __iter__(self):
        return self

    def __next__(self):
        cdef object item, tag
        item = next(self.iter_seq)
        tag = self.key(item)
        while PySet_Contains(self.seen, tag):
            item = next(self.iter_seq)
            tag = self.key(item)
        PySet_Add(self.seen, tag)
        return item


cdef class _unique_identity:
    def __cinit__(self, object seq):
        self.iter_seq = iter(seq)
        self.seen = set()

    def __iter__(self):
        return self

    def __next__(self):
        cdef object item
        item = next(self.iter_seq)
        while PySet_Contains(self.seen, item):
            item = next(self.iter_seq)
        PySet_Add(self.seen, item)
        return item


cpdef object unique(object seq, object key=identity):
    """ Return only unique elements of a sequence

    >>> tuple(unique((1, 2, 3)))
    (1, 2, 3)
    >>> tuple(unique((1, 2, 1, 3)))
    (1, 2, 3)

    Uniqueness can be defined by key keyword

    >>> tuple(unique(['cat', 'mouse', 'dog', 'hen'], key=len))
    ('cat', 'mouse')
    """
    if key is identity:
        return _unique_identity(seq)
    else:
        return _unique_key(seq, key)


cpdef bint isiterable(object x):
    """ Is x iterable?

    >>> isiterable([1, 2, 3])
    True
    >>> isiterable('abc')
    True
    >>> isiterable(5)
    False
    """
    try:
        iter(x)
        return True
    except TypeError:
        pass
    return False


cpdef bint isdistinct(object seq):
    """ All values in sequence are distinct

    >>> isdistinct([1, 2, 3])
    True
    >>> isdistinct([1, 2, 1])
    False

    >>> isdistinct("Hello")
    False
    >>> isdistinct("World")
    True
    """
    if iter(seq) is seq:
        seen = set()
        for item in seq:
            if PySet_Contains(seen, item):
                return False
            PySet_Add(seen, item)
        return True
    else:
        return len(seq) == len(set(seq))


cpdef inline object take(int n, object seq):
    """ The first n elements of a sequence

    >>> list(take(2, [10, 20, 30, 40, 50]))
    [10, 20]
    """
    return islice(seq, n)


cpdef object drop(int n, object seq):
    """ The sequence following the first n elements

    >>> list(drop(2, [10, 20, 30, 40, 50]))
    [30, 40, 50]
    """
    if n < 0:
        raise ValueError('n argument for drop() must be non-negative')
    cdef int i
    cdef object iter_seq
    i = 0
    iter_seq = iter(seq)
    try:
        while i < n:
            i += 1
            next(iter_seq)
    except StopIteration:
        pass
    return iter_seq


cpdef inline object take_nth(int n, object seq):
    """ Every nth item in seq

    >>> list(take_nth(2, [10, 20, 30, 40, 50]))
    [10, 30, 50]
    """
    return islice(seq, 0, None, n)


cpdef object first(object seq):
    """ The first element in a sequence

    >>> first('ABC')
    'A'
    """
    return next(iter(seq))


cpdef object second(object seq):
    """ The second element in a sequence

    >>> second('ABC')
    'B'
    """
    seq = iter(seq)
    next(seq)
    return next(seq)


cpdef object nth(int n, object seq):
    """ The nth element in a sequence

    >>> nth(1, 'ABC')
    'B'
    """
    if PySequence_Check(seq):
        return seq[n]
    seq = iter(seq)
    while n > 0:
        n -= 1
        next(seq)
    return next(seq)


cpdef object last(object seq):
    """ The last element in a sequence

    >>> last('ABC')
    'C'
    """
    cdef object val
    if PySequence_Check(seq):
        return seq[-1]
    seq = iter(seq)
    try:
        while True:
            val = next(seq)
    except StopIteration:
        pass
    return val


cpdef object rest(object seq):
    seq = iter(seq)
    next(seq)
    return seq


no_default = '__no__default__'


cdef tuple _get_exceptions = (IndexError, KeyError, TypeError)


cpdef object get(object ind, object seq, object default=no_default):
    """ Get element in a sequence or dict

    Provides standard indexing

    >>> get(1, 'ABC')       # Same as 'ABC'[1]
    'B'

    Pass a list to get multiple values

    >>> get([1, 2], 'ABC')  # ('ABC'[1], 'ABC'[2])
    ('B', 'C')

    Works on any value that supports indexing/getitem
    For example here we see that it works with dictionaries

    >>> phonebook = {'Alice':  '555-1234',
    ...              'Bob':    '555-5678',
    ...              'Charlie':'555-9999'}
    >>> get('Alice', phonebook)
    '555-1234'

    >>> get(['Alice', 'Bob'], phonebook)
    ('555-1234', '555-5678')

    Provide a default for missing values

    >>> get(['Alice', 'Dennis'], phonebook, None)
    ('555-1234', None)

    See Also:
        pluck
    """
    cdef int i
    cdef object val
    cdef tuple result
    cdef PyObject *obj
    if PyList_Check(ind):
        i = PyList_GET_SIZE(ind)
        result = PyTuple_New(i)
        # List of indices, no default
        if default is no_default:
            for i, val in enumerate(ind):
                val = seq[val]
                Py_INCREF(val)
                PyTuple_SET_ITEM(result, i, val)
            return result

        # List of indices with default
        for i, val in enumerate(ind):
            obj = PyObject_GetItem(seq, val)
            if obj is NULL:
                PyErr_Clear()
                Py_INCREF(default)
                PyTuple_SET_ITEM(result, i, default)
            else:
                val = <object>obj
                Py_INCREF(val)
                PyTuple_SET_ITEM(result, i, val)
        return result

    obj = PyObject_GetItem(seq, ind)
    if obj is NULL:
        val = <object>PyErr_Occurred()
        if default is no_default:
            raise val
        if PyErr_GivenExceptionMatches(val, _get_exceptions):
            PyErr_Clear()
            return default
        raise val
    return <object>obj


cpdef inline object cons(object el, object seq):
    """ Add el to beginning of (possibly infinite) sequence seq.

    >>> list(cons(1, [2, 3]))
    [1, 2, 3]
    """
    return chain((el,), seq)


cdef class interpose:
    """ Introduce element between each pair of elements in seq

    >>> list(interpose("a", [1, 2, 3]))
    [1, 'a', 2, 'a', 3]
    """
    def __cinit__(self, object el, object seq):
        self.el = el
        self.iter_seq = iter(seq)
        self.do_el = False
        try:
            self.val = next(self.iter_seq)
        except StopIteration:
            self.do_el = True

    def __iter__(self):
        return self

    def __next__(self):
        if self.do_el:
            self.val = next(self.iter_seq)
            self.do_el = False
            return self.el
        else:
            self.do_el = True
            return self.val


cpdef dict frequencies(object seq):
    """ Find number of occurrences of each value in seq

    >>> frequencies(['cat', 'cat', 'ox', 'pig', 'pig', 'cat'])  #doctest: +SKIP
    {'cat': 3, 'ox': 1, 'pig': 2}

    See Also:
        countby
        groupby
    """
    cdef dict d
    cdef PyObject *obj
    cdef int val
    d = PyDict_New()
    for item in seq:
        obj = PyDict_GetItem(d, item)
        if obj is NULL:
            PyDict_SetItem(d, item, 1)
        else:
            val = <object>obj
            PyDict_SetItem(d, item, val + 1)
    return d


''' Alternative implementation of `frequencies`
cpdef dict frequencies(object seq):
    cdef dict d
    cdef int val
    d = PyDict_New()
    for item in seq:
        if PyDict_Contains(d, item):
            val = PyObject_GetItem(d, item)
            PyDict_SetItem(d, item, val + 1)
        else:
            PyDict_SetItem(d, item, 1)
    return d
'''


cpdef dict reduceby(object key, object binop, object seq, object init):
    """ Perform a simultaneous groupby and reduction

    The computation:

    >>> result = reduceby(key, binop, seq, init)      # doctest: +SKIP

    is equivalent to the following:

    >>> def reduction(group):                           # doctest: +SKIP
    ...     return reduce(binop, group, init)           # doctest: +SKIP

    >>> groups = groupby(key, seq)                    # doctest: +SKIP
    >>> result = valmap(reduction, groups)              # doctest: +SKIP

    But the former does not build the intermediate groups, allowing it to
    operate in much less space.  This makes it suitable for larger datasets
    that do not fit comfortably in memory

    >>> from operator import add, mul
    >>> data = [1, 2, 3, 4, 5]
    >>> iseven = lambda x: x % 2 == 0
    >>> reduceby(iseven, add, data, 0)
    {False: 9, True: 6}
    >>> reduceby(iseven, mul, data, 1)
    {False: 15, True: 8}

    >>> projects = [{'name': 'build roads', 'state': 'CA', 'cost': 1000000},
    ...             {'name': 'fight crime', 'state': 'IL', 'cost': 100000},
    ...             {'name': 'help farmers', 'state': 'IL', 'cost': 2000000},
    ...             {'name': 'help farmers', 'state': 'CA', 'cost': 200000}]
    >>> reduceby(lambda x: x['state'],              # doctest: +SKIP
    ...          lambda acc, x: acc + x['cost'],
    ...          projects, 0)
    {'CA': 1200000, 'IL': 2100000}
    """
    cdef dict d
    cdef object item, k, val
    cdef PyObject *obj
    d = PyDict_New()
    for item in seq:
        k = key(item)
        obj = PyDict_GetItem(d, k)
        if obj is NULL:
            val = binop(init, item)
        else:
            val = <object>obj
            val = binop(val, item)
        PyDict_SetItem(d, k, val)
    return d


cdef class iterate:
    """ Repeatedly apply a function func onto an original input

    Yields x, then func(x), then func(func(x)), then func(func(func(x))), etc..

    >>> def inc(x):  return x + 1
    >>> counter = iterate(inc, 0)
    >>> next(counter)
    0
    >>> next(counter)
    1
    >>> next(counter)
    2

    >>> double = lambda x: x * 2
    >>> powers_of_two = iterate(double, 1)
    >>> next(powers_of_two)
    1
    >>> next(powers_of_two)
    2
    >>> next(powers_of_two)
    4
    >>> next(powers_of_two)
    8

    """
    def __cinit__(self, object func, object x):
        self.func = func
        self.x = x
        self.val = self  # sentinel

    def __iter__(self):
        return self

    def __next__(self):
        if self.val is self:
            self.val = self.x
        else:
            self.x = self.func(self.x)
        return self.x


cpdef int count(object seq):
    """ Count the number of items in seq

    Like the builtin ``len`` but works on lazy sequencies.

    Not to be confused with ``itertools.count``

    See also:
        len
    """
    if iter(seq) is not seq and hasattr(seq, '__len__'):
        return len(seq)
    cdef object _
    cdef int i = 0
    for _ in seq:
        i += 1
    return i


no_pad = '__no__pad__'

cdef class partition:
    """ Partition sequence into tuples of length n

    >>> list(partition(2, [1, 2, 3, 4]))
    [(1, 2), (3, 4)]

    If the length of ``seq`` is not evenly divisible by ``n``, the final tuple
    is dropped if ``pad`` is not specified, or filled to length ``n`` by pad:

    >>> list(partition(2, [1, 2, 3, 4, 5]))
    [(1, 2), (3, 4)]

    >>> list(partition(2, [1, 2, 3, 4, 5], pad=None))
    [(1, 2), (3, 4), (5, None)]

    See Also:
        partition_all
    """
    def __cinit__(self, int n, object seq, object pad=no_pad):
        self.n = n
        self.seq = iter(seq)
        self.pad = pad

    def __iter__(self):
        return self

    def __next__(self):
        cdef tuple result
        cdef int i
        cdef object val
        result = PyTuple_New(self.n)
        i = 0
        for val in self.seq:
            PyTuple_SET_ITEM(result, i, val)
            i += 1
            if i == self.n:
                return result

        if self.pad == no_pad or i == 0:
            raise StopIteration()

        else:
            for j in range(i, self.n):
                PyTuple_SET_ITEM(result, j, self.pad)

        return result
