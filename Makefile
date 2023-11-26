
PYTHON := python3
SEEDS := 3

ifeq ($(OS),Windows_NT)     # is Windows_NT on XP, 2000, 7, Vista, 10...
    detected_OS := Windows
else
    detected_OS := $(shell uname)  # same as "uname -s"
endif


all: build install test docs

build:
	${PYTHON} -m pip install maturin --upgrade
	${PYTHON} -m pip install sphinx-rtd-theme
	if [ $(detected_OS) = Darwin ]; then\
		rustup target add aarch64-apple-darwin;\
		rustup target add x86_64-apple-darwin;\
		${PYTHON} -m maturin build --release -i ${PYTHON} --target universal2-apple-darwin;\
	else\
		${PYTHON} -m maturin build --release -i ${PYTHON};\
	fi


install:
	${PYTHON} -m pip install .

install-x86-64:
        ARCHFLAGS="-arch x86_64" pip install . --compile --no-cache-dir



test:
	cd tests && ${PYTHON} test.py

docs: kwargs
	cd docs && make html

clean:
	cargo clean
	cd experiments && make clean

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

claim-2-minimal:
	cd experiments && make claim-2-minimal SEEDS=${SEEDS}

claim-2-tiny:
	cd experiments && make claim-2-tiny SEEDS=${SEEDS}


benchmark: all clean claim-1 claim-2
benchmark-minimal: all clean claim-1 claim-2-minimal
benchmark-tiny: all clean claim-1 claim-2-tiny

plots-old:
	rm -rf experiments/plots_old
	cp -r experiments/plots experiments/plots_old

eta-long:
	cd experiments && make eta-long

.PHONY: all build build_osx install test docs clean claim-1 claim-2 benchmark plots-old eta-long