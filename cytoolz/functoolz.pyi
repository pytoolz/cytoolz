# pyright: reportAny=false
import collections.abc
import functools
import inspect
import typing

__all__ = (
    "identity",
    "apply",
    "thread_first",
    "thread_last",
    "memoize",
    "compose",
    "compose_left",
    "pipe",
    "complement",
    "juxt",
    "do",
    "curry",
    "flip",
    "excepts",
)
PYPY = bool

### Internal type stubs
_T = typing.TypeVar("_T")
_Instance = typing.TypeVar("_Instance")
_Getter = typing.Callable[[_Instance], _T]
_Setter = typing.Callable[[_Instance, _T], None]
_Deleter = typing.Callable[[_Instance], None]
type _InstancePropertyState[_Instance, _T] = tuple[
    _Getter[_Instance, _T] | None,
    _Setter[_Instance, _T] | None,
    _Deleter[_Instance] | None,
    str | None,
    _T | None,
]

class _AnyCallable[ReturnT](typing.Protocol):
    def __call__(self, *args: object, **kwargs: object) -> ReturnT: ...

type _ThreadForm[ReturnT] = tuple[_AnyCallable[ReturnT], *tuple[object, ...]]

### Toolz

def identity[T](x: T) -> T:
    """Identity function. Return x

    >>> identity(3)
    3
    """
    ...

def apply[**P, T](func: typing.Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
    """Applies a function and returns the results

    >>> def double(x): return 2*x
    >>> def inc(x):    return x + 1
    >>> apply(double, 5)
    10

    >>> tuple(map(apply, [double, inc, double], [10, 500, 8000]))
    (20, 501, 16000)
    """
    ...

def thread_first[T, R](
    val: T, *forms: typing.Callable[[T], R] | _ThreadForm[R]
) -> R:
    """Thread value through a sequence of functions/forms

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
    ...

def thread_last[T, U](
    val: T, *forms: typing.Callable[[T], U] | _ThreadForm[U]
) -> U:
    """Thread value through a sequence of functions/forms

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
    ...

class _CacheInfo(typing.NamedTuple):
    hits: int
    misses: int
    maxsize: int | None
    currsize: int

class _LRUCache[**P, T](typing.Protocol):
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T: ...
    def cache_info(self) -> _CacheInfo: ...
    def cache_clear(self) -> None: ...
    def cache_parameters(self) -> dict[str, int | None]: ...
    def __wrapped__(self) -> typing.Callable[P, T]: ...

@typing.overload
def memoize[**P, T](
    func: typing.Callable[P, T],
    cache: collections.abc.MutableMapping[object, object] = ...,
) -> _LRUCache[P, T]: ...
@typing.overload
def memoize[**P, T](
    func: None = None,
    cache: collections.abc.MutableMapping[object, object] = ...,
) -> typing.Callable[[typing.Callable[P, T]], _LRUCache[P, T]]: ...

@typing.overload
def excepts[**P, T](
    exc: type[Exception] | tuple[type[Exception], ...],
    func: typing.Callable[P, T],
    handler: typing.Callable[[Exception], T],
) -> typing.Callable[P, T]: ...
@typing.overload
def excepts[**P, T](
    exc: type[Exception] | tuple[type[Exception], ...],
    func: None = None,
    handler: typing.Callable[[Exception], T] | None = None,
) -> typing.Callable[[typing.Callable[P, T]], typing.Callable[P, T]]: ...

class ExceptionWrapper(typing.NamedTuple):
    """Wraps an exception, optionally with a default value

    Items in this tuple can be accessed via the tuple interface or by
    attribute.  They are the exception and the default value, respectively.
    """

    exc: Exception
    default: object

class InstanceProperty[_Instance, _T]:
    __slots__ = ("fget", "fset", "fdel", "__doc__", "classval")

    fget: _Getter[_Instance, _T] | None
    fset: _Setter[_Instance, _T] | None
    fdel: _Deleter[_Instance] | None
    __doc__: str | None
    classval: _T | None

    def __init__(
        self,
        fget: _Getter[_Instance, _T] | None,
        fset: _Setter[_Instance, _T] | None,
        fdel: _Deleter[_Instance] | None,
        doc: str | None,
        classval: _T | None,
    ) -> None: ...

    def __get__(self, instance: _Instance | None, owner: type[_Instance]) -> _T: ...

    def __set__(self, instance: _Instance, value: _T) -> None: ...

    def __delete__(self, instance: _Instance) -> None: ...

    @typing.override
    def __getstate__(
        self,
    ) -> tuple[type[InstanceProperty[_Instance, _T]], _InstancePropertyState[_Instance, _T]]:
        # TODO figure out how to type this correctly
        ...

    def __setstate__(
        self, state: tuple[type[InstanceProperty[_Instance, _T]], _InstancePropertyState[_Instance, _T]]
    ) -> None:
        # TODO figure out how to type this correctly
        ...

@typing.overload
def instanceproperty(
    fget: _Getter[_Instance, _T],
    fset: _Setter[_Instance, _T] | None = ...,
    fdel: _Deleter[_Instance] | None = ...,
    doc: str | None = ...,
    classval: _T | None = ...,
) -> InstanceProperty[_Instance, _T]: ...
@typing.overload
def instanceproperty(
    fget: typing.Literal[None] | None = None,
    fset: _Setter[_Instance, _T] | None = ...,  # pyright: ignore[reportInvalidTypeVarUse]
    fdel: _Deleter[_Instance] | None = ...,
    doc: str | None = ...,
    classval: _T | None = ...,
) -> typing.Callable[[_Getter[_Instance, _T]], InstanceProperty[_Instance, _T]]: ...
type _CurryState = tuple[object, ...]

class curry[T]:
    """Curry a callable function

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
        toolz.curried - namespace of curried functions
                        https://toolz.readthedocs.io/en/latest/curry.html
    """
    def __init__[**P](
        self,
        func: typing.Callable[P, T],
        /,  # Must be positional-only
        *args: object,
        **kwargs: object,
    ) -> None: ...
    @instanceproperty
    def func(self) -> _AnyCallable[T]: ...
    @instanceproperty
    def __signature__(self) -> inspect.Signature: ...
    def __call__(self, *args: object, **kwargs: object) -> T: ...
    @typing.override
    def __repr__(self) -> str: ...
    @typing.override
    def __getstate__(self) -> tuple[object, _CurryState]: ...
    def __setstate__(self, state: tuple[object, _CurryState]) -> None: ...
    @typing.override
    def __reduce__(self) -> tuple[object, tuple[object, ...]]: ...
    @typing.override
    def __reduce_ex__(self, protocol: typing.SupportsIndex) -> tuple[object, tuple[object, ...]]: ...
    @typing.override
    def __sizeof__(self) -> int: ...

class Compose(typing.Protocol):
    def __call__(self, *args: object, **kwargs: object) -> object: ...

@typing.overload
def compose() -> Compose: ...
@typing.overload
def compose[A, B](f1: typing.Callable[[A], B], /) -> typing.Callable[[A], B]: ...
@typing.overload
def compose[A, B, C](
    f1: typing.Callable[[B], C],
    f2: typing.Callable[[A], B],
    /,
) -> typing.Callable[[A], C]: ...
@typing.overload
def compose[A, B, C, D](
    f1: typing.Callable[[C], D],
    f2: typing.Callable[[B], C],
    f3: typing.Callable[[A], B],
    /,
) -> typing.Callable[[A], D]: ...
@typing.overload
def compose[A, B, C, D, E](
    f1: typing.Callable[[D], E],
    f2: typing.Callable[[C], D],
    f3: typing.Callable[[B], C],
    f4: typing.Callable[[A], B],
    /,
) -> typing.Callable[[A], E]: ...
@typing.overload
def compose[A, B, C, D, E, F](
    f1: typing.Callable[[E], F],
    f2: typing.Callable[[D], E],
    f3: typing.Callable[[C], D],
    f4: typing.Callable[[B], C],
    f5: typing.Callable[[A], B],
    /,
) -> typing.Callable[[A], F]: ...
@typing.overload
def compose[A, B, C, D, E, F, G](
    f1: typing.Callable[[F], G],
    f2: typing.Callable[[E], F],
    f3: typing.Callable[[D], E],
    f4: typing.Callable[[C], D],
    f5: typing.Callable[[B], C],
    f6: typing.Callable[[A], B],
    /,
) -> typing.Callable[[A], G]: ...
@typing.overload
def compose[A, B, C, D, E, F, G, H](
    f1: typing.Callable[[G], H],
    f2: typing.Callable[[F], G],
    f3: typing.Callable[[E], F],
    f4: typing.Callable[[D], E],
    f5: typing.Callable[[C], D],
    f6: typing.Callable[[B], C],
    f7: typing.Callable[[A], B],
    /,
) -> typing.Callable[[A], H]: ...
@typing.overload
def compose[A, B, C, D, E, F, G, H, I](
    f1: typing.Callable[[H], I],
    f2: typing.Callable[[G], H],
    f3: typing.Callable[[F], G],
    f4: typing.Callable[[E], F],
    f5: typing.Callable[[D], E],
    f6: typing.Callable[[C], D],
    f7: typing.Callable[[B], C],
    f8: typing.Callable[[A], B],
    /,
) -> typing.Callable[[A], I]: ...
@typing.overload
def compose[A, B, C, D, E, F, G, H, I, J](
    f1: typing.Callable[[I], J],
    f2: typing.Callable[[H], I],
    f3: typing.Callable[[G], H],
    f4: typing.Callable[[F], G],
    f5: typing.Callable[[E], F],
    f6: typing.Callable[[D], E],
    f7: typing.Callable[[C], D],
    f8: typing.Callable[[B], C],
    f9: typing.Callable[[A], B],
    /,
) -> typing.Callable[[A], J]: ...
@typing.overload
def compose[A, B, C, D, E, F, G, H, I, J, K](
    f1: typing.Callable[[J], K],
    f2: typing.Callable[[I], J],
    f3: typing.Callable[[H], I],
    f4: typing.Callable[[G], H],
    f5: typing.Callable[[F], G],
    f6: typing.Callable[[E], F],
    f7: typing.Callable[[D], E],
    f8: typing.Callable[[C], D],
    f9: typing.Callable[[B], C],
    f10: typing.Callable[[A], B],
    /,
) -> typing.Callable[[A], K]: ...
@typing.overload
def compose[A, B, C, D, E, F, G, H, I, J, K, L](
    f1: typing.Callable[[K], L],
    f2: typing.Callable[[J], K],
    f3: typing.Callable[[I], J],
    f4: typing.Callable[[H], I],
    f5: typing.Callable[[G], H],
    f6: typing.Callable[[F], G],
    f7: typing.Callable[[E], F],
    f8: typing.Callable[[D], E],
    f9: typing.Callable[[C], D],
    f10: typing.Callable[[B], C],
    f11: typing.Callable[[A], B],
    /,
) -> typing.Callable[[A], L]: ...
@typing.overload
def compose[A, B, C, D, E, F, G, H, I, J, K, L, M](
    f1: typing.Callable[[L], M],
    f2: typing.Callable[[K], L],
    f3: typing.Callable[[J], K],
    f4: typing.Callable[[I], J],
    f5: typing.Callable[[H], I],
    f6: typing.Callable[[G], H],
    f7: typing.Callable[[F], G],
    f8: typing.Callable[[E], F],
    f9: typing.Callable[[D], E],
    f10: typing.Callable[[C], D],
    f11: typing.Callable[[B], C],
    f12: typing.Callable[[A], B],
    /,
) -> typing.Callable[[A], M]: ...
@typing.overload
def compose[A, B, C, D, E, F, G, H, I, J, K, L, M, N](
    f1: typing.Callable[[M], N],
    f2: typing.Callable[[L], M],
    f3: typing.Callable[[K], L],
    f4: typing.Callable[[J], K],
    f5: typing.Callable[[I], J],
    f6: typing.Callable[[H], I],
    f7: typing.Callable[[G], H],
    f8: typing.Callable[[F], G],
    f9: typing.Callable[[E], F],
    f10: typing.Callable[[D], E],
    f11: typing.Callable[[C], D],
    f12: typing.Callable[[B], C],
    f13: typing.Callable[[A], B],
    /,
) -> typing.Callable[[A], N]: ...
@typing.overload
def compose[A, B, C, D, E, F, G, H, I, J, K, L, M, N, O](
    f1: typing.Callable[[N], O],
    f2: typing.Callable[[M], N],
    f3: typing.Callable[[L], M],
    f4: typing.Callable[[K], L],
    f5: typing.Callable[[J], K],
    f6: typing.Callable[[I], J],
    f7: typing.Callable[[H], I],
    f8: typing.Callable[[G], H],
    f9: typing.Callable[[F], G],
    f10: typing.Callable[[E], F],
    f11: typing.Callable[[D], E],
    f12: typing.Callable[[C], D],
    f13: typing.Callable[[B], C],
    f14: typing.Callable[[A], B],
    /,
) -> typing.Callable[[A], O]: ...
@typing.overload
def compose[A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P](
    f1: typing.Callable[[O], P],
    f2: typing.Callable[[N], O],
    f3: typing.Callable[[M], N],
    f4: typing.Callable[[L], M],
    f5: typing.Callable[[K], L],
    f6: typing.Callable[[J], K],
    f7: typing.Callable[[I], J],
    f8: typing.Callable[[H], I],
    f9: typing.Callable[[G], H],
    f10: typing.Callable[[F], G],
    f11: typing.Callable[[E], F],
    f12: typing.Callable[[D], E],
    f13: typing.Callable[[C], D],
    f14: typing.Callable[[B], C],
    f15: typing.Callable[[A], B],
    /,
) -> typing.Callable[[A], P]: ...
@typing.overload
def compose[A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q](
    f1: typing.Callable[[P], Q],
    f2: typing.Callable[[O], P],
    f3: typing.Callable[[N], O],
    f4: typing.Callable[[M], N],
    f5: typing.Callable[[L], M],
    f6: typing.Callable[[K], L],
    f7: typing.Callable[[J], K],
    f8: typing.Callable[[I], J],
    f9: typing.Callable[[H], I],
    f10: typing.Callable[[G], H],
    f11: typing.Callable[[F], G],
    f12: typing.Callable[[E], F],
    f13: typing.Callable[[D], E],
    f14: typing.Callable[[C], D],
    f15: typing.Callable[[B], C],
    f16: typing.Callable[[A], B],
    /,
) -> typing.Callable[[A], Q]: ...
@typing.overload
def compose[A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R](
    f1: typing.Callable[[Q], R],
    f2: typing.Callable[[P], Q],
    f3: typing.Callable[[O], P],
    f4: typing.Callable[[N], O],
    f5: typing.Callable[[M], N],
    f6: typing.Callable[[L], M],
    f7: typing.Callable[[K], L],
    f8: typing.Callable[[J], K],
    f9: typing.Callable[[I], J],
    f10: typing.Callable[[H], I],
    f11: typing.Callable[[G], H],
    f12: typing.Callable[[F], G],
    f13: typing.Callable[[E], F],
    f14: typing.Callable[[D], E],
    f15: typing.Callable[[C], D],
    f16: typing.Callable[[B], C],
    f17: typing.Callable[[A], B],
    /,
) -> typing.Callable[[A], R]: ...
@typing.overload
def compose[A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S](
    f1: typing.Callable[[R], S],
    f2: typing.Callable[[Q], R],
    f3: typing.Callable[[P], Q],
    f4: typing.Callable[[O], P],
    f5: typing.Callable[[N], O],
    f6: typing.Callable[[M], N],
    f7: typing.Callable[[L], M],
    f8: typing.Callable[[K], L],
    f9: typing.Callable[[J], K],
    f10: typing.Callable[[I], J],
    f11: typing.Callable[[H], I],
    f12: typing.Callable[[G], H],
    f13: typing.Callable[[F], G],
    f14: typing.Callable[[E], F],
    f15: typing.Callable[[D], E],
    f16: typing.Callable[[C], D],
    f17: typing.Callable[[B], C],
    f18: typing.Callable[[A], B],
    /,
) -> typing.Callable[[A], S]: ...
@typing.overload
def compose[A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T](
    f1: typing.Callable[[S], T],
    f2: typing.Callable[[R], S],
    f3: typing.Callable[[Q], R],
    f4: typing.Callable[[P], Q],
    f5: typing.Callable[[O], P],
    f6: typing.Callable[[N], O],
    f7: typing.Callable[[M], N],
    f8: typing.Callable[[L], M],
    f9: typing.Callable[[K], L],
    f10: typing.Callable[[J], K],
    f11: typing.Callable[[I], J],
    f12: typing.Callable[[H], I],
    f13: typing.Callable[[G], H],
    f14: typing.Callable[[F], G],
    f15: typing.Callable[[E], F],
    f16: typing.Callable[[D], E],
    f17: typing.Callable[[C], D],
    f18: typing.Callable[[B], C],
    f19: typing.Callable[[A], B],
    /,
) -> typing.Callable[[A], T]: ...
@typing.overload
def compose[A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U](
    f1: typing.Callable[[T], U],
    f2: typing.Callable[[S], T],
    f3: typing.Callable[[R], S],
    f4: typing.Callable[[Q], R],
    f5: typing.Callable[[P], Q],
    f6: typing.Callable[[O], P],
    f7: typing.Callable[[N], O],
    f8: typing.Callable[[M], N],
    f9: typing.Callable[[L], M],
    f10: typing.Callable[[K], L],
    f11: typing.Callable[[J], K],
    f12: typing.Callable[[I], J],
    f13: typing.Callable[[H], I],
    f14: typing.Callable[[G], H],
    f15: typing.Callable[[F], G],
    f16: typing.Callable[[E], F],
    f17: typing.Callable[[D], E],
    f18: typing.Callable[[C], D],
    f19: typing.Callable[[B], C],
    f20: typing.Callable[[A], B],
    /,
) -> typing.Callable[[A], U]: ...
@typing.overload
def compose[A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V](
    f1: typing.Callable[[U], V],
    f2: typing.Callable[[T], U],
    f3: typing.Callable[[S], T],
    f4: typing.Callable[[R], S],
    f5: typing.Callable[[Q], R],
    f6: typing.Callable[[P], Q],
    f7: typing.Callable[[O], P],
    f8: typing.Callable[[N], O],
    f9: typing.Callable[[M], N],
    f10: typing.Callable[[L], M],
    f11: typing.Callable[[K], L],
    f12: typing.Callable[[J], K],
    f13: typing.Callable[[I], J],
    f14: typing.Callable[[H], I],
    f15: typing.Callable[[G], H],
    f16: typing.Callable[[F], G],
    f17: typing.Callable[[E], F],
    f18: typing.Callable[[D], E],
    f19: typing.Callable[[C], D],
    f20: typing.Callable[[B], C],
    f21: typing.Callable[[A], B],
    /,
) -> typing.Callable[[A], V]: ...
@typing.overload
def compose[A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W](
    f1: typing.Callable[[V], W],
    f2: typing.Callable[[U], V],
    f3: typing.Callable[[T], U],
    f4: typing.Callable[[S], T],
    f5: typing.Callable[[R], S],
    f6: typing.Callable[[Q], R],
    f7: typing.Callable[[P], Q],
    f8: typing.Callable[[O], P],
    f9: typing.Callable[[N], O],
    f10: typing.Callable[[M], N],
    f11: typing.Callable[[L], M],
    f12: typing.Callable[[K], L],
    f13: typing.Callable[[J], K],
    f14: typing.Callable[[I], J],
    f15: typing.Callable[[H], I],
    f16: typing.Callable[[G], H],
    f17: typing.Callable[[F], G],
    f18: typing.Callable[[E], F],
    f19: typing.Callable[[D], E],
    f20: typing.Callable[[C], D],
    f21: typing.Callable[[B], C],
    f22: typing.Callable[[A], B],
    /,
) -> typing.Callable[[A], W]: ...
@typing.overload
def compose[A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X](
    f1: typing.Callable[[W], X],
    f2: typing.Callable[[V], W],
    f3: typing.Callable[[U], V],
    f4: typing.Callable[[T], U],
    f5: typing.Callable[[S], T],
    f6: typing.Callable[[R], S],
    f7: typing.Callable[[Q], R],
    f8: typing.Callable[[P], Q],
    f9: typing.Callable[[O], P],
    f10: typing.Callable[[N], O],
    f11: typing.Callable[[M], N],
    f12: typing.Callable[[L], M],
    f13: typing.Callable[[K], L],
    f14: typing.Callable[[J], K],
    f15: typing.Callable[[I], J],
    f16: typing.Callable[[H], I],
    f17: typing.Callable[[G], H],
    f18: typing.Callable[[F], G],
    f19: typing.Callable[[E], F],
    f20: typing.Callable[[D], E],
    f21: typing.Callable[[C], D],
    f22: typing.Callable[[B], C],
    f23: typing.Callable[[A], B],
    /,
) -> typing.Callable[[A], X]: ...
@typing.overload
def compose[A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y](
    f1: typing.Callable[[X], Y],
    f2: typing.Callable[[W], X],
    f3: typing.Callable[[V], W],
    f4: typing.Callable[[U], V],
    f5: typing.Callable[[T], U],
    f6: typing.Callable[[S], T],
    f7: typing.Callable[[R], S],
    f8: typing.Callable[[Q], R],
    f9: typing.Callable[[P], Q],
    f10: typing.Callable[[O], P],
    f11: typing.Callable[[N], O],
    f12: typing.Callable[[M], N],
    f13: typing.Callable[[L], M],
    f14: typing.Callable[[K], L],
    f15: typing.Callable[[J], K],
    f16: typing.Callable[[I], J],
    f17: typing.Callable[[H], I],
    f18: typing.Callable[[G], H],
    f19: typing.Callable[[F], G],
    f20: typing.Callable[[E], F],
    f21: typing.Callable[[D], E],
    f22: typing.Callable[[C], D],
    f23: typing.Callable[[B], C],
    f24: typing.Callable[[A], B],
    /,
) -> typing.Callable[[A], Y]: ...
@typing.overload
def compose[A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z](
    f1: typing.Callable[[Y], Z],
    f2: typing.Callable[[X], Y],
    f3: typing.Callable[[W], X],
    f4: typing.Callable[[V], W],
    f5: typing.Callable[[U], V],
    f6: typing.Callable[[T], U],
    f7: typing.Callable[[S], T],
    f8: typing.Callable[[R], S],
    f9: typing.Callable[[Q], R],
    f10: typing.Callable[[P], Q],
    f11: typing.Callable[[O], P],
    f12: typing.Callable[[N], O],
    f13: typing.Callable[[M], N],
    f14: typing.Callable[[L], M],
    f15: typing.Callable[[K], L],
    f16: typing.Callable[[J], K],
    f17: typing.Callable[[I], J],
    f18: typing.Callable[[H], I],
    f19: typing.Callable[[G], H],
    f20: typing.Callable[[F], G],
    f21: typing.Callable[[E], F],
    f22: typing.Callable[[D], E],
    f23: typing.Callable[[C], D],
    f24: typing.Callable[[B], C],
    f25: typing.Callable[[A], B],
    /,
) -> typing.Callable[[A], Z]: ...

def compose_left(*funcs: typing.Callable[[object], object]) -> Compose: ...

def flip[**P, T](func: typing.Callable[P, T], /) -> typing.Callable[P, T]: ...

@typing.overload
def complement[**P](func: typing.Callable[P, object], /) -> typing.Callable[P, bool]: ...
@typing.overload
def complement[**P](func: typing.Callable[P, bool], /) -> typing.Callable[P, bool]: ...

@typing.overload
def do[**P, T](func: typing.Callable[P, T], /) -> typing.Callable[P, T]: ...
@typing.overload
def do[**P](func: typing.Callable[P, object], /) -> typing.Callable[P, object]: ...

@typing.overload
def juxt[A, B](func: typing.Callable[[A], B], /) -> typing.Callable[[A], tuple[B]]: ...
@typing.overload
def juxt[A, B, C](
    func1: typing.Callable[[A], B],
    func2: typing.Callable[[A], C],
    /,
) -> typing.Callable[[A], tuple[B, C]]: ...
@typing.overload
def juxt[A, B, C, D](
    func1: typing.Callable[[A], B],
    func2: typing.Callable[[A], C],
    func3: typing.Callable[[A], D],
    /,
) -> typing.Callable[[A], tuple[B, C, D]]: ...
@typing.overload
def juxt[A, B, C, D, E](
    func1: typing.Callable[[A], B],
    func2: typing.Callable[[A], C],
    func3: typing.Callable[[A], D],
    func4: typing.Callable[[A], E],
    /,
) -> typing.Callable[[A], tuple[B, C, D, E]]: ...
@typing.overload
def juxt[A, B, C, D, E, F](
    func1: typing.Callable[[A], B],
    func2: typing.Callable[[A], C],
    func3: typing.Callable[[A], D],
    func4: typing.Callable[[A], E],
    func5: typing.Callable[[A], F],
    /,
) -> typing.Callable[[A], tuple[B, C, D, E, F]]: ...
@typing.overload
def juxt[A, B, C, D, E, F, G](
    func1: typing.Callable[[A], B],
    func2: typing.Callable[[A], C],
    func3: typing.Callable[[A], D],
    func4: typing.Callable[[A], E],
    func5: typing.Callable[[A], F],
    func6: typing.Callable[[A], G],
    /,
) -> typing.Callable[[A], tuple[B, C, D, E, F, G]]: ...
@typing.overload
def juxt[A, B, C, D, E, F, G, H](
    func1: typing.Callable[[A], B],
    func2: typing.Callable[[A], C],
    func3: typing.Callable[[A], D],
    func4: typing.Callable[[A], E],
    func5: typing.Callable[[A], F],
    func6: typing.Callable[[A], G],
    func7: typing.Callable[[A], H],
    /,
) -> typing.Callable[[A], tuple[B, C, D, E, F, G, H]]: ...
@typing.overload
def juxt[A, B, C, D, E, F, G, H, I](
    func1: typing.Callable[[A], B],
    func2: typing.Callable[[A], C],
    func3: typing.Callable[[A], D],
    func4: typing.Callable[[A], E],
    func5: typing.Callable[[A], F],
    func6: typing.Callable[[A], G],
    func7: typing.Callable[[A], H],
    func8: typing.Callable[[A], I],
    /,
) -> typing.Callable[[A], tuple[B, C, D, E, F, G, H, I]]: ...
@typing.overload
def juxt[A, B, C, D, E, F, G, H, I, J](
    func1: typing.Callable[[A], B],
    func2: typing.Callable[[A], C],
    func3: typing.Callable[[A], D],
    func4: typing.Callable[[A], E],
    func5: typing.Callable[[A], F],
    func6: typing.Callable[[A], G],
    func7: typing.Callable[[A], H],
    func8: typing.Callable[[A], I],
    func9: typing.Callable[[A], J],
    /,
) -> typing.Callable[[A], tuple[B, C, D, E, F, G, H, I, J]]: ...
@typing.overload
def juxt[A, B, C, D, E, F, G, H, I, J, K](
    func1: typing.Callable[[A], B],
    func2: typing.Callable[[A], C],
    func3: typing.Callable[[A], D],
    func4: typing.Callable[[A], E],
    func5: typing.Callable[[A], F],
    func6: typing.Callable[[A], G],
    func7: typing.Callable[[A], H],
    func8: typing.Callable[[A], I],
    func9: typing.Callable[[A], J],
    func10: typing.Callable[[A], K],
    /,
) -> typing.Callable[[A], tuple[B, C, D, E, F, G, H, I, J, K]]: ...
@typing.overload
def juxt[A, B, C, D, E, F, G, H, I, J, K, L](
    func1: typing.Callable[[A], B],
    func2: typing.Callable[[A], C],
    func3: typing.Callable[[A], D],
    func4: typing.Callable[[A], E],
    func5: typing.Callable[[A], F],
    func6: typing.Callable[[A], G],
    func7: typing.Callable[[A], H],
    func8: typing.Callable[[A], I],
    func9: typing.Callable[[A], J],
    func10: typing.Callable[[A], K],
    func11: typing.Callable[[A], L],
    /,
) -> typing.Callable[[A], tuple[B, C, D, E, F, G, H, I, J, K, L]]: ...
@typing.overload
def juxt[A, B, C, D, E, F, G, H, I, J, K, L, M](
    func1: typing.Callable[[A], B],
    func2: typing.Callable[[A], C],
    func3: typing.Callable[[A], D],
    func4: typing.Callable[[A], E],
    func5: typing.Callable[[A], F],
    func6: typing.Callable[[A], G],
    func7: typing.Callable[[A], H],
    func8: typing.Callable[[A], I],
    func9: typing.Callable[[A], J],
    func10: typing.Callable[[A], K],
    func11: typing.Callable[[A], L],
    func12: typing.Callable[[A], M],
    /,
) -> typing.Callable[[A], tuple[B, C, D, E, F, G, H, I, J, K, L, M]]: ...
@typing.overload
def juxt[A, B, C, D, E, F, G, H, I, J, K, L, M, N](
    func1: typing.Callable[[A], B],
    func2: typing.Callable[[A], C],
    func3: typing.Callable[[A], D],
    func4: typing.Callable[[A], E],
    func5: typing.Callable[[A], F],
    func6: typing.Callable[[A], G],
    func7: typing.Callable[[A], H],
    func8: typing.Callable[[A], I],
    func9: typing.Callable[[A], J],
    func10: typing.Callable[[A], K],
    func11: typing.Callable[[A], L],
    func12: typing.Callable[[A], M],
    func13: typing.Callable[[A], N],
    /,
) -> typing.Callable[[A], tuple[B, C, D, E, F, G, H, I, J, K, L, M, N]]: ...
@typing.overload
def juxt[A, B, C, D, E, F, G, H, I, J, K, L, M, N, O](
    func1: typing.Callable[[A], B],
    func2: typing.Callable[[A], C],
    func3: typing.Callable[[A], D],
    func4: typing.Callable[[A], E],
    func5: typing.Callable[[A], F],
    func6: typing.Callable[[A], G],
    func7: typing.Callable[[A], H],
    func8: typing.Callable[[A], I],
    func9: typing.Callable[[A], J],
    func10: typing.Callable[[A], K],
    func11: typing.Callable[[A], L],
    func12: typing.Callable[[A], M],
    func13: typing.Callable[[A], N],
    func14: typing.Callable[[A], O],
    /,
) -> typing.Callable[[A], tuple[B, C, D, E, F, G, H, I, J, K, L, M, N, O]]: ...
@typing.overload
def juxt[A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P](
    func1: typing.Callable[[A], B],
    func2: typing.Callable[[A], C],
    func3: typing.Callable[[A], D],
    func4: typing.Callable[[A], E],
    func5: typing.Callable[[A], F],
    func6: typing.Callable[[A], G],
    func7: typing.Callable[[A], H],
    func8: typing.Callable[[A], I],
    func9: typing.Callable[[A], J],
    func10: typing.Callable[[A], K],
    func11: typing.Callable[[A], L],
    func12: typing.Callable[[A], M],
    func13: typing.Callable[[A], N],
    func14: typing.Callable[[A], O],
    func15: typing.Callable[[A], P],
    /,
) -> typing.Callable[[A], tuple[B, C, D, E, F, G, H, I, J, K, L, M, N, O, P]]: ...
@typing.overload
def juxt[A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q](
    func1: typing.Callable[[A], B],
    func2: typing.Callable[[A], C],
    func3: typing.Callable[[A], D],
    func4: typing.Callable[[A], E],
    func5: typing.Callable[[A], F],
    func6: typing.Callable[[A], G],
    func7: typing.Callable[[A], H],
    func8: typing.Callable[[A], I],
    func9: typing.Callable[[A], J],
    func10: typing.Callable[[A], K],
    func11: typing.Callable[[A], L],
    func12: typing.Callable[[A], M],
    func13: typing.Callable[[A], N],
    func14: typing.Callable[[A], O],
    func15: typing.Callable[[A], P],
    func16: typing.Callable[[A], Q],
    /,
) -> typing.Callable[[A], tuple[B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q]]: ...
@typing.overload
def juxt[A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R](
    func1: typing.Callable[[A], B],
    func2: typing.Callable[[A], C],
    func3: typing.Callable[[A], D],
    func4: typing.Callable[[A], E],
    func5: typing.Callable[[A], F],
    func6: typing.Callable[[A], G],
    func7: typing.Callable[[A], H],
    func8: typing.Callable[[A], I],
    func9: typing.Callable[[A], J],
    func10: typing.Callable[[A], K],
    func11: typing.Callable[[A], L],
    func12: typing.Callable[[A], M],
    func13: typing.Callable[[A], N],
    func14: typing.Callable[[A], O],
    func15: typing.Callable[[A], P],
    func16: typing.Callable[[A], Q],
    func17: typing.Callable[[A], R],
    /,
) -> typing.Callable[[A], tuple[B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R]]: ...
@typing.overload
def juxt[A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S](
    func1: typing.Callable[[A], B],
    func2: typing.Callable[[A], C],
    func3: typing.Callable[[A], D],
    func4: typing.Callable[[A], E],
    func5: typing.Callable[[A], F],
    func6: typing.Callable[[A], G],
    func7: typing.Callable[[A], H],
    func8: typing.Callable[[A], I],
    func9: typing.Callable[[A], J],
    func10: typing.Callable[[A], K],
    func11: typing.Callable[[A], L],
    func12: typing.Callable[[A], M],
    func13: typing.Callable[[A], N],
    func14: typing.Callable[[A], O],
    func15: typing.Callable[[A], P],
    func16: typing.Callable[[A], Q],
    func17: typing.Callable[[A], R],
    func18: typing.Callable[[A], S],
    /,
) -> typing.Callable[[A], tuple[B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S]]: ...
@typing.overload
def juxt[A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T](
    func1: typing.Callable[[A], B],
    func2: typing.Callable[[A], C],
    func3: typing.Callable[[A], D],
    func4: typing.Callable[[A], E],
    func5: typing.Callable[[A], F],
    func6: typing.Callable[[A], G],
    func7: typing.Callable[[A], H],
    func8: typing.Callable[[A], I],
    func9: typing.Callable[[A], J],
    func10: typing.Callable[[A], K],
    func11: typing.Callable[[A], L],
    func12: typing.Callable[[A], M],
    func13: typing.Callable[[A], N],
    func14: typing.Callable[[A], O],
    func15: typing.Callable[[A], P],
    func16: typing.Callable[[A], Q],
    func17: typing.Callable[[A], R],
    func18: typing.Callable[[A], S],
    func19: typing.Callable[[A], T],
    /,
) -> typing.Callable[[A], tuple[B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T]]: ...
@typing.overload
def juxt[A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U](
    func1: typing.Callable[[A], B],
    func2: typing.Callable[[A], C],
    func3: typing.Callable[[A], D],
    func4: typing.Callable[[A], E],
    func5: typing.Callable[[A], F],
    func6: typing.Callable[[A], G],
    func7: typing.Callable[[A], H],
    func8: typing.Callable[[A], I],
    func9: typing.Callable[[A], J],
    func10: typing.Callable[[A], K],
    func11: typing.Callable[[A], L],
    func12: typing.Callable[[A], M],
    func13: typing.Callable[[A], N],
    func14: typing.Callable[[A], O],
    func15: typing.Callable[[A], P],
    func16: typing.Callable[[A], Q],
    func17: typing.Callable[[A], R],
    func18: typing.Callable[[A], S],
    func19: typing.Callable[[A], T],
    func20: typing.Callable[[A], U],
    /,
) -> typing.Callable[[A], tuple[B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U]]: ...
@typing.overload
def juxt[A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V](
    func1: typing.Callable[[A], B],
    func2: typing.Callable[[A], C],
    func3: typing.Callable[[A], D],
    func4: typing.Callable[[A], E],
    func5: typing.Callable[[A], F],
    func6: typing.Callable[[A], G],
    func7: typing.Callable[[A], H],
    func8: typing.Callable[[A], I],
    func9: typing.Callable[[A], J],
    func10: typing.Callable[[A], K],
    func11: typing.Callable[[A], L],
    func12: typing.Callable[[A], M],
    func13: typing.Callable[[A], N],
    func14: typing.Callable[[A], O],
    func15: typing.Callable[[A], P],
    func16: typing.Callable[[A], Q],
    func17: typing.Callable[[A], R],
    func18: typing.Callable[[A], S],
    func19: typing.Callable[[A], T],
    func20: typing.Callable[[A], U],
    func21: typing.Callable[[A], V],
    /,
) -> typing.Callable[[A], tuple[B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V]]: ...
@typing.overload
def juxt[A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W](
    func1: typing.Callable[[A], B],
    func2: typing.Callable[[A], C],
    func3: typing.Callable[[A], D],
    func4: typing.Callable[[A], E],
    func5: typing.Callable[[A], F],
    func6: typing.Callable[[A], G],
    func7: typing.Callable[[A], H],
    func8: typing.Callable[[A], I],
    func9: typing.Callable[[A], J],
    func10: typing.Callable[[A], K],
    func11: typing.Callable[[A], L],
    func12: typing.Callable[[A], M],
    func13: typing.Callable[[A], N],
    func14: typing.Callable[[A], O],
    func15: typing.Callable[[A], P],
    func16: typing.Callable[[A], Q],
    func17: typing.Callable[[A], R],
    func18: typing.Callable[[A], S],
    func19: typing.Callable[[A], T],
    func20: typing.Callable[[A], U],
    func21: typing.Callable[[A], V],
    func22: typing.Callable[[A], W],
    /,
) -> typing.Callable[[A], tuple[B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W]]: ...
@typing.overload
def juxt[A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X](
    func1: typing.Callable[[A], B],
    func2: typing.Callable[[A], C],
    func3: typing.Callable[[A], D],
    func4: typing.Callable[[A], E],
    func5: typing.Callable[[A], F],
    func6: typing.Callable[[A], G],
    func7: typing.Callable[[A], H],
    func8: typing.Callable[[A], I],
    func9: typing.Callable[[A], J],
    func10: typing.Callable[[A], K],
    func11: typing.Callable[[A], L],
    func12: typing.Callable[[A], M],
    func13: typing.Callable[[A], N],
    func14: typing.Callable[[A], O],
    func15: typing.Callable[[A], P],
    func16: typing.Callable[[A], Q],
    func17: typing.Callable[[A], R],
    func18: typing.Callable[[A], S],
    func19: typing.Callable[[A], T],
    func20: typing.Callable[[A], U],
    func21: typing.Callable[[A], V],
    func22: typing.Callable[[A], W],
    func23: typing.Callable[[A], X],
    /,
) -> typing.Callable[[A], tuple[B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X]]: ...
@typing.overload
def juxt[A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y](
    func1: typing.Callable[[A], B],
    func2: typing.Callable[[A], C],
    func3: typing.Callable[[A], D],
    func4: typing.Callable[[A], E],
    func5: typing.Callable[[A], F],
    func6: typing.Callable[[A], G],
    func7: typing.Callable[[A], H],
    func8: typing.Callable[[A], I],
    func9: typing.Callable[[A], J],
    func10: typing.Callable[[A], K],
    func11: typing.Callable[[A], L],
    func12: typing.Callable[[A], M],
    func13: typing.Callable[[A], N],
    func14: typing.Callable[[A], O],
    func15: typing.Callable[[A], P],
    func16: typing.Callable[[A], Q],
    func17: typing.Callable[[A], R],
    func18: typing.Callable[[A], S],
    func19: typing.Callable[[A], T],
    func20: typing.Callable[[A], U],
    func21: typing.Callable[[A], V],
    func22: typing.Callable[[A], W],
    func23: typing.Callable[[A], X],
    func24: typing.Callable[[A], Y],
    /,
) -> typing.Callable[[A], tuple[B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y]]: ...
@typing.overload
def juxt[A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z](
    func1: typing.Callable[[A], B],
    func2: typing.Callable[[A], C],
    func3: typing.Callable[[A], D],
    func4: typing.Callable[[A], E],
    func5: typing.Callable[[A], F],
    func6: typing.Callable[[A], G],
    func7: typing.Callable[[A], H],
    func8: typing.Callable[[A], I],
    func9: typing.Callable[[A], J],
    func10: typing.Callable[[A], K],
    func11: typing.Callable[[A], L],
    func12: typing.Callable[[A], M],
    func13: typing.Callable[[A], N],
    func14: typing.Callable[[A], O],
    func15: typing.Callable[[A], P],
    func16: typing.Callable[[A], Q],
    func17: typing.Callable[[A], R],
    func18: typing.Callable[[A], S],
    func19: typing.Callable[[A], T],
    func20: typing.Callable[[A], U],
    func21: typing.Callable[[A], V],
    func22: typing.Callable[[A], W],
    func23: typing.Callable[[A], X],
    func24: typing.Callable[[A], Y],
    func25: typing.Callable[[A], Z],
    /,
) -> typing.Callable[[A], tuple[B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z]]: ...

@typing.overload
def pipe[T, U](data: T, func: typing.Callable[[T], U], /) -> U: ...
@typing.overload
def pipe[T, U, V](
    data: T, func: typing.Callable[[T], U], func2: typing.Callable[[U], V], /
) -> V: ...
@typing.overload
def pipe[T, U, V, W](
    data: T,
    func: typing.Callable[[T], U],
    func2: typing.Callable[[U], V],
    func3: typing.Callable[[V], W],
    /,
) -> W: ...
@typing.overload
def pipe[T, U, V, W, X](
    data: T,
    func: typing.Callable[[T], U],
    func2: typing.Callable[[U], V],
    func3: typing.Callable[[V], W],
    func4: typing.Callable[[W], X],
    /,
) -> X: ...
@typing.overload
def pipe[T, U, V, W, X, Y](
    data: T,
    func: typing.Callable[[T], U],
    func2: typing.Callable[[U], V],
    func3: typing.Callable[[V], W],
    func4: typing.Callable[[W], X],
    func5: typing.Callable[[X], Y],
    /,
) -> Y: ...
@typing.overload
def pipe[T, U, V, W, X, Y, Z](
    data: T,
    func: typing.Callable[[T], U],
    func2: typing.Callable[[U], V],
    func3: typing.Callable[[V], W],
    func4: typing.Callable[[W], X],
    func5: typing.Callable[[X], Y],
    func6: typing.Callable[[Y], Z],
    /,
) -> Z: ...
@typing.overload
def pipe[T, U, V, W, X, Y, Z, A](
    data: T,
    func: typing.Callable[[T], U],
    func2: typing.Callable[[U], V],
    func3: typing.Callable[[V], W],
    func4: typing.Callable[[W], X],
    func5: typing.Callable[[X], Y],
    func6: typing.Callable[[Y], Z],
    func7: typing.Callable[[Z], A],
    /,
) -> A: ...
@typing.overload
def pipe[T, U, V, W, X, Y, Z, A, B](
    data: T,
    func: typing.Callable[[T], U],
    func2: typing.Callable[[U], V],
    func3: typing.Callable[[V], W],
    func4: typing.Callable[[W], X],
    func5: typing.Callable[[X], Y],
    func6: typing.Callable[[Y], Z],
    func7: typing.Callable[[Z], A],
    func8: typing.Callable[[A], B],
    /,
) -> B: ...
@typing.overload
def pipe[T, U, V, W, X, Y, Z, A, B, C](
    data: T,
    func: typing.Callable[[T], U],
    func2: typing.Callable[[U], V],
    func3: typing.Callable[[V], W],
    func4: typing.Callable[[W], X],
    func5: typing.Callable[[X], Y],
    func6: typing.Callable[[Y], Z],
    func7: typing.Callable[[Z], A],
    func8: typing.Callable[[A], B],
    func9: typing.Callable[[B], C],
    /,
) -> C: ...
@typing.overload
def pipe[T, U, V, W, X, Y, Z, A, B, C, D](
    data: T,
    func: typing.Callable[[T], U],
    func2: typing.Callable[[U], V],
    func3: typing.Callable[[V], W],
    func4: typing.Callable[[W], X],
    func5: typing.Callable[[X], Y],
    func6: typing.Callable[[Y], Z],
    func7: typing.Callable[[Z], A],
    func8: typing.Callable[[A], B],
    func9: typing.Callable[[B], C],
    func10: typing.Callable[[C], D],
    /,
) -> D: ...
@typing.overload
def pipe[T, U, V, W, X, Y, Z, A, B, C, D, E](
    data: T,
    func: typing.Callable[[T], U],
    func2: typing.Callable[[U], V],
    func3: typing.Callable[[V], W],
    func4: typing.Callable[[W], X],
    func5: typing.Callable[[X], Y],
    func6: typing.Callable[[Y], Z],
    func7: typing.Callable[[Z], A],
    func8: typing.Callable[[A], B],
    func9: typing.Callable[[B], C],
    func10: typing.Callable[[C], D],
    func11: typing.Callable[[D], E],
    /,
) -> E: ...
@typing.overload
def pipe[T, U, V, W, X, Y, Z, A, B, C, D, E, F](
    data: T,
    func: typing.Callable[[T], U],
    func2: typing.Callable[[U], V],
    func3: typing.Callable[[V], W],
    func4: typing.Callable[[W], X],
    func5: typing.Callable[[X], Y],
    func6: typing.Callable[[Y], Z],
    func7: typing.Callable[[Z], A],
    func8: typing.Callable[[A], B],
    func9: typing.Callable[[B], C],
    func10: typing.Callable[[C], D],
    func11: typing.Callable[[D], E],
    func12: typing.Callable[[E], F],
    /,
) -> F: ...
@typing.overload
def pipe[T, U, V, W, X, Y, Z, A, B, C, D, E, F, G](
    data: T,
    func: typing.Callable[[T], U],
    func2: typing.Callable[[U], V],
    func3: typing.Callable[[V], W],
    func4: typing.Callable[[W], X],
    func5: typing.Callable[[X], Y],
    func6: typing.Callable[[Y], Z],
    func7: typing.Callable[[Z], A],
    func8: typing.Callable[[A], B],
    func9: typing.Callable[[B], C],
    func10: typing.Callable[[C], D],
    func11: typing.Callable[[D], E],
    func12: typing.Callable[[E], F],
    func13: typing.Callable[[F], G],
    /,
) -> G: ...
@typing.overload
def pipe[T, U, V, W, X, Y, Z, A, B, C, D, E, F, G, H](
    data: T,
    func: typing.Callable[[T], U],
    func2: typing.Callable[[U], V],
    func3: typing.Callable[[V], W],
    func4: typing.Callable[[W], X],
    func5: typing.Callable[[X], Y],
    func6: typing.Callable[[Y], Z],
    func7: typing.Callable[[Z], A],
    func8: typing.Callable[[A], B],
    func9: typing.Callable[[B], C],
    func10: typing.Callable[[C], D],
    func11: typing.Callable[[D], E],
    func12: typing.Callable[[E], F],
    func13: typing.Callable[[F], G],
    func14: typing.Callable[[G], H],
    /,
) -> H: ...
@typing.overload
def pipe[T, U, V, W, X, Y, Z, A, B, C, D, E, F, G, H, I](
    data: T,
    func: typing.Callable[[T], U],
    func2: typing.Callable[[U], V],
    func3: typing.Callable[[V], W],
    func4: typing.Callable[[W], X],
    func5: typing.Callable[[X], Y],
    func6: typing.Callable[[Y], Z],
    func7: typing.Callable[[Z], A],
    func8: typing.Callable[[A], B],
    func9: typing.Callable[[B], C],
    func10: typing.Callable[[C], D],
    func11: typing.Callable[[D], E],
    func12: typing.Callable[[E], F],
    func13: typing.Callable[[F], G],
    func14: typing.Callable[[G], H],
    func15: typing.Callable[[H], I],
    /,
) -> I: ...
@typing.overload
def pipe[T, U, V, W, X, Y, Z, A, B, C, D, E, F, G, H, I, J](
    data: T,
    func: typing.Callable[[T], U],
    func2: typing.Callable[[U], V],
    func3: typing.Callable[[V], W],
    func4: typing.Callable[[W], X],
    func5: typing.Callable[[X], Y],
    func6: typing.Callable[[Y], Z],
    func7: typing.Callable[[Z], A],
    func8: typing.Callable[[A], B],
    func9: typing.Callable[[B], C],
    func10: typing.Callable[[C], D],
    func11: typing.Callable[[D], E],
    func12: typing.Callable[[E], F],
    func13: typing.Callable[[F], G],
    func14: typing.Callable[[G], H],
    func15: typing.Callable[[H], I],
    func16: typing.Callable[[I], J],
    /,
) -> J: ...
@typing.overload
def pipe[T, U, V, W, X, Y, Z, A, B, C, D, E, F, G, H, I, J, K](
    data: T,
    func: typing.Callable[[T], U],
    func2: typing.Callable[[U], V],
    func3: typing.Callable[[V], W],
    func4: typing.Callable[[W], X],
    func5: typing.Callable[[X], Y],
    func6: typing.Callable[[Y], Z],
    func7: typing.Callable[[Z], A],
    func8: typing.Callable[[A], B],
    func9: typing.Callable[[B], C],
    func10: typing.Callable[[C], D],
    func11: typing.Callable[[D], E],
    func12: typing.Callable[[E], F],
    func13: typing.Callable[[F], G],
    func14: typing.Callable[[G], H],
    func15: typing.Callable[[H], I],
    func16: typing.Callable[[I], J],
    func17: typing.Callable[[J], K],
    /,
) -> K: ...
@typing.overload
def pipe[T, U, V, W, X, Y, Z, A, B, C, D, E, F, G, H, I, J, K, L](
    data: T,
    func: typing.Callable[[T], U],
    func2: typing.Callable[[U], V],
    func3: typing.Callable[[V], W],
    func4: typing.Callable[[W], X],
    func5: typing.Callable[[X], Y],
    func6: typing.Callable[[Y], Z],
    func7: typing.Callable[[Z], A],
    func8: typing.Callable[[A], B],
    func9: typing.Callable[[B], C],
    func10: typing.Callable[[C], D],
    func11: typing.Callable[[D], E],
    func12: typing.Callable[[E], F],
    func13: typing.Callable[[F], G],
    func14: typing.Callable[[G], H],
    func15: typing.Callable[[H], I],
    func16: typing.Callable[[I], J],
    func17: typing.Callable[[J], K],
    func18: typing.Callable[[K], L],
    /,
) -> L: ...
@typing.overload
def pipe[T, U, V, W, X, Y, Z, A, B, C, D, E, F, G, H, I, J, K, L, M](
    data: T,
    func: typing.Callable[[T], U],
    func2: typing.Callable[[U], V],
    func3: typing.Callable[[V], W],
    func4: typing.Callable[[W], X],
    func5: typing.Callable[[X], Y],
    func6: typing.Callable[[Y], Z],
    func7: typing.Callable[[Z], A],
    func8: typing.Callable[[A], B],
    func9: typing.Callable[[B], C],
    func10: typing.Callable[[C], D],
    func11: typing.Callable[[D], E],
    func12: typing.Callable[[E], F],
    func13: typing.Callable[[F], G],
    func14: typing.Callable[[G], H],
    func15: typing.Callable[[H], I],
    func16: typing.Callable[[I], J],
    func17: typing.Callable[[J], K],
    func18: typing.Callable[[K], L],
    func19: typing.Callable[[L], M],
    /,
) -> M: ...
@typing.overload
def pipe[T, U, V, W, X, Y, Z, A, B, C, D, E, F, G, H, I, J, K, L, M, N](
    data: T,
    func: typing.Callable[[T], U],
    func2: typing.Callable[[U], V],
    func3: typing.Callable[[V], W],
    func4: typing.Callable[[W], X],
    func5: typing.Callable[[X], Y],
    func6: typing.Callable[[Y], Z],
    func7: typing.Callable[[Z], A],
    func8: typing.Callable[[A], B],
    func9: typing.Callable[[B], C],
    func10: typing.Callable[[C], D],
    func11: typing.Callable[[D], E],
    func12: typing.Callable[[E], F],
    func13: typing.Callable[[F], G],
    func14: typing.Callable[[G], H],
    func15: typing.Callable[[H], I],
    func16: typing.Callable[[I], J],
    func17: typing.Callable[[J], K],
    func18: typing.Callable[[K], L],
    func19: typing.Callable[[L], M],
    func20: typing.Callable[[M], N],
    /,
) -> N: ...
@typing.overload
def pipe[T, U, V, W, X, Y, Z, A, B, C, D, E, F, G, H, I, J, K, L, M, N, O](
    data: T,
    func: typing.Callable[[T], U],
    func2: typing.Callable[[U], V],
    func3: typing.Callable[[V], W],
    func4: typing.Callable[[W], X],
    func5: typing.Callable[[X], Y],
    func6: typing.Callable[[Y], Z],
    func7: typing.Callable[[Z], A],
    func8: typing.Callable[[A], B],
    func9: typing.Callable[[B], C],
    func10: typing.Callable[[C], D],
    func11: typing.Callable[[D], E],
    func12: typing.Callable[[E], F],
    func13: typing.Callable[[F], G],
    func14: typing.Callable[[G], H],
    func15: typing.Callable[[H], I],
    func16: typing.Callable[[I], J],
    func17: typing.Callable[[J], K],
    func18: typing.Callable[[K], L],
    func19: typing.Callable[[L], M],
    func20: typing.Callable[[M], N],
    func21: typing.Callable[[N], O],
    /,
) -> O: ...
@typing.overload
def pipe[T, U, V, W, X, Y, Z, A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P](
    data: T,
    func: typing.Callable[[T], U],
    func2: typing.Callable[[U], V],
    func3: typing.Callable[[V], W],
    func4: typing.Callable[[W], X],
    func5: typing.Callable[[X], Y],
    func6: typing.Callable[[Y], Z],
    func7: typing.Callable[[Z], A],
    func8: typing.Callable[[A], B],
    func9: typing.Callable[[B], C],
    func10: typing.Callable[[C], D],
    func11: typing.Callable[[D], E],
    func12: typing.Callable[[E], F],
    func13: typing.Callable[[F], G],
    func14: typing.Callable[[G], H],
    func15: typing.Callable[[H], I],
    func16: typing.Callable[[I], J],
    func17: typing.Callable[[J], K],
    func18: typing.Callable[[K], L],
    func19: typing.Callable[[L], M],
    func20: typing.Callable[[M], N],
    func21: typing.Callable[[N], O],
    func22: typing.Callable[[O], P],
    /,
) -> P: ...
@typing.overload
def pipe[T, U, V, W, X, Y, Z, A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q](
    data: T,
    func: typing.Callable[[T], U],
    func2: typing.Callable[[U], V],
    func3: typing.Callable[[V], W],
    func4: typing.Callable[[W], X],
    func5: typing.Callable[[X], Y],
    func6: typing.Callable[[Y], Z],
    func7: typing.Callable[[Z], A],
    func8: typing.Callable[[A], B],
    func9: typing.Callable[[B], C],
    func10: typing.Callable[[C], D],
    func11: typing.Callable[[D], E],
    func12: typing.Callable[[E], F],
    func13: typing.Callable[[F], G],
    func14: typing.Callable[[G], H],
    func15: typing.Callable[[H], I],
    func16: typing.Callable[[I], J],
    func17: typing.Callable[[J], K],
    func18: typing.Callable[[K], L],
    func19: typing.Callable[[L], M],
    func20: typing.Callable[[M], N],
    func21: typing.Callable[[N], O],
    func22: typing.Callable[[O], P],
    func23: typing.Callable[[P], Q],
    /,
) -> Q: ...
@typing.overload
def pipe[T, U, V, W, X, Y, Z, A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R](
    data: T,
    func: typing.Callable[[T], U],
    func2: typing.Callable[[U], V],
    func3: typing.Callable[[V], W],
    func4: typing.Callable[[W], X],
    func5: typing.Callable[[X], Y],
    func6: typing.Callable[[Y], Z],
    func7: typing.Callable[[Z], A],
    func8: typing.Callable[[A], B],
    func9: typing.Callable[[B], C],
    func10: typing.Callable[[C], D],
    func11: typing.Callable[[D], E],
    func12: typing.Callable[[E], F],
    func13: typing.Callable[[F], G],
    func14: typing.Callable[[G], H],
    func15: typing.Callable[[H], I],
    func16: typing.Callable[[I], J],
    func17: typing.Callable[[J], K],
    func18: typing.Callable[[K], L],
    func19: typing.Callable[[L], M],
    func20: typing.Callable[[M], N],
    func21: typing.Callable[[N], O],
    func22: typing.Callable[[O], P],
    func23: typing.Callable[[P], Q],
    func24: typing.Callable[[Q], R],
    /,
) -> R: ...
@typing.overload
def pipe[T, U, V, W, X, Y, Z, A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S](
    data: T,
    func: typing.Callable[[T], U],
    func2: typing.Callable[[U], V],
    func3: typing.Callable[[V], W],
    func4: typing.Callable[[W], X],
    func5: typing.Callable[[X], Y],
    func6: typing.Callable[[Y], Z],
    func7: typing.Callable[[Z], A],
    func8: typing.Callable[[A], B],
    func9: typing.Callable[[B], C],
    func10: typing.Callable[[C], D],
    func11: typing.Callable[[D], E],
    func12: typing.Callable[[E], F],
    func13: typing.Callable[[F], G],
    func14: typing.Callable[[G], H],
    func15: typing.Callable[[H], I],
    func16: typing.Callable[[I], J],
    func17: typing.Callable[[J], K],
    func18: typing.Callable[[K], L],
    func19: typing.Callable[[L], M],
    func20: typing.Callable[[M], N],
    func21: typing.Callable[[N], O],
    func22: typing.Callable[[O], P],
    func23: typing.Callable[[P], Q],
    func24: typing.Callable[[Q], R],
    func25: typing.Callable[[R], S],
    /,
) -> S: ...
@typing.overload
def pipe[T, U, V, W, X, Y, Z, A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, TOut](
    data: T,
    func: typing.Callable[[T], U],
    func2: typing.Callable[[U], V],
    func3: typing.Callable[[V], W],
    func4: typing.Callable[[W], X],
    func5: typing.Callable[[X], Y],
    func6: typing.Callable[[Y], Z],
    func7: typing.Callable[[Z], A],
    func8: typing.Callable[[A], B],
    func9: typing.Callable[[B], C],
    func10: typing.Callable[[C], D],
    func11: typing.Callable[[D], E],
    func12: typing.Callable[[E], F],
    func13: typing.Callable[[F], G],
    func14: typing.Callable[[G], H],
    func15: typing.Callable[[H], I],
    func16: typing.Callable[[I], J],
    func17: typing.Callable[[J], K],
    func18: typing.Callable[[K], L],
    func19: typing.Callable[[L], M],
    func20: typing.Callable[[M], N],
    func21: typing.Callable[[N], O],
    func22: typing.Callable[[O], P],
    func23: typing.Callable[[P], Q],
    func24: typing.Callable[[Q], R],
    func25: typing.Callable[[R], S],
    func26: typing.Callable[[S], TOut],
    /,
) -> TOut: ...
