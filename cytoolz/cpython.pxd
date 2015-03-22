""" Additional bindings to Python's C-API.

These differ from Cython's bindings in ``cpython``.
"""
from cpython.ref cimport PyObject

cdef extern from "Python.h":
    PyObject* PtrIter_Next "PyIter_Next"(object o)
    PyObject* PtrObject_Call "PyObject_Call"(object callable_object, object args, object kw)
    PyObject* PtrObject_GetItem "PyObject_GetItem"(object o, object key)
    bint PyObject_RichCompareBool_ptr "PyObject_RichCompareBool"(PyObject *o1, PyObject *o2, int opid) except -1
