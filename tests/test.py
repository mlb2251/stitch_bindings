import json
import stitch

# define a list of programs as a list of strings - see the stitch documentation for supported program formats
programs = ["(a a a)", "(b b b)"]

# define the arguments to stitch - these are identical to the arguments to `cargo run --release --bin=compress`
args = "--max-arity=2 --iterations=1 --silent"

# stitch.compression() will return a json-parseable string with contents identical to out/out.json that the `--bin=compress`
# usually produces. In this case, we'd expect it to find the `(#0 #0 #0)` abstraction
out_json = stitch.compress(programs, 3, 2, silent=False, cost_app="300")
print(stitch.compress.__doc__)
print(out_json['rewritten'])
print(out_json['abstractions'][0])


