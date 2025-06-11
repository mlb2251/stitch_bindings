import glob
import json
import os
import subprocess
import numpy as np
import tqdm
from permacache import permacache

from run import run_compression

num_seeds = 10
num_iterations = 3


def set_revision(rev):
    # look at ../Cargo.toml and set revision stitch_core = { git = "https://github.com/mlb2251/stitch", rev = "3819a7d" }
    with open("../Cargo.toml", "r") as f:
        text = f.read()
    import re

    text = re.sub(
        r'stitch_core\s*=\s*\{[^}]*rev\s*=\s*"[^"]*"\s*}',
        'stitch_core = { git = "https://github.com/mlb2251/stitch", rev = "%s" }' % rev,
        text,
    )
    with open("../Cargo.toml", "w") as f:
        f.write(text)
    subprocess.check_call(["make", "all"], cwd="..")


def multiple_evaluations(programs, compression_kwargs, all_args):
    argses = []
    for seed in range(num_seeds):
        args = (
            seed,
            programs,
            dict(compression_kwargs, seed=seed, iterations=num_iterations),
        )
        all_args.append(args)
        argses.append(len(all_args) - 1)
    return argses

cache_dir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "cache"
)

@permacache(
    os.path.join(cache_dir, "smc_experiment/run_all_experiments"),
    shelf_type="individual-file",
)
def run_all_experiments(revision, programs, num_arities, num_particles):
    set_revision(revision)
    all_args = []
    by_arity = {
        arity: multiple_evaluations(programs, dict(max_arity=arity), all_args)
        for arity in num_arities
    }
    by_particles = {
        particles: multiple_evaluations(
            programs, dict(smc=True, smc_particles=particles), all_args
        )
        for particles in num_particles
    }
    all_results = [None] * len(all_args)
    for i in tqdm.tqdm(np.random.RandomState(0).permutation(len(all_args))):
        all_results[i] = run_compression(*all_args[i])

    return {
        "by_arity": {k: [all_results[i] for i in v] for k, v in by_arity.items()},
        "by_particles": {
            k: [all_results[i] for i in v] for k, v in by_particles.items()
        },
    }


def main():
    num_arities = range(2, 1 + 6)
    num_particles = [10, 20, 50, 100, 200, 500, 1000, 2000]

    for fname in sorted(glob.glob("../data/cogsci/*.json")):
        with open(fname, "r") as f:
            programs = json.load(f)
        print(run_all_experiments("3819a7d", programs, num_arities, num_particles))


if __name__ == "__main__":
    main()
