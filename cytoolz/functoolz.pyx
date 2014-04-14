import inspect
from cpython.dict cimport PyDict_Merge, PyDict_New
from cpython.exc cimport PyErr_Clear, PyErr_ExceptionMatches, PyErr_Occurred
from cpython.object cimport PyCallable_Check, PyObject_Call, PyObject_CallObject
from cpython.ref cimport PyObject
from cpython.sequence cimport PySequence_Concat
from cpython.set cimport PyFrozenSet_New
from cpython.tuple cimport PyTuple_Check, PyTuple_GET_SIZE

# Locally defined bindings that differ from `cython.cpython` bindings
from .cpython cimport PyObject_Call as CyObject_Call


__all__ = ['identity', 'thread_first', 'thread_last', 'memoize', 'compose',
           'pipe', 'complement', 'juxt', 'do', 'curry', 'memoize']


cpdef object identity(object x):
    return x


cdef object c_thread_first(object val, object forms):
    cdef object form, func
    cdef tuple args
    for form in forms:
        if PyCallable_Check(form):
            val = form(val)
        elif PyTuple_Check(form):
            func, args = form[0], (val,) + form[1:]
            val = PyObject_CallObject(func, args)
    return val


def thread_first(val, *forms):
    """ Thread value through a sequence of functions/forms

    >>> def double(x): return 2*x
    >>> def inc(x):    return x + 1
    >>> thread_first(1, inc, double)
    4

    If the function expects more than one input you can specify those inputs
    in a tuple.  The value is used as the first input.

    >>> def add(x, y): return x + y
    >>> def pow(x, y): return x**y
    >>> thread_first(1, (add, 4), (pow, 2))  # pow(add(1, 4), 2)
    25

    So in general
        thread_first(x, f, (g, y, z))
    expands to
        g(f(x), y, z)

    See Also:
        thread_last
    """
    return c_thread_first(val, forms)


cdef object c_thread_last(object val, object forms):
    cdef object form, func
    cdef tuple args
    for form in forms:
        if PyCallable_Check(form):
            val = form(val)
        elif PyTuple_Check(form):
            func, args = form[0], form[1:] + (val,)
            val = PyObject_CallObject(func, args)
    return val


def thread_last(val, *forms):
    """ Thread value through a sequence of functions/forms

    >>> def double(x): return 2*x
    >>> def inc(x):    return x + 1
    >>> thread_last(1, inc, double)
    4

    If the function expects more than one input you can specify those inputs
    in a tuple.  The value is used as the last input.

    >>> def add(x, y): return x + y
    >>> def pow(x, y): return x**y
    >>> thread_last(1, (add, 4), (pow, 2))  # pow(2, add(4, 1))
    32

    So in general
        thread_last(x, f, (g, y, z))
    expands to
        g(y, z, f(x))

    >>> def iseven(x):
    ...     return x % 2 == 0
    >>> list(thread_last([1, 2, 3], (map, inc), (filter, iseven)))
    [2, 4]

    See Also:
        thread_first
    """
    return c_thread_last(val, forms)


cpdef object _num_required_args(object func):
    """ Number of args for func

    >>> def foo(a, b, c=None):
    ...     return a + b + c

    >>> _num_required_args(foo)
    2

    >>> def bar(*args):
    ...     return sum(args)

    >>> print(_num_required_args(bar))
    None
    """
    try:
        spec = inspect.getargspec(func)
        if spec.varargs:
            return None
        num_defaults = len(spec.defaults) if spec.defaults else 0
        return len(spec.args) - num_defaults
    except TypeError:
        pass
    return None


cdef class curry:
    """ Curry a callable function

    Enables partial application of arguments through calling a function with an
    incomplete set of arguments.

    >>> def mul(x, y):
    ...     return x * y
    >>> mul = curry(mul)

    >>> double = mul(2)
    >>> double(10)
    20

    Also supports keyword arguments

    >>> @curry                  # Can use curry as a decorator
    ... def f(x, y, a=10):
    ...     return a * (x + y)

    >>> add = f(a=1)
    >>> add(2, 3)
    5

    See Also:
        cytoolz.curried - namespace of curried functions
                        http://toolz.readthedocs.org/en/latest/curry.html
    """
    property __doc__:
        def __get__(self):
            return self.func.__doc__

    property __name__:
        def __get__(self):
            return self.func.__name__

    def __cinit__(self, func, *args, **kwargs):
        if not PyCallable_Check(func):
            raise TypeError("Input must be callable")

        # curry- or functools.partial-like object?  Unpack and merge arguments
        if (hasattr(func, 'func') and hasattr(func, 'args')
                and hasattr(func, 'keywords')):
            if func.keywords:
                PyDict_Merge(kwargs, func.keywords, False)
                ## Equivalent to:
                # for key, val in func.keywords.items():
                #     if key not in kwargs:
                #         kwargs[key] = val
            args = func.args + args
            func = func.func

        self.func = func
        self.args = args
        self.keywords = kwargs if kwargs else None

    def __str__(self):
        return str(self.func)

    def __repr__(self):
        return repr(self.func)

    def __call__(self, *args, **kwargs):
        cdef PyObject *obj
        cdef object val

        if PyTuple_GET_SIZE(args) == 0:
            args = self.args
        elif PyTuple_GET_SIZE(self.args) != 0:
            args = PySequence_Concat(self.args, args)
        if self.keywords is not None:
            PyDict_Merge(kwargs, self.keywords, False)

        obj = CyObject_Call(self.func, args, kwargs)
        if obj is not NULL:
            val = <object>obj
            return val

        val = <object>PyErr_Occurred()
        if PyErr_ExceptionMatches(TypeError):
            PyErr_Clear()
            required_args = _num_required_args(self.func)
            # If there was a genuine TypeError
            if required_args is None or len(args) < required_args:
                return curry(self.func, *args, **kwargs)
        raise val


cdef class c_memoize:
    property __doc__:
        def __get__(self):
            return self.func.__doc__

    property __name__:
        def __get__(self):
            return self.func.__name__

    def __cinit__(self, func, cache=None, key=None):
        self.func = func
        if cache is None:
            self.cache = PyDict_New()
        else:
            self.cache = cache
        self.key = key

        try:
            spec = inspect.getargspec(func)
            self.may_have_kwargs = bool(not spec or spec.keywords or
                                        spec.defaults)
            # Is unary function (single arg, no variadic argument or keywords)?
            self.is_unary = (spec and spec.varargs is None and
                             not self.may_have_kwargs and len(spec.args) == 1)
        except TypeError:
            self.is_unary = False
            self.may_have_kwargs = True

    def __call__(self, *args, **kwargs):
        cdef object key
        if self.key is not None:
            key = self.key(args, kwargs)
        elif self.is_unary:
            key = args[0]
        elif self.may_have_kwargs:
            key = (args or None,
                   PyFrozenSet_New(kwargs.items()) if kwargs else None)
        else:
            key = args

        if key in self.cache:
            return self.cache[key]
        else:
            result = PyObject_Call(self.func, args, kwargs)
            self.cache[key] = result
            return result


cpdef object memoize(object func=None, object cache=None, object key=None):
    """ Cache a function's result for speedy future evaluation

    Considerations:
        Trades memory for speed.
        Only use on pure functions.

    >>> def add(x, y):  return x + y
    >>> add = memoize(add)

    Or use as a decorator

    >>> @memoize
    ... def add(x, y):
    ...     return x + y

    Use the ``cache`` keyword to provide a dict-like object as an initial cache

    >>> @memoize(cache={(1, 2): 3})
    ... def add(x, y):
    ...     return x + y

    Note that the above works as a decorator because ``memoize`` is curried.

    It is also possible to provide a ``key(args, kwargs)`` function that
    calculates keys used for the cache, which receives an ``args`` tuple and
    ``kwargs`` dict as input, and must return a hashable value.  However,
    the default key function should be sufficient most of the time.

    >>> # Use key function that ignores extraneous keyword arguments
    >>> @memoize(key=lambda args, kwargs: args)
    ... def add(x, y, verbose=False):
    ...     if verbose:
    ...         print('Calculating %s + %s' % (x, y))
    ...     return x + y
    """
    # pseudo-curry
    if func is None:
        return curry(c_memoize, cache=cache, key=key)
    return c_memoize(func, cache=cache, key=key)


cdef class Compose:
    """ A composition of functions

    See Also:
        compose
    """
    def __cinit__(self, *funcs):
        self.firstfunc = funcs[-1]
        self.funcs = tuple(reversed(funcs[:-1]))

    def __call__(self, *args, **kwargs):
        cdef object func, ret
        ret = PyObject_Call(self.firstfunc, args, kwargs)
        for func in self.funcs:
            ret = func(ret)
        return ret


cdef object c_compose(object funcs):
    if not funcs:
        return identity
    elif len(funcs) == 1:
        return funcs[0]
    else:
        return Compose(*funcs)


def compose(*funcs):
    """ Compose functions to operate in series.

    Returns a function that applies other functions in sequence.

    Functions are applied from right to left so that
    ``compose(f, g, h)(x, y)`` is the same as ``f(g(h(x, y)))``.

    If no arguments are provided, the identity function (f(x) = x) is returned.

    >>> inc = lambda i: i + 1
    >>> compose(str, inc)(3)
    '4'

    See Also:
        pipe
    """
    return c_compose(funcs)


cdef object c_pipe(object data, object funcs):
    cdef object func
    for func in funcs:
        data = func(data)
    return data


def pipe(data, *funcs):
    """ Pipe a value through a sequence of functions

    I.e. ``pipe(data, f, g, h)`` is equivalent to ``h(g(f(data)))``

    We think of the value as progressing through a pipe of several
    transformations, much like pipes in UNIX

    ``$ cat data | f | g | h``

    >>> double = lambda i: 2 * i
    >>> pipe(3, double, str)
    '6'

    See Also:
        compose
        thread_first
        thread_last
    """
    return c_pipe(data, funcs)


cdef class complement:
    """ Convert a predicate function to its logical complement.

    In other words, return a function that, for inputs that normally
    yield True, yields False, and vice-versa.

    >>> def iseven(n): return n % 2 == 0
    >>> isodd = complement(iseven)
    >>> iseven(2)
    True
    >>> isodd(2)
    False
    """
    def __cinit__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        return not PyObject_Call(self.func, args, kwargs)  # use PyObject_Not?


cdef class _juxt_inner:
    def __cinit__(self, funcs):
        self.funcs = funcs

    def __call__(self, *args, **kwargs):
        if kwargs:
            return (PyObject_Call(func, args, kwargs) for func in self.funcs)
        else:
            return (PyObject_CallObject(func, args) for func in self.funcs)


cdef object c_juxt(object funcs):
    return _juxt_inner(funcs)


def juxt(*funcs):
    """
    Creates a function that calls several functions with the same arguments.

    Takes several functions and returns a function that applies its arguments
    to each of those functions then returns a sequence of the results.

    Name comes from juxtaposition: the fact of two things being seen or placed
    close together with contrasting effect.

    >>> inc = lambda x: x + 1
    >>> double = lambda x: x * 2
    >>> list(juxt(inc, double)(10))
    [11, 20]
    >>> list(juxt([inc, double])(10))
    [11, 20]
    """
    if len(funcs) == 1 and not PyCallable_Check(funcs[0]):
        funcs = tuple(funcs[0])
    return c_juxt(funcs)



cpdef object do(object func, object x):
    """ Runs ``func`` on ``x``, returns ``x``

    Because the results of ``func`` are not returned, only the side
    effects of ``func`` are relevant.

    Logging functions can be made by composing ``do`` with a storage function
    like ``list.append`` or ``file.write``

    >>> from cytoolz import compose
    >>> from cytoolz.curried import do

    >>> log = []
    >>> inc = lambda x: x + 1
    >>> inc = compose(inc, do(log.append))
    >>> inc(1)
    2
    >>> inc(11)
    12
    >>> log
    [1, 11]

    """
    func(x)
    return x
