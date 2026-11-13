import pytest

from cytoolz import join


@pytest.mark.parametrize('rightkey', [lambda row: row[0], 0, [0]])
@pytest.mark.parametrize('defaults', [
    {},
    {'left_default': None},
    {'right_default': None},
    {'left_default': None, 'right_default': None},
])
def test_join_rejects_unhashable_right_keys(rightkey, defaults):
    with pytest.raises(TypeError):
        list(join(
            lambda row: row[0], [(1,)],
            rightkey, [([1],)],
            **defaults
        ))


@pytest.mark.parametrize('defaults', [{}, {'left_default': None}])
def test_join_propagates_key_hash_errors(defaults):
    class BadKey:
        def __hash__(self):
            raise RuntimeError('hash failed')

    with pytest.raises(RuntimeError, match='hash failed'):
        list(join(
            lambda value: value, [1],
            lambda value: value, [BadKey()],
            **defaults
        ))


@pytest.mark.parametrize('defaults', [
    {},
    {'left_default': None},
    {'right_default': None},
    {'left_default': None, 'right_default': None},
])
def test_join_propagates_key_equality_errors(defaults):
    class BadKey:
        def __hash__(self):
            return 0

        def __eq__(self, other):
            raise RuntimeError('comparison failed')

    with pytest.raises(RuntimeError, match='comparison failed'):
        list(join(
            lambda value: value, [BadKey()],
            lambda value: value, [BadKey()],
            **defaults
        ))
