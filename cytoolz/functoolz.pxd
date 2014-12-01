cpdef object identity(object x)


cdef object c_thread_first(object val, object forms)


cdef object c_thread_last(object val, object forms)


cdef class Curry:
    cdef readonly object func
    cdef readonly tuple args
    cdef readonly dict keywords
    cdef public object __doc__
    cdef public object __name__
    cdef public object _numargs


cdef class c_memoize:
    cdef object func
    cdef object cache
    cdef object key
    cdef bint is_unary
    cdef bint may_have_kwargs


cpdef object memoize(object func=*, object cache=*, object key=*)


cdef class Compose:
    cdef object firstfunc
    cdef tuple funcs


cdef object c_compose(object funcs)


cdef object c_pipe(object data, object funcs)


cdef class complement:
    cdef object func


cdef class _juxt_inner:
    cdef public tuple funcs


cdef object c_juxt(object funcs)


cpdef object do(object func, object x)
