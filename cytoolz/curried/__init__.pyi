# pyright: reportAny=false, reportUnreachable=false
"""
Stubs for toolz.curried - an alternate namespace where functions are curried.

This module uses three patterns:
1. Direct re-exports: Non-curried functions imported from relative modules.
2. Explicit overloads: Curried functions with bespoke type signatures for precise inference
    (e.g., accumulate, assoc, do, filter, map).
3. Curry wrappers: Curried functions using curry(module.func).
    Placeholders until explicit overloads are added.
    See https://github.com/mgrinshpon/toolz-stubs/issues/16 to help.
"""

import collections.abc
import functools
import sys
import typing

from _typeshed import SupportsRichComparison

if sys.version_info >= (3, 13):
    from typing import TypeIs
else:
    from typing_extensions import TypeIs

from .. import dicttoolz as _dicttoolz, itertoolz as _itertoolz, recipes as _recipes
from ..functoolz import (
    apply as apply,
    complement as complement,
    compose as comp,
    compose as compose,
    compose_left as compose_left,
    curry as curry,
    excepts as _excepts_func,
    flip as flip,
    identity as identity,
    juxt as juxt,
    memoize as memoize,
    pipe as pipe,
    thread_first as thread_first,
    thread_last as thread_last,
)
from ..itertoolz import (
    concat as concat,
    concatv as concatv,
    count as count,
    diff as diff,
    first as first,
    frequencies as frequencies,
    interleave as interleave,
    isdistinct as isdistinct,
    isiterable as isiterable,
    last as last,
    merge_sorted as merge_sorted,
    peek as peek,
    second as second,
)

# All functions from operator module are re-exported here.
# Binary and n-ary functions are curried; unary functions are not.
# From a typing perspective, curried functions have identical signatures.
from . import operator
from .exceptions import merge, merge_with

class _AnyCallable[ReturnT](typing.Protocol):
    def __call__(self, *args: object, **kwargs: object) -> ReturnT: ...

type _Curried = curry[object]

__all__ = [
    # Curried functions (defined in this module)
    "accumulate",
    "assoc",
    "assoc_in",
    "cons",
    "countby",
    "dissoc",
    "do",
    "drop",
    "excepts",
    "filter",
    "get",
    "get_in",
    "groupby",
    "interpose",
    "itemfilter",
    "itemmap",
    "iterate",
    "join",
    "keyfilter",
    "keymap",
    "map",
    "mapcat",
    "nth",
    "partial",
    "partition",
    "partition_all",
    "partitionby",
    "peekn",
    "pluck",
    "random_sample",
    "reduce",
    "reduceby",
    "remove",
    "sliding_window",
    "sorted",
    "tail",
    "take",
    "take_nth",
    "topk",
    "unique",
    "update_in",
    "valfilter",
    "valmap",
    # Re-exported (not curried)
    "apply",
    "comp",
    "complement",
    "compose",
    "compose_left",
    "concat",
    "concatv",
    "count",
    "curry",
    "diff",
    "first",
    "flip",
    "frequencies",
    "identity",
    "interleave",
    "isdistinct",
    "isiterable",
    "juxt",
    "last",
    "memoize",
    "merge_sorted",
    "peek",
    "pipe",
    "second",
    "thread_first",
    "thread_last",
    # Re-exported from .exceptions
    "merge",
    "merge_with",
    # Submodule
    "operator",
]

# Curried accumulate with explicit overloads for type safety
# Stage 0: No arguments - returns a callable
@typing.overload
def accumulate[T]() -> _AnyCallable[collections.abc.Iterator[T]]: ...

# Stage 1: Just binop - returns callable waiting for seq (and optional initial)
@typing.overload
def accumulate[T](
    binop: typing.Callable[[T, T], T], /
) -> _AnyCallable[collections.abc.Iterator[T]]: ...

# Stage 2a: binop + seq (no initial) - executes immediately
@typing.overload
def accumulate[T](
    binop: typing.Callable[[T, T], T], seq: collections.abc.Iterable[T], /
) -> collections.abc.Iterator[T]: ...

# Stage 2b: binop + seq + initial - executes immediately
@typing.overload
def accumulate[T](
    binop: typing.Callable[[T, T], T],
    seq: collections.abc.Iterable[T],
    initial: T,
    /,
) -> collections.abc.Iterator[T]: ...
@typing.overload
def assoc[K, V]() -> _AnyCallable[dict[K, V] | collections.abc.MutableMapping[K, V]
]: ...
@typing.overload
def assoc[K, V](
    d: collections.abc.Mapping[K, V], /
) -> _AnyCallable[dict[K, V] | collections.abc.MutableMapping[K, V]]: ...
@typing.overload
def assoc[K, V](
    d: collections.abc.Mapping[K, V], key: K, /
) -> typing.Callable[[V], dict[K, V]]: ...
@typing.overload
def assoc[K, V](
    d: collections.abc.Mapping[K, V],
    key: K,
    /,
    *,
    factory: typing.Callable[[], collections.abc.MutableMapping[K, V]],
) -> typing.Callable[[V], collections.abc.MutableMapping[K, V]]: ...
@typing.overload
def assoc[K, V](
    d: collections.abc.Mapping[K, V], key: K, value: V, /
) -> dict[K, V]: ...
@typing.overload
def assoc[K, V](
    d: collections.abc.Mapping[K, V],
    key: K,
    value: V,
    /,
    *,
    factory: typing.Callable[[], collections.abc.MutableMapping[K, V]],
) -> collections.abc.MutableMapping[K, V]: ...
assoc_in: _Curried = curry(_dicttoolz.assoc_in)

# Curried cons with explicit overloads for type safety
# Stage 0: No arguments - returns a callable
@typing.overload
def cons[T]() -> _AnyCallable[collections.abc.Iterator[T]]: ...

# Stage 1: Just el - returns callable waiting for seq
@typing.overload
def cons[T](
    el: T, /
) -> typing.Callable[[collections.abc.Iterable[T]], collections.abc.Iterator[T]]: ...

# Stage 2: Full application - executes immediately
@typing.overload
def cons[T](
    el: T, seq: collections.abc.Iterable[T], /
) -> collections.abc.Iterator[T]: ...
countby: _Curried = curry(_recipes.countby)
dissoc: _Curried = curry(_dicttoolz.dissoc)
excepts: _Curried = curry(_excepts_func)

# Curried do with explicit overloads for type safety
# Stage 0: No arguments - returns a callable
@typing.overload
def do[T]() -> _AnyCallable[T]: ...

# Stage 1: Just func - returns callable waiting for x
@typing.overload
def do[T](func: typing.Callable[[T], object], /) -> typing.Callable[[T], T]: ...

# Stage 2: Full application - executes immediately
@typing.overload
def do[T](func: typing.Callable[[T], object], x: T, /) -> T: ...
@typing.overload
def drop[T]() -> _AnyCallable[collections.abc.Iterator[T]]: ...
@typing.overload
def drop[T](
    n: int, /
) -> typing.Callable[[collections.abc.Iterable[T]], collections.abc.Iterator[T]]: ...
@typing.overload
def drop[T](
    n: int, seq: collections.abc.Iterable[T], /
) -> collections.abc.Iterator[T]: ...
@typing.overload
def filter[T]() -> _AnyCallable[collections.abc.Iterator[T] | _AnyCallable[collections.abc.Iterator[T]]
]: ...
@typing.overload
def filter[T](
    function: None, /
) -> typing.Callable[
    [collections.abc.Iterable[T | None]], collections.abc.Iterator[T]
]: ...
@typing.overload
def filter[S, T](
    function: typing.Callable[[S], typing.TypeGuard[T]], /
) -> typing.Callable[[collections.abc.Iterable[S]], collections.abc.Iterator[T]]: ...
@typing.overload
def filter[S, T](
    function: typing.Callable[[S], TypeIs[T]], /
) -> typing.Callable[[collections.abc.Iterable[S]], collections.abc.Iterator[T]]: ...
@typing.overload
def filter[T](
    function: typing.Callable[[T], object], /
) -> typing.Callable[[collections.abc.Iterable[T]], collections.abc.Iterator[T]]: ...
@typing.overload
def filter[T](
    function: None, iterable: collections.abc.Iterable[T | None], /
) -> collections.abc.Iterator[T]: ...
@typing.overload
def filter[S, T](
    function: typing.Callable[[S], typing.TypeGuard[T]],
    iterable: collections.abc.Iterable[S],
    /,
) -> collections.abc.Iterator[T]: ...
@typing.overload
def filter[S, T](
    function: typing.Callable[[S], TypeIs[T]],
    iterable: collections.abc.Iterable[S],
    /,
) -> collections.abc.Iterator[T]: ...
@typing.overload
def filter[T](
    function: typing.Callable[[T], object],
    iterable: collections.abc.Iterable[T],
    /,
) -> collections.abc.Iterator[T]: ...
@typing.overload
def get[T]() -> _AnyCallable[T | tuple[T, ...]]: ...
@typing.overload
def get[T](
    ind: object, /
) -> (
    typing.Callable[
        [collections.abc.Sequence[T] | collections.abc.Mapping[object, T]],
        T | tuple[T, ...],
    ]
    | typing.Callable[
        [collections.abc.Sequence[T] | collections.abc.Mapping[object, T], T],
        T | tuple[T, ...],
    ]
): ...
@typing.overload
def get[T](
    ind: collections.abc.Sequence[object],
    seq: collections.abc.Sequence[T] | collections.abc.Mapping[object, T],
    /,
) -> tuple[T, ...]: ...
@typing.overload
def get[T](
    ind: object,
    seq: collections.abc.Sequence[T] | collections.abc.Mapping[object, T],
    /,
) -> T: ...
@typing.overload
def get[T](
    ind: collections.abc.Sequence[object],
    seq: collections.abc.Sequence[T] | collections.abc.Mapping[object, T],
    default: T,
    /,
) -> tuple[T, ...]: ...
@typing.overload
def get[T](
    ind: object,
    seq: collections.abc.Sequence[T] | collections.abc.Mapping[object, T],
    default: T,
    /,
) -> T: ...
get_in: _Curried = curry(_dicttoolz.get_in)

@typing.overload
def groupby[KT, T]() -> _AnyCallable[dict[KT, list[T]]]: ...
@typing.overload
def groupby[T](
    key: object, /
) -> typing.Callable[[collections.abc.Iterable[T]], dict[object, list[T]]]: ...
@typing.overload
def groupby[T](
    key: object, seq: collections.abc.Iterable[T], /
) -> dict[object, list[T]]: ...
# Curried interpose with explicit overloads for type safety
# Stage 0: No arguments - returns a callable
@typing.overload
def interpose[T]() -> _AnyCallable[collections.abc.Iterator[T]]: ...

# Stage 1: Just el - returns callable waiting for seq
@typing.overload
def interpose[T](
    el: T, /
) -> typing.Callable[[collections.abc.Iterable[T]], collections.abc.Iterator[T]]: ...

# Stage 2: Full application - executes immediately
@typing.overload
def interpose[T](
    el: T, seq: collections.abc.Iterable[T], /
) -> collections.abc.Iterator[T]: ...
@typing.overload
def itemfilter[K, V]() -> _AnyCallable[dict[K, V] | collections.abc.MutableMapping[K, V]
]: ...

# Stage 1a: Just predicate (no factory) - returns callable waiting for dict
@typing.overload
def itemfilter[K, V](
    predicate: typing.Callable[[tuple[K, V]], bool], /
) -> typing.Callable[[collections.abc.Mapping[K, V]], dict[K, V]]: ...

# Stage 1b: Predicate with factory - returns callable waiting for dict
@typing.overload
def itemfilter[K, V](
    predicate: typing.Callable[[tuple[K, V]], bool],
    /,
    *,
    factory: typing.Callable[[], collections.abc.MutableMapping[K, V]],
) -> typing.Callable[
    [collections.abc.Mapping[K, V]], collections.abc.MutableMapping[K, V]
]: ...

# Stage 2a: Full application (no factory) - executes immediately
@typing.overload
def itemfilter[K, V](
    predicate: typing.Callable[[tuple[K, V]], bool],
    d: collections.abc.Mapping[K, V],
    /,
) -> dict[K, V]: ...

# Stage 2b: Full application (with factory) - executes immediately
@typing.overload
def itemfilter[K, V](
    predicate: typing.Callable[[tuple[K, V]], bool],
    d: collections.abc.Mapping[K, V],
    /,
    *,
    factory: typing.Callable[[], collections.abc.MutableMapping[K, V]],
) -> collections.abc.MutableMapping[K, V]: ...
@typing.overload
def itemmap[K0, V0, K1, V1]() -> _AnyCallable[dict[K1, V1] | collections.abc.MutableMapping[K1, V1]
]: ...

# Stage 1a: Just func (no factory) - returns callable waiting for dict
@typing.overload
def itemmap[K0, V0, K1, V1](
    func: typing.Callable[[tuple[K0, V0]], tuple[K1, V1]], /
) -> typing.Callable[[collections.abc.Mapping[K0, V0]], dict[K1, V1]]: ...

# Stage 1b: Func with factory - returns callable waiting for dict
@typing.overload
def itemmap[K0, V0, K1, V1](
    func: typing.Callable[[tuple[K0, V0]], tuple[K1, V1]],
    /,
    *,
    factory: typing.Callable[[], collections.abc.MutableMapping[K1, V1]],
) -> typing.Callable[
    [collections.abc.Mapping[K0, V0]], collections.abc.MutableMapping[K1, V1]
]: ...

# Stage 2a: Full application (no factory) - executes immediately
@typing.overload
def itemmap[K0, V0, K1, V1](
    func: typing.Callable[[tuple[K0, V0]], tuple[K1, V1]],
    d: collections.abc.Mapping[K0, V0],
    /,
) -> dict[K1, V1]: ...

# Stage 2b: Full application (with factory) - executes immediately
@typing.overload
def itemmap[K0, V0, K1, V1](
    func: typing.Callable[[tuple[K0, V0]], tuple[K1, V1]],
    d: collections.abc.Mapping[K0, V0],
    /,
    *,
    factory: typing.Callable[[], collections.abc.MutableMapping[K1, V1]],
) -> collections.abc.MutableMapping[K1, V1]: ...
# Curried iterate with explicit overloads for type safety
# Stage 0: No arguments - returns a callable
@typing.overload
def iterate[T]() -> _AnyCallable[collections.abc.Iterator[T]]: ...

# Stage 1: Just func - returns callable waiting for x
@typing.overload
def iterate[T](
    func: typing.Callable[[T], T], /
) -> typing.Callable[[T], collections.abc.Iterator[T]]: ...

# Stage 2: Full application - executes immediately
@typing.overload
def iterate[T](
    func: typing.Callable[[T], T], x: T, /
) -> collections.abc.Iterator[T]: ...
# Curried join with explicit overloads for type safety
# Stage 0: No arguments - returns a callable
@typing.overload
def join[T, U]() -> _AnyCallable[collections.abc.Iterator[tuple[T, U]]]: ...

# Stage 1: Just leftkey - returns a callable
@typing.overload
def join[T, U](
    leftkey: typing.Callable[[T], typing.Hashable], /
) -> _AnyCallable[collections.abc.Iterator[tuple[T, U]]]: ...

# Stage 2: leftkey + leftseq - returns a callable
@typing.overload
def join[T, U](
    leftkey: typing.Callable[[T], typing.Hashable],
    leftseq: collections.abc.Iterable[T],
    /,
) -> _AnyCallable[collections.abc.Iterator[tuple[T, U]]]: ...

# Stage 3: leftkey + leftseq + rightkey - returns callable waiting for rightseq
# This is the key overload for pipe usage!
# Note: We use object for U because U can't be inferred until rightseq is provided.
# The callable will properly infer types when called with rightseq.
@typing.overload
def join[T](
    leftkey: typing.Callable[[T], typing.Hashable],
    leftseq: collections.abc.Iterable[T],
    rightkey: _AnyCallable[typing.Hashable],
    /,
) -> typing.Callable[
    [collections.abc.Iterable[object]],
    collections.abc.Iterator[tuple[T, object]],
]: ...

# Stage 4a: Full application (inner join) - executes immediately
@typing.overload
def join[T, U](
    leftkey: typing.Callable[[T], typing.Hashable],
    leftseq: collections.abc.Iterable[T],
    rightkey: typing.Callable[[U], typing.Hashable],
    rightseq: collections.abc.Iterable[U],
    /,
) -> collections.abc.Iterator[tuple[T, U]]: ...

# Stage 4b: Full application with left_default only (right outer join)
@typing.overload
def join[T, U, L](
    leftkey: typing.Callable[[T], typing.Hashable],
    leftseq: collections.abc.Iterable[T],
    rightkey: typing.Callable[[U], typing.Hashable],
    rightseq: collections.abc.Iterable[U],
    /,
    left_default: L,
) -> collections.abc.Iterator[tuple[T | L, U]]: ...

# Stage 4c: Full application with right_default only (left outer join)
@typing.overload
def join[T, U, R](
    leftkey: typing.Callable[[T], typing.Hashable],
    leftseq: collections.abc.Iterable[T],
    rightkey: typing.Callable[[U], typing.Hashable],
    rightseq: collections.abc.Iterable[U],
    /,
    *,
    right_default: R,
) -> collections.abc.Iterator[tuple[T, U | R]]: ...

# Stage 4d: Full application with both defaults (full outer join)
@typing.overload
def join[T, U, L, R](
    leftkey: typing.Callable[[T], typing.Hashable],
    leftseq: collections.abc.Iterable[T],
    rightkey: typing.Callable[[U], typing.Hashable],
    rightseq: collections.abc.Iterable[U],
    /,
    left_default: L,
    right_default: R,
) -> collections.abc.Iterator[tuple[T | L, U | R]]: ...

# Stage 3 with defaults: leftkey + leftseq + rightkey + defaults - returns callable
@typing.overload
def join[T, U, L, R](
    leftkey: typing.Callable[[T], typing.Hashable],
    leftseq: collections.abc.Iterable[T],
    rightkey: typing.Callable[[U], typing.Hashable],
    /,
    left_default: L,
    right_default: R,
) -> typing.Callable[
    [collections.abc.Iterable[U]], collections.abc.Iterator[tuple[T | L, U | R]]
]: ...

# Implementation signature
# Curried keyfilter with explicit overloads for type safety
# Stage 0: No arguments - returns a callable
@typing.overload
def keyfilter[K, V]() -> _AnyCallable[dict[K, V] | collections.abc.MutableMapping[K, V]
]: ...

# Stage 1a: Just predicate (no factory) - returns callable waiting for dict
@typing.overload
def keyfilter[K, V](
    predicate: typing.Callable[[K], bool], /
) -> typing.Callable[[collections.abc.Mapping[K, V]], dict[K, V]]: ...

# Stage 1b: Predicate with factory - returns callable waiting for dict
@typing.overload
def keyfilter[K, V](
    predicate: typing.Callable[[K], bool],
    /,
    *,
    factory: typing.Callable[[], collections.abc.MutableMapping[K, V]],
) -> typing.Callable[
    [collections.abc.Mapping[K, V]], collections.abc.MutableMapping[K, V]
]: ...

# Stage 2a: Full application (no factory) - executes immediately
@typing.overload
def keyfilter[K, V](
    predicate: typing.Callable[[K], bool],
    d: collections.abc.Mapping[K, V],
    /,
) -> dict[K, V]: ...

# Stage 2b: Full application (with factory) - executes immediately
@typing.overload
def keyfilter[K, V](
    predicate: typing.Callable[[K], bool],
    d: collections.abc.Mapping[K, V],
    /,
    *,
    factory: typing.Callable[[], collections.abc.MutableMapping[K, V]],
) -> collections.abc.MutableMapping[K, V]: ...
@typing.overload
def keymap[K0, K1, V]() -> _AnyCallable[dict[K1, V] | collections.abc.MutableMapping[K1, V]
]: ...

# Stage 1a: Just func (no factory) - returns callable waiting for dict
@typing.overload
def keymap[K0, K1, V](
    func: typing.Callable[[K0], K1], /
) -> typing.Callable[[collections.abc.Mapping[K0, V]], dict[K1, V]]: ...

# Stage 1b: Func with factory - returns callable waiting for dict
@typing.overload
def keymap[K0, K1, V](
    func: typing.Callable[[K0], K1],
    /,
    *,
    factory: typing.Callable[[], collections.abc.MutableMapping[K1, V]],
) -> typing.Callable[
    [collections.abc.Mapping[K0, V]], collections.abc.MutableMapping[K1, V]
]: ...

# Stage 2a: Full application (no factory) - executes immediately
@typing.overload
def keymap[K0, K1, V](
    func: typing.Callable[[K0], K1],
    d: collections.abc.Mapping[K0, V],
    /,
) -> dict[K1, V]: ...

# Stage 2b: Full application (with factory) - executes immediately
@typing.overload
def keymap[K0, K1, V](
    func: typing.Callable[[K0], K1],
    d: collections.abc.Mapping[K0, V],
    /,
    *,
    factory: typing.Callable[[], collections.abc.MutableMapping[K1, V]],
) -> collections.abc.MutableMapping[K1, V]: ...
@typing.overload
def map[T1, S]() -> _AnyCallable[collections.abc.Iterator[S] | _AnyCallable[collections.abc.Iterator[S]]
]: ...
@typing.overload
def map[T1, S](
    func: typing.Callable[[T1], S], /
) -> typing.Callable[[collections.abc.Iterable[T1]], collections.abc.Iterator[S]]: ...
@typing.overload
def map[T1, T2, S](
    func: typing.Callable[[T1, T2], S], /
) -> typing.Callable[
    [collections.abc.Iterable[T1], collections.abc.Iterable[T2]],
    collections.abc.Iterator[S],
]: ...
@typing.overload
def map[T1, T2, T3, S](
    func: typing.Callable[[T1, T2, T3], S], /
) -> typing.Callable[
    [
        collections.abc.Iterable[T1],
        collections.abc.Iterable[T2],
        collections.abc.Iterable[T3],
    ],
    collections.abc.Iterator[S],
]: ...
@typing.overload
def map[T1, T2, T3, T4, S](
    func: typing.Callable[[T1, T2, T3, T4], S], /
) -> typing.Callable[
    [
        collections.abc.Iterable[T1],
        collections.abc.Iterable[T2],
        collections.abc.Iterable[T3],
        collections.abc.Iterable[T4],
    ],
    collections.abc.Iterator[S],
]: ...
@typing.overload
def map[T1, T2, T3, T4, T5, S](
    func: typing.Callable[[T1, T2, T3, T4, T5], S], /
) -> typing.Callable[
    [
        collections.abc.Iterable[T1],
        collections.abc.Iterable[T2],
        collections.abc.Iterable[T3],
        collections.abc.Iterable[T4],
        collections.abc.Iterable[T5],
    ],
    collections.abc.Iterator[S],
]: ...
@typing.overload
def map[T1, S](
    func: typing.Callable[[T1], S], iterable: collections.abc.Iterable[T1], /
) -> collections.abc.Iterator[S]: ...
@typing.overload
def map[T1, T2, S](
    func: typing.Callable[[T1, T2], S],
    iterable: collections.abc.Iterable[T1],
    iter2: collections.abc.Iterable[T2],
    /,
) -> collections.abc.Iterator[S]: ...
@typing.overload
def map[T1, T2, T3, S](
    func: typing.Callable[[T1, T2, T3], S],
    iterable: collections.abc.Iterable[T1],
    iter2: collections.abc.Iterable[T2],
    iter3: collections.abc.Iterable[T3],
    /,
) -> collections.abc.Iterator[S]: ...
@typing.overload
def map[T1, T2, T3, T4, S](
    func: typing.Callable[[T1, T2, T3, T4], S],
    iterable: collections.abc.Iterable[T1],
    iter2: collections.abc.Iterable[T2],
    iter3: collections.abc.Iterable[T3],
    iter4: collections.abc.Iterable[T4],
    /,
) -> collections.abc.Iterator[S]: ...
@typing.overload
def map[T1, T2, T3, T4, T5, S](
    func: typing.Callable[[T1, T2, T3, T4, T5], S],
    iterable: collections.abc.Iterable[T1],
    iter2: collections.abc.Iterable[T2],
    iter3: collections.abc.Iterable[T3],
    iter4: collections.abc.Iterable[T4],
    iter5: collections.abc.Iterable[T5],
    /,
) -> collections.abc.Iterator[S]: ...
@typing.overload
def map[S](
    func: _AnyCallable[S],
    iterable: collections.abc.Iterable[object],
    iter2: collections.abc.Iterable[object],
    iter3: collections.abc.Iterable[object],
    iter4: collections.abc.Iterable[object],
    iter5: collections.abc.Iterable[object],
    iter6: collections.abc.Iterable[object],
    /,
    *iterables: collections.abc.Iterable[object],
) -> collections.abc.Iterator[S]: ...
@typing.overload
def mapcat[T, R]() -> _AnyCallable[collections.abc.Iterator[R] | _AnyCallable[collections.abc.Iterator[R]]
]: ...
@typing.overload
def mapcat[T, R](
    func: typing.Callable[[T], collections.abc.Iterable[R]], /
) -> typing.Callable[[collections.abc.Iterable[T]], collections.abc.Iterator[R]]: ...
@typing.overload
def mapcat[T, R](
    func: typing.Callable[[T], collections.abc.Iterable[R]],
    seqs: collections.abc.Iterable[T],
    /,
) -> collections.abc.Iterator[R]: ...
# Curried nth with explicit overloads for type safety
# Stage 0: No arguments - returns a callable
@typing.overload
def nth[T]() -> _AnyCallable[T]: ...

# Stage 1: Just n - returns callable waiting for seq
@typing.overload
def nth[T](n: int, /) -> typing.Callable[[collections.abc.Iterable[T]], T]: ...

# Stage 2: Full application - executes immediately
@typing.overload
def nth[T](n: int, seq: collections.abc.Iterable[T], /) -> T: ...
partial: _Curried = curry(functools.partial)

@typing.overload
def partition[T]() -> _AnyCallable[collections.abc.Iterator[tuple[T, ...]]]: ...
@typing.overload
def partition[T](
    n: int, /
) -> _AnyCallable[collections.abc.Iterator[tuple[T, ...]]]: ...
@typing.overload
def partition[T](
    n: typing.Literal[1], seq: collections.abc.Iterable[T], /
) -> collections.abc.Iterator[tuple[T]]: ...
@typing.overload
def partition[T](
    n: int, seq: collections.abc.Iterable[T], /
) -> collections.abc.Iterator[tuple[T, ...]]: ...
@typing.overload
def partition[T](
    n: typing.Literal[1], seq: collections.abc.Iterable[T], pad: object, /
) -> collections.abc.Iterator[tuple[T]]:
    # Note: With n=1, tuples always have exactly 1 element, so pad is never used
    ...

@typing.overload
def partition[T, P](
    n: int, seq: collections.abc.Iterable[T], pad: P, /
) -> collections.abc.Iterator[tuple[T | P, ...]]: ...
# Curried partition_all with explicit overloads for type safety
# Stage 0: No arguments - returns a callable
@typing.overload
def partition_all[T]() -> _AnyCallable[collections.abc.Iterator[tuple[T, ...]]
]: ...

# Stage 1: Just n - returns callable waiting for seq
@typing.overload
def partition_all[T](
    n: typing.Literal[1], /
) -> typing.Callable[
    [collections.abc.Iterable[T]], collections.abc.Iterator[tuple[T]]
]: ...
@typing.overload
def partition_all[T](
    n: int, /
) -> typing.Callable[
    [collections.abc.Iterable[T]], collections.abc.Iterator[tuple[T, ...]]
]: ...

# Stage 2: Full application - executes immediately
@typing.overload
def partition_all[T](
    n: typing.Literal[1], seq: collections.abc.Iterable[T], /
) -> collections.abc.Iterator[tuple[T]]: ...
@typing.overload
def partition_all[T](
    n: int, seq: collections.abc.Iterable[T], /
) -> collections.abc.Iterator[tuple[T, ...]]: ...
partitionby: _Curried = curry(_recipes.partitionby)
peekn: _Curried = curry(_itertoolz.peekn)

@typing.overload
def pluck[T]() -> _AnyCallable[collections.abc.Iterator[T] | collections.abc.Iterator[tuple[T, ...]]
]: ...
@typing.overload
def pluck[T](
    ind: object, /
) -> (
    typing.Callable[
        [
            collections.abc.Iterable[
                collections.abc.Sequence[T] | collections.abc.Mapping[object, T]
            ]
        ],
        collections.abc.Iterator[T] | collections.abc.Iterator[tuple[T, ...]],
    ]
    | typing.Callable[
        [
            collections.abc.Iterable[
                collections.abc.Sequence[T] | collections.abc.Mapping[object, T]
            ],
            T,
        ],
        collections.abc.Iterator[T] | collections.abc.Iterator[tuple[T, ...]],
    ]
): ...
@typing.overload
def pluck[T](
    ind: object,
    seqs: collections.abc.Iterable[
        collections.abc.Sequence[T] | collections.abc.Mapping[object, T]
    ],
    /,
) -> collections.abc.Iterator[T] | collections.abc.Iterator[tuple[T, ...]]: ...
@typing.overload
def pluck[T](
    ind: object,
    seqs: collections.abc.Iterable[
        collections.abc.Sequence[T] | collections.abc.Mapping[object, T]
    ],
    default: T,
    /,
) -> collections.abc.Iterator[T] | collections.abc.Iterator[tuple[T, ...]]: ...
random_sample: _Curried = curry(_itertoolz.random_sample)

@typing.overload
def reduce[T]() -> _AnyCallable[T]: ...
@typing.overload
def reduce[T](
    function: typing.Callable[[T, T], T], /
) -> typing.Callable[[collections.abc.Iterable[T]], T]: ...
@typing.overload
def reduce[T, S](
    function: typing.Callable[[T, S], T], /
) -> _AnyCallable[T]: ...
@typing.overload
def reduce[T](
    function: typing.Callable[[T, T], T],
    iterable: collections.abc.Iterable[T],
    /,
) -> T: ...
@typing.overload
def reduce[T, S](
    function: typing.Callable[[T, S], T],
    iterable: collections.abc.Iterable[S],
    initial: T,
    /,
) -> T: ...
reduceby: _Curried = curry(_itertoolz.reduceby)

# Curried remove with explicit overloads for type safety
# Stage 0: No arguments - returns a callable
@typing.overload
def remove[T]() -> _AnyCallable[collections.abc.Iterable[T]]: ...

# Stage 1: Just predicate - returns callable waiting for seq
@typing.overload
def remove[T](
    predicate: typing.Callable[[T], bool], /
) -> typing.Callable[[collections.abc.Iterable[T]], collections.abc.Iterable[T]]: ...

# Stage 2: Full application - executes immediately
@typing.overload
def remove[T](
    predicate: typing.Callable[[T], bool], seq: collections.abc.Iterable[T], /
) -> collections.abc.Iterable[T]: ...
# Curried sliding_window with explicit overloads for type safety
# Stage 0: No arguments - returns a callable
@typing.overload
def sliding_window[T]() -> _AnyCallable[collections.abc.Iterator[tuple[T, ...]]
]: ...

# Stage 1a: Just n=1 - returns callable waiting for seq
@typing.overload
def sliding_window[T](
    n: typing.Literal[1], /
) -> typing.Callable[
    [collections.abc.Iterable[T]], collections.abc.Iterator[tuple[T]]
]: ...

# Stage 1b: Just n=2 - returns callable waiting for seq
@typing.overload
def sliding_window[T](
    n: typing.Literal[2], /
) -> typing.Callable[
    [collections.abc.Iterable[T]], collections.abc.Iterator[tuple[T, T]]
]: ...

# Stage 1c: Just n=3 - returns callable waiting for seq
@typing.overload
def sliding_window[T](
    n: typing.Literal[3], /
) -> typing.Callable[
    [collections.abc.Iterable[T]], collections.abc.Iterator[tuple[T, T, T]]
]: ...

# Stage 1d: Just n (general) - returns callable waiting for seq
@typing.overload
def sliding_window[T](
    n: int, /
) -> typing.Callable[
    [collections.abc.Iterable[T]], collections.abc.Iterator[tuple[T, ...]]
]: ...

# Stage 2a: Full application with n=1 - executes immediately
@typing.overload
def sliding_window[T](
    n: typing.Literal[1], seq: collections.abc.Iterable[T], /
) -> collections.abc.Iterator[tuple[T]]: ...

# Stage 2b: Full application with n=2 - executes immediately
@typing.overload
def sliding_window[T](
    n: typing.Literal[2], seq: collections.abc.Iterable[T], /
) -> collections.abc.Iterator[tuple[T, T]]: ...

# Stage 2c: Full application with n=3 - executes immediately
@typing.overload
def sliding_window[T](
    n: typing.Literal[3], seq: collections.abc.Iterable[T], /
) -> collections.abc.Iterator[tuple[T, T, T]]: ...

# Stage 2d: Full application (general) - executes immediately
@typing.overload
def sliding_window[T](
    n: int, seq: collections.abc.Iterable[T], /
) -> collections.abc.Iterator[tuple[T, ...]]: ...
# Curried sorted with explicit overloads for type safety
# Note: key and reverse are keyword-only parameters in builtin sorted
# Stage 0: No arguments - returns a callable
@typing.overload
def sorted[T]() -> _AnyCallable[list[T]]: ...

# Stage 1a: Partial application with keyword args only (no key) - returns callable
@typing.overload
def sorted[T](
    *,
    key: None = None,
    reverse: bool = False,
) -> collections.abc.Callable[[collections.abc.Iterable[T]], list[T]]: ...

# Stage 1b: Partial application with keyword args only (with key) - returns callable
@typing.overload
def sorted[T](
    *,
    key: collections.abc.Callable[[T], SupportsRichComparison],
    reverse: bool = False,
) -> collections.abc.Callable[[collections.abc.Iterable[T]], list[T]]: ...

# Stage 2a: Full application (no key) - executes immediately
@typing.overload
def sorted[T](
    iterable: collections.abc.Iterable[T],
    /,
    *,
    key: None = None,
    reverse: bool = False,
) -> list[T]: ...

# Stage 2b: Full application (with key function) - executes immediately
@typing.overload
def sorted[T](
    iterable: collections.abc.Iterable[T],
    /,
    *,
    key: collections.abc.Callable[[T], SupportsRichComparison],
    reverse: bool = False,
) -> list[T]: ...

# Implementation signature (catch-all)
# Curried tail with explicit overloads for type safety
# Stage 0: No arguments - returns a callable
@typing.overload
def tail[T]() -> _AnyCallable[collections.abc.Iterator[T]]: ...

# Stage 1: Just n - returns callable waiting for seq
@typing.overload
def tail[T](
    n: int, /
) -> typing.Callable[[collections.abc.Iterable[T]], collections.abc.Iterator[T]]: ...

# Stage 2: Full application - executes immediately
@typing.overload
def tail[T](
    n: int, seq: collections.abc.Iterable[T], /
) -> collections.abc.Iterator[T]: ...
@typing.overload
def take[T]() -> _AnyCallable[collections.abc.Iterator[T]]: ...
@typing.overload
def take[T](
    n: int, /
) -> typing.Callable[[collections.abc.Iterable[T]], collections.abc.Iterator[T]]: ...
@typing.overload
def take[T](
    n: int, seq: collections.abc.Iterable[T], /
) -> collections.abc.Iterator[T]: ...
# Curried take_nth with explicit overloads for type safety
# Stage 0: No arguments - returns a callable
@typing.overload
def take_nth[T]() -> _AnyCallable[collections.abc.Iterator[T]]: ...

# Stage 1: Just n - returns callable waiting for seq
@typing.overload
def take_nth[T](
    n: int, /
) -> typing.Callable[[collections.abc.Iterable[T]], collections.abc.Iterator[T]]: ...

# Stage 2: Full application - executes immediately
@typing.overload
def take_nth[T](
    n: int, seq: collections.abc.Iterable[T], /
) -> collections.abc.Iterator[T]: ...
topk: _Curried = curry(_itertoolz.topk)
unique: _Curried = curry(_itertoolz.unique)
update_in: _Curried = curry(_dicttoolz.update_in)

@typing.overload
def valfilter[K, V]() -> _AnyCallable[dict[K, V] | collections.abc.MutableMapping[K, V]
]: ...

# Stage 1a: Just predicate (no factory) - returns callable waiting for dict
@typing.overload
def valfilter[K, V](
    predicate: typing.Callable[[V], bool], /
) -> typing.Callable[[collections.abc.Mapping[K, V]], dict[K, V]]: ...

# Stage 1b: Predicate with factory - returns callable waiting for dict
@typing.overload
def valfilter[K, V](
    predicate: typing.Callable[[V], bool],
    /,
    *,
    factory: typing.Callable[[], collections.abc.MutableMapping[K, V]],
) -> typing.Callable[
    [collections.abc.Mapping[K, V]], collections.abc.MutableMapping[K, V]
]: ...

# Stage 2a: Full application (no factory) - executes immediately
@typing.overload
def valfilter[K, V](
    predicate: typing.Callable[[V], bool],
    d: collections.abc.Mapping[K, V],
    /,
) -> dict[K, V]: ...

# Stage 2b: Full application (with factory) - executes immediately
@typing.overload
def valfilter[K, V](
    predicate: typing.Callable[[V], bool],
    d: collections.abc.Mapping[K, V],
    /,
    *,
    factory: typing.Callable[[], collections.abc.MutableMapping[K, V]],
) -> collections.abc.MutableMapping[K, V]: ...
@typing.overload
def valmap[K, V0, V1]() -> _AnyCallable[dict[K, V1] | collections.abc.MutableMapping[K, V1]
]: ...

# Stage 1a: Just func (no factory) - returns callable waiting for dict
@typing.overload
def valmap[K, V0, V1](
    func: typing.Callable[[V0], V1], /
) -> typing.Callable[[collections.abc.Mapping[K, V0]], dict[K, V1]]: ...

# Stage 1b: Func with factory - returns callable waiting for dict
@typing.overload
def valmap[K, V0, V1](
    func: typing.Callable[[V0], V1],
    /,
    *,
    factory: typing.Callable[[], collections.abc.MutableMapping[K, V1]],
) -> typing.Callable[
    [collections.abc.Mapping[K, V0]], collections.abc.MutableMapping[K, V1]
]: ...

# Stage 2a: Full application (no factory) - executes immediately
@typing.overload
def valmap[K, V0, V1](
    func: typing.Callable[[V0], V1],
    d: collections.abc.Mapping[K, V0],
    /,
) -> dict[K, V1]: ...

# Stage 2b: Full application (with factory) - executes immediately
@typing.overload
def valmap[K, V0, V1](
    func: typing.Callable[[V0], V1],
    d: collections.abc.Mapping[K, V0],
    /,
    *,
    factory: typing.Callable[[], collections.abc.MutableMapping[K, V1]],
) -> collections.abc.MutableMapping[K, V1]: ...
