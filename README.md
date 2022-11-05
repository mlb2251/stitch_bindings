# Stitch Bindings

Run `make osx` or `make linux` to build [stitch](https://github.com/mlb2251/stitch) bindings and add them to `bindings/`. Please open a GitHub issue if you have any problems with this.

Test the bindings with `cd bindings && python3` and then `import stitch`.

As a simple example run the Python code `json.loads(stitch.compression(["(a a a)", "(b b b)"], iterations=1, max_arity=2))` and it should find the `(#0 #0 #0)` abstraction.
- Note that currently it outputs a large python dictionary similar to the usual `out/out.json` output of `stitch`, and currently also produces a lot of debug output.
- There are a lot more keyword arguments available (full list in `src/lib.rs`). Basically everything that you would find in the original `stitch` command `cargo run --release --bin=compress -- --help` run in the [stitch](https://github.com/mlb2251/stitch) repo is included.

You can add `/path/to/stitch_bindings/bindings/` to your python path (`export PYTHONPATH="$PYTHONPATH:path/to/stitch_bindings/bindings/"` in your `.bash_profile` on linux and `.zshrc` on OS X).