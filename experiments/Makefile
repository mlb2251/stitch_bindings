.PHONY: claim-2 clean claim-1 clean-plots clean-benchmark

PYTHON := python3

# CLAIM 1

clean: clean-benchmark clean-dreamcoder clean-plots
	rm -f out/out.json
	echo "cleaned all outputs"

clean-plots:
	rm -f plots/*


claim-1: run-install compression_benchmark clean-plots
	${PYTHON} run.py claim-1 compression_benchmark/benches

run-install:
	${PYTHON} -m pip install -r run_requirements.txt

compression_benchmark:
	git clone -b popl23_camera_ready https://github.com/mlb2251/compression_benchmark.git compression_benchmark

clean-benchmark:
	rm -rf compression_benchmark

eta-long: dreamcoder compression_benchmark
	${PYTHON} eta_long.py

dreamcoder:
	git clone https://github.com/CatherineWong/laps_dreamcoder.git -b laps --depth 1 dreamcoder

dreamcoder-install:
	cd dreamcoder && make setup-ocaml && make
	${PYTHON} -m pip install -r dreamcoder_requirements.txt

clean-dreamcoder:
	rm -rf dreamcoder

bench-dreamcoder: compression_benchmark clean-dreamcoder
	./bench_dreamcoder_all.sh

clean-bench-dreamcoder:
	rm -rf compression_benchmark/benches/*/out/dc

SEEDS := 3

claim-2: run-install
	${PYTHON} run.py claim-2 ${SEEDS}
