.PHONY: claim-2 clean claim-1 clean-plots clean-benchmark

# CLAIM 1

clean: clean-benchmark clean-plots
	rm -f out/out.json
	echo "cleaned all outputs"

clean-plots:
	rm plots/*


claim-1: compression_benchmark clean-plots
	python3 run.py claim-1 compression_benchmark/benches

compression_benchmark:
	git clone -b popl23_camera_ready https://github.com/mlb2251/compression_benchmark.git compression_benchmark

clean-benchmark:
	rm -rf compression_benchmark

dreamcoder: compression_benchmark clean-dreamcoder
	./bench_dreamcoder_all.sh

clean-dreamcoder:
	rm -rf compression_benchmark/benches/*/out/dc

# CLAIM 2

SEEDS := 3

claim-2:
	python3 run.py claim-2 ${SEEDS}
