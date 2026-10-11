# Final corrected-revision commands

```sh
python3 tests/test_cuda_sort_handoff.py
```

Exit 0; [record](commands/targeted.json).

```sh
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_CUDA=OFF -DMAB_ENABLE_CUDA_SORT=OFF -DMAB_ENABLE_OPENMP=ON -DMAB_ENABLE_SANITIZERS=OFF
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
cmake -S . -B build/sanitize -DCMAKE_BUILD_TYPE=Debug -DMAB_ENABLE_CUDA=OFF -DMAB_ENABLE_CUDA_SORT=OFF -DMAB_ENABLE_OPENMP=ON -DMAB_ENABLE_SANITIZERS=ON
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

