#cython: embedsignature=True
from cpython.dict cimport PyDict_GetItem
from cpython.exc cimport (PyErr_Clear, PyErr_ExceptionMatches,
                          PyErr_GivenExceptionMatches, PyErr_Occurred)
from cpython.list cimport (PyList_Append, PyList_GET_ITEM, PyList_GET_SIZE)
from cpython.ref cimport PyObject, Py_DECREF, Py_INCREF, Py_XDECREF
from cpython.sequence cimport PySequence_Check
from cpython.set cimport PySet_Add, PySet_Contains
from cpython.tuple cimport PyTuple_GetSlice, PyTuple_New, PyTuple_SET_ITEM

# Locally defined bindings that differ from `cython.cpython` bindings
from .cpython cimport PtrIter_Next, PtrObject_GetItem

from heapq import heapify, heappop, heapreplace
from itertools import chain, islice
from operator import itemgetter
from .compatibility import map, zip, zip_longest


__all__ = ['remove', 'accumulate', 'groupby', 'merge_sorted', 'interleave',
           'unique', 'isiterable', 'isdistinct', 'take', 'drop', 'take_nth',
           'first', 'second', 'nth', 'last', 'get', 'concat', 'concatv',
           'mapcat', 'cons', 'interpose', 'frequencies', 'reduceby', 'iterate',
           'sliding_window', 'partition', 'partition_all', 'count', 'pluck']


cpdef object identity(object x):
    return x


cdef class remove:
    """ remove(predicate, seq)

    Return those items of collection for which predicate(item) is true.

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
    """ accumulate(binop, seq)

    Repeatedly apply binary function to a sequence, accumulating results

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
    """
    Group a collection by a key function

    >>> names = ['Alice', 'Bob', 'Charlie', 'Dan', 'Edith', 'Frank']
    >>> groupby(len, names)
    {3: ['Bob', 'Dan'], 5: ['Alice', 'Edith', 'Frank'], 7: ['Charlie']}

    >>> iseven = lambda x: x % 2 == 0
    >>> groupby(iseven, [1, 2, 3, 4, 5, 6, 7, 8])
    {False: [1, 3, 5, 7], True: [2, 4, 6, 8]}

    See Also:
        ``countby``
    """
    cdef dict d = {}
    cdef list vals
    cdef PyObject *obj
    cdef object item, key
    for item in seq:
        key = func(item)
        obj = PyDict_GetItem(d, key)
        if obj is NULL:
            d[key] = [item]
        else:
            PyList_Append(<object>obj, item)
    return d


cdef class _merge_sorted:
    def __cinit__(self, seqs):
        cdef Py_ssize_t i
        cdef object item, it
        self.pq = []
        self.shortcut = None

        for i, item in enumerate(seqs):
            it = iter(item)
            try:
                item = next(it)
                PyList_Append(self.pq, [item, i, it])
            except StopIteration:
                pass
        i = PyList_GET_SIZE(self.pq)
        if i == 0:
            self.shortcut = iter([])
        elif i == 1:
            self.shortcut = True
        else:
            heapify(self.pq)

    def __iter__(self):
        return self

    def __next__(self):
        cdef list item
        cdef object retval, it
        # Fast when only a single iterator remains
        if self.shortcut is not None:
            if self.shortcut is True:
                item = self.pq[0]
                self.shortcut = item[2]
                return item[0]
            return next(self.shortcut)

        item = self.pq[0]
        retval = item[0]
        it = item[2]
        try:
            item[0] = next(it)
            heapreplace(self.pq, item)
        except StopIteration:
            heappop(self.pq)
            if PyList_GET_SIZE(self.pq) == 1:
                self.shortcut = True
        return retval


# Having `_merge_sorted` and `_merge_sorted_key` separate violates the DRY
# principle.  The increased performance *barely* justifies this.
# `_merge_sorted` is always faster (sometimes by only 15%), but it can be
# more than 3x faster when a single iterable remains.
#
# The differences in implementation are that `_merge_sorted_key` calls a key
# function on each item (of course), and the layout of the lists in the
# priority queue are different:
#     `_merge_sorted` uses `[item, itnum, iterator]`
#     `_merge_sorted_key` uses `[key(item), itnum, item, iterator]`

cdef class _merge_sorted_key:
    def __cinit__(self, seqs, key):
        cdef Py_ssize_t i
        cdef object item, it, k
        self.pq = []
        self.key = key
        self.shortcut = None

        for i, item in enumerate(seqs):
            it = iter(item)
            try:
                item = next(it)
                k = key(item)
                PyList_Append(self.pq, [k, i, item, it])
            except StopIteration:
                pass
        i = PyList_GET_SIZE(self.pq)
        if i == 0:
            self.shortcut = iter([])
        elif i == 1:
            self.shortcut = True
        else:
            heapify(self.pq)

    def __iter__(self):
        return self

    def __next__(self):
        cdef list item
        cdef object retval, it, k
        # Fast when only a single iterator remains
        if self.shortcut is not None:
            if self.shortcut is True:
                item = self.pq[0]
                self.shortcut = item[3]
                return item[2]
            retval = next(self.shortcut)
            return self.key(retval)

        item = self.pq[0]
        retval = item[2]
        it = item[3]
        try:
            k = next(it)
            item[2] = k
            item[0] = self.key(k)
            heapreplace(self.pq, item)
        except StopIteration:
            heappop(self.pq)
            if PyList_GET_SIZE(self.pq) == 1:
                self.shortcut = True
        return retval


cdef object c_merge_sorted(object seqs, object key=None):
    if key is None:
        return _merge_sorted(seqs)
    return _merge_sorted_key(seqs, key)


def merge_sorted(*seqs, **kwargs):
    """
    Merge and sort a collection of sorted collections

    This works lazily and only keeps one value from each iterable in memory.

    >>> list(merge_sorted([1, 3, 5], [2, 4, 6]))
    [1, 2, 3, 4, 5, 6]

    >>> ''.join(merge_sorted('abc', 'abc', 'abc'))
    'aaabbbccc'

    The "key" function used to sort the input may be passed as a keyword.

    >>> list(merge_sorted([2, 3], [1, 3], key=lambda x: x // 3))
    [2, 1, 3, 3]
    """
    if 'key' in kwargs:
        return c_merge_sorted(seqs, kwargs['key'])
    return c_merge_sorted(seqs)


cdef class interleave:
    """ interleave(seqs, pass_exceptions=())

    Interleave a sequence of sequences

    >>> list(interleave([[1, 2], [3, 4]]))
    [1, 3, 2, 4]

    >>> ''.join(interleave(('ABC', 'XY')))
    'AXBYC'

    Both the individual sequences and the sequence of sequences may be infinite

    Returns a lazy iterator
    """
    def __cinit__(self, seqs, pass_exceptions=()):
        self.iters = [iter(seq) for seq in seqs]
        self.newiters = []
        self.pass_exceptions = tuple(pass_exceptions)
        self.i = 0
        self.n = PyList_GET_SIZE(self.iters)

    def __iter__(self):
        return self

    def __next__(self):
        # This implementation is similar to what is done in `toolz` in that we
        # construct a new list of iterators, `self.newiters`, when a value is
        # successfully retrieved from an iterator from `self.iters`.
        cdef PyObject *obj
        cdef object val

        if self.i == self.n:
            self.n = PyList_GET_SIZE(self.newiters)
            self.i = 0
            if self.n == 0:
                raise StopIteration
            self.iters = self.newiters
            self.newiters = []
        val = <object>PyList_GET_ITEM(self.iters, self.i)
        self.i += 1
        obj = PtrIter_Next(val)

        while obj is NULL:
            obj = PyErr_Occurred()
            if obj is not NULL:
                val = <object>obj
                if not PyErr_GivenExceptionMatches(val, self.pass_exceptions):
                    raise val
                PyErr_Clear()

            if self.i == self.n:
                self.n = PyList_GET_SIZE(self.newiters)
                self.i = 0
                if self.n == 0:
                    raise StopIteration
                self.iters = self.newiters
                self.newiters = []
            val = <object>PyList_GET_ITEM(self.iters, self.i)
            self.i += 1
            obj = PtrIter_Next(val)

        PyList_Append(self.newiters, val)
        val = <object>obj
        Py_XDECREF(obj)
        return val


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
    """
    Return only unique elements of a sequence

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


cpdef object isiterable(object x):
    """
    Is x iterable?

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


cpdef object isdistinct(object seq):
    """
    All values in sequence are distinct

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
            seen.add(item)
        return True
    else:
        return len(seq) == len(set(seq))


cpdef object take(Py_ssize_t n, object seq):
    """
    The first n elements of a sequence

    >>> list(take(2, [10, 20, 30, 40, 50]))
    [10, 20]
    """
    return islice(seq, n)


cpdef object drop(Py_ssize_t n, object seq):
    """
    The sequence following the first n elements

    >>> list(drop(2, [10, 20, 30, 40, 50]))
    [30, 40, 50]
    """
    if n < 0:
        raise ValueError('n argument for drop() must be non-negative')
    cdef Py_ssize_t i
    cdef object iter_seq
    iter_seq = iter(seq)
    try:
        for i in range(n):
            next(iter_seq)
    except StopIteration:
        pass
    return iter_seq


cpdef object take_nth(Py_ssize_t n, object seq):
    """
    Every nth item in seq

    >>> list(take_nth(2, [10, 20, 30, 40, 50]))
    [10, 30, 50]
    """
    return islice(seq, 0, None, n)


cpdef object first(object seq):
    """
    The first element in a sequence

    >>> first('ABC')
    'A'
    """
    return next(iter(seq))


cpdef object second(object seq):
    """
    The second element in a sequence

    >>> second('ABC')
    'B'
    """
    seq = iter(seq)
    next(seq)
    return next(seq)


cpdef object nth(Py_ssize_t n, object seq):
    """
    The nth element in a sequence

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


no_default = '__no__default__'


cpdef object last(object seq):
    """
    The last element in a sequence

    >>> last('ABC')
    'C'
    """
    cdef object val
    if PySequence_Check(seq):
        return seq[-1]
    val = no_default
    for val in seq:
        pass
    if val is no_default:
        raise IndexError
    return val


cpdef object rest(object seq):
    seq = iter(seq)
    next(seq)
    return seq


cdef tuple _get_exceptions = (IndexError, KeyError, TypeError)
cdef tuple _get_list_exc = (IndexError, KeyError)


cpdef object get(object ind, object seq, object default=no_default):
    """
    Get element in a sequence or dict

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
    cdef Py_ssize_t i
    cdef object val
    cdef tuple result
    cdef PyObject *obj
    if isinstance(ind, list):
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
            obj = PtrObject_GetItem(seq, val)
            if obj is NULL:
                if not PyErr_ExceptionMatches(_get_list_exc):
                    raise <object>PyErr_Occurred()
                PyErr_Clear()
                Py_INCREF(default)
                PyTuple_SET_ITEM(result, i, default)
            else:
                val = <object>obj
                Py_INCREF(val)
                PyTuple_SET_ITEM(result, i, val)
        return result

    obj = PtrObject_GetItem(seq, ind)
    if obj is NULL:
        val = <object>PyErr_Occurred()
        if default is no_default:
            raise val
        if PyErr_GivenExceptionMatches(val, _get_exceptions):
            PyErr_Clear()
            return default
        raise val
    return <object>obj


_concat = chain.from_iterable


cpdef object concat(object seqs):
    """
    Concatenate zero or more iterables, any of which may be infinite.

    An infinite sequence will prevent the rest of the arguments from
    being included.

    We use chain.from_iterable rather than chain(*seqs) so that seqs
    can be a generator.

    >>> list(concat([[], [1], [2, 3]]))
    [1, 2, 3]

    See also:
        itertools.chain.from_iterable  equivalent
    """
    return _concat(seqs)


def concatv(*seqs):
    """
    Variadic version of concat

    >>> list(concatv([], ["a"], ["b", "c"]))
    ['a', 'b', 'c']

    See also:
        itertools.chain
    """
    return _concat(seqs)


cpdef object mapcat(object func, object seqs):
    """
    Apply func to each sequence in seqs, concatenating results.

    >>> list(mapcat(lambda s: [c.upper() for c in s],
    ...             [["a", "b"], ["c", "d", "e"]]))
    ['A', 'B', 'C', 'D', 'E']
    """
    return concat(map(func, seqs))


cpdef object cons(object el, object seq):
    """
    Add el to beginning of (possibly infinite) sequence seq.

    >>> list(cons(1, [2, 3]))
    [1, 2, 3]
    """
    return chain((el,), seq)


cdef class interpose:
    """ interpose(el, seq)

    Introduce element between each pair of elements in seq

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
    """
    Find number of occurrences of each value in seq

    >>> frequencies(['cat', 'cat', 'ox', 'pig', 'pig', 'cat'])  #doctest: +SKIP
    {'cat': 3, 'ox': 1, 'pig': 2}

    See Also:
        countby
        groupby
    """
    cdef dict d = {}
    cdef PyObject *obj
    cdef Py_ssize_t val
    for item in seq:
        obj = PyDict_GetItem(d, item)
        if obj is NULL:
            d[item] = 1
        else:
            val = <object>obj
            d[item] = val + 1
    return d


''' Alternative implementation of `frequencies`
cpdef dict frequencies(object seq):
    cdef dict d = {}
    cdef Py_ssize_t val
    for item in seq:
        if item in d:
            val = d[item]
            d[item] = val + 1
        else:
            d[item] = 1
    return d
'''


cpdef dict reduceby(object key, object binop, object seq, object init=no_default):
    """
    Perform a simultaneous groupby and reduction

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
    cdef dict d = {}
    cdef object item, k, val
    cdef PyObject *obj
    for item in seq:
        k = key(item)
        obj = PyDict_GetItem(d, k)
        if obj is NULL:
            if init is no_default:
                val = item
            else:
                val = binop(init, item)
        else:
            val = <object>obj
            val = binop(val, item)
        d[k] = val
    return d


cdef class iterate:
    """ iterate(func, x)

    Repeatedly apply a function func onto an original input

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


cdef class sliding_window:
    """ sliding_window(n, seq)

    A sequence of overlapping subsequences

    >>> list(sliding_window(2, [1, 2, 3, 4]))
    [(1, 2), (2, 3), (3, 4)]

    This function creates a sliding window suitable for transformations like
    sliding means / smoothing

    >>> mean = lambda seq: float(sum(seq)) / len(seq)
    >>> list(map(mean, sliding_window(2, [1, 2, 3, 4])))
    [1.5, 2.5, 3.5]
    """
    def __cinit__(self, Py_ssize_t n, object seq):
        cdef Py_ssize_t i
        self.iterseq = iter(seq)
        self.prev = PyTuple_New(n)
        for i in range(1, n):
            seq = next(self.iterseq)
            Py_INCREF(seq)
            PyTuple_SET_ITEM(self.prev, i, seq)
        self.n = n

    def __iter__(self):
        return self

    def __next__(self):
        cdef tuple current
        cdef object item
        cdef Py_ssize_t i
        current = PyTuple_New(self.n)
        for i in range(1, self.n):
            item = self.prev[i]
            Py_INCREF(item)
            PyTuple_SET_ITEM(current, i-1, item)
        item = next(self.iterseq)
        Py_INCREF(item)
        PyTuple_SET_ITEM(current, self.n-1, item)
        self.prev = current
        return current


no_pad = '__no__pad__'


cpdef object partition(Py_ssize_t n, object seq, object pad=no_pad):
    """
    Partition sequence into tuples of length n

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
    args = [iter(seq)] * n
    if pad is no_pad:
        return zip(*args)
    else:
        return zip_longest(*args, fillvalue=pad)


cdef class partition_all:
    """ partition_all(n, seq)

    Partition all elements of sequence into tuples of length at most n

    The final tuple may be shorter to accommodate extra elements.

    >>> list(partition_all(2, [1, 2, 3, 4]))
    [(1, 2), (3, 4)]

    >>> list(partition_all(2, [1, 2, 3, 4, 5]))
    [(1, 2), (3, 4), (5,)]

    See Also:
        partition
    """
    def __cinit__(self, Py_ssize_t n, object seq):
        self.n = n
        self.iterseq = iter(seq)

    def __iter__(self):
        return self

    def __next__(self):
        cdef tuple result
        cdef object item
        cdef Py_ssize_t i = 0
        result = PyTuple_New(self.n)
        for item in self.iterseq:
            Py_INCREF(item)
            PyTuple_SET_ITEM(result, i, item)
            i += 1
            if i == self.n:
                return result
        # iterable exhausted before filling the tuple
        if i == 0:
            raise StopIteration
        return PyTuple_GetSlice(result, 0, i)


cpdef object count(object seq):
    """
    Count the number of items in seq

    Like the builtin ``len`` but works on lazy sequencies.

    Not to be confused with ``itertools.count``

    See also:
        len
    """
    if iter(seq) is not seq and hasattr(seq, '__len__'):
        return len(seq)
    cdef Py_ssize_t i = 0
    for _ in seq:
        i += 1
    return i


cdef class _pluck_index:
    def __cinit__(self, object ind, object seqs):
        self.ind = ind
        self.iterseqs = iter(seqs)

    def __iter__(self):
        return self

    def __next__(self):
        val = next(self.iterseqs)
        return val[self.ind]


cdef class _pluck_index_default:
    def __cinit__(self, object ind, object seqs, object default):
        self.ind = ind
        self.iterseqs = iter(seqs)

    def __iter__(self):
        return self

    def __next__(self):
        cdef PyObject *obj
        cdef object val
        val = next(self.iterseqs)
        obj = PtrObject_GetItem(val, self.ind)
        if obj is NULL:
            if not PyErr_ExceptionMatches(_get_exceptions):
                raise <object>PyErr_Occurred()
            PyErr_Clear()
            return self.default
        return <object>obj


cdef class _pluck_list:
    def __cinit__(self, list ind not None, object seqs):
        self.ind = ind
        self.iterseqs = iter(seqs)
        self.n = len(ind)

    def __iter__(self):
        return self

    def __next__(self):
        cdef Py_ssize_t i
        cdef tuple result
        cdef object val, seq
        seq = next(self.iterseqs)
        result = PyTuple_New(self.n)
        for i, val in enumerate(self.ind):
            val = seq[val]
            Py_INCREF(val)
            PyTuple_SET_ITEM(result, i, val)
        return result


cdef class _pluck_list_default:
    def __cinit__(self, list ind not None, object seqs, object default):
        self.ind = ind
        self.iterseqs = iter(seqs)
        self.default = default
        self.n = len(ind)

    def __iter__(self):
        return self

    def __next__(self):
        cdef Py_ssize_t i
        cdef object val, seq
        cdef tuple result
        seq = next(self.iterseqs)
        result = PyTuple_New(self.n)
        for i, val in enumerate(self.ind):
            obj = PtrObject_GetItem(seq, val)
            if obj is NULL:
                if not PyErr_ExceptionMatches(_get_list_exc):
                    raise <object>PyErr_Occurred()
                PyErr_Clear()
                Py_INCREF(self.default)
                PyTuple_SET_ITEM(result, i, self.default)
            else:
                val = <object>obj
                Py_INCREF(val)
                PyTuple_SET_ITEM(result, i, val)  # TODO: redefine with "PyObject* val" and avoid cast
        return result


cpdef object pluck(object ind, object seqs, object default=no_default):
    """
    plucks an element or several elements from each item in a sequence.

    ``pluck`` maps ``itertoolz.get`` over a sequence and returns one or more
    elements of each item in the sequence.

    This is equivalent to running `map(curried.get(ind), seqs)`

    ``ind`` can be either a single string/index or a sequence of
    strings/indices.
    ``seqs`` should be sequence containing sequences or dicts.

    e.g.

    >>> data = [{'id': 1, 'name': 'Cheese'}, {'id': 2, 'name': 'Pies'}]
    >>> list(pluck('name', data))
    ['Cheese', 'Pies']
    >>> list(pluck([0, 1], [[1, 2, 3], [4, 5, 7]]))
    [(1, 2), (4, 5)]

    See Also:
        get
        map
    """
    if isinstance(ind, list):
        if default is not no_default:
            return _pluck_list_default(ind, seqs, default)
        if PyList_GET_SIZE(ind) < 10:
            return _pluck_list(ind, seqs)
        return map(itemgetter(*ind), seqs)
    if default is no_default:
        return _pluck_index(ind, seqs)
    return _pluck_index_default(ind, seqs, default)
