# Phase 4 recorded commands

Each JSON record retains exact argv, stdout/stderr, cwd, timestamps and exit status. Commands ran at the repository root; historical logs have separate names.

- `commands/baseline_build.json` — exit 0

```sh
cmake --build build/release --parallel 2
```

- `commands/baseline_configure.json` — exit 0

```sh
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_SANITIZERS=OFF
```

- `commands/baseline_ctest.json` — exit 0

```sh
ctest --test-dir build/release --output-on-failure -V
```

- `commands/corrected_release_ctest.json` — exit 0

```sh
ctest --test-dir build/release --output-on-failure -V
```

- `commands/engine_build.json` — exit 0

```sh
cmake --build build/release --parallel 2
```

- `commands/engine_configure.json` — exit 0

```sh
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_SANITIZERS=OFF
```

- `commands/engine_tests.json` — exit 0

```sh
ctest --test-dir build/release --output-on-failure -V -R '^structure'
```

- `commands/final_release_build.json` — exit 0

```sh
cmake --build build/release --parallel 2
```

- `commands/final_release_configure.json` — exit 0

```sh
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_SANITIZERS=OFF
```

- `commands/final_release_ctest.json` — exit 0

```sh
ctest --test-dir build/release --output-on-failure -V
```

- `commands/final_sanitize_build.json` — exit 0

```sh
cmake --build build/sanitize --parallel 2
```

- `commands/final_sanitize_configure.json` — exit 0

```sh
cmake -S . -B build/sanitize -DCMAKE_BUILD_TYPE=Debug -DMAB_ENABLE_SANITIZERS=ON
```

- `commands/final_sanitize_ctest.json` — exit 0

```sh
env -u ASAN_OPTIONS -u LSAN_OPTIONS UBSAN_OPTIONS=halt_on_error=1 ctest --test-dir build/sanitize --output-on-failure -V
```

- `commands/git_status.json` — exit 128

```sh
git status --short
```

- `commands/release_environment_command.json` — exit 0

```sh
python3 scripts/capture_environment.py --build-dir build/release --output results/raw/structures_validation_20261009T181402878134Z/release_environment.json
```

- `commands/reviewed_release_build.json` — exit 0

```sh
cmake --build build/release --parallel 2
```

- `commands/reviewed_release_configure.json` — exit 0

```sh
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_SANITIZERS=OFF
```

- `commands/reviewed_release_ctest.json` — exit 8

```sh
ctest --test-dir build/release --output-on-failure -V
```

- `commands/reviewed_sanitize_build.json` — exit 0

```sh
cmake --build build/sanitize --parallel 2
```

- `commands/reviewed_sanitize_configure.json` — exit 0

```sh
cmake -S . -B build/sanitize -DCMAKE_BUILD_TYPE=Debug -DMAB_ENABLE_SANITIZERS=ON
```

- `commands/reviewed_sanitize_ctest.json` — exit 0

```sh
env -u ASAN_OPTIONS -u LSAN_OPTIONS UBSAN_OPTIONS=halt_on_error=1 ctest --test-dir build/sanitize --output-on-failure -V
```

- `commands/sanitize_environment_command.json` — exit 0

```sh
python3 scripts/capture_environment.py --build-dir build/sanitize --output results/raw/structures_validation_20261009T181402878134Z/sanitize_environment.json
```

- `commands/smoke_analysis_command.json` — exit 0

```sh
python3 scripts/analyze_structure_results.py results/raw/structures_validation_20261009T181402878134Z/smoke_matrix --output results/processed/structures_smoke_20261009T181402878134Z.json
```

- `commands/smoke_matrix_command.json` — exit 0

```sh
python3 scripts/run_structure_matrix.py --binary build/release/structure_benchmark --output results/raw/structures_validation_20261009T181402878134Z/smoke_matrix --sizes 0,1,64,1000 --seeds 1729 --query-seeds 2718 --structure-seed 1729 --distributions uniform,duplicate_heavy --structures all --categories all --queries 64 --repetitions 5 --warmups 1 --memory-limit-mib 256 --distinct 16
```

- `commands/structures_build.json` — exit 0

```sh
cmake --build build/release --parallel 2
```

- `commands/structures_build_reviewed.json` — exit 0

```sh
cmake --build build/release --parallel 2
```

- `commands/structures_configure.json` — exit 0

```sh
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_SANITIZERS=OFF
```

- `commands/structures_ctest.json` — exit 0

```sh
ctest --test-dir build/release --output-on-failure -V
```

- `commands/structures_sanitize_build.json` — exit 0

```sh
cmake --build build/sanitize --parallel 2
```

- `commands/structures_sanitize_configure.json` — exit 0

```sh
cmake -S . -B build/sanitize -DCMAKE_BUILD_TYPE=Debug -DMAB_ENABLE_SANITIZERS=ON
```

- `commands/structures_sanitize_ctest.json` — exit 0

```sh
env -u ASAN_OPTIONS -u LSAN_OPTIONS UBSAN_OPTIONS=halt_on_error=1 ctest --test-dir build/sanitize --output-on-failure -V
```

- `commands/verification_command.json` — exit 0

```sh
python3 results/raw/structures_validation_20261009T181402878134Z/verify.py
```

