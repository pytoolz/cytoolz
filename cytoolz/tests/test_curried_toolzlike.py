import cytoolz
import cytoolz.curried
import toolz
import toolz.curried
import inspect
import types
from dev_skip_test import dev_skip_test


def numargs(f):
    if f._numargs is not None:
        return f._numargs
    spec = inspect.getargspec(f.func)
    return len(spec.args) - len(spec.defaults or ())


@dev_skip_test
def test_toolzcurry_is_function():
    assert isinstance(toolz.curry, type) is False
    assert isinstance(toolz.curry, types.FunctionType) is True
    assert isinstance(toolz.functoolz.Curry, type) is True
    assert isinstance(toolz.functoolz.Curry, types.FunctionType) is False


@dev_skip_test
def test_cytoolz_like_toolz():
    for key, val in toolz.curried.__dict__.items():
        if isinstance(val, toolz.functoolz.Curry):
            if val.func is toolz.curry:  # XXX: Python 3.4 work-around!
                continue
            assert hasattr(cytoolz.curried, key), (
                    'cytoolz.curried.%s does not exist' % key)
            assert isinstance(getattr(cytoolz.curried, key), cytoolz.functoolz.Curry), (
                    'cytoolz.curried.%s should be curried' % key)
            assert getattr(cytoolz.curried, key)._numargs == numargs(val), (
                    'cytoolz.curried.%s has incorrect "numargs" (should be %s)'
                    % (key, numargs(val)))


@dev_skip_test
def test_toolz_like_cytoolz():
    for key, val in cytoolz.curried.__dict__.items():
        if isinstance(val, cytoolz.functoolz.Curry):
            assert hasattr(toolz.curried, key), (
                    'cytoolz.curried.%s should not exist' % key)
            assert isinstance(getattr(toolz.curried, key), toolz.functoolz.Curry), (
                    'cytoolz.curried.%s should not be curried' % key)
