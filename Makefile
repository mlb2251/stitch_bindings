

build:
	python3.8 -m maturin build --release -i python3.8
	python3.8 -m pip install .

test:
	cd tests && python3.8 test.py

clean:
	cargo clean
