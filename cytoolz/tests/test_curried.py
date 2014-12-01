import cytoolz
import cytoolz.curried
from cytoolz.curried import take, first, second, sorted, merge_with, reduce
from cytoolz.utils import raises
from operator import add


def test_take():
    assert list(take(2)([1, 2, 3])) == [1, 2]


def test_first():
    assert first is cytoolz.itertoolz.first


def test_merge_with():
    assert merge_with(sum)({1: 1}, {1: 2}) == {1: 3}


def test_merge_with_list():
    assert merge_with(sum, [{'a': 1}, {'a': 2}]) == {'a': 3}


def test_sorted():
    assert sorted(key=second)([(1, 2), (2, 1)]) == [(2, 1), (1, 2)]


def test_reduce():
    assert reduce(add)((1, 2, 3)) == 6


def test_module_name():
    assert cytoolz.curried.__name__ == 'cytoolz.curried'


def test_raises_typeerror():
    badmap = cytoolz.curried.map(1)([1, 2])
    assert raises(TypeError, lambda: list(badmap))
