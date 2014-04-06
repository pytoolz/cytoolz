from cytoolz.utils import testmod

import cytoolz
import cytoolz.dicttoolz
import cytoolz.functoolz
import cytoolz.itertoolz
import cytoolz.dicttoolz.core
import cytoolz.functoolz.core
import cytoolz.itertoolz.core


# This currently doesn't work.  Use `cydoctest.py` instead.
def test_doctest():
    testmod(cytoolz)
    testmod(cytoolz.dicttoolz)
    testmod(cytoolz.functoolz)
    testmod(cytoolz.itertoolz)
    testmod(cytoolz.dicttoolz.core)
    testmod(cytoolz.functoolz.core)
    testmod(cytoolz.itertoolz.core)
