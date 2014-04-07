cdef class remove:
    cdef object predicate
    cdef object iter_seq


cdef class accumulate:
    cdef object binop
    cdef object iter_seq
    cdef object result


cpdef dict groupby(object func, object seq)


cdef class _unique_key:
    cdef object key
    cdef object iter_seq
    cdef object seen


cdef class _unique_identity:
    cdef object iter_seq
    cdef object seen


cdef class partition:
    cdef int n
    cdef object seq
    cdef object pad


cpdef object unique(object seq, object key=*)


cpdef bint isiterable(object x)


cpdef bint isdistinct(object seq)


cpdef inline object take(int n, object seq)


cpdef object drop(int n, object seq)


cpdef inline object take_nth(int n, object seq)


cpdef object first(object seq)


cpdef object second(object seq)


cpdef object nth(int n, object seq)


cpdef object last(object seq)


cpdef object rest(object seq)


cpdef object get(object ind, object seq, object default=*)


cpdef inline object cons(object el, object seq)


cdef class interpose:
    cdef object el
    cdef object iter_seq
    cdef object val
    cdef bint do_el


cpdef dict frequencies(object seq)


cpdef dict reduceby(object key, object binop, object seq, object init)


cdef class iterate:
    cdef object func
    cdef object x
    cdef object val


cpdef int count(object seq)
