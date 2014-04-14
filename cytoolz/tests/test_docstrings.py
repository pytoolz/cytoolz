import difflib
import cytoolz
import toolz

from cytoolz.utils import raises


# `cytoolz` functions for which "# doctest: +SKIP" were added.
# This may have been done because the error message may not exactly match.
# The skipped tests should be added below with results and explanations.
skipped_doctests = ['get_in']


def convertdoc(doc):
    """ Convert docstring from `toolz` to `cytoolz`."""
    if hasattr(doc, '__doc__'):
        doc = doc.__doc__
    doc = doc.replace('toolz', 'cytoolz')
    doc = doc.replace('dictcytoolz', 'dicttoolz')
    doc = doc.replace('funccytoolz', 'functoolz')
    doc = doc.replace('itercytoolz', 'itertoolz')
    doc = doc.replace('cytoolz.readthedocs', 'toolz.readthedocs')
    return doc


def test_docstrings_uptodate():
    differ = difflib.Differ()
    for key, toolz_func in sorted(toolz.__dict__.items()):
        # only consider items created in `toolz`
        toolz_mod = getattr(toolz_func, '__module__', '') or ''
        if toolz_mod.startswith('toolz'):
            # full API coverage should be tested elsewhere
            if key not in cytoolz.__dict__:
                print 'Warning: cytoolz.%s not defined' % key
                continue

            # only test functions created in `cytoolz`
            cytoolz_func = cytoolz.__dict__[key]
            cytoolz_mod = getattr(cytoolz_func, '__module__', '') or ''
            if not cytoolz_mod.startswith('cytoolz'):
                print ('Warning: cytoolz.%s exists, but is defined outside '
                       'the package' % key)
                continue

            # only test functions that have docstrings defined in `toolz`
            if not getattr(toolz_func, '__doc__', ''):
                print 'Warning: toolz.%s has no docstring' % key
                continue

            # only check if the new doctstring *contains* the expected docstring
            toolz_doc = convertdoc(toolz_func)
            cytoolz_doc = cytoolz_func.__doc__
            if toolz_doc not in cytoolz_doc:
                diff = list(differ.compare(toolz_doc.splitlines(),
                                           cytoolz_doc.splitlines()))
                fulldiff = list(diff)
                # remove additional lines at the beginning
                while diff and diff[0].startswith('+'):
                    diff.pop(0)
                # remove additional lines at the end
                while diff and diff[-1].startswith('+'):
                    diff.pop()

                def checkbad(line):
                    return (line.startswith('+') and
                            not ('# doctest: +SKIP' in line and
                                 key in skipped_doctests))

                if any(map(checkbad, diff)):
                    assert False, 'Error: cytoolz.%s has a bad docstring:\n%s\n' % (
                        key, '\n'.join(fulldiff))


def test_get_in_doctest():
    # Original doctest:
    #     >>> get_in(['y'], {}, no_default=True)
    #     Traceback (most recent call last):
    #         ...
    #     KeyError: 'y'

    # cytoolz result:
    #     KeyError:

    raises(KeyError, lambda: cytoolz.get_in(['y'], {}, no_default=True))
