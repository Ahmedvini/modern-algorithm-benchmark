# Exact local validation commands

No command below ran in Colab/cloud. JSON records retain argv/cwd, timestamps, stdout/stderr and status.

```sh
python3 results/raw/gpu_cloud_gate1_20261009T211734154323Z/validate_archive.py
```

Exit 0; [record](commands/archive.json).

```sh
python3 build/gpu_cloud_archive_20261009T211734154323Z/modern-algorithm-benchmark/scripts/cuda_preflight.py --output results/raw/gpu_cloud_gate1_20261009T211734154323Z/local_preflight
```

Exit 2; [record](commands/local_preflight.json).

```sh
cmake -S build/gpu_cloud_archive_20261009T211734154323Z/modern-algorithm-benchmark -B build/gpu_cloud_archive_20261009T211734154323Z/cpu_build -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_CUDA=OFF -DMAB_ENABLE_OPENMP=OFF -DBUILD_TESTING=OFF
```

Exit 0; [record](commands/archive_cpu_configure.json).

```sh
cmake --build build/gpu_cloud_archive_20261009T211734154323Z/cpu_build --target sort_benchmark --parallel 2
```

Exit 0; [record](commands/archive_cpu_build.json).

```sh
build/gpu_cloud_archive_20261009T211734154323Z/cpu_build/sort_benchmark --list-sorts
```

Exit 0; [record](commands/archive_cpu_registry.json).

```sh
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_CUDA=OFF -DMAB_ENABLE_OPENMP=ON -DMAB_ENABLE_SANITIZERS=OFF
```

Exit 0; [record](commands/release_configure.json).

```sh
cmake --build build/release --parallel 2
```

Exit 0; [record](commands/release_build.json).

```sh
ctest --test-dir build/release --output-on-failure -V
```

Exit 0; [record](commands/release_ctest.json).

```sh
cmake -S . -B build/sanitize -DCMAKE_BUILD_TYPE=Debug -DMAB_ENABLE_CUDA=OFF -DMAB_ENABLE_OPENMP=ON -DMAB_ENABLE_SANITIZERS=ON
```

Exit 0; [record](commands/sanitize_configure.json).

```sh
cmake --build build/sanitize --parallel 2
```

Exit 0; [record](commands/sanitize_build.json).

```sh
env -u ASAN_OPTIONS -u LSAN_OPTIONS UBSAN_OPTIONS=halt_on_error=1 ctest --test-dir build/sanitize --output-on-failure -V
```

Exit 0; [record](commands/sanitize_ctest.json).

```sh
python3 scripts/capture_environment.py --build-dir build/release --output results/raw/gpu_cloud_gate1_20261009T211734154323Z/cpu_environment.json
```

Exit 0; [record](commands/cpu_environment.json).

