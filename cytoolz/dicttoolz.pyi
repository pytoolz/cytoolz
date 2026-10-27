# pyright: reportAny=false
import collections.abc
import typing

class _AnyCallable[ReturnT](typing.Protocol):
    def __call__(self, *args: object, **kwargs: object) -> ReturnT: ...

__all__ = (
    "merge",
    "merge_with",
    "valmap",
    "keymap",
    "itemmap",
    "valfilter",
    "keyfilter",
    "itemfilter",
    "assoc",
    "dissoc",
    "assoc_in",
    "update_in",
    "get_in",
)

@typing.overload
def merge[K, V](*dicts: collections.abc.Mapping[K, V]) -> dict[K, V]: ...
@typing.overload
def merge[K, V](
    *dicts: collections.abc.Mapping[K, V],
    factory: typing.Callable[[], collections.abc.MutableMapping[K, V]],
) -> collections.abc.MutableMapping[K, V]: ...
@typing.overload
def merge_with[K, V](
    func: typing.Callable[[list[V]], V],
    *dicts: collections.abc.Mapping[K, V],
) -> dict[K, V]: ...
@typing.overload
def merge_with[K, V](
    func: typing.Callable[[list[V]], V],
    *dicts: collections.abc.Mapping[K, V],
    factory: typing.Callable[[], collections.abc.MutableMapping[K, V]],
) -> collections.abc.MutableMapping[K, V]: ...
@typing.overload
def valmap[K, V0, V1](
    func: typing.Callable[[V0], V1],
    d: collections.abc.Mapping[K, V0],
) -> dict[K, V1]: ...
@typing.overload
def valmap[K, V0, V1](
    func: typing.Callable[[V0], V1],
    d: collections.abc.Mapping[K, V0],
    *,
    factory: typing.Callable[[], collections.abc.MutableMapping[K, V1]],
) -> collections.abc.MutableMapping[K, V1]: ...
@typing.overload
def keymap[K0, K1, V](
    func: typing.Callable[[K0], K1],
    d: collections.abc.Mapping[K0, V],
) -> dict[K1, V]: ...
@typing.overload
def keymap[K0, K1, V](
    func: typing.Callable[[K0], K1],
    d: collections.abc.Mapping[K0, V],
    *,
    factory: typing.Callable[[], collections.abc.MutableMapping[K1, V]],
) -> collections.abc.MutableMapping[K1, V]: ...
@typing.overload
def itemmap[K0, V0, K1, V1](
    func: typing.Callable[[tuple[K0, V0]], tuple[K1, V1]],
    d: collections.abc.Mapping[K0, V0],
) -> dict[K1, V1]: ...
@typing.overload
def itemmap[K0, V0, K1, V1](
    func: typing.Callable[[tuple[K0, V0]], tuple[K1, V1]],
    d: collections.abc.Mapping[K0, V0],
    *,
    factory: typing.Callable[[], collections.abc.MutableMapping[K1, V1]],
) -> collections.abc.MutableMapping[K1, V1]: ...
@typing.overload
def valfilter[K, V](
    predicate: typing.Callable[[V], bool],
    d: collections.abc.Mapping[K, V],
) -> dict[K, V]: ...
@typing.overload
def valfilter[K, V](
    predicate: typing.Callable[[V], bool],
    d: collections.abc.Mapping[K, V],
    *,
    factory: typing.Callable[[], collections.abc.MutableMapping[K, V]],
) -> collections.abc.MutableMapping[K, V]: ...
@typing.overload
def keyfilter[K, V](
    predicate: typing.Callable[[K], bool],
    d: collections.abc.Mapping[K, V],
) -> dict[K, V]: ...
@typing.overload
def keyfilter[K, V](
    predicate: typing.Callable[[K], bool],
    d: collections.abc.Mapping[K, V],
    *,
    factory: typing.Callable[[], collections.abc.MutableMapping[K, V]],
) -> collections.abc.MutableMapping[K, V]: ...
@typing.overload
def itemfilter[K, V](
    predicate: typing.Callable[[tuple[K, V]], bool],
    d: collections.abc.Mapping[K, V],
) -> dict[K, V]: ...
@typing.overload
def itemfilter[K, V](
    predicate: typing.Callable[[tuple[K, V]], bool],
    d: collections.abc.Mapping[K, V],
    *,
    factory: typing.Callable[[], collections.abc.MutableMapping[K, V]],
) -> collections.abc.MutableMapping[K, V]: ...
@typing.overload
def assoc[K, V](
    d: collections.abc.Mapping[K, V],
    key: K,
    value: V,
) -> dict[K, V]: ...
@typing.overload
def assoc[K, V](
    d: collections.abc.Mapping[K, V],
    key: K,
    value: V,
    *,
    factory: typing.Callable[[], collections.abc.MutableMapping[K, V]],
) -> collections.abc.MutableMapping[K, V]: ...
@typing.overload
def dissoc[K, V](
    d: collections.abc.Mapping[K, V],
    *keys: K,
) -> dict[K, V]: ...
@typing.overload
def dissoc[K, V](
    d: collections.abc.Mapping[K, V],
    *keys: K,
    factory: typing.Callable[[], collections.abc.MutableMapping[K, V]],
) -> collections.abc.MutableMapping[K, V]: ...
# Overloads for nested dictionaries with tuple keys (2-level nesting)
@typing.overload
def assoc_in[K1, K2, V1, V2](
    d: collections.abc.Mapping[K1, collections.abc.Mapping[K2, V2] | V1],
    keys: tuple[K1, K2],
    value: V2,
) -> dict[K1, dict[K2, V2] | V1 | V2]: ...
@typing.overload
def assoc_in[K1, K2, V1, V2](
    d: collections.abc.Mapping[K1, collections.abc.Mapping[K2, V2] | V1],
    keys: tuple[K1, K2],
    value: V2,
    *,
    factory: typing.Callable[[], collections.abc.MutableMapping[K1, object]],
) -> collections.abc.MutableMapping[K1, object]: ...

# Overloads for nested dictionaries with tuple keys (3-level nesting)
@typing.overload
def assoc_in[K1, K2, K3, V1, V2, V3](
    d: collections.abc.Mapping[
        K1, collections.abc.Mapping[K2, collections.abc.Mapping[K3, V3] | V2] | V1
    ],
    keys: tuple[K1, K2, K3],
    value: V3,
) -> dict[K1, dict[K2, dict[K3, V3] | V2 | V3] | V1 | V3]: ...
@typing.overload
def assoc_in[K1, K2, K3, V1, V2, V3](
    d: collections.abc.Mapping[
        K1, collections.abc.Mapping[K2, collections.abc.Mapping[K3, V3] | V2] | V1
    ],
    keys: tuple[K1, K2, K3],
    value: V3,
    *,
    factory: typing.Callable[[], collections.abc.MutableMapping[K1, object]],
) -> collections.abc.MutableMapping[K1, object]: ...

# General overloads for backwards compatibility
@typing.overload
def assoc_in[K, V](
    d: collections.abc.Mapping[K, V],
    keys: collections.abc.Iterable[K] | K,
    value: V,
) -> dict[K, V]: ...
@typing.overload
def assoc_in[K, V](
    d: collections.abc.Mapping[K, V],
    keys: collections.abc.Iterable[K] | K,
    value: V,
    *,
    factory: typing.Callable[[], collections.abc.MutableMapping[K, V]],
) -> collections.abc.MutableMapping[K, V]: ...
@typing.overload
def update_in[K, V](
    d: collections.abc.Mapping[K, V],
    keys: collections.abc.Iterable[K] | K,
    func: _AnyCallable[V],
    default: object | None = None,
) -> dict[K, V]: ...
@typing.overload
def update_in[K, V](
    d: collections.abc.Mapping[K, V],
    keys: collections.abc.Iterable[K] | K,
    func: _AnyCallable[V],
    default: object | None,
    factory: typing.Callable[[], collections.abc.MutableMapping[K, V]],
) -> collections.abc.MutableMapping[K, V]: ...
@typing.overload
def update_in[K, V](
    d: collections.abc.Mapping[K, V],
    keys: collections.abc.Iterable[K] | K,
    func: _AnyCallable[V],
    default: object | None = None,
    factory: typing.Callable[[], collections.abc.MutableMapping[K, V]] = dict,
) -> collections.abc.MutableMapping[K, V]: ...
@typing.overload
def get_in[K, V, D](
    keys: collections.abc.Iterable[K] | K,
    coll: collections.abc.Iterable[V] | collections.abc.Mapping[K, V],
    default: V,
    no_default: bool = ...,
) -> V: ...
@typing.overload
def get_in[K, V, D](
    keys: collections.abc.Iterable[K] | K,
    coll: collections.abc.Iterable[V] | collections.abc.Mapping[K, V],
    default: D = ...,
    no_default: bool = ...,
) -> V | D: ...
