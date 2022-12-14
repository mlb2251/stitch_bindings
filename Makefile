

build:
	python3 -m maturin build --release -i python3
	python3 -m pip install .

test:
	python3 tests/test.py

clean:
	cargo clean
