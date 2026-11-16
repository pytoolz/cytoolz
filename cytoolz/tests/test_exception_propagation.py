from cytoolz import get, interleave, pluck


class LookupFails:
    def __init__(self, exc):
        self.exc = exc

    def __getitem__(self, key):
        raise self.exc


def failing_iter(exc):
    yield 1
    raise exc


def test_original_exceptions_propagate():
    exc = ValueError('bad record')
    obj = LookupFails(exc)
    for func in [lambda: list(interleave([failing_iter(exc), [2]])),
                 lambda: get('x', obj),
                 lambda: get('x', obj, default=0),
                 lambda: get(['x'], obj, default=0),
                 lambda: list(pluck('x', [obj], default=0)),
                 lambda: list(pluck(['x'], [obj], default=0))]:
        try:
            func()
        except ValueError as err:
            assert err is exc
        else:
            raise AssertionError('ValueError was not raised')
