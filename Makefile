

build:
	python3 -m maturin build --release -i python3

install:
	python3 -m pip install .

test:
	cd tests && python3 test.py

clean:
	cargo clean
