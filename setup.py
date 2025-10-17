""" Build ``cytoolz`` with or without Cython.

By default, CyToolz will be built using Cython if available.
If Cython is not available, then the default C compiler will be used
to compile the distributed *.c files instead.

Pass "--cython" or "--with-cython" as a command line argument to setup.py to
force the project to build using Cython (and fail if Cython is unavailable).

Pass "--no-cython" or "--without-cython" to disable usage of Cython.

For convenience, developmental versions (with 'dev' in the version number)
automatically use Cython unless disabled via a command line argument.

To summarize differently, the rules are as follows (apply first applicable rule):

  1. If `--no-cython` or `--without-cython` are used, then only build from `.*c` files.
  2. If this is a dev version, then cythonize only the files that have changed.
  3. If `--cython` or `--with-cython` are used, then force cythonize all files.
  4. If no arguments are passed, then force cythonize all files if Cython is available,
     else build from `*.c` files.  This is default when installing via pip.

By forcing cythonization of all files (except in dev) if Cython is available,
we avoid the case where the generated `*.c` files are not forward-compatible.

"""
import os
import sys
from setuptools import setup, Extension

try:
    import Cython
    from Cython.Build import cythonize
    has_cython = True
except ImportError:
    has_cython = False

try:
    from setuptools_git_versioning import get_version

    version = get_version(
        {
            'dev_template': '{tag}+{ccount}.g{sha}',
            'dirty_template': '{tag}+{ccount}.g{sha}.dirty',
        }
    )
    is_dev = '+' in str(version)
except ModuleNotFoundError:
    is_dev = True

use_cython = True
strict_cython = is_dev or os.environ.get('CIBUILDWHEEL', '0') != '1'
if '--no-cython' in sys.argv:
    use_cython = False
    sys.argv.remove('--no-cython')
if '--without-cython' in sys.argv:
    use_cython = False
    sys.argv.remove('--without-cython')
if '--cython' in sys.argv:
    strict_cython = True
    sys.argv.remove('--cython')
if '--with-cython' in sys.argv:
    strict_cython = True
    sys.argv.remove('--with-cython')

if use_cython and not has_cython:
    if strict_cython:
        raise RuntimeError('Cython required to build dev version of cytoolz.')
    print('ALERT: Cython not installed.  Building without Cython.')
    use_cython = False

if use_cython:
    suffix = '.pyx'
else:
    suffix = '.c'

ext_modules = []
for modname in ['dicttoolz', 'functoolz', 'itertoolz', 'recipes', 'utils']:
    ext_modules.append(Extension('cytoolz.' + modname.replace('/', '.'),
                                 ['cytoolz/' + modname + suffix]))

if use_cython:
    try:
        from Cython.Compiler.Options import get_directive_defaults
        directive_defaults = get_directive_defaults()
    except ImportError:
        # for Cython < 0.25
        from Cython.Compiler.Options import directive_defaults
    directive_defaults['embedsignature'] = True
    directive_defaults['binding'] = True
    directive_defaults['language_level'] = '3'
    if Cython.__version__ >= '3.1':
        # This is experimental! Use at your own risk (and please let us know of issues)
        directive_defaults['freethreading_compatible'] = True
    # The distributed *.c files may not be forward compatible.
    # If we are cythonizing a non-dev version, then force everything to cythonize.
    ext_modules = cythonize(ext_modules, force=not is_dev)

setup(ext_modules=ext_modules)
