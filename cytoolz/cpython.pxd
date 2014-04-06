""" Additional bindings to Python's C-API.

These differ from Cython's bindings in ``cpython``.
"""
from cpython.ref cimport PyObject

cdef extern from "Python.h":
    PyObject* PyObject_GetItem(object o, object key)
