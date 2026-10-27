# Builtins - re-export to make them available in toolz namespace
from builtins import filter as filter, map as map, sorted as sorted
from functools import partial as partial, reduce as reduce

# Re-export all public APIs from submodules
# Submodules
from . import curried as curried

# Specific functions
from .dicttoolz import (
    assoc as assoc,
    assoc_in as assoc_in,
    dissoc as dissoc,
    get_in as get_in,
    itemfilter as itemfilter,
    itemmap as itemmap,
    keyfilter as keyfilter,
    keymap as keymap,
    merge as merge,
    merge_with as merge_with,
    update_in as update_in,
    valfilter as valfilter,
    valmap as valmap,
)
from .functoolz import (
    apply as apply,
    complement as complement,
    compose as compose,
    compose_left as compose_left,
    curry as curry,
    do as do,
    excepts as excepts,
    flip as flip,
    identity as identity,
    juxt as juxt,
    memoize as memoize,
    pipe as pipe,
    thread_first as thread_first,
    thread_last as thread_last,
)
from .itertoolz import (
    accumulate as accumulate,
    concat as concat,
    concatv as concatv,
    cons as cons,
    count as count,
    diff as diff,
    drop as drop,
    first as first,
    frequencies as frequencies,
    get as get,
    groupby as groupby,
    interleave as interleave,
    interpose as interpose,
    isdistinct as isdistinct,
    isiterable as isiterable,
    iterate as iterate,
    join as join,
    last as last,
    mapcat as mapcat,
    merge_sorted as merge_sorted,
    nth as nth,
    partition as partition,
    partition_all as partition_all,
    peek as peek,
    peekn as peekn,
    pluck as pluck,
    random_sample as random_sample,
    reduceby as reduceby,
    remove as remove,
    second as second,
    sliding_window as sliding_window,
    tail as tail,
    take as take,
    take_nth as take_nth,
    topk as topk,
    unique as unique,
)
from .recipes import countby as countby, partitionby as partitionby

# Aliases
comp = compose

# Version attribute (available via __getattr__ at runtime)
__toolz_version__: str

__version__: str
