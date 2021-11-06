SHELL= /bin/bash
PYTHON ?= python

inplace:
	$(PYTHON) setup.py build_ext --inplace --cython

test: inplace
	pytest -s --doctest-modules cytoolz/
	echo 'cimport cytoolz ; from cytoolz.functoolz cimport memoize' > try_cimport_cytoolz.pyx
	cythonize -i try_cimport_cytoolz.pyx
	python -c 'import try_cimport_cytoolz'
	rm try_cimport_cytoolz.*

clean:
	rm -f cytoolz/*.c cytoolz/*.so cytoolz/*/*.c cytoolz/*/*.so
	rm -rf build/ cytoolz/__pycache__/ cytoolz/*/__pycache__/

curried:
	sed -e 's/toolz/cytoolz/g' -e 's/itercytoolz/itertoolz/' \
		-e 's/dictcytoolz/dicttoolz/g' -e 's/funccytoolz/functoolz/g' \
		../toolz/toolz/curried/__init__.py > cytoolz/curried/__init__.py

copytests:
	for f in ../toolz/toolz/tests/test*py; \
	do \
		if [[ $$f == *test_utils* ]]; then continue ; fi;  \
		if [[ $$f == *test_curried_doctests* ]]; then continue ; fi;  \
		if [[ $$f == *test_tlz* ]]; then continue ; fi;  \
		newf=`echo $$f | sed 's/...toolz.toolz/cytoolz/g'`; \
		sed -e 's/toolz/cytoolz/g' -e 's/itercytoolz/itertoolz/' \
			-e 's/dictcytoolz/dicttoolz/g' -e 's/funccytoolz/functoolz/g' \
			$$f > $$newf; \
		echo $$f $$newf; \
	done
