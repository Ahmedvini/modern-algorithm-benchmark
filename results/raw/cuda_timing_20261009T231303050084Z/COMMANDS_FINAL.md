# Executed validation commands

Commands below are copied from retained subprocess JSON records. Each record contains full stdout/stderr, timestamps or durations, working directory and actual exit status. Shell quoting is for reproduction only. Private CLI credential files are excluded from all bundles.

Initial inspection (before recorder): `pwd`; `git status --short` returned128 (no .git); `colab sessions` returned0 with no active sessions; old configured session status returned0 and pruned an expired session. Those were availability diagnostics, not passing GPU checks.

## Local download_evidence

Exit: `0`; record `results/raw/cuda_timing_20261009T231303050084Z/commands/download_evidence.json`.

```bash
timeout --signal=TERM 180 colab --config build/cuda_timing_20261009T231303050084Z/private_cli/sessions.json download /content/cuda_timing_20261009T231303050084Z_evidence.tar.gz results/raw/cuda_timing_20261009T231303050084Z/colab_gpu_timing_evidence.tar.gz --session mab-t4-20261009T231303050084Z
```

## Local extract_source

Exit: `0`; record `results/raw/cuda_timing_20261009T231303050084Z/commands/extract_source.json`.

```bash
timeout --signal=TERM 150 colab --config build/cuda_timing_20261009T231303050084Z/private_cli/sessions.json exec --session mab-t4-20261009T231303050084Z --file results/raw/cuda_timing_20261009T231303050084Z/extract_remote.py --timeout 120
```

## Local git_status_final

Exit: `128`; record `results/raw/cuda_timing_20261009T231303050084Z/commands/git_status_final.json`.

```bash
git status --short
```

## Local host_cuda_analysis

Exit: `0`; record `results/raw/cuda_timing_20261009T231303050084Z/commands/host_cuda_analysis.json`.

```bash
/usr/bin/python3 tests/test_cuda_benchmark.py
```

## Local host_cuda_analysis_final

Exit: `0`; record `results/raw/cuda_timing_20261009T231303050084Z/commands/host_cuda_analysis_final.json`.

```bash
python3 tests/test_cuda_benchmark.py
```

## Local independent_verification

Exit: `0`; record `results/raw/cuda_timing_20261009T231303050084Z/commands/independent_verification.json`.

```bash
python3 results/raw/cuda_timing_20261009T231303050084Z/verify_results.py
```

## Local inspect_replacement

Exit: `0`; record `results/raw/cuda_timing_20261009T231303050084Z/commands/inspect_replacement.json`.

```bash
timeout --signal=TERM 120 colab --config build/cuda_timing_20261009T231303050084Z/private_cli/sessions.json exec --session mab-t4-20261009T231303050084Z --file results/raw/cuda_timing_20261009T231303050084Z/inspect_remote.py --timeout 90
```

## Local package_evidence

Exit: `0`; record `results/raw/cuda_timing_20261009T231303050084Z/commands/package_evidence.json`.

```bash
timeout --signal=TERM 180 colab --config build/cuda_timing_20261009T231303050084Z/private_cli/sessions.json exec --session mab-t4-20261009T231303050084Z --file results/raw/cuda_timing_20261009T231303050084Z/package_remote.py --timeout 150
```

## Local release_build

Exit: `0`; record `results/raw/cuda_timing_20261009T231303050084Z/commands/release_build.json`.

```bash
cmake --build build/cuda_timing_20261009T231303050084Z/cpu-release --parallel 2
```

## Local release_configure

Exit: `0`; record `results/raw/cuda_timing_20261009T231303050084Z/commands/release_configure.json`.

```bash
cmake -S . -B build/cuda_timing_20261009T231303050084Z/cpu-release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_CUDA=OFF -DMAB_ENABLE_CUDA_SORT=OFF
```

## Local release_ctest

Exit: `0`; record `results/raw/cuda_timing_20261009T231303050084Z/commands/release_ctest.json`.

```bash
ctest --test-dir build/cuda_timing_20261009T231303050084Z/cpu-release --output-on-failure -V
```

## Local release_ctest_final

Exit: `0`; record `results/raw/cuda_timing_20261009T231303050084Z/commands/release_ctest_final.json`.

```bash
ctest --test-dir build/cuda_timing_20261009T231303050084Z/cpu-release --output-on-failure -V
```

## Local remote_validation

Exit: `0`; record `results/raw/cuda_timing_20261009T231303050084Z/commands/remote_validation.json`.

```bash
timeout --signal=TERM 2700 colab --config build/cuda_timing_20261009T231303050084Z/private_cli/sessions.json exec --session mab-t4-20261009T231303050084Z --file results/raw/cuda_timing_20261009T231303050084Z/run_remote.py --timeout 2500
```

## Local replacement_t4

Exit: `0`; record `results/raw/cuda_timing_20261009T231303050084Z/commands/replacement_t4.json`.

```bash
timeout --signal=TERM 120 colab --config build/cuda_timing_20261009T231303050084Z/private_cli/sessions.json new --gpu T4 --session mab-t4-20261009T231303050084Z
```

## Local sanitize_build

Exit: `0`; record `results/raw/cuda_timing_20261009T231303050084Z/commands/sanitize_build.json`.

```bash
cmake --build build/cuda_timing_20261009T231303050084Z/cpu-sanitize --parallel 2
```

## Local sanitize_configure

Exit: `0`; record `results/raw/cuda_timing_20261009T231303050084Z/commands/sanitize_configure.json`.

```bash
cmake -S . -B build/cuda_timing_20261009T231303050084Z/cpu-sanitize -DCMAKE_BUILD_TYPE=Debug -DMAB_ENABLE_SANITIZERS=ON -DMAB_ENABLE_CUDA=OFF -DMAB_ENABLE_CUDA_SORT=OFF
```

## Local sanitize_ctest

Exit: `0`; record `results/raw/cuda_timing_20261009T231303050084Z/commands/sanitize_ctest.json`.

```bash
env -u ASAN_OPTIONS -u LSAN_OPTIONS UBSAN_OPTIONS=halt_on_error=1 ctest --test-dir build/cuda_timing_20261009T231303050084Z/cpu-sanitize --output-on-failure -V
```

## Local upload_source

Exit: `0`; record `results/raw/cuda_timing_20261009T231303050084Z/commands/upload_source.json`.

```bash
timeout --signal=TERM 120 colab --config build/cuda_timing_20261009T231303050084Z/private_cli/sessions.json upload results/raw/cuda_timing_20261009T231303050084Z/cuda_timing_source_v1.tar.gz /content/cuda_timing_20261009T231303050084Z_source.tar.gz --session mab-t4-20261009T231303050084Z
```

## Remote analyze_matrix.json

Exit: `0`; cwd `/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark`.

```bash
/usr/bin/python3 /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/scripts/analyze_cuda_results.py /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/processed/NEW_GPU_TIMING/matrix.json
```

## Remote analyze_smallest.json

Exit: `0`; cwd `/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark`.

```bash
/usr/bin/python3 /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/scripts/analyze_cuda_results.py /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/smallest --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/processed/NEW_GPU_TIMING/smallest.json
```

## Remote build_benchmark.json

Exit: `0`; cwd `/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark`.

```bash
cmake --build /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build --target cuda_sort_benchmark --parallel 2
```

## Remote correctness/build.json

Exit: `0`; cwd `/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark`.

```bash
cmake --build /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build --target test_cuda_sorting --parallel 2
```

## Remote correctness/configure.json

Exit: `0`; cwd `/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark`.

```bash
cmake -S /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark -B /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_CUDA=ON -DMAB_ENABLE_CUDA_SORT=ON -DMAB_ENABLE_OPENMP=OFF -DMAB_ENABLE_SANITIZERS=OFF -DBUILD_TESTING=ON -DCMAKE_CUDA_COMPILER=/usr/local/cuda/bin/nvcc -DCMAKE_CUDA_ARCHITECTURES=75
```

## Remote correctness/ctest.json

Exit: `0`; cwd `/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark`.

```bash
ctest --test-dir /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build --output-on-failure -V -R '^cuda_sorting$'
```

## Remote correctness/preflight.json

Exit: `0`; cwd `/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark`.

```bash
/usr/bin/python3 /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/scripts/cuda_preflight.py --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/preflight --timeout-seconds 180
```

## Remote correctness/sorting.json

Exit: `0`; cwd `/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/test_cuda_sorting
```

## Remote correctness.json

Exit: `0`; cwd `/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark`.

```bash
/usr/bin/python3 /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/scripts/validate_cuda_sort.py --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness
```

## Remote gpu_framework.json

Exit: `0`; cwd `/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark`.

```bash
ctest --test-dir /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build --output-on-failure -V -R '^cuda_benchmark_gpu_framework$'
```

## Remote matrix/commands/run_0000.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0000 --run-id run_0000 --size 0 --distribution uniform --seed 1729 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0001.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0001 --run-id run_0001 --size 0 --distribution uniform --seed 42 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0002.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0002 --run-id run_0002 --size 0 --distribution sorted --seed 1729 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0003.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0003 --run-id run_0003 --size 0 --distribution sorted --seed 42 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0004.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0004 --run-id run_0004 --size 0 --distribution reverse_sorted --seed 1729 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0005.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0005 --run-id run_0005 --size 0 --distribution reverse_sorted --seed 42 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0006.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0006 --run-id run_0006 --size 0 --distribution duplicate_heavy --seed 1729 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0007.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0007 --run-id run_0007 --size 0 --distribution duplicate_heavy --seed 42 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0008.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0008 --run-id run_0008 --size 0 --distribution nearly_sorted --seed 1729 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0009.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0009 --run-id run_0009 --size 0 --distribution nearly_sorted --seed 42 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0010.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0010 --run-id run_0010 --size 0 --distribution signed_edges --seed 1729 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0011.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0011 --run-id run_0011 --size 0 --distribution signed_edges --seed 42 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0012.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0012 --run-id run_0012 --size 1 --distribution uniform --seed 1729 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0013.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0013 --run-id run_0013 --size 1 --distribution uniform --seed 42 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0014.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0014 --run-id run_0014 --size 1 --distribution sorted --seed 1729 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0015.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0015 --run-id run_0015 --size 1 --distribution sorted --seed 42 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0016.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0016 --run-id run_0016 --size 1 --distribution reverse_sorted --seed 1729 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0017.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0017 --run-id run_0017 --size 1 --distribution reverse_sorted --seed 42 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0018.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0018 --run-id run_0018 --size 1 --distribution duplicate_heavy --seed 1729 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0019.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0019 --run-id run_0019 --size 1 --distribution duplicate_heavy --seed 42 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0020.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0020 --run-id run_0020 --size 1 --distribution nearly_sorted --seed 1729 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0021.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0021 --run-id run_0021 --size 1 --distribution nearly_sorted --seed 42 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0022.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0022 --run-id run_0022 --size 1 --distribution signed_edges --seed 1729 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0023.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0023 --run-id run_0023 --size 1 --distribution signed_edges --seed 42 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0024.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0024 --run-id run_0024 --size 1025 --distribution uniform --seed 1729 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0025.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0025 --run-id run_0025 --size 1025 --distribution uniform --seed 42 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0026.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0026 --run-id run_0026 --size 1025 --distribution sorted --seed 1729 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0027.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0027 --run-id run_0027 --size 1025 --distribution sorted --seed 42 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0028.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0028 --run-id run_0028 --size 1025 --distribution reverse_sorted --seed 1729 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0029.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0029 --run-id run_0029 --size 1025 --distribution reverse_sorted --seed 42 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0030.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0030 --run-id run_0030 --size 1025 --distribution duplicate_heavy --seed 1729 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0031.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0031 --run-id run_0031 --size 1025 --distribution duplicate_heavy --seed 42 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0032.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0032 --run-id run_0032 --size 1025 --distribution nearly_sorted --seed 1729 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0033.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0033 --run-id run_0033 --size 1025 --distribution nearly_sorted --seed 42 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0034.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0034 --run-id run_0034 --size 1025 --distribution signed_edges --seed 1729 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0035.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0035 --run-id run_0035 --size 1025 --distribution signed_edges --seed 42 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0036.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0036 --run-id run_0036 --size 65537 --distribution uniform --seed 1729 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0037.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0037 --run-id run_0037 --size 65537 --distribution uniform --seed 42 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0038.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0038 --run-id run_0038 --size 65537 --distribution sorted --seed 1729 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0039.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0039 --run-id run_0039 --size 65537 --distribution sorted --seed 42 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0040.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0040 --run-id run_0040 --size 65537 --distribution reverse_sorted --seed 1729 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0041.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0041 --run-id run_0041 --size 65537 --distribution reverse_sorted --seed 42 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0042.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0042 --run-id run_0042 --size 65537 --distribution duplicate_heavy --seed 1729 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0043.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0043 --run-id run_0043 --size 65537 --distribution duplicate_heavy --seed 42 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0044.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0044 --run-id run_0044 --size 65537 --distribution nearly_sorted --seed 1729 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0045.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0045 --run-id run_0045 --size 65537 --distribution nearly_sorted --seed 42 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0046.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0046 --run-id run_0046 --size 65537 --distribution signed_edges --seed 1729 --warmups 1 --repetitions 5
```

## Remote matrix/commands/run_0047.json

Exit: `0`; cwd `see parent command record`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix/run_0047 --run-id run_0047 --size 65537 --distribution signed_edges --seed 42 --warmups 1 --repetitions 5
```

## Remote regenerate_matrix.json

Exit: `0`; cwd `/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark`.

```bash
/usr/bin/python3 /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/scripts/analyze_cuda_results.py /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/processed/NEW_GPU_TIMING/matrix_regenerated.json
```

## Remote regenerate_smallest.json

Exit: `0`; cwd `/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark`.

```bash
/usr/bin/python3 /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/scripts/analyze_cuda_results.py /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/smallest --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/processed/NEW_GPU_TIMING/smallest_regenerated.json
```

## Remote smallest_smoke.json

Exit: `0`; cwd `/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark`.

```bash
/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/smallest --size 1025 --distribution uniform --seed 1729 --warmups 1 --repetitions 5
```

## Remote smoke_matrix.json

Exit: `0`; cwd `/content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark`.

```bash
/usr/bin/python3 /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/scripts/run_cuda_matrix.py --executable /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/correctness/build/cuda_sort_benchmark --output /content/cuda_timing_20261009T231303050084Z/modern-algorithm-benchmark/results/raw/NEW_GPU_TIMING/matrix --sizes 0,1,1025,65537 --seeds 1729,42 --distributions uniform,sorted,reverse_sorted,duplicate_heavy,nearly_sorted,signed_edges --warmups 1 --repetitions 5
```

## Local regeneration and independent verification

The command `python3 results/raw/cuda_timing_20261009T231303050084Z/verify_results.py` regenerated both bundles twice, checked every group against remote summaries, recalculated all196 metric-statistic groups with Python statistics and verified9568 prior artifacts plus1115 transferred files. Its exact four analyzer argv values are defined in that retained script and exit0 was required for each.

## Final review diagnostics and corrected command

The first inline Python inventory command returned1 because its collector omitted `.gitignore`; the file remained present. See review_inventory_attempt1.json. It did not write a source inventory or change project files.

Exit `1`: record commands/final_review.json.

```bash
python3 results/raw/cuda_timing_20261009T231303050084Z/final_review.py
```

Exit `0`: record commands/final_review_v2.json.

```bash
python3 results/raw/cuda_timing_20261009T231303050084Z/final_review_v2.py
```

The recorded first reviewer matched a period instead of the actual comma in a CMake comment, causing an assertion failure. Corrected v2 verified the unchanged dependency-pin prefix,125 tested non-document files,131 protected starting files, new frozen timing protocol and9568 earlier artifacts. No implementation/test was changed for these helper failures.
