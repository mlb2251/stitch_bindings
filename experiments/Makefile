.PHONY: claim-2 claim-2-3 claim-2-50 claim-2-viz claim-3 claim-3-viz clean claim-1 claim-1-viz clean-1 clean-2 clean-3 claim-4 claim-4-viz clean-4

# CLAIM 1

clean: clean-2 clean-3 clean-4 clean-benchmark
	rm -f out/out.json
	echo "cleaned all outputs"

claim-1: compression_benchmark
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
