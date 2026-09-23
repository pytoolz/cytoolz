import typing

def raises(err: type[Exception], lamda: typing.Callable[[], None]) -> bool: ...

no_default = "__no__default__"
