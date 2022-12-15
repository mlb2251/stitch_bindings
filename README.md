# Stitch Bindings

This repo provides Python bindings to [stitch](https://github.com/mlb2251/stitch) compatible with `python >= 3.7`

## Installing the bindings
```bash
pip install stitch-core
```

Opening a new `python` session and running `import stitch_core` should succeed.

## Using the bindings

**Dec 15 Note: Tutorial coming shortly**

For more usage examples, see `tests/test.py` in this repo.

## Using a specific version of `stitch`
To build the bindings for a specific commit, modify the line beginning with `stitch_core =` in `Cargo.toml` to have the SHA of the desired commit, for example:


## Locally building the bindings
Adjust the `rev` value in `Cargo.toml` to the desired commit SHA:
```toml
stitch_core = { git = "https://github.com/mlb2251/stitch", rev = "058890ecc3c3137c5105d673979304edfb0ab333"}
```

To build, install, and test the bindings run:
```bash
make
```
which install the bindings for `python3` by default. To use a specific interpreter pass it in like so:
```bash
make PYTHON=python3.10
```

Note on testing bindings: simply executing `python3 tests/test.py` may fail for strange PYTHONPATH-related reasons so use `make test` or `cd tests && python3 test.py` instead.

## Publishing the bindings to PyPI

### Automated method
Whenever a tag is pushed to the repo, a GitHub Action will build wheels on many common distributions of Windows / OS X / Linux and upload them all to PyPI. This is better than the manual method below in that it uploads wheels for many versions, while in the manual method there are fewer precompiled wheels so `pip` must build the wheels during `pip install stitch_core` on most distributions.

### Manual method
To upload the bindings to PyPI, ensure that the version number in `Cargo.toml` is incremented (or you'll get an error when uploading), and run:
```bash
maturin publish
```

This will upload any wheels that were built during `make`, along with a more generic `stitch_core-*.*.*.tar.gz` archive from which can be used by any platform that doesn't have a pre-built wheel.

