""" Build ``cytoolz`` with or without Cython.

Deployed versions of CyToolz do not rely on Cython by default even if the
user has Cython installed.  A C compiler is used to compile the distributed
*.c files instead.

Pass "--cython" or "--with-cython" as a command line argument to setup.py
to build the project using Cython.

Pass "--no-cython" or "--without-cython" to disable usage of Cython.

For convenience, developmental versions (with 'dev' in the version number)
automatically use Cython unless disabled via a command line argument.

"""
import os.path
import sys
from setuptools import setup, Extension

info = {}
filename = os.path.join('cytoolz', '_version.py')
exec(compile(open(filename, "rb").read().replace(b'\r\n', b'\n'),
             filename, 'exec'), info)
VERSION = info['__version__']

try:
    from Cython.Build import cythonize
    has_cython = True
except ImportError:
    has_cython = False

is_dev = 'dev' in VERSION
use_cython = is_dev or '--cython' in sys.argv or '--with-cython' in sys.argv
if '--no-cython' in sys.argv:
    use_cython = False
    sys.argv.remove('--no-cython')
if '--without-cython' in sys.argv:
    use_cython = False
    sys.argv.remove('--without-cython')
if '--cython' in sys.argv:
    sys.argv.remove('--cython')
if '--with-cython' in sys.argv:
    sys.argv.remove('--with-cython')

if use_cython and not has_cython:
    if is_dev:
        raise RuntimeError('Cython required to build dev version of cytoolz.')
    print('WARNING: Cython not installed.  Building without Cython.')
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
    ext_modules = cythonize(ext_modules)

setup(
    name='cytoolz',
    version=VERSION,
    description=('Cython implementation of Toolz: '
                    'High performance functional utilities'),
    ext_modules=ext_modules,
    long_description=(open('README.rst').read()
                        if os.path.exists('README.rst')
                        else ''),
    url='https://github.com/pytoolz/cytoolz',
    author='https://raw.github.com/pytoolz/cytoolz/master/AUTHORS.md',
    author_email='erik.n.welch@gmail.com',
    maintainer='Erik Welch',
    maintainer_email='erik.n.welch@gmail.com',
    license = 'BSD',
    packages=['cytoolz', 'cytoolz.curried'],
    package_data={'cytoolz': ['*.pyx', '*.pxd', 'curried/*.pyx', 'tests/*.py']},
    # include_package_data = True,
    keywords=('functional utility itertools functools iterator generator '
                'curry memoize lazy streaming bigdata cython toolz cytoolz'),
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Cython',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
    install_requires=['toolz >= 0.8.0'],
    zip_safe=False,
)
