"""
Curried versions of Python's operator module functions.

Binary and n-ary operators are curried to support partial application.
Unary operators are not curried (since they only take one argument).

From a typing perspective, curried functions have identical signatures
to their uncurried versions, so we use toolz.curry to wrap them.

Dunder operators (__add__, __mul__, etc.) are aliased to their non-dunder
equivalents (add, mul, etc.) following typeshed's pattern. This reduces
duplication and makes it easier to add overloads in the future.
"""

import operator

# Unary operators and special cases - not curried (from IGNORE set in operator.py)
from operator import (
    __abs__ as __abs__,
    __index__ as __index__,
    __inv__ as __inv__,
    __invert__ as __invert__,
    __neg__ as __neg__,
    __not__ as __not__,
    __pos__ as __pos__,
    abs as abs,
    attrgetter as attrgetter,
    index as index,
    inv as inv,
    invert as invert,
    itemgetter as itemgetter,
    neg as neg,
    not_ as not_,
    pos as pos,
    truth as truth,
)

from ..functoolz import curry

type _CurriedOp = curry[object]

__all__ = [
    # Unary operators and special cases (not curried)
    "__abs__",
    "abs",
    "__index__",
    "index",
    "__inv__",
    "inv",
    "__invert__",
    "invert",
    "__neg__",
    "neg",
    "__not__",
    "not_",
    "__pos__",
    "pos",
    "truth",
    "attrgetter",
    "itemgetter",
    # Binary and n-ary operators (curried)
    "__add__",
    "add",
    "__and__",
    "and_",
    "__call__",
    "call",
    "__concat__",
    "concat",
    "__contains__",
    "contains",
    "countOf",
    "__delitem__",
    "delitem",
    "__eq__",
    "eq",
    "__floordiv__",
    "floordiv",
    "__ge__",
    "ge",
    "__getitem__",
    "getitem",
    "__gt__",
    "gt",
    "__iadd__",
    "iadd",
    "__iand__",
    "iand",
    "__iconcat__",
    "iconcat",
    "__ifloordiv__",
    "ifloordiv",
    "__ilshift__",
    "ilshift",
    "__imatmul__",
    "imatmul",
    "__imod__",
    "imod",
    "__imul__",
    "imul",
    "indexOf",
    "__ior__",
    "ior",
    "__ipow__",
    "ipow",
    "__irshift__",
    "irshift",
    "is_",
    "is_not",
    "__isub__",
    "isub",
    "__itruediv__",
    "itruediv",
    "__ixor__",
    "ixor",
    "__le__",
    "le",
    "length_hint",
    "__lshift__",
    "lshift",
    "__lt__",
    "lt",
    "__matmul__",
    "matmul",
    "methodcaller",
    "__mod__",
    "mod",
    "__mul__",
    "mul",
    "__ne__",
    "ne",
    "__or__",
    "or_",
    "__pow__",
    "pow",
    "__rshift__",
    "rshift",
    "__setitem__",
    "setitem",
    "__sub__",
    "sub",
    "__truediv__",
    "truediv",
    "__xor__",
    "xor",
]

# Binary and n-ary operators - curried
# Define non-dunder versions (canonical), then alias dunder versions

# Arithmetic operators
add: _CurriedOp = curry(operator.add)
__add__ = add

sub: _CurriedOp = curry(operator.sub)
__sub__ = sub

mul: _CurriedOp = curry(operator.mul)
__mul__ = mul

truediv: _CurriedOp = curry(operator.truediv)
__truediv__ = truediv

floordiv: _CurriedOp = curry(operator.floordiv)
__floordiv__ = floordiv

mod: _CurriedOp = curry(operator.mod)
__mod__ = mod

pow: _CurriedOp = curry(operator.pow)
__pow__ = pow

matmul: _CurriedOp = curry(operator.matmul)
__matmul__ = matmul

# Bitwise operators
and_: _CurriedOp = curry(operator.and_)
__and__ = and_

or_: _CurriedOp = curry(operator.or_)
__or__ = or_

xor: _CurriedOp = curry(operator.xor)
__xor__ = xor

lshift: _CurriedOp = curry(operator.lshift)
__lshift__ = lshift

rshift: _CurriedOp = curry(operator.rshift)
__rshift__ = rshift

# Comparison operators
eq: _CurriedOp = curry(operator.eq)
__eq__ = eq

ne: _CurriedOp = curry(operator.ne)
__ne__ = ne

lt: _CurriedOp = curry(operator.lt)
__lt__ = lt

le: _CurriedOp = curry(operator.le)
__le__ = le

gt: _CurriedOp = curry(operator.gt)
__gt__ = gt

ge: _CurriedOp = curry(operator.ge)
__ge__ = ge

# In-place operators
iadd: _CurriedOp = curry(operator.iadd)
__iadd__ = iadd

isub: _CurriedOp = curry(operator.isub)
__isub__ = isub

imul: _CurriedOp = curry(operator.imul)
__imul__ = imul

itruediv: _CurriedOp = curry(operator.itruediv)
__itruediv__ = itruediv

ifloordiv: _CurriedOp = curry(operator.ifloordiv)
__ifloordiv__ = ifloordiv

imod: _CurriedOp = curry(operator.imod)
__imod__ = imod

ipow: _CurriedOp = curry(operator.ipow)
__ipow__ = ipow

imatmul: _CurriedOp = curry(operator.imatmul)
__imatmul__ = imatmul

iand: _CurriedOp = curry(operator.iand)
__iand__ = iand

ior: _CurriedOp = curry(operator.ior)
__ior__ = ior

ixor: _CurriedOp = curry(operator.ixor)
__ixor__ = ixor

ilshift: _CurriedOp = curry(operator.ilshift)
__ilshift__ = ilshift

irshift: _CurriedOp = curry(operator.irshift)
__irshift__ = irshift

# Sequence/container operators
concat: _CurriedOp = curry(operator.concat)
__concat__ = concat

iconcat: _CurriedOp = curry(operator.iconcat)
__iconcat__ = iconcat

contains: _CurriedOp = curry(operator.contains)
__contains__ = contains

getitem: _CurriedOp = curry(operator.getitem)
__getitem__ = getitem

setitem: _CurriedOp = curry(operator.setitem)
__setitem__ = setitem

delitem: _CurriedOp = curry(operator.delitem)
__delitem__ = delitem

# Other binary operators
is_: _CurriedOp = curry(operator.is_)
is_not: _CurriedOp = curry(operator.is_not)

call: _CurriedOp = curry(operator.call)
__call__ = call

# Utility functions
countOf: _CurriedOp = curry(operator.countOf)
indexOf: _CurriedOp = curry(operator.indexOf)
length_hint: _CurriedOp = curry(operator.length_hint)
methodcaller: _CurriedOp = curry(operator.methodcaller)
