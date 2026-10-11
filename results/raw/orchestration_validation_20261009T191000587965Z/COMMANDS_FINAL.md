# Final Phase 5 command ledger

Working directory: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark. Each JSON records stdout/stderr, return code and timestamps. Family experiment.json and *_command.json retain all child benchmark commands. This final ledger extends COMMANDS.md with the review checks, including both failed helper invocations.

- `cmake --build build/release --parallel 2` — **exit 0**; [baseline_build.json](commands/baseline_build.json).
- `cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_SANITIZERS=OFF` — **exit 0**; [baseline_configure.json](commands/baseline_configure.json).
- `ctest --test-dir build/release --output-on-failure -V` — **exit 0**; [baseline_ctest.json](commands/baseline_ctest.json).
- `python3 scripts/run_experiments.py --config results/raw/orchestration_validation_20261009T191000587965Z/calibration_config.json --run-id phase5_calibration_20261009T191000587965Z` — **exit 0**; [calibration_pipeline.json](commands/calibration_pipeline.json).
- `python3 scripts/assess_experiment.py results/raw/phase5_calibration_20261009T191000587965Z --output results/raw/orchestration_validation_20261009T191000587965Z/calibration_runtime_assessment.json` — **exit 0**; [calibration_runtime_assessment.json](commands/calibration_runtime_assessment.json).
- `python3 tests/test_experiments.py build/release` — **exit 0**; [completion_python_tests.json](commands/completion_python_tests.json).
- `cmake --build build/release --parallel 2` — **exit 0**; [completion_release_build.json](commands/completion_release_build.json).
- `cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_SANITIZERS=OFF` — **exit 0**; [completion_release_configure.json](commands/completion_release_configure.json).
- `ctest --test-dir build/release --output-on-failure -V` — **exit 0**; [completion_release_ctest.json](commands/completion_release_ctest.json).
- `cmake --build build/sanitize --parallel 2` — **exit 0**; [completion_sanitize_build.json](commands/completion_sanitize_build.json).
- `cmake -S . -B build/sanitize -DCMAKE_BUILD_TYPE=Debug -DMAB_ENABLE_SANITIZERS=ON` — **exit 0**; [completion_sanitize_configure.json](commands/completion_sanitize_configure.json).
- `env -u ASAN_OPTIONS -u LSAN_OPTIONS UBSAN_OPTIONS=halt_on_error=1 ctest --test-dir build/sanitize --output-on-failure -V` — **exit 0**; [completion_sanitize_ctest.json](commands/completion_sanitize_ctest.json).
- `python3 tests/test_experiments.py build/release` — **exit 0**; [corrected_python_tests.json](commands/corrected_python_tests.json).
- `cmake --build build/release --parallel 2` — **exit 0**; [final_release_build.json](commands/final_release_build.json).
- `cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_SANITIZERS=OFF` — **exit 0**; [final_release_configure.json](commands/final_release_configure.json).
- `ctest --test-dir build/release --output-on-failure -V` — **exit 0**; [final_release_ctest.json](commands/final_release_ctest.json).
- `python3 results/raw/orchestration_validation_20261009T191000587965Z/final_review.py` — **exit 1**; [final_review.json](commands/final_review.json).
- `python3 results/raw/orchestration_validation_20261009T191000587965Z/final_review.py` — **exit 0**; [final_review_complete.json](commands/final_review_complete.json).
- `python3 results/raw/orchestration_validation_20261009T191000587965Z/final_review.py` — **exit 1**; [final_review_corrected.json](commands/final_review_corrected.json).
- `cmake --build build/sanitize --parallel 2` — **exit 0**; [final_sanitize_build.json](commands/final_sanitize_build.json).
- `cmake -S . -B build/sanitize -DCMAKE_BUILD_TYPE=Debug -DMAB_ENABLE_SANITIZERS=ON` — **exit 0**; [final_sanitize_configure.json](commands/final_sanitize_configure.json).
- `env -u ASAN_OPTIONS -u LSAN_OPTIONS UBSAN_OPTIONS=halt_on_error=1 ctest --test-dir build/sanitize --output-on-failure -V` — **exit 0**; [final_sanitize_ctest.json](commands/final_sanitize_ctest.json).
- `python3 scripts/run_experiments.py --preset full --run-id phase5_full_20261009T191000587965Z --dry-run` — **exit 0**; [full_dry_run.json](commands/full_dry_run.json).
- `python3 scripts/run_experiments.py --preset full --run-id phase5_full_20261009T191000587965Z` — **exit 0**; [full_pipeline.json](commands/full_pipeline.json).
- `python3 results/raw/orchestration_validation_20261009T191000587965Z/verify_full.py` — **exit 0**; [full_verification.json](commands/full_verification.json).
- `cmake --build build/release --parallel 2` — **exit 0**; [integrated_release_build.json](commands/integrated_release_build.json).
- `cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_SANITIZERS=OFF` — **exit 0**; [integrated_release_configure.json](commands/integrated_release_configure.json).
- `ctest --test-dir build/release --output-on-failure -V` — **exit 0**; [integrated_release_ctest.json](commands/integrated_release_ctest.json).
- `cmake --build build/sanitize --parallel 2` — **exit 0**; [integrated_sanitize_build.json](commands/integrated_sanitize_build.json).
- `cmake -S . -B build/sanitize -DCMAKE_BUILD_TYPE=Debug -DMAB_ENABLE_SANITIZERS=ON` — **exit 0**; [integrated_sanitize_configure.json](commands/integrated_sanitize_configure.json).
- `env -u ASAN_OPTIONS -u LSAN_OPTIONS UBSAN_OPTIONS=halt_on_error=1 ctest --test-dir build/sanitize --output-on-failure -V` — **exit 0**; [integrated_sanitize_ctest.json](commands/integrated_sanitize_ctest.json).
- `cmake --build build/release --parallel 2` — **exit 0**; [reviewed_final_release_build.json](commands/reviewed_final_release_build.json).
- `cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_SANITIZERS=OFF` — **exit 0**; [reviewed_final_release_configure.json](commands/reviewed_final_release_configure.json).
- `ctest --test-dir build/release --output-on-failure -V` — **exit 0**; [reviewed_final_release_ctest.json](commands/reviewed_final_release_ctest.json).
- `cmake --build build/sanitize --parallel 2` — **exit 0**; [reviewed_final_sanitize_build.json](commands/reviewed_final_sanitize_build.json).
- `cmake -S . -B build/sanitize -DCMAKE_BUILD_TYPE=Debug -DMAB_ENABLE_SANITIZERS=ON` — **exit 0**; [reviewed_final_sanitize_configure.json](commands/reviewed_final_sanitize_configure.json).
- `env -u ASAN_OPTIONS -u LSAN_OPTIONS UBSAN_OPTIONS=halt_on_error=1 ctest --test-dir build/sanitize --output-on-failure -V` — **exit 0**; [reviewed_final_sanitize_ctest.json](commands/reviewed_final_sanitize_ctest.json).
- `python3 tests/test_experiments.py build/release` — **exit 0**; [reviewed_python_tests.json](commands/reviewed_python_tests.json).
- `python3 scripts/run_experiments.py --preset smoke --run-id phase5_smoke_20261009T191000587965Z --dry-run` — **exit 0**; [smoke_dry_run.json](commands/smoke_dry_run.json).
- `python3 scripts/run_experiments.py --preset smoke --run-id phase5_smoke_20261009T191000587965Z` — **exit 0**; [smoke_pipeline.json](commands/smoke_pipeline.json).
- `python3 scripts/assess_experiment.py results/raw/phase5_smoke_20261009T191000587965Z --output results/raw/orchestration_validation_20261009T191000587965Z/smoke_runtime_assessment.json` — **exit 0**; [smoke_runtime_assessment.json](commands/smoke_runtime_assessment.json).
- `python3 results/raw/orchestration_validation_20261009T191000587965Z/verify.py` — **exit 0**; [smoke_verification.json](commands/smoke_verification.json).

Additional earlier unwrapped commands: `python3 tests/test_experiments.py build/release` exited 1 (18/19 passed; SIGTERM test timeout, subsequently fixed; initial_python_failure.log and initial_python_result.json). `git status --short` exited 128 (no Git metadata). Both final-review helper errors are documented in FINAL_AUDIT.md; final_review_complete exited 0. No experiment command failed. All final build/test/validation commands passed.
