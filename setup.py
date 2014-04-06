from distutils.core import setup
from distutils.extension import Extension
# from Cython.Build import cythonize
from Cython.Distutils import build_ext

ext_modules = [
    Extension("cytoolz.itertoolz.core",
              ["cytoolz/itertoolz/core.pyx"]),
    Extension("cytoolz.functoolz.core",
              ["cytoolz/functoolz/core.pyx"]),
    Extension("cytoolz.dicttoolz.core",
              ["cytoolz/dicttoolz/core.pyx"]),
]

setup(
    name="cytoolz",
    cmdclass={"build_ext": build_ext},
    ext_modules=ext_modules,
    packages=['cytoolz',
              'cytoolz.itertoolz',
              'cytoolz.functoolz',
              'cytoolz.dicttoolz',
              # 'cytoolz.sandbox',
              ],
    package_data={'cytoolz': ['*.pxd', '*/*.pxd']},
)
