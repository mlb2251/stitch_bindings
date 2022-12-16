
PYTHON := python3

all: build install test docs

build:
	${PYTHON} -m pip install maturin --upgrade
	${PYTHON} -m maturin build --release -i ${PYTHON}

install:
	${PYTHON} -m pip install .

test:
	cd tests && ${PYTHON} test.py

docs: kwargs
	cd docs && make html

clean:
	cargo clean

kwargs:
	cd scripts && ${PYTHON} gen_kwargs_listing.py > ../docs/source/generated_kwargs_table.rst

.PHONY: all build install test docs clean