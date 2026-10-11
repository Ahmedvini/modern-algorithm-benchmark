# Repair command ledger

Exact validation argv, exit codes and safety classifications follow. Full stdout/stderr and timestamps are retained in commands/*.json.

## comparison_synthetic_regressions

```sh
env PYTHONDONTWRITEBYTECODE=1 python3 -B tests/test_cpu_gpu_comparison.py build/cpu_gpu_full_tooling_20261010T121208603276Z/release/comparison_input
```

Exit: 0. Safety: `synthetic_only_small_untimed_input_generation_no_gpu`. Log: `commands/comparison_synthetic_regressions.json`.

## ctest_discovery

```sh
ctest --test-dir results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/discovery -N --show-only=json-v1
```

Exit: 0. Safety: `discovery_only_N_no_timing_no_gpu`. Log: `commands/ctest_discovery.json`.

## exact_full_matrix_reproducer

```sh
env PYTHONDONTWRITEBYTECODE=1 python3 -B results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/reproducer.py
```

Exit: 0. Safety: `synthetic_only_no_sorting_no_gpu`. Log: `commands/exact_full_matrix_reproducer.json`.

## finalize_repair

```sh
env PYTHONDONTWRITEBYTECODE=1 python3 -B results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/finalize_repair.py
```

Exit: 0. Safety: `static_hash_audit_sealing_no_timing_no_gpu`. Log: `commands/finalize_repair.json`.

## focused_regressions

```sh
env PYTHONDONTWRITEBYTECODE=1 python3 -B tests/test_cpu_gpu_safety.py -v
```

Exit: 1. Safety: `synthetic_and_static_no_timing_no_gpu`. Log: `commands/focused_regressions.json`.

## focused_regressions_final

```sh
env PYTHONDONTWRITEBYTECODE=1 python3 -B tests/test_cpu_gpu_safety.py -v
```

Exit: 0. Safety: `synthetic_only_no_timing_no_gpu`. Log: `commands/focused_regressions_final.json`.

## git_status

```sh
git status --short --branch
```

Exit: 128. Safety: `read_only_metadata`. Log: `commands/git_status.json`.

## integrity_after

```sh
env PYTHONDONTWRITEBYTECODE=1 python3 -B results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/verify_integrity.py
```

Exit: 0. Safety: `read_only_hash_verification_no_timing_no_gpu`. Log: `commands/integrity_after.json`.

## pilot_read_only_regeneration

```sh
env PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/analyze_cpu_gpu.py results/raw/cpu_gpu_pilot_20261010T001232473460Z/remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3 --output results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/PILOT_REANALYSIS.json
```

Exit: 0. Safety: `read_only_existing_results_analysis_no_timing_no_gpu`. Log: `commands/pilot_read_only_regeneration.json`.

## prepare_selection

```sh
env PYTHONDONTWRITEBYTECODE=1 python3 -B results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/prepare_selection.py
```

Exit: 0. Safety: `static_no_timing_no_gpu`. Log: `commands/prepare_selection.json`.

## selector_plan

```sh
env PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/non_timing_tests.py --build-dir build/cpu_gpu_full_tooling_20261010T121208603276Z/release --discovery-json results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/CTEST_DISCOVERY.json --output results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/SELECTED_TESTS.json
```

Exit: 0. Safety: `static_selection_no_tests_no_gpu`. Log: `commands/selector_plan.json`.

## selector_plan_final

```sh
env PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/non_timing_tests.py --build-dir build/cpu_gpu_full_tooling_20261010T121208603276Z/release --discovery-json results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/CTEST_DISCOVERY.json --output results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/SELECTED_TESTS_FINAL.json
```

Exit: 0. Safety: `discovery_only`. Log: `commands/selector_plan_final.json`.

## static_review

```sh
env PYTHONDONTWRITEBYTECODE=1 python3 -B results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/static_review.py
```

Exit: 0. Safety: `static_syntax_provenance_and_read_only_summary_comparison`. Log: `commands/static_review.json`.

## Inspection and preparation

Read-only pwd/cat/sed/rg/file-list inspections covered instructions, latest review, frozen artifacts, pilot/workspace evidence, CMake and test/implementation files. One initial rg referenced nonexistent tests/test_capture_environment.py and exited2; tests/test_environment.py was inspected instead. Inspection output is in the terminal and is not represented as retained subprocess logs. No measurement code was executed by these reads.

New snapshots/scripts were created exclusively, and source edits used apply_patch. prepare_selection.py created reviewed metadata and a byte-exact CTest discovery-file copy. CTest discovery used -N only, with unchanged absolute commands, avoiding writes to old build logs. attempt1/ preserves source/manifest before the compatibility correction. An attempted audit-generation heredoc failed with a quoting SyntaxError, followed by an absent-file error (exit2); no final audit/evidence file was created by that failed command. It was corrected using apply_patch. This preparation failure is not a validation pass.

No prerequisite validator, selected/broad CTest, fresh build, GPU command, timing test, pilot or study ran. Synthetic interrupt/failure/completion text comes from doubles.
