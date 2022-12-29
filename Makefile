
PYTHON := python3
SEEDS := 3

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

publish-test:
	make all
	${PYTHON} -m maturin publish --repository testpypi
	${PYTHON} -m pip uninstall stitch_core
	${PYTHON} -m pip install -i https://test.pypi.org/simple/ stitch-core

claim-1:
	cd experiments && make claim-1

claim-2:
	cd experiments && make claim-2 SEEDS=${SEEDS}

.PHONY: all build install test docs clean claim-1 claim-2