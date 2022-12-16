# Stitch Bindings

This repo provides Python bindings to [stitch](https://github.com/mlb2251/stitch) compatible with `python >= 3.7`

See the [Documentation](https://stitch-bindings.readthedocs.io/en/stable/) for installation instructions and a tutorial.

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

Note on testing bindings: simply executing `python3 tests/test.py` may fail for strange `PYTHONPATH`-related reasons so use `make test` or `cd tests && python3 test.py` instead.

## Publishing the bindings to PyPI

### Automated method
**Increment the version number in `Cargo.toml` (if you don't do this, the new bindings will silently not upload)**, and then publish a new release. This will trigger a GitHub Action to build wheels on many common distributions of Windows / OS X / Linux and many versions of Python for each and upload them all to PyPI.

### Manual method
To upload the bindings to PyPI, ensure that the version number in `Cargo.toml` is incremented (or you'll get an error when uploading), and run:
```bash
maturin publish
```

This will upload any wheels that were built during `make`, along with a more generic `stitch_core-*.*.*.tar.gz` archive from which can be used by any platform that doesn't have a pre-built wheel. This is worse than the automated GitHub Action method above in that the Action will upload wheels for many different Python versions and OS distributions, while the manual method will upload one wheel plus a source distribution that `pip install stitch_core` will have to manually build a wheel from (requiring build dependencies etc) on each target OS, which is generally slower and less convenient.

