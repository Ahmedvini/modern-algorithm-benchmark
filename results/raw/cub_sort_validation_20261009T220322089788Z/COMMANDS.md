# Exact command records

All new commands ran locally. Cloud evidence is historical, separately reviewed.

```sh
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_CUDA=OFF -DMAB_ENABLE_OPENMP=ON -DMAB_ENABLE_SANITIZERS=OFF
```

Exit 0; [diagnostics](commands/baseline_configure.json).

```sh
cmake --build build/release --parallel 2
```

Exit 0; [diagnostics](commands/baseline_build.json).

```sh
ctest --test-dir build/release --output-on-failure -V
```

Exit 0; [diagnostics](commands/baseline_ctest.json).

```sh
python3 tests/test_cuda_sort_handoff.py
```

Exit 0; [diagnostics](commands/targeted_handoff.json).

```sh
cmake -S . -B build/cub_sort_unavailable -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_CUDA=ON -DMAB_ENABLE_CUDA_SORT=ON -DMAB_ENABLE_OPENMP=OFF
```

Exit 1; [diagnostics](commands/local_cuda_configure.json).

```sh
python3 scripts/cuda_preflight.py --output results/raw/cub_sort_validation_20261009T220322089788Z/local_preflight
```

Exit 2; [diagnostics](commands/local_preflight.json).

```sh
python3 tests/test_cuda_sort_handoff.py
```

Exit 0; [diagnostics](commands/final_targeted.json).

```sh
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_CUDA=OFF -DMAB_ENABLE_CUDA_SORT=OFF -DMAB_ENABLE_OPENMP=ON -DMAB_ENABLE_SANITIZERS=OFF
```

Exit 0; [diagnostics](commands/release_configure.json).

```sh
cmake --build build/release --parallel 2
```

Exit 0; [diagnostics](commands/release_build.json).

```sh
ctest --test-dir build/release --output-on-failure -V
```

Exit 0; [diagnostics](commands/release_ctest.json).

```sh
cmake -S . -B build/sanitize -DCMAKE_BUILD_TYPE=Debug -DMAB_ENABLE_CUDA=OFF -DMAB_ENABLE_CUDA_SORT=OFF -DMAB_ENABLE_OPENMP=ON -DMAB_ENABLE_SANITIZERS=ON
```

Exit 0; [diagnostics](commands/sanitize_configure.json).

```sh
cmake --build build/sanitize --parallel 2
```

Exit 0; [diagnostics](commands/sanitize_build.json).

```sh
env -u ASAN_OPTIONS -u LSAN_OPTIONS UBSAN_OPTIONS=halt_on_error=1 ctest --test-dir build/sanitize --output-on-failure -V
```

Exit 0; [diagnostics](commands/sanitize_ctest.json).

```sh
python3 tests/test_cuda_sort_handoff.py
```

Exit 0; [diagnostics](commands/reviewed_targeted.json).

```sh
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_CUDA=OFF -DMAB_ENABLE_CUDA_SORT=OFF -DMAB_ENABLE_OPENMP=ON -DMAB_ENABLE_SANITIZERS=OFF
```

Exit 0; [diagnostics](commands/reviewed_release_configure.json).

```sh
cmake --build build/release --parallel 2
```

Exit 0; [diagnostics](commands/reviewed_release_build.json).

```sh
ctest --test-dir build/release --output-on-failure -V
```

Exit 0; [diagnostics](commands/reviewed_release_ctest.json).

```sh
git status --short
```

Exit 128; [diagnostics](commands/git_status.json).

```sh
git branch --all
```

Exit 128; [diagnostics](commands/git_branch.json).

```sh
git log -5 --oneline
```

Exit 128; [diagnostics](commands/git_log.json).

```sh
cmake -S . -B build/sanitize -DCMAKE_BUILD_TYPE=Debug -DMAB_ENABLE_CUDA=OFF -DMAB_ENABLE_CUDA_SORT=OFF -DMAB_ENABLE_OPENMP=ON -DMAB_ENABLE_SANITIZERS=ON
```

Exit 0; [diagnostics](commands/reviewed_sanitize_configure.json).

```sh
cmake --build build/sanitize --parallel 2
```

Exit 0; [diagnostics](commands/reviewed_sanitize_build.json).

```sh
env -u ASAN_OPTIONS -u LSAN_OPTIONS UBSAN_OPTIONS=halt_on_error=1 ctest --test-dir build/sanitize --output-on-failure -V
```

Exit 0; [diagnostics](commands/reviewed_sanitize_ctest.json).

```sh
python3 scripts/capture_environment.py --build-dir build/release --output results/raw/cub_sort_validation_20261009T220322089788Z/cpu_environment.json
```

Exit 0; [diagnostics](commands/cpu_environment.json).

