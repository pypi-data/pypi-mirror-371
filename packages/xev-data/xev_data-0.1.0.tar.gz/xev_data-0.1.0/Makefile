.PHONY: all tests
all = tests
VERSION=0.1.0

version: clean
	echo "__version__ = '${VERSION}'" > __version__.py
	echo "__version__ = '${VERSION}'" > src/xdata/__version__.py
	sed --in-place "s/version = .*/version = \"${VERSION}\"/g" pyproject.toml

DIST=dist/xev_data-${VERSION}.tar.gz

$(DIST): clean
	- git add src
	- git commit
	python3 -m build

install: version $(DIST)
	python3 -m pip install $(DIST)

test_hello: install
	python3 tests/test_hello.py

test_database: install
	python3 tests/test_database.py

test_import: install
	python3 tests/test_import.py

test_merge: install
	python3 tests/test_merge.py

test_registry: install
	python3 tests/test_registry.py

tests: install test_import test_database test_merge

testpypi: tests
	python3 -m twine upload --repository testpypi $(DIST)

pypi: testpypi
	python3 -m twine upload $(DIST)

clean:
	rm -rf src/xdata.egg
	rm -rf build
	rm -rf dist
	rm -rf HelloWorld.txt
	rm -rf test_alias.hdf5
	rm -rf test_database.hdf5
	rm -rf test_shard*.hdf5
	rm -rf test_merge.hdf5
	rm -rf test_merge_origin.hdf5
	rm -rf test_merge_head.hdf5
	rm -rf test*.hdf5
	rm -rf src/*.egg*
