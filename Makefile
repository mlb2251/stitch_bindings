linux:
	mkdir -p bindings
	cargo rustc --release -- -C link-arg=-undefined
	mv target/release/libstitch_bindings.so bindings/stitch.so
	echo "added bindings: bindings/stitch.so"

osx:
	mkdir -p bindings
	cargo rustc --release -- -C link-arg=-undefined -C link-arg=dynamic_lookup
	mv target/release/libstitch_bindings.dylib bindings/stitch.so
	echo "added bindings: bindings/stitch.so"