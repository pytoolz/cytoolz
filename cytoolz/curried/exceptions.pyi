import collections.abc
import typing

__all__ = ["merge", "merge_with"]

class _AnyCallable[ReturnT](typing.Protocol):
    def __call__(self, *args: object, **kwargs: object) -> ReturnT: ...

@typing.overload
def merge_with[K, V]() -> _AnyCallable[
    dict[K, V] | collections.abc.MutableMapping[K, V]
]: ...
@typing.overload
def merge_with[K, V](
    func: typing.Callable[[list[V]], V], /
) -> _AnyCallable[dict[K, V] | collections.abc.MutableMapping[K, V]]: ...
@typing.overload
def merge_with[K, V](
    func: typing.Callable[[list[V]], V],
    d: collections.abc.Mapping[K, V],
    /,
) -> dict[K, V]: ...
@typing.overload
def merge_with[K, V](
    func: typing.Callable[[list[V]], V],
    d: collections.abc.Mapping[K, V],
    d2: collections.abc.Mapping[K, V],
    /,
    *dicts: collections.abc.Mapping[K, V],
) -> dict[K, V]: ...
@typing.overload
def merge_with[K, V](
    func: typing.Callable[[list[V]], V],
    d: collections.abc.Mapping[K, V],
    d2: collections.abc.Mapping[K, V],
    /,
    *dicts: collections.abc.Mapping[K, V],
    factory: typing.Callable[[], collections.abc.MutableMapping[K, V]],
) -> collections.abc.MutableMapping[K, V]: ...
@typing.overload
def merge_with[K, V](
    func: typing.Callable[[list[V]], V],
    /,
    *,
    factory: typing.Callable[[], collections.abc.MutableMapping[K, V]],
) -> _AnyCallable[collections.abc.MutableMapping[K, V]]: ...
@typing.overload
def merge[K, V]() -> _AnyCallable[
    dict[K, V] | collections.abc.MutableMapping[K, V]
]: ...
@typing.overload
def merge[K, V](d: collections.abc.Mapping[K, V], /) -> dict[K, V]: ...
@typing.overload
def merge[K, V](
    d: collections.abc.Mapping[K, V],
    d2: collections.abc.Mapping[K, V],
    /,
    *dicts: collections.abc.Mapping[K, V],
) -> dict[K, V]: ...
@typing.overload
def merge[K, V](
    d: collections.abc.Mapping[K, V],
    d2: collections.abc.Mapping[K, V],
    /,
    *dicts: collections.abc.Mapping[K, V],
    factory: typing.Callable[[], collections.abc.MutableMapping[K, V]],
) -> collections.abc.MutableMapping[K, V]: ...
@typing.overload
def merge[K, V](
    *,
    factory: typing.Callable[[], collections.abc.MutableMapping[K, V]],
) -> _AnyCallable[collections.abc.MutableMapping[K, V]]: ...
