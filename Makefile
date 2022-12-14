

build:
	maturin build --release -i python3
	python3 -m pip install .

test:
	python3 tests/test.py

linux:
	mkdir -p bindings
	cargo rustc --release -- -C link-arg=-undefined
	mv target/release/libstitch_bindings.so bindings/stitch.so
	echo "added bindings: bindings/stitch.so"

clean:
	cargo clean