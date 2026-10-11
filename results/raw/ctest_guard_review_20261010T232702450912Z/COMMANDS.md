# Independent review commands and exit statuses

Only static inspections and evidence writes ran. No repository Python module, selector, guard, test or validation entry point was executed.

Recorder invocation: `python3 -B results/raw/ctest_guard_review_20261010T232702450912Z/record.py NAME SAFETY CHILD_ARGV...`. Each JSON contains the exact child argv/cwd, stdout, stderr, safety classification and observed exit code.

Early unwrapped commands and evidence-only tool writes: EARLY_COMMANDS.md.


## audit_and_current_scope

```sh
cat results/raw/ctest_hook_repair_20261010T223851377458Z/FINAL_AUDIT.md results/raw/cpu_gpu_repair_review_20261010T185659333607Z/FINAL_AUDIT.md results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/FINAL_AUDIT.md
```

Exit 0; safety: read-only audit/documentation text; no workloads. Full output: `commands/audit_and_current_scope.json`.


## boundary_review

```sh
cat scripts/ctest_build_guard.py scripts/non_timing_tests.py docs/CTEST_BUILD_GUARD_v1.md
```

Exit 0; safety: static source only; no discovery or helpers invoked. Full output: `commands/boundary_review.json`.


## callers_and_hooks

```sh
rg -n 'selected_ctest|select_tests|pre_discovery_gate|validate_build_tree|show-only|prerequisites-only|CTestCustom|CTestTestfile|TEST_INCLUDE_FILES|ctest' scripts CMakeLists.txt cmake
```

Exit 0; safety: read_only_callsite_search. Full output: `commands/callers_and_hooks.json`.


## changed_framework_fixture

```sh
sed -n 425,505p tests/test_cpu_gpu_comparison.py
```

Exit 0; safety: static text of mocked framework case; test not run. Full output: `commands/changed_framework_fixture.json`.


## current_project_scope

```sh
tail -n 85 README.md docs/ROADMAP.md docs/EXPERIMENT_PROTOCOL.md
```

Exit 0; safety: read-only project documentation; no commands embedded in docs executed. Full output: `commands/current_project_scope.json`.


## cwd_and_entrypoint_trace

```sh
nl -ba scripts/run_cpu_gpu_pilot.py
```

Exit 0; safety: static source/command inspection only; no callbacks, imports, or workloads executed. Full output: `commands/cwd_and_entrypoint_trace.json`.


## declaration_sources

```sh
cat CMakeLists.txt cmake/cuda.cmake
```

Exit 0; safety: source_read_only. Full output: `commands/declaration_sources.json`.


## evidence_patch_rejection_state

```sh
cat results/raw/ctest_guard_review_20261010T232702450912Z/EARLY_COMMANDS.md
```

Exit 0; safety: read-only inspection after rejected evidence-only patch; no project files involved. Full output: `commands/evidence_patch_rejection_state.json`.


## execution_wrappers

```sh
sed -n 1,165p scripts/run_cpu_gpu_pilot.py
```

Exit 0; safety: source_read_only. Full output: `commands/execution_wrappers.json`.


## fixture_and_test_wrapper

```sh
cat tests/ctest_fixture.py results/raw/ctest_hook_repair_20261010T223851377458Z/run_existing_inert_selection_tests.py
```

Exit 0; safety: source_inspection_only. Full output: `commands/fixture_and_test_wrapper.json`.


## focused_test_source

```sh
cat tests/test_ctest_build_guard.py tests/ctest_fixture.py results/raw/ctest_hook_repair_20261010T223851377458Z/run_existing_inert_selection_tests.py
```

Exit 0; safety: static test/source text only; tests not run. Full output: `commands/focused_test_source.json`.


## guard_contract

```sh
cat docs/CTEST_BUILD_GUARD_v1.md
```

Exit 0; safety: source_read_only. Full output: `commands/guard_contract.json`.


## guard_regressions

```sh
nl -ba tests/test_ctest_build_guard.py
```

Exit 0; safety: source_inspection_only. Full output: `commands/guard_regressions.json`.


## import_and_existing_selector_tests

```sh
sed -n 1,245p tests/test_cpu_gpu_safety.py
```

Exit 0; safety: static imports/tests only; module bodies not executed. Full output: `commands/import_and_existing_selector_tests.json`.


## independent_hash_verification

```sh
python3 -B results/raw/ctest_guard_review_20261010T232702450912Z/verify_evidence.py
```

Exit 0; safety: stdlib-only reads and SHA-256 comparisons; writes only new review evidence; no repo code invoked. Full output: `commands/independent_hash_verification.json`.


## installed_cmake_contract

```sh
cat /usr/share/cmake-3.28/Help/command/ctest_read_custom_files.rst /usr/share/cmake-3.28/Help/variable/CTEST_CUSTOM_PRE_TEST.rst /usr/share/cmake-3.28/Help/variable/CTEST_CUSTOM_POST_TEST.rst /usr/share/cmake-3.28/Help/prop_dir/TEST_INCLUDE_FILES.rst /usr/share/cmake-3.28/Help/prop_dir/TEST_INCLUDE_FILE.rst
```

Exit 0; safety: read-only installed primary documentation; CMake and CTest binaries not invoked. Full output: `commands/installed_cmake_contract.json`.


## legacy_validation_paths

```sh
rg -n 'ctest|cwd=|def invoke|def call|selected_ctest|build_dir' scripts/non_timing_tests.py scripts/ctest_build_guard.py scripts/run_cpu_gpu_pilot.py scripts/validate_cpu_gpu_pilot.py scripts/validate_cuda_sort.py scripts/validate_cuda_timing.py tests/test_ctest_build_guard.py tests/test_cpu_gpu_safety.py
```

Exit 0; safety: read-only source search; no validation commands invoked. Full output: `commands/legacy_validation_paths.json`.


## prerequisite_paths

```sh
nl -ba scripts/validate_cpu_gpu_pilot.py
```

Exit 0; safety: static runner/source text; no runner or child launched. Full output: `commands/prerequisite_paths.json`.


## prerequisites

```sh
nl -ba scripts/validate_cpu_gpu_pilot.py
```

Exit 0; safety: numbered_source_read_only. Full output: `commands/prerequisites.json`.


## preservation_logic

```sh
cat results/raw/ctest_hook_repair_20261010T223851377458Z/verify_preservation_v2.py results/raw/ctest_hook_repair_20261010T223851377458Z/seal_repair.py results/raw/ctest_hook_repair_20261010T223851377458Z/COMMANDS.md results/raw/ctest_hook_repair_20261010T223851377458Z/PRE_RECORDER_COMMANDS.md
```

Exit 0; safety: static text only; reviewed script not executed. Full output: `commands/preservation_logic.json`.


## protocol_helpers

```sh
cat scripts/cpu_gpu_protocol.py scripts/cpu_gpu_provenance.py
```

Exit 0; safety: source_read_only. Full output: `commands/protocol_helpers.json`.


## related_validators

```sh
cat scripts/validate_cuda_sort.py scripts/validate_cuda_timing.py
```

Exit 0; safety: source_read_only. Full output: `commands/related_validators.json`.


## retained_inventory

```sh
python3 -B -c 'import json;from pathlib import Path; b=Path("results/raw/ctest_hook_repair_20261010T223851377458Z");print(sorted(p.name for p in b.iterdir()));
for name in ["BEFORE.json","FINAL_INTEGRITY.json","FILE_REVIEW.json","PRESERVATION_FINAL.json"]:
 p=b/name
 if p.exists():
  d=json.loads(p.read_text());print(name,[(k,len(v) if isinstance(v,(list,dict)) else v) for k,v in d.items()]);print(str(d)[:2500] if name=="FILE_REVIEW.json" else "")
for p in [Path("docs/studies/cpu_gpu_comparison_v1.freeze.json"),Path("docs/NON_TIMING_TEST_SELECTION_v1.json")]:
 d=json.loads(p.read_text());print(str(p),list(d));print(str(d)[:1800])'
```

Exit 0; safety: read-only JSON inspection; no repository imports or execution. Full output: `commands/retained_inventory.json`.


## retained_regression_logs

```sh
python3 -B -c 'import json;from pathlib import Path;b=Path("results/raw/ctest_hook_repair_20261010T223851377458Z");
for name in ["metadata_policy_review","inert_regressions","inert_regressions_v2","inert_regressions_sealed_source","existing_inert_selection_tests_final","retained_cuda_metadata_inspection"]:
 d=json.loads((b/"commands"/(name+".json")).read_text());print("LOG",name,"ARGV",d["argv"],"EXIT",d["exit_code"]);print(d.get("stdout",""));print(d.get("stderr",""))'
```

Exit 0; safety: read-only JSON log rendering; no tests executed. Full output: `commands/retained_regression_logs.json`.


## selector

```sh
nl -ba scripts/non_timing_tests.py
```

Exit 0; safety: numbered_source_read_only. Full output: `commands/selector.json`.


## selector_regressions

```sh
nl -ba tests/test_cpu_gpu_safety.py
```

Exit 0; safety: source_inspection_only. Full output: `commands/selector_regressions.json`.


## shared_guard

```sh
nl -ba scripts/ctest_build_guard.py
```

Exit 0; safety: numbered_source_read_only. Full output: `commands/shared_guard.json`.


## static_test_and_control_flow_review

```sh
python3 -B results/raw/ctest_guard_review_20261010T232702450912Z/static_review.py
```

Exit 0; safety: AST/retained-log comparison and pure path arithmetic only; no test/helper execution. Full output: `commands/static_test_and_control_flow_review.json`.


## Final evidence seal

```sh
python3 -B results/raw/ctest_guard_review_20261010T232702450912Z/seal_review.py
```

Exit0 on successful completion; unwrapped terminal command. Only file hashes, retained log checks and exclusive new evidence writes; no workloads.
