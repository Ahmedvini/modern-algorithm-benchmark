# Phase7 exact command ledger

Each command JSON retains argv,cwd,UTC start/end,exit code,stdout/stderr and wall time. Exit2 for local preflight is expected unavailable readiness, not a failed CPU test. Missing tools inside preflight have null returncode/status unavailable; configure/build/runtime were skipped. No CUDA-enabled configure or hardware execution took place.

| Record | Exit | Wall seconds | Exact command |
|---|---:|---:|---|
| [baseline_configure](commands/baseline_configure.json) | 0 | 0.131741 | `cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release` |
| [baseline_build](commands/baseline_build.json) | 0 | 0.287694 | `cmake --build build/release --parallel 2` |
| [baseline_ctest](commands/baseline_ctest.json) | 0 | 30.151447 | `ctest --test-dir build/release --output-on-failure -V` |
| [preflight_unit_tests](commands/preflight_unit_tests.json) | 0 | 0.426558 | `/usr/bin/python3 tests/test_cuda_preflight.py` |
| [local_preflight](commands/local_preflight.json) | 2 | 0.095000 | `/usr/bin/python3 scripts/cuda_preflight.py --output results/raw/cuda_preflight_20261009T205410772326Z` |
| [final_preflight_unit_tests](commands/final_preflight_unit_tests.json) | 0 | 0.421696 | `/usr/bin/python3 tests/test_cuda_preflight.py` |
| [release_configure](commands/release_configure.json) | 0 | 0.133537 | `cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_CUDA=OFF -DMAB_ENABLE_OPENMP=ON -DMAB_ENABLE_SANITIZERS=OFF` |
| [release_build](commands/release_build.json) | 0 | 0.293796 | `cmake --build build/release --parallel 2` |
| [release_ctest](commands/release_ctest.json) | 0 | 27.505528 | `ctest --test-dir build/release --output-on-failure -V` |
| [sanitize_configure](commands/sanitize_configure.json) | 0 | 0.134724 | `cmake -S . -B build/sanitize -DCMAKE_BUILD_TYPE=Debug -DMAB_ENABLE_CUDA=OFF -DMAB_ENABLE_OPENMP=ON -DMAB_ENABLE_SANITIZERS=ON` |
| [sanitize_build](commands/sanitize_build.json) | 0 | 0.277085 | `cmake --build build/sanitize --parallel 2` |
| [sanitize_ctest](commands/sanitize_ctest.json) | 0 | 80.102021 | `env -u ASAN_OPTIONS -u LSAN_OPTIONS UBSAN_OPTIONS=halt_on_error=1 ctest --test-dir build/sanitize --output-on-failure -V` |
| [reviewed_local_preflight](commands/reviewed_local_preflight.json) | 2 | 0.082832 | `/usr/bin/python3 scripts/cuda_preflight.py --output results/raw/cuda_preflight_20261009T205410772326Z_reviewed` |
| [reviewed_preflight_unit_tests](commands/reviewed_preflight_unit_tests.json) | 0 | 0.418680 | `/usr/bin/python3 tests/test_cuda_preflight.py` |
| [reviewed_release_configure](commands/reviewed_release_configure.json) | 0 | 0.131379 | `cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_CUDA=OFF -DMAB_ENABLE_OPENMP=ON -DMAB_ENABLE_SANITIZERS=OFF` |
| [reviewed_release_build](commands/reviewed_release_build.json) | 0 | 0.275505 | `cmake --build build/release --parallel 2` |
| [reviewed_release_ctest](commands/reviewed_release_ctest.json) | 0 | 27.101205 | `ctest --test-dir build/release --output-on-failure -V` |
| [cpu_environment](commands/cpu_environment.json) | 0 | 0.043241 | `/usr/bin/python3 scripts/capture_environment.py --build-dir build/release --output results/raw/cuda_preflight_validation_20261009T205410772326Z/cpu_environment.json` |
| [reviewed_sanitize_configure](commands/reviewed_sanitize_configure.json) | 0 | 0.131336 | `cmake -S . -B build/sanitize -DCMAKE_BUILD_TYPE=Debug -DMAB_ENABLE_CUDA=OFF -DMAB_ENABLE_OPENMP=ON -DMAB_ENABLE_SANITIZERS=ON` |
| [reviewed_sanitize_build](commands/reviewed_sanitize_build.json) | 0 | 0.275464 | `cmake --build build/sanitize --parallel 2` |
| [reviewed_sanitize_ctest](commands/reviewed_sanitize_ctest.json) | 0 | 78.650656 | `env -u ASAN_OPTIONS -u LSAN_OPTIONS UBSAN_OPTIONS=halt_on_error=1 ctest --test-dir build/sanitize --output-on-failure -V` |
| [cpu_fallback_configure](commands/cpu_fallback_configure.json) | 0 | 0.165871 | `cmake -S . -B build/cuda_cpu_fallback -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_CUDA=OFF -DMAB_ENABLE_OPENMP=OFF -DBUILD_TESTING=OFF` |
| [cpu_fallback_build](commands/cpu_fallback_build.json) | 0 | 3.384496 | `cmake --build build/cuda_cpu_fallback --target sort_benchmark --parallel 2` |
| [cpu_fallback_registry](commands/cpu_fallback_registry.json) | 0 | 0.001347 | `build/cuda_cpu_fallback/sort_benchmark --list-sorts` |
| [source_bundle](commands/source_bundle.json) | 0 | 0.307906 | `python3 -B results/raw/cuda_preflight_validation_20261009T205410772326Z/prepare_source_bundle.py` |
| [final_review](commands/final_review.json) | 0 | 0.346347 | `python3 -B results/raw/cuda_preflight_validation_20261009T205410772326Z/final_review.py` |

Preflight per-tool commands/statuses are in ../cuda_preflight_20261009T205410772326Z_reviewed/report.json; archive extraction/relocated CMake commands/statuses in source_bundle_validation.json.

Git status128 is retained in cpu_environment.json. Test-mocked operational cases and temporary CUDA-OFF CMake cases are not hardware capability evidence.

Final review passed before ledger generation. Ledger generation reads captured records; no experiment files are modified.
