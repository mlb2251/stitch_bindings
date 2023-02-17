
PYTHON := python3
SEEDS := 3

all: build install test docs

build:
	${PYTHON} -m pip install maturin --upgrade
	${PYTHON} -m maturin build --release -i ${PYTHON} --universal2

install:
	${PYTHON} -m pip install . && ${PYTHON} -m pip install sphinx-rtd-theme

install-x86-64:
        ARCHFLAGS="-arch x86_64" pip install . --compile --no-cache-dir

osx-setup:
	rustup target add aarch64-apple-darwin
	rustup target add x86_64-apple-darwin

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

eta-long:
	cd experiments && make eta-long

.PHONY: all build install test docs clean claim-1 claim-2
