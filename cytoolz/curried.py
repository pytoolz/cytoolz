"""
Alternate namespece for cytoolz such that all functions are curried

Currying provides implicit partial evaluation of all functions

Example:

    Get usually requires two arguments, an index and a collection
    >>> from cytoolz.curried import get
    >>> get(0, ('a', 'b'))
    'a'

    When we use it in higher order functions we often want to pass a partially
    evaluated form
    >>> data = [(1, 2), (11, 22), (111, 222)]
    >>> list(map(lambda seq: get(0, seq), data))
    [1, 11, 111]

    The curried version allows simple expression of partial evaluation
    >>> list(map(get(0), data))
    [1, 11, 111]

See Also:
    cytoolz.functoolz.curry
"""

import cytoolz
from cytoolz import *


# Here is the recipe used to create the list below
# (and "cytoolz/tests/test_curried_toolzlike.py" verifies the list is correct):
#
# import toolz
# import toolz.curried
#
# for key, val in sorted(toolz.curried.__dict__.items()):
#     if isinstance(val, toolz.functoolz.Curry):
#         print '%s = cytoolz.curry(%s, numargs=%s)' % (key, key, val._numargs)

accumulate = cytoolz.curry(accumulate, numargs=2)
assoc = cytoolz.curry(assoc, numargs=3)
cons = cytoolz.curry(cons, numargs=2)
countby = cytoolz.curry(countby, numargs=2)
do = cytoolz.curry(do, numargs=2)
drop = cytoolz.curry(drop, numargs=2)
filter = cytoolz.curry(filter, numargs=2)
get = cytoolz.curry(get, numargs=2)
get_in = cytoolz.curry(get_in, numargs=2)
groupby = cytoolz.curry(groupby, numargs=2)
interleave = cytoolz.curry(interleave, numargs=1)
interpose = cytoolz.curry(interpose, numargs=2)
iterate = cytoolz.curry(iterate, numargs=2)
join = cytoolz.curry(join, numargs=4)
keyfilter = cytoolz.curry(keyfilter, numargs=2)
keymap = cytoolz.curry(keymap, numargs=2)
map = cytoolz.curry(map, numargs=2)
mapcat = cytoolz.curry(mapcat, numargs=2)
memoize = cytoolz.curry(memoize, numargs=1)
merge_sorted = cytoolz.curry(merge_sorted, numargs=1)
merge_with = cytoolz.curry(merge_with, numargs=2)
nth = cytoolz.curry(nth, numargs=2)
partition = cytoolz.curry(partition, numargs=2)
partition_all = cytoolz.curry(partition_all, numargs=2)
partitionby = cytoolz.curry(partitionby, numargs=2)
pluck = cytoolz.curry(pluck, numargs=2)
reduce = cytoolz.curry(reduce, numargs=2)
reduceby = cytoolz.curry(reduceby, numargs=3)
remove = cytoolz.curry(remove, numargs=2)
sliding_window = cytoolz.curry(sliding_window, numargs=2)
sorted = cytoolz.curry(sorted, numargs=1)
take = cytoolz.curry(take, numargs=2)
take_nth = cytoolz.curry(take_nth, numargs=2)
unique = cytoolz.curry(unique, numargs=1)
update_in = cytoolz.curry(update_in, numargs=3)
valfilter = cytoolz.curry(valfilter, numargs=2)
valmap = cytoolz.curry(valmap, numargs=2)
