# Exact commands and safety classifications

Only focused inert Python collections ran. No CTest/native test, discovery, prerequisite/resource, timing, pilot/study or GPU command ran.

record.py executed each listed child argv; JSON retains complete stdout/stderr and actual exit status.

Recorder prefix: `python3 -B results/raw/ctest_hook_repair_20261010T223851377458Z/record.py NAME SAFETY` followed by the exact child command below.

Early/unwrapped shell commands and apply_patch failure disclosure: PRE_RECORDER_COMMANDS.md.


## discovery_callers_final

```sh
rg -n 'select_tests|selected_ctest|pre_discovery_gate|validate_build_tree|show-only=json-v1|non_timing_tests' scripts tests
```

Exit 0; safety `read_only_callsite_inspection`; log `commands/discovery_callers_final.json`. No actual CTest, timing workload or GPU work.


## documentation_patch_state

```sh
python3 -B -c 'from pathlib import Path; p=Path("docs/CTEST_BUILD_GUARD_v1.md"); print("guard document exists:",p.exists()); print(Path("README.md").read_text()[-800:]); print(Path("docs/ROADMAP.md").read_text()[-500:])'
```

Exit 0; safety `read_only_patch_state_inspection`; log `commands/documentation_patch_state.json`. No actual CTest, timing workload or GPU work.


## documentation_scope_inspection

```sh
tail -n 35 README.md docs/ROADMAP.md docs/AUDIT.md
```

Exit 0; safety `read_only_documentation_tail`; log `commands/documentation_scope_inspection.json`. No actual CTest, timing workload or GPU work.


## existing_inert_selection_tests

```sh
env PYTHONDONTWRITEBYTECODE=1 python3 -B results/raw/ctest_hook_repair_20261010T223851377458Z/run_existing_inert_selection_tests.py
```

Exit 0; safety `inspected_selector_class_only_process_launch_blocked`; log `commands/existing_inert_selection_tests.json`. No actual CTest, timing workload or GPU work.


## existing_inert_selection_tests_final

```sh
env PYTHONDONTWRITEBYTECODE=1 python3 -B results/raw/ctest_hook_repair_20261010T223851377458Z/run_existing_inert_selection_tests.py
```

Exit 0; safety `inspected_selector_class_only_process_launch_blocked`; log `commands/existing_inert_selection_tests_final.json`. No actual CTest, timing workload or GPU work.


## final_file_review

```sh
python3 -B results/raw/ctest_hook_repair_20261010T223851377458Z/file_review.py
```

Exit 0; safety `ast_and_diff_capture_only`; log `commands/final_file_review.json`. No actual CTest, timing workload or GPU work.


## final_source_and_document_review

```sh
cat scripts/ctest_build_guard.py scripts/non_timing_tests.py docs/CTEST_BUILD_GUARD_v1.md
```

Exit 0; safety `read_only_changed_source_inspection`; log `commands/final_source_and_document_review.json`. No actual CTest, timing workload or GPU work.


## focused_source_inspection

```sh
cat tests/test_ctest_build_guard.py tests/ctest_fixture.py scripts/ctest_build_guard.py scripts/non_timing_tests.py
```

Exit 0; safety `read_only_source_before_focused_execution`; log `commands/focused_source_inspection.json`. No actual CTest, timing workload or GPU work.


## historical_preservation_method_inspection

```sh
rg -n -A 8 -B 5 'production_headers|production =|production=' results/raw/cpu_gpu_repair_review_20261010T185659333607Z/verify_evidence_v2.py
```

Exit 0; safety `read_only_hash_verifier_source`; log `commands/historical_preservation_method_inspection.json`. No actual CTest, timing workload or GPU work.


## inert_regressions

```sh
env PYTHONDONTWRITEBYTECODE=1 python3 -B tests/test_ctest_build_guard.py -v
```

Exit 1; safety `inert_python_fixtures_all_real_subprocesses_blocked`; log `commands/inert_regressions.json`. No actual CTest, timing workload or GPU work.


## inert_regressions_final

```sh
env PYTHONDONTWRITEBYTECODE=1 python3 -B tests/test_ctest_build_guard.py -v
```

Exit 0; safety `inert_python_fixtures_all_real_subprocesses_blocked`; log `commands/inert_regressions_final.json`. No actual CTest, timing workload or GPU work.


## inert_regressions_reviewed_stack

```sh
env PYTHONDONTWRITEBYTECODE=1 python3 -B tests/test_ctest_build_guard.py -v
```

Exit 0; safety `inert_python_fixtures_all_real_subprocesses_blocked`; log `commands/inert_regressions_reviewed_stack.json`. No actual CTest, timing workload or GPU work.


## inert_regressions_sealed_source

```sh
env PYTHONDONTWRITEBYTECODE=1 python3 -B tests/test_ctest_build_guard.py -v
```

Exit 0; safety `inert_python_fixtures_all_real_subprocesses_blocked`; log `commands/inert_regressions_sealed_source.json`. No actual CTest, timing workload or GPU work.


## inert_regressions_v2

```sh
env PYTHONDONTWRITEBYTECODE=1 python3 -B tests/test_ctest_build_guard.py -v
```

Exit 0; safety `inert_python_fixtures_all_real_subprocesses_blocked`; log `commands/inert_regressions_v2.json`. No actual CTest, timing workload or GPU work.


## metadata_policy_cuda_stack_review

```sh
env PYTHONDONTWRITEBYTECODE=1 python3 -B results/raw/ctest_hook_repair_20261010T223851377458Z/create_reviewed_policy.py
```

Exit 0; safety `static_metadata_parse_and_policy_write_only`; log `commands/metadata_policy_cuda_stack_review.json`. No actual CTest, timing workload or GPU work.


## metadata_policy_review

```sh
env PYTHONDONTWRITEBYTECODE=1 python3 -B results/raw/ctest_hook_repair_20261010T223851377458Z/create_reviewed_policy.py
```

Exit 1; safety `static_metadata_parse_and_policy_write_only`; log `commands/metadata_policy_review.json`. No actual CTest, timing workload or GPU work.


## metadata_policy_review_final

```sh
env PYTHONDONTWRITEBYTECODE=1 python3 -B results/raw/ctest_hook_repair_20261010T223851377458Z/create_reviewed_policy.py
```

Exit 0; safety `static_metadata_parse_and_policy_write_only`; log `commands/metadata_policy_review_final.json`. No actual CTest, timing workload or GPU work.


## preservation_before

```sh
python3 -B results/raw/ctest_hook_repair_20261010T223851377458Z/verify_preservation.py PRESERVATION_BEFORE
```

Exit 0; safety `static_file_hashes_only`; log `commands/preservation_before.json`. No actual CTest, timing workload or GPU work.


## preservation_final_before_audit

```sh
python3 -B results/raw/ctest_hook_repair_20261010T223851377458Z/verify_preservation_v2.py PRESERVATION_FINAL
```

Exit 0; safety `file_hashes_and_historical_seals_only`; log `commands/preservation_final_before_audit.json`. No actual CTest, timing workload or GPU work.


## preservation_reviewed_source

```sh
python3 -B results/raw/ctest_hook_repair_20261010T223851377458Z/verify_preservation_v2.py PRESERVATION_REVIEWED_SOURCE
```

Exit 0; safety `file_hashes_and_historical_seals_only`; log `commands/preservation_reviewed_source.json`. No actual CTest, timing workload or GPU work.


## retained_ctest_paths

```sh
python3 -B -c 'from pathlib import Path; print("\n".join(str(p) for p in Path("results/raw").rglob("*") if p.is_file() and ("ctest" in p.name.lower() or "discovery" in p.name.lower())))'
```

Exit 0; safety `read_only_retained_evidence_listing`; log `commands/retained_ctest_paths.json`. No actual CTest, timing workload or GPU work.


## retained_cuda_metadata_inspection

```sh
python3 -B -
```

Exit 0; safety `read_only_historical_metadata_source_comparison`; log `commands/retained_cuda_metadata_inspection.json`. No actual CTest, timing workload or GPU work.


## retained_inert_plan_and_rejection

```sh
env PYTHONDONTWRITEBYTECODE=1 python3 -B results/raw/ctest_hook_repair_20261010T223851377458Z/offline_plan_proof.py
```

Exit 0; safety `inert_metadata_only_real_process_launch_blocked`; log `commands/retained_inert_plan_and_rejection.json`. No actual CTest, timing workload or GPU work.


## reviewed_source_renewal

```sh
env PYTHONDONTWRITEBYTECODE=1 python3 -B results/raw/ctest_hook_repair_20261010T223851377458Z/repin_reviewed_source.py SOURCE_REVIEW.json
```

Exit 0; safety `static_ast_hashes_and_explicit_policy_write_only`; log `commands/reviewed_source_renewal.json`. No actual CTest, timing workload or GPU work.


## reviewed_source_renewal_final

```sh
env PYTHONDONTWRITEBYTECODE=1 python3 -B results/raw/ctest_hook_repair_20261010T223851377458Z/repin_reviewed_source.py SOURCE_REVIEW_FINAL.json
```

Exit 0; safety `static_ast_hashes_and_explicit_policy_write_only`; log `commands/reviewed_source_renewal_final.json`. No actual CTest, timing workload or GPU work.


## reviewed_source_renewal_v2

```sh
env PYTHONDONTWRITEBYTECODE=1 python3 -B results/raw/ctest_hook_repair_20261010T223851377458Z/repin_reviewed_source.py SOURCE_REVIEW_V2.json
```

Exit 0; safety `static_ast_hashes_and_explicit_policy_write_only`; log `commands/reviewed_source_renewal_v2.json`. No actual CTest, timing workload or GPU work.


## reviewed_source_renewal_v3

```sh
env PYTHONDONTWRITEBYTECODE=1 python3 -B results/raw/ctest_hook_repair_20261010T223851377458Z/repin_reviewed_source.py SOURCE_REVIEW_V3.json
```

Exit 0; safety `static_ast_hashes_and_explicit_policy_write_only`; log `commands/reviewed_source_renewal_v3.json`. No actual CTest, timing workload or GPU work.


## reviewed_source_renewal_v4

```sh
env PYTHONDONTWRITEBYTECODE=1 python3 -B results/raw/ctest_hook_repair_20261010T223851377458Z/repin_reviewed_source.py SOURCE_REVIEW_V4.json
```

Exit 0; safety `static_ast_hashes_and_explicit_policy_write_only`; log `commands/reviewed_source_renewal_v4.json`. No actual CTest, timing workload or GPU work.


## Final sealing

```sh
python3 -B results/raw/ctest_hook_repair_20261010T223851377458Z/seal_repair.py
```

Exit 0 on successful completion; safety: file hashes, retained-log checks and new evidence writes only. This terminal command is not wrapped by record.py; FINAL_INTEGRITY.json records its completed assertions.
