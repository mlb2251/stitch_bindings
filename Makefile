
PYTHON := python3

all: build install test

build:
	${PYTHON} -m pip install maturin --upgrade
	${PYTHON} -m maturin build --release -i ${PYTHON}

install:
	${PYTHON} -m pip install .

test:
	cd tests && ${PYTHON} test.py

clean:
	cargo clean
