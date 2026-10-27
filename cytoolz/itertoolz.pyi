# pyright: reportAny=false
import collections.abc
import typing

from _typeshed import SupportsRichComparison

from .utils import no_default

__all__ = (
    "remove",
    "accumulate",
    "groupby",
    "merge_sorted",
    "interleave",
    "unique",
    "isiterable",
    "isdistinct",
    "take",
    "drop",
    "take_nth",
    "first",
    "second",
    "nth",
    "last",
    "get",
    "concat",
    "concatv",
    "mapcat",
    "cons",
    "interpose",
    "frequencies",
    "reduceby",
    "iterate",
    "sliding_window",
    "partition",
    "partition_all",
    "count",
    "pluck",
    "join",
    "tail",
    "diff",
    "topk",
    "peek",
    "peekn",
    "random_sample",
)

### Special types for toolz
type _NoDefaultType = typing.Literal["__no_default__"]
type _NoPadType = typing.Literal["__no_pad__"]

class _Randomable(typing.Protocol):
    def random(self) -> float: ...

### Toolz itself

def remove[T](
    predicate: typing.Callable[[T], bool], seq: collections.abc.Iterable[T]
) -> collections.abc.Iterable[T]:
    """Return those items of sequence for which predicate(item) is False

    >>> def iseven(x):
    ...     return x % 2 == 0
    >>> list(remove(iseven, [1, 2, 3, 4]))
    [1, 3]
    """
    ...

@typing.overload
def accumulate[T](
    binop: typing.Callable[[T, T], T],
    seq: collections.abc.Iterable[T],
) -> collections.abc.Iterator[T]: ...
@typing.overload
def accumulate[T](
    binop: typing.Callable[[T, T], T], seq: collections.abc.Iterable[T], initial: T
) -> collections.abc.Iterator[T]: ...
def groupby[KT, T](
    key: typing.Callable[[T], KT], seq: collections.abc.Iterable[T]
) -> dict[KT, list[T]]:
    """Group a collection by a key function

    >>> names = ['Alice', 'Bob', 'Charlie', 'Dan', 'Edith', 'Frank']
    >>> groupby(len, names)  # doctest: +SKIP
    {3: ['Bob', 'Dan'], 5: ['Alice', 'Edith', 'Frank'], 7: ['Charlie']}

    >>> iseven = lambda x: x % 2 == 0
    >>> groupby(iseven, [1, 2, 3, 4, 5, 6, 7, 8])  # doctest: +SKIP
    {False: [1, 3, 5, 7], True: [2, 4, 6, 8]}

    Non-callable keys imply grouping on a member.

    >>> groupby('gender', [{'name': 'Alice', 'gender': 'F'},
    ...                    {'name': 'Bob', 'gender': 'M'},
    ...                    {'name': 'Charlie', 'gender': 'M'}]) # doctest:+SKIP
    {'F': [{'gender': 'F', 'name': 'Alice'}],
     'M': [{'gender': 'M', 'name': 'Bob'},
           {'name': 'Charlie', 'gender': 'M'}]}

    Not to be confused with ``itertools.groupby``

    See Also:
        countby
    """
    ...

def merge_sorted[CT: SupportsRichComparison](
    *seqs: collections.abc.Iterable[CT], key: typing.Callable[[CT], CT] | None = None
) -> collections.abc.Iterator[CT]:
    """Merge and sort a collection of sorted collections

    This works lazily and only keeps one value from each iterable in memory.

    >>> list(merge_sorted([1, 3, 5], [2, 4, 6]))
    [1, 2, 3, 4, 5, 6]

    >>> ''.join(merge_sorted('abc', 'abc', 'abc'))
    'aaabbbccc'

    The "key" function used to sort the input may be passed as a keyword.

    >>> list(merge_sorted([2, 3], [1, 3], key=lambda x: x // 3))
    [2, 1, 3, 3]
    """
    ...

def interleave[T](
    seqs: collections.abc.Iterable[collections.abc.Iterable[T]],
) -> collections.abc.Iterator[T]:
    """Interleave a sequence of sequences

    >>> list(interleave([[1, 2], [3, 4]]))
    [1, 3, 2, 4]

    >>> ''.join(interleave(('ABC', 'XY')))
    'AXBYC'

    Both the individual sequences and the sequence of sequences may be infinite

    Returns a lazy iterator
    """
    ...

def unique[T](
    seq: collections.abc.Sequence[T],
    key: typing.Callable[[T], object] | None = None,
) -> collections.abc.Iterator[T]:
    """Return only unique elements of a sequence

    >>> tuple(unique((1, 2, 3)))
    (1, 2, 3)
    >>> tuple(unique((1, 2, 1, 3)))
    (1, 2, 3)

    Uniqueness can be defined by key keyword

    >>> tuple(unique(['cat', 'mouse', 'dog', 'hen'], key=len))
    ('cat', 'mouse')
    """
    ...

def isiterable(x: object) -> typing.TypeGuard[collections.abc.Iterable[object]]:
    """Is x iterable?

    >>> isiterable([1, 2, 3])
    True
    >>> isiterable('abc')
    True
    >>> isiterable(5)
    False
    """
    ...

def isdistinct(
    seq: collections.abc.Iterable[object] | collections.abc.Sequence[object],
) -> bool:
    """All values in sequence are distinct

    >>> isdistinct([1, 2, 3])
    True
    >>> isdistinct([1, 2, 1])
    False

    >>> isdistinct("Hello")
    False
    >>> isdistinct("World")
    True
    """
    ...

def take[T](n: int, seq: collections.abc.Iterable[T]) -> collections.abc.Iterator[T]:
    """The first n elements of a sequence

    >>> list(take(2, [10, 20, 30, 40, 50]))
    [10, 20]

    See Also:
        drop
        tail
    """
    ...

def tail[T](n: int, seq: collections.abc.Iterable[T]) -> collections.abc.Iterator[T]:
    """The last n elements of a sequence

    >>> tail(2, [10, 20, 30, 40, 50])
    [40, 50]

    See Also:
        drop
        take
    """
    ...

def drop[T](n: int, seq: collections.abc.Iterable[T]) -> collections.abc.Iterator[T]:
    """The sequence following the first n elements

    >>> list(drop(2, [10, 20, 30, 40, 50]))
    [30, 40, 50]

    See Also:
        take
        tail
    """
    ...

def take_nth[T](
    n: int, seq: collections.abc.Iterable[T]
) -> collections.abc.Iterator[T]:
    """Every nth item in seq

    >>> list(take_nth(2, [10, 20, 30, 40, 50]))
    [10, 30, 50]
    """
    ...

def first[T](seq: collections.abc.Iterable[T]) -> T:
    """The first element in a sequence

    >>> first('ABC')
    'A'
    """
    ...

def second[T](seq: collections.abc.Iterable[T]) -> T:
    """The second element in a sequence

    >>> second('ABC')
    'B'
    """
    ...

def nth[T](n: int, seq: collections.abc.Iterable[T]) -> T:
    """The nth element in a sequence

    >>> nth(1, 'ABC')
    'B'
    """
    ...

def last[T](seq: collections.abc.Iterable[T]) -> T:
    """The last element in a sequence

    >>> last('ABC')
    'C'
    """
    ...

def rest[T](seq: collections.abc.Iterable[T]) -> collections.abc.Iterable[T]:
    """All but the first element in a sequence

    >>> rest('ABC')
    'BC'
    """
    # Warning - this function is not exposed via __all__ and should be considered private.
    ...

@typing.overload
def get[T](
    ind: list[object],
    seq: collections.abc.Sequence[T] | collections.abc.Mapping[object, T],
    default: T | _NoDefaultType = ...,
) -> tuple[T, ...]: ...
@typing.overload
def get[T](
    ind: object,
    seq: collections.abc.Sequence[T] | collections.abc.Mapping[object, T],
    default: T | _NoDefaultType = ...,
) -> T: ...
def concat[T](
    seqs: collections.abc.Iterable[collections.abc.Iterable[T]],
) -> collections.abc.Iterator[T]:
    """Concatenate zero or more iterables, any of which may be infinite.

    An infinite sequence will prevent the rest of the arguments from
    being included.

    We use chain.from_iterable rather than ``chain(*seqs)`` so that seqs
    can be a generator.

    >>> list(concat([[], [1], [2, 3]]))
    [1, 2, 3]

    See also:
        itertools.chain.from_iterable  equivalent
    """
    ...

def concatv[T](*seqs: collections.abc.Iterable[T]) -> collections.abc.Iterator[T]:
    """Variadic version of concat

    >>> list(concatv([], ["a"], ["b", "c"]))
    ['a', 'b', 'c']

    See also:
        itertools.chain
    """
    ...

def mapcat[T, R](
    func: typing.Callable[[T], collections.abc.Iterable[R]],
    seqs: collections.abc.Iterable[T],
) -> collections.abc.Iterator[R]:
    """Apply func to each sequence in seqs, concatenating results.

    >>> list(mapcat(lambda s: [c.upper() for c in s],
    ...             [["a", "b"], ["c", "d", "e"]]))
    ['A', 'B', 'C', 'D', 'E']
    """
    ...

def cons[T](el: T, seq: collections.abc.Iterable[T]) -> collections.abc.Iterator[T]:
    """Add el to beginning of (possibly infinite) sequence seq.

    >>> list(cons(1, [2, 3]))
    [1, 2, 3]
    """
    ...

def interpose[T](
    el: T, seq: collections.abc.Iterable[T]
) -> collections.abc.Iterator[T]:
    """Introduce element between each pair of elements in seq

    >>> list(interpose("a", [1, 2, 3]))
    [1, 'a', 2, 'a', 3]
    """
    ...

def frequencies[T](seq: collections.abc.Iterable[T]) -> dict[T, int]:
    """Find number of occurrences of each value in seq

    >>> frequencies(['cat', 'cat', 'ox', 'pig', 'pig', 'cat'])  #doctest: +SKIP
    {'cat': 3, 'ox': 1, 'pig': 2}

    See Also:
        countby
        groupby
    """
    ...

@typing.overload
def reduceby[T, K](
    key: typing.Callable[[T], K],
    binop: typing.Callable[[T, T], T],
    seq: collections.abc.Iterable[T],
) -> dict[K, T]: ...
@typing.overload
def reduceby[T, K](
    key: typing.Callable[[T], K],
    binop: typing.Callable[[T, T], T],
    seq: collections.abc.Iterable[T],
    init: T | typing.Callable[[], T],
) -> dict[K, T]: ...
@typing.overload
def reduceby[T](
    key: object,  # when not callable, use identity function
    binop: typing.Callable[[T, T], T],
    seq: collections.abc.Iterable[T],
) -> dict[T, T]: ...
@typing.overload
def reduceby[T](
    key: object,  # when not callable, use identity function
    binop: typing.Callable[[T, T], T],
    seq: collections.abc.Iterable[T],
    init: T | typing.Callable[[], T],
) -> dict[T, T]: ...
def iterate[T](func: typing.Callable[[T], T], x: T) -> collections.abc.Iterator[T]:
    """Repeatedly apply a function func onto an original input

    Yields x, then func(x), then func(func(x)), then func(func(func(x))), etc..

    >>> def inc(x):  return x + 1
    >>> counter = iterate(inc, 0)
    >>> next(counter)
    0
    >>> next(counter)
    1
    >>> next(counter)
    2

    >>> double = lambda x: x * 2
    >>> powers_of_two = iterate(double, 1)
    >>> next(powers_of_two)
    1
    >>> next(powers_of_two)
    2
    >>> next(powers_of_two)
    4
    >>> next(powers_of_two)
    8
    """
    ...

def sliding_window[T](
    n: int, seq: collections.abc.Iterable[T]
) -> collections.abc.Iterator[tuple[T, ...]]:
    """A sequence of overlapping subsequences

    >>> list(sliding_window(2, [1, 2, 3, 4]))
    [(1, 2), (2, 3), (3, 4)]

    This function creates a sliding window suitable for transformations like
    sliding means / smoothing

    >>> mean = lambda seq: float(sum(seq)) / len(seq)
    >>> list(map(mean, sliding_window(2, [1, 2, 3, 4])))
    [1.5, 2.5, 3.5]
    """
    ...

no_pad = "__no_pad__"

@typing.overload
def partition[T, P](
    n: typing.Literal[1], seq: collections.abc.Iterable[T], pad: object = ...
) -> collections.abc.Iterator[tuple[T]]: ...
@typing.overload
def partition[T](
    n: int, seq: collections.abc.Iterable[T], pad: _NoPadType = ...
) -> collections.abc.Iterator[tuple[T, ...]]: ...
@typing.overload
def partition[T, P](
    n: int, seq: collections.abc.Iterable[T], pad: P
) -> collections.abc.Iterator[tuple[T | P, ...]]: ...
@typing.overload
def partition_all[T](
    n: typing.Literal[1], seq: collections.abc.Iterable[T]
) -> collections.abc.Iterator[tuple[T]]: ...
@typing.overload
def partition_all[T](
    n: int, seq: collections.abc.Iterable[T]
) -> collections.abc.Iterator[tuple[T, ...]]: ...
def count(seq: collections.abc.Iterable[object]) -> int:
    """Count the number of items in seq

    Like the builtin ``len`` but works on lazy sequences.

    Not to be confused with ``itertools.count``

    See also:
        len
    """
    ...

@typing.overload
def pluck[T](
    ind: list[object],
    seqs: collections.abc.Iterable[
        collections.abc.Sequence[T] | collections.abc.Mapping[object, T]
    ],
    default: T | _NoDefaultType = ...,
) -> collections.abc.Iterator[tuple[T, ...]]: ...
@typing.overload
def pluck[T](
    ind: object,
    seqs: collections.abc.Iterable[
        collections.abc.Sequence[T] | collections.abc.Mapping[object, T]
    ],
    default: T | _NoDefaultType = ...,
) -> collections.abc.Iterator[T]: ...
def getter[T](
    index: object,
) -> typing.Callable[
    [collections.abc.Sequence[T] | collections.abc.Mapping[object, T]],
    T | tuple[T, ...],
]: ...
# === CALLABLE + CALLABLE (4 overloads) ===
@typing.overload
def join[T, U](
    leftkey: typing.Callable[[T], typing.Hashable],
    leftseq: collections.abc.Iterable[T],
    rightkey: typing.Callable[[U], typing.Hashable],
    rightseq: collections.abc.Iterable[U],
) -> collections.abc.Iterator[tuple[T, U]]: ...
@typing.overload
def join[T, U, L](
    leftkey: typing.Callable[[T], typing.Hashable],
    leftseq: collections.abc.Iterable[T],
    rightkey: typing.Callable[[U], typing.Hashable],
    rightseq: collections.abc.Iterable[U],
    left_default: L,
) -> collections.abc.Iterator[tuple[T | L, U]]: ...
@typing.overload
def join[T, U, R](
    leftkey: typing.Callable[[T], typing.Hashable],
    leftseq: collections.abc.Iterable[T],
    rightkey: typing.Callable[[U], typing.Hashable],
    rightseq: collections.abc.Iterable[U],
    *,
    right_default: R,
) -> collections.abc.Iterator[tuple[T, U | R]]: ...
@typing.overload
def join[T, U, L, R](
    leftkey: typing.Callable[[T], typing.Hashable],
    leftseq: collections.abc.Iterable[T],
    rightkey: typing.Callable[[U], typing.Hashable],
    rightseq: collections.abc.Iterable[U],
    left_default: L,
    right_default: R,
) -> collections.abc.Iterator[tuple[T | L, U | R]]: ...

# === HASHABLE + CALLABLE (4 overloads) ===
@typing.overload
def join[T, U](
    leftkey: typing.Hashable,
    leftseq: collections.abc.Iterable[T],
    rightkey: typing.Callable[[U], typing.Hashable],
    rightseq: collections.abc.Iterable[U],
) -> collections.abc.Iterator[tuple[T, U]]: ...
@typing.overload
def join[T, U, L](
    leftkey: typing.Hashable,
    leftseq: collections.abc.Iterable[T],
    rightkey: typing.Callable[[U], typing.Hashable],
    rightseq: collections.abc.Iterable[U],
    left_default: L,
) -> collections.abc.Iterator[tuple[T | L, U]]: ...
@typing.overload
def join[T, U, R](
    leftkey: typing.Hashable,
    leftseq: collections.abc.Iterable[T],
    rightkey: typing.Callable[[U], typing.Hashable],
    rightseq: collections.abc.Iterable[U],
    *,
    right_default: R,
) -> collections.abc.Iterator[tuple[T, U | R]]: ...
@typing.overload
def join[T, U, L, R](
    leftkey: typing.Hashable,
    leftseq: collections.abc.Iterable[T],
    rightkey: typing.Callable[[U], typing.Hashable],
    rightseq: collections.abc.Iterable[U],
    left_default: L,
    right_default: R,
) -> collections.abc.Iterator[tuple[T | L, U | R]]: ...

# === CALLABLE + HASHABLE (4 overloads) ===
@typing.overload
def join[T, U](
    leftkey: typing.Callable[[T], typing.Hashable],
    leftseq: collections.abc.Iterable[T],
    rightkey: typing.Hashable,
    rightseq: collections.abc.Iterable[U],
) -> collections.abc.Iterator[tuple[T, U]]: ...
@typing.overload
def join[T, U, L](
    leftkey: typing.Callable[[T], typing.Hashable],
    leftseq: collections.abc.Iterable[T],
    rightkey: typing.Hashable,
    rightseq: collections.abc.Iterable[U],
    left_default: L,
) -> collections.abc.Iterator[tuple[T | L, U]]: ...
@typing.overload
def join[T, U, R](
    leftkey: typing.Callable[[T], typing.Hashable],
    leftseq: collections.abc.Iterable[T],
    rightkey: typing.Hashable,
    rightseq: collections.abc.Iterable[U],
    *,
    right_default: R,
) -> collections.abc.Iterator[tuple[T, U | R]]: ...
@typing.overload
def join[T, U, L, R](
    leftkey: typing.Callable[[T], typing.Hashable],
    leftseq: collections.abc.Iterable[T],
    rightkey: typing.Hashable,
    rightseq: collections.abc.Iterable[U],
    left_default: L,
    right_default: R,
) -> collections.abc.Iterator[tuple[T | L, U | R]]: ...

# === HASHABLE + HASHABLE (4 overloads) ===
@typing.overload
def join[T, U](
    leftkey: typing.Hashable,
    leftseq: collections.abc.Iterable[T],
    rightkey: typing.Hashable,
    rightseq: collections.abc.Iterable[U],
) -> collections.abc.Iterator[tuple[T, U]]: ...
@typing.overload
def join[T, U, L](
    leftkey: typing.Hashable,
    leftseq: collections.abc.Iterable[T],
    rightkey: typing.Hashable,
    rightseq: collections.abc.Iterable[U],
    left_default: L,
) -> collections.abc.Iterator[tuple[T | L, U]]: ...
@typing.overload
def join[T, U, R](
    leftkey: typing.Hashable,
    leftseq: collections.abc.Iterable[T],
    rightkey: typing.Hashable,
    rightseq: collections.abc.Iterable[U],
    *,
    right_default: R,
) -> collections.abc.Iterator[tuple[T, U | R]]: ...
@typing.overload
def join[T, U, L, R](
    leftkey: typing.Hashable,
    leftseq: collections.abc.Iterable[T],
    rightkey: typing.Hashable,
    rightseq: collections.abc.Iterable[U],
    left_default: L,
    right_default: R,
) -> collections.abc.Iterator[tuple[T | L, U | R]]: ...

# Implementation signature
@typing.overload
def diff[T](
    *seqs: collections.abc.Iterable[T],
    key: typing.Callable[[T], object] | None = None,
) -> collections.abc.Iterator[tuple[T, ...]]: ...
@typing.overload
def diff[T](
    *seqs: collections.abc.Iterable[T],
    default: T,
    key: typing.Callable[[T], object] | None = None,
) -> collections.abc.Iterator[tuple[T, ...]]: ...
def topk[T](
    k: int,
    seq: collections.abc.Iterable[T],
    key: typing.Callable[[T], SupportsRichComparison] | None = None,
) -> tuple[T, ...]:
    """Find the k largest elements of a sequence

    Operates lazily in ``n*log(k)`` time

    >>> topk(2, [1, 100, 10, 1000])
    (1000, 100)

    Use a key function to change sorted order

    >>> topk(2, ['Alice', 'Bob', 'Charlie', 'Dan'], key=len)
    ('Charlie', 'Alice')

    See also:
        heapq.nlargest
    """
    ...

def peek[T](
    seq: collections.abc.Iterable[T],
) -> tuple[T, collections.abc.Iterator[T]]:
    """Retrieve the next element of a sequence

    Returns the first element and an iterable equivalent to the original
    sequence, still having the element retrieved.

    >>> seq = [0, 1, 2, 3, 4]
    >>> first, seq = peek(seq)
    >>> first
    0
    >>> list(seq)
    [0, 1, 2, 3, 4]
    """
    ...

def peekn[T](
    n: int, seq: collections.abc.Iterable[T]
) -> tuple[tuple[T, ...], collections.abc.Iterator[T]]:
    """Retrieve the next n elements of a sequence

    Returns a tuple of the first n elements and an iterable equivalent
    to the original, still having the elements retrieved.

    >>> seq = [0, 1, 2, 3, 4]
    >>> first_two, seq = peekn(2, seq)
    >>> first_two
    (0, 1)
    >>> list(seq)
    [0, 1, 2, 3, 4]
    """
    ...

def random_sample[T](
    prob: float,
    seq: collections.abc.Iterable[T],
    random_state: int | _Randomable | None = None,
) -> collections.abc.Iterator[T]:
    """Return elements from a sequence with probability of prob

    Returns a lazy iterator of random items from seq.

    ``random_sample`` considers each item independently and without
    replacement. See below how the first time it returned 13 items and the
    next time it returned 6 items.

    >>> seq = list(range(100))
    >>> list(random_sample(0.1, seq)) # doctest: +SKIP
    [6, 9, 19, 35, 45, 50, 58, 62, 68, 72, 78, 86, 95]
    >>> list(random_sample(0.1, seq)) # doctest: +SKIP
    [6, 44, 54, 61, 69, 94]

    Providing an integer seed for ``random_state`` will result in
    deterministic sampling. Given the same seed it will return the same sample
    every time.

    >>> list(random_sample(0.1, seq, random_state=2016))
    [7, 9, 19, 25, 30, 32, 34, 48, 59, 60, 81, 98]
    >>> list(random_sample(0.1, seq, random_state=2016))
    [7, 9, 19, 25, 30, 32, 34, 48, 59, 60, 81, 98]

    ``random_state`` can also be any object with a method ``random`` that
    returns floats between 0.0 and 1.0 (exclusive).

    >>> from random import Random
    >>> randobj = Random(2016)
    >>> list(random_sample(0.1, seq, random_state=randobj))
    [7, 9, 19, 25, 30, 32, 34, 48, 59, 60, 81, 98]
    """
    ...
