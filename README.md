# Stitch Bindings

**Dec 6: Bindings are being renovated for useability and will be available within a week!**

This repo provides Python bindings to [stitch](https://github.com/mlb2251/stitch). At some point, stitch bindings will be published to pip, but in the mean time the instructions below allow for building the latest version of stitch from the GitHub repo (or any desired branch/commit). The goal for the stitch interface is to be nearly identical to running stitch in the commandline with `cargo run --release --bin=compress`, by exposing the function `stitch.compression(programs,args)` where `programs` is a list of programs (as strings) and `args` is a string containing commandline arguments, like `"--max-arity=3 --iterations=3"`.


## Using a specific version of `stitch`

By default, the following instructions will build the latest version of stitch on the `main` branch of the [stitch repo](https://github.com/mlb2251/stitch). To build the bindings for a specific commit, replace the following line in `Cargo.toml`:
```toml
stitch_core = { git = "https://github.com/mlb2251/stitch", branch = "main"}
```
with the following (replacing the SHA with the desired commit SHA):

```toml
stitch_core = { git = "https://github.com/mlb2251/stitch", rev = "058890ecc3c3137c5105d673979304edfb0ab333"}
```

## Building the bindings
```bash
PYO3_PYTHON=python3.8 make osx
```

`make linux` is also supported. Adjust the `PYO3_PYTHON` variable to be whichever python interpreter you would like to compile for. It will default to `python3` if you don't set it.

To use the bindings, open a new python interpreter and run the following:

```python
import sys, os, json

# First add the bindings to your PYTHONPATH - you can do this by adding `export PYTHONPATH="$PYTHONPATH:path/to/stitch_bindings/bindings/"`
# to your `~/.bashrc`, `~/.zshrc`, and/or `~/.bash_profile`, or just for the current session through sys.path.append() as below:
sys.path.append(os.getcwd() + '/bindings')

# Now the following import should succeed
import stitch

# define a list of programs as a list of strings - see the stitch documentation for supported program formats
programs = ["(a a a)", "(b b b)"]

# define the arguments to stitch - these are identical to the arguments to `cargo run --release --bin=compress`
args = "--max-arity=2 --iterations=1 --silent"

# stitch.compression() will return a json-parseable string with contents identical to out/out.json that the `--bin=compress`
# usually produces. In this case, we'd expect it to find the `(#0 #0 #0)` abstraction
out_json = json.loads(stitch.compression(programs, args))
print(out_json['rewritten'])
print(out_json['abstractions'][0])
```

## Troubleshooting
If `import stitch` fails, create an issue on GitHub including your python version and OS.
Sometimes changing to a different `PYO3_PYTHON` can be helpful as well.

## Adding to PYTHONPATH
You can add the bindings to your PYTHONPATH by adding `export PYTHONPATH="$PYTHONPATH:path/to/stitch_bindings/bindings/"`
to your `~/.bashrc`, `~/.zshrc`, and/or `~/.bash_profile`.
