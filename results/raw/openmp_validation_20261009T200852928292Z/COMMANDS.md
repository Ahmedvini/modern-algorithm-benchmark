# Phase 6 exact recorded commands

Each record retains cwd, UTC start/end, argv, exit status, stdout/stderr and wall duration. The original recorder setup failure is separate in initial_recorder_failure.json; no child was launched. Git absence is recorded in each environment manifest. Exploratory source reads are not benchmark/test commands.

| Record | Exit | Wall seconds | Exact command |
|---|---:|---:|---|
| [baseline_configure](commands/baseline_configure.json) | 0 | 0.127933 | `cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_SANITIZERS=OFF` |
| [baseline_build](commands/baseline_build.json) | 0 | 0.263533 | `cmake --build build/release --parallel 2` |
| [baseline_ctest](commands/baseline_ctest.json) | 0 | 17.545856 | `ctest --test-dir build/release --output-on-failure -V` |
| [openmp_probe_compile](commands/openmp_probe_compile.json) | 0 | 0.227655 | `c++ -std=c++17 -Wall -Wextra -Wpedantic -fopenmp build/openmp_probe/probe.cpp -o build/openmp_probe/probe` |
| [openmp_probe](commands/openmp_probe.json) | 0 | 0.002127 | `env OMP_DYNAMIC=FALSE OMP_THREAD_LIMIT=8 build/openmp_probe/probe` |
| [implementation_configure](commands/implementation_configure.json) | 0 | 0.339876 | `cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_SANITIZERS=OFF -DMAB_ENABLE_OPENMP=ON` |
| [implementation_build](commands/implementation_build.json) | 0 | 8.140394 | `cmake --build build/release --parallel 2` |
| [parallel_correctness](commands/parallel_correctness.json) | 0 | 0.809121 | `env OMP_DYNAMIC=FALSE OMP_THREAD_LIMIT=8 OMP_WAIT_POLICY=PASSIVE build/release/test_parallel_mergesort` |
| [tsan_compile](commands/tsan_compile.json) | 0 | 2.814295 | `c++ -std=c++17 -g -O1 -fopenmp -fsanitize=thread -fno-omit-frame-pointer -Iinclude -Itests tests/test_parallel_mergesort.cpp src/algorithms/parallel_mergesort.cpp src/algorithms/mergesort.cpp src/benchmark/parallel_timing.cpp src/benchmark/timing.cpp build/release/libmab_core.a -pthread -o build/openmp_probe/test_parallel_tsan` |
| [tsan_run](commands/tsan_run.json) | 66 | 0.008685 | `env OMP_DYNAMIC=FALSE OMP_THREAD_LIMIT=8 OMP_WAIT_POLICY=PASSIVE TSAN_OPTIONS=halt_on_error=1 build/openmp_probe/test_parallel_tsan` |
| [parallel_python](commands/parallel_python.json) | 0 | 3.404503 | `python3 tests/test_parallel_benchmark.py build/release/parallel_sort_benchmark` |
| [tsan_standalone_compile](commands/tsan_standalone_compile.json) | 0 | 0.162515 | `c++ -g -O1 -std=c++17 -fsanitize=thread build/openmp_probe/tsan_standalone.cpp -pthread -o build/openmp_probe/tsan_standalone` |
| [tsan_standalone_run](commands/tsan_standalone_run.json) | 66 | 0.006579 | `env TSAN_OPTIONS=halt_on_error=1 build/openmp_probe/tsan_standalone` |
| [reviewed_parallel_python](commands/reviewed_parallel_python.json) | 0 | 3.585388 | `python3 tests/test_parallel_benchmark.py build/release/parallel_sort_benchmark` |
| [release_configure](commands/release_configure.json) | 0 | 0.133887 | `cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_SANITIZERS=OFF -DMAB_ENABLE_OPENMP=ON` |
| [release_build](commands/release_build.json) | 0 | 1.200857 | `cmake --build build/release --parallel 2` |
| [release_ctest](commands/release_ctest.json) | 0 | 22.678742 | `ctest --test-dir build/release --output-on-failure -V` |
| [sanitize_configure](commands/sanitize_configure.json) | 0 | 0.337653 | `cmake -S . -B build/sanitize -DCMAKE_BUILD_TYPE=Debug -DMAB_ENABLE_SANITIZERS=ON -DMAB_ENABLE_OPENMP=ON` |
| [sanitize_build](commands/sanitize_build.json) | 0 | 9.593070 | `cmake --build build/sanitize --parallel 2` |
| [reviewed_release_configure](commands/reviewed_release_configure.json) | 0 | 0.134238 | `cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_SANITIZERS=OFF -DMAB_ENABLE_OPENMP=ON` |
| [reviewed_release_build](commands/reviewed_release_build.json) | 0 | 2.000988 | `cmake --build build/release --parallel 2` |
| [reviewed_sanitize_configure](commands/reviewed_sanitize_configure.json) | 0 | 0.142649 | `cmake -S . -B build/sanitize -DCMAKE_BUILD_TYPE=Debug -DMAB_ENABLE_SANITIZERS=ON -DMAB_ENABLE_OPENMP=ON` |
| [reviewed_sanitize_build](commands/reviewed_sanitize_build.json) | 0 | 2.384911 | `cmake --build build/sanitize --parallel 2` |
| [reviewed_release_ctest](commands/reviewed_release_ctest.json) | 0 | 23.534400 | `ctest --test-dir build/release --output-on-failure -V` |
| [reviewed_sanitize_ctest](commands/reviewed_sanitize_ctest.json) | 0 | 74.695863 | `env -u ASAN_OPTIONS -u LSAN_OPTIONS UBSAN_OPTIONS=halt_on_error=1 ctest --test-dir build/sanitize --output-on-failure -V` |
| [no_openmp_configure](commands/no_openmp_configure.json) | 0 | 0.187329 | `cmake -S . -B build/no_openmp -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_OPENMP=OFF -DBUILD_TESTING=OFF` |
| [no_openmp_build](commands/no_openmp_build.json) | 0 | 3.708654 | `cmake --build build/no_openmp --target sort_benchmark --parallel 2` |
| [no_openmp_registry](commands/no_openmp_registry.json) | 0 | 0.001357 | `build/no_openmp/sort_benchmark --list-sorts` |
| [smoke_dry_run](commands/smoke_dry_run.json) | 0 | 0.037522 | `python3 scripts/run_parallel_matrix.py --preset smoke --output results/raw/openmp_smoke_20261009T200852928292Z --processed results/processed/openmp_smoke_20261009T200852928292Z --figures results/figures/openmp_smoke_20261009T200852928292Z --dry-run` |
| [smoke_pipeline](commands/smoke_pipeline.json) | 0 | 3.768080 | `python3 scripts/run_parallel_matrix.py --preset smoke --output results/raw/openmp_smoke_20261009T200852928292Z --processed results/processed/openmp_smoke_20261009T200852928292Z --figures results/figures/openmp_smoke_20261009T200852928292Z` |
| [smoke_verification](commands/smoke_verification.json) | 0 | 3.113545 | `python3 -B results/raw/openmp_validation_20261009T200852928292Z/verify_smoke.py` |
| [freeze_full](commands/freeze_full.json) | 0 | 0.291004 | `python3 -B results/raw/openmp_validation_20261009T200852928292Z/freeze_full.py` |
| [full_dry_run](commands/full_dry_run.json) | 0 | 0.040326 | `python3 scripts/run_parallel_matrix.py --preset full --output results/raw/openmp_scaling_20261009T200852928292Z --processed results/processed/openmp_scaling_20261009T200852928292Z --figures results/figures/openmp_scaling_20261009T200852928292Z --dry-run` |
| [full_pipeline](commands/full_pipeline.json) | 1 | 24.900420 | `python3 scripts/run_parallel_matrix.py --preset full --output results/raw/openmp_scaling_20261009T200852928292Z --processed results/processed/openmp_scaling_20261009T200852928292Z --figures results/figures/openmp_scaling_20261009T200852928292Z` |
| [corrected_parallel_python](commands/corrected_parallel_python.json) | 0 | 9.338346 | `python3 tests/test_parallel_benchmark.py build/release/parallel_sort_benchmark` |
| [corrected_release_configure](commands/corrected_release_configure.json) | 0 | 0.139213 | `cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_SANITIZERS=OFF -DMAB_ENABLE_OPENMP=ON` |
| [corrected_release_build](commands/corrected_release_build.json) | 0 | 0.308875 | `cmake --build build/release --parallel 2` |
| [corrected_release_ctest](commands/corrected_release_ctest.json) | 0 | 30.097197 | `ctest --test-dir build/release --output-on-failure -V` |
| [corrected_sanitize_configure](commands/corrected_sanitize_configure.json) | 0 | 0.154681 | `cmake -S . -B build/sanitize -DCMAKE_BUILD_TYPE=Debug -DMAB_ENABLE_SANITIZERS=ON -DMAB_ENABLE_OPENMP=ON` |
| [corrected_sanitize_build](commands/corrected_sanitize_build.json) | 0 | 0.328316 | `cmake --build build/sanitize --parallel 2` |
| [corrected_sanitize_ctest](commands/corrected_sanitize_ctest.json) | 0 | 84.518772 | `env -u ASAN_OPTIONS -u LSAN_OPTIONS UBSAN_OPTIONS=halt_on_error=1 ctest --test-dir build/sanitize --output-on-failure -V` |
| [retry_smoke_dry_run](commands/retry_smoke_dry_run.json) | 0 | 0.045323 | `/usr/bin/python3 scripts/run_parallel_matrix.py --preset smoke --output results/raw/openmp_smoke_20261009T200852928292Z_retry1 --processed results/processed/openmp_smoke_20261009T200852928292Z_retry1 --figures results/figures/openmp_smoke_20261009T200852928292Z_retry1 --dry-run` |
| [retry_smoke_pipeline](commands/retry_smoke_pipeline.json) | 0 | 3.732744 | `/usr/bin/python3 scripts/run_parallel_matrix.py --preset smoke --output results/raw/openmp_smoke_20261009T200852928292Z_retry1 --processed results/processed/openmp_smoke_20261009T200852928292Z_retry1 --figures results/figures/openmp_smoke_20261009T200852928292Z_retry1` |
| [retry_smoke_verification](commands/retry_smoke_verification.json) | 0 | 3.452166 | `/usr/bin/python3 -B results/raw/openmp_validation_20261009T200852928292Z/verify_run.py smoke` |
| [freeze_retry_full](commands/freeze_retry_full.json) | 0 | 0.307706 | `/usr/bin/python3 results/raw/openmp_validation_20261009T200852928292Z/freeze_retry_full.py` |
| [retry_full_dry_run](commands/retry_full_dry_run.json) | 0 | 0.048369 | `/usr/bin/python3 scripts/run_parallel_matrix.py --preset full --output results/raw/openmp_scaling_20261009T200852928292Z_retry1 --processed results/processed/openmp_scaling_20261009T200852928292Z_retry1 --figures results/figures/openmp_scaling_20261009T200852928292Z_retry1 --dry-run` |
| [retry_full_pipeline](commands/retry_full_pipeline.json) | 0 | 33.123315 | `/usr/bin/python3 scripts/run_parallel_matrix.py --preset full --output results/raw/openmp_scaling_20261009T200852928292Z_retry1 --processed results/processed/openmp_scaling_20261009T200852928292Z_retry1 --figures results/figures/openmp_scaling_20261009T200852928292Z_retry1` |
| [retry_full_verification](commands/retry_full_verification.json) | 0 | 8.837284 | `/usr/bin/python3 -B results/raw/openmp_validation_20261009T200852928292Z/verify_run.py full` |
| [final_review](commands/final_review.json) | 0 | 0.815890 | `python3 -B results/raw/openmp_validation_20261009T200852928292Z/final_review.py` |

## Per-configuration benchmark commands

Full retry: ../openmp_scaling_20261009T200852928292Z_retry1/matrix.json and run_XXXXXX_command.json (180 children, all exit0).
Smoke retry: ../openmp_smoke_20261009T200852928292Z_retry1/matrix.json (32 children, all exit0).
Original full attempt: ../openmp_scaling_20261009T200852928292Z/matrix.json (180 children exit0; runner exit1, metadata-analysis defect, retained FAILED).

Diagnostics and all failed attempts are retained; timing observations from different attempts are never pooled. No CUDA or100M command was run.

Ledger generated with `python3 results/raw/openmp_validation_20261009T200852928292Z/generate_ledger.py` after final_review exited0.
