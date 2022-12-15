# Stitch Bindings

This repo provides Python bindings to [stitch](https://github.com/mlb2251/stitch).

## Installing the bindings
```bash
pip install stitch-core
```

Opening a new `python` session and running `import stitch_core` should succeed.

## Using the bindings

For more usage examples, see `tests/test.py` in this repo.

## Using a specific version of `stitch`
To build the bindings for a specific commit, modify the line beginning with `stitch_core =` in `Cargo.toml` to have the SHA of the desired commit, for example:
```toml
stitch_core = { git = "https://github.com/mlb2251/stitch", rev = "058890ecc3c3137c5105d673979304edfb0ab333"}
```
## Building the bindings
```bash
make build
make install
make test
```
## Publishing the bindings to PYPI
