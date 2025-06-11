import json
from sys import argv

import numpy as np
import tqdm

from run import run_compression


num_seeds = 10
num_iterations = 3


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


def run_experiment(programs, num_arities, num_particles):
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
    print(
        json.dumps(
            run_experiment(
                json.loads(argv[1]),
                json.loads(argv[2]),
                json.loads(argv[3]),
            )
        )
    )

if __name__ == "__main__":
    main()