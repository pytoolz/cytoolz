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
from distutils.core import setup
from distutils.extension import Extension

info = {}
filename = os.path.join('cytoolz', '_version.py')
exec(compile(open(filename, "rb").read(), filename, 'exec'), info)
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
    ext_modules.append(Extension('cytoolz.' + modname,
                                 ['cytoolz/' + modname + suffix]))

if use_cython:
    ext_modules = cythonize(ext_modules)


if __name__ == '__main__':
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
        packages=['cytoolz'],
        package_data={'cytoolz': ['*.pxd']},
        # include_package_data = True,
        keywords=('functional utility itertools functools iterator generator '
                  'curry memoize lazy streaming bigdata cython toolz cytoolz'),
        classifiers = [
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'Intended Audience :: Education',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: BSD License',
            'Operating System :: OS Independent',
            'Programming Language :: Cython',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Topic :: Scientific/Engineering',
            'Topic :: Scientific/Engineering :: Information Analysis',
            'Topic :: Software Development',
            'Topic :: Software Development :: Libraries',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Utilities',
        ],
        # zip_safe=False
    )
