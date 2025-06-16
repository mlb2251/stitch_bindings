import glob
import json
import os
import subprocess
from sys import argv
from tempfile import NamedTemporaryFile
import numpy as np
import tqdm
from permacache import permacache


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


cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")


@permacache(
    os.path.join(cache_dir, "smc_experiment/run_all_experiments"),
    shelf_type="individual-file",
)
def run_all_experiments(revision, programs, num_arities, num_particles):
    set_revision(revision)
    # splitting off to ensure that the revision is set before importing stitch
    with NamedTemporaryFile("w", suffix=".json") as programs_file:
        json.dump(programs, programs_file)
        programs_file.close()
        output = subprocess.check_output(
            [
                "python3",
                "smc_experiment_direct.py",
                programs_file.name,
                json.dumps(num_arities),
                json.dumps(num_particles),
            ]
        )
    output = output.decode("utf-8")
    output = json.loads(output)
    return output


def main():
    num_arities = list(range(2, 1 + 6))
    num_particles = [10, 20, 50, 100, 200, 500, 1000, 2000]

    for fname in sorted(glob.glob("../data/cogsci/*.json")):
        with open(fname, "r") as f:
            programs = json.load(f)
        print(fname)
        print(run_all_experiments(argv[1], programs, num_arities, num_particles))


if __name__ == "__main__":
    main()
