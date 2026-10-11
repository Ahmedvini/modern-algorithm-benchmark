# Independent review commands

No listed command executes tests, CTest, timing workloads, GPU work, prerequisites or fresh resource checks. Subprocess use in the recorder launches only the read-only inspections or offline review scripts listed below. Repository subprocess execution is blocked inside the pure-function review scripts.

## analyzer_callers_read

```sh
rg -n 'analyze_cpu_gpu|allow_synthetic|validate_study_metadata|validate_retained_source|selected_ctest|non_timing_tests' scripts tests CMakeLists.txt
```

Exit 0; safety `read_only_source_inspection`; full output `commands/analyzer_callers_read.json`.

## analyzer_entry_read

```sh
sed -n 1,150p scripts/analyze_cpu_gpu.py
```

Exit 0; safety `read_only_source_inspection`; full output `commands/analyzer_entry_read.json`.

## analyzer_read

```sh
cat scripts/analyze_cpu_gpu.py
```

Exit 0; safety `read_only_source_inspection`; full output `commands/analyzer_read.json`.

## cmake_read

```sh
cat CMakeLists.txt cmake/cuda.cmake
```

Exit 0; safety `read_only_source_inspection`; full output `commands/cmake_read.json`.

## comparison_tests_read

```sh
cat tests/test_cpu_gpu_comparison.py
```

Exit 0; safety `read_only_source_inspection`; full output `commands/comparison_tests_read.json`.

## compatibility_correction_read

```sh
diff -u results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/attempt1/scripts/cpu_gpu_provenance.py scripts/cpu_gpu_provenance.py
```

Exit 1; safety `read_only_diff_expected_exit_one`; full output `commands/compatibility_correction_read.json`.

## ctest_hook_docs

```sh
cat /usr/share/cmake-3.28/Help/variable/CTEST_CUSTOM_PRE_TEST.rst /usr/share/cmake-3.28/Help/variable/CTEST_CUSTOM_POST_TEST.rst /usr/share/cmake-3.28/Help/command/ctest_read_custom_files.rst /usr/share/cmake-3.28/Help/prop_dir/TEST_INCLUDE_FILES.rst /usr/share/cmake-3.28/Help/prop_dir/TEST_INCLUDE_FILE.rst
```

Exit 0; safety `read_only_installed_documentation`; full output `commands/ctest_hook_docs.json`.

## cuda_mock_tests_read

```sh
cat tests/test_cuda_preflight.py tests/test_cuda_sort_handoff.py
```

Exit 0; safety `read_only_source_inspection`; full output `commands/cuda_mock_tests_read.json`.

## datasets_test_read

```sh
cat tests/test_datasets.cpp
```

Exit 0; safety `read_only_source_inspection`; full output `commands/datasets_test_read.json`.

## evidence_verification

```sh
python3 -B results/raw/cpu_gpu_repair_review_20261010T185659333607Z/verify_evidence.py
```

Exit 1; safety `file_hashes_and_retained_log_inspection_only`; full output `commands/evidence_verification.json`.

## evidence_verification_v2

```sh
python3 -B results/raw/cpu_gpu_repair_review_20261010T185659333607Z/verify_evidence_v2.py
```

Exit 0; safety `file_hashes_and_retained_log_inspection_only`; full output `commands/evidence_verification_v2.json`.

## hook_metadata_review

```sh
env PYTHONDONTWRITEBYTECODE=1 python3 -B results/raw/cpu_gpu_repair_review_20261010T185659333607Z/hook_metadata_review.py
```

Exit 0; safety `inert_metadata_only_subprocesses_blocked`; full output `commands/hook_metadata_review.json`.

## hooks_search

```sh
rg -n 'CTEST_CUSTOM_PRE_TEST|CTEST_CUSTOM_POST_TEST|CTEST_TEST_ARGS|TEST_INCLUDE_FILES|TEST_INCLUDE_FILE|execute_process|add_custom_command|add_custom_target|CMAKE_PROJECT_INCLUDE|CMAKE_TOOLCHAIN_FILE' CMakeLists.txt cmake scripts/non_timing_tests.py scripts/validate_cpu_gpu_pilot.py /usr/share/cmake-3.28/Help/variable/CTEST_CUSTOM_PRE_TEST.rst /usr/share/cmake-3.28/Help/variable/CTEST_CUSTOM_POST_TEST.rst /usr/share/cmake-3.28/Help/command/ctest_read_custom_files.rst
```

Exit 0; safety `read_only_source_and_installed_documentation`; full output `commands/hooks_search.json`.

## implementation_read

```sh
sed -n 1,260p scripts/non_timing_tests.py
```

Exit 0; safety `read_only_source_inspection`; full output `commands/implementation_read.json`.

## metadata_guard_lines

```sh
nl -ba scripts/non_timing_tests.py
```

Exit 0; safety `read_only_numbered_source_inspection`; full output `commands/metadata_guard_lines.json`.

## offline_path_review

```sh
env PYTHONDONTWRITEBYTECODE=1 python3 -B results/raw/cpu_gpu_repair_review_20261010T185659333607Z/offline_path_review.py
```

Exit 0; safety `pure_metadata_validation_only_subprocesses_blocked`; full output `commands/offline_path_review.json`.

## pilot_processed_paths

```sh
rg --files results/processed/cpu_gpu_pilot_20261010T001232473460Z
```

Exit 0; safety `read_only_file_listing`; full output `commands/pilot_processed_paths.json`.

## pilot_summary_bytes

```sh
python3 -B -c 'import hashlib,json; from pathlib import Path; base=Path("results/raw/cpu_gpu_repair_review_20261010T185659333607Z"); root=Path("results/processed/cpu_gpu_pilot_20261010T001232473460Z"); paths=[root/"summary.json",root/"summary_regenerated.json",root/"reviewed/summary.json",Path("results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/PILOT_REANALYSIS.json"),Path("results/raw/cpu_gpu_tooling_review_20261010T125855526277Z/PILOT_REANALYSIS.json")]; digest={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}; assert len(set(digest.values()))==1; report=dict(byte_identical=all(p.read_bytes()==paths[0].read_bytes() for p in paths),sha256=digest,regeneration_executed=False); stream=(base/"PILOT_SUMMARY_BYTES.json").open("x"); json.dump(report,stream,indent=2,sort_keys=True); stream.write("\n"); stream.close(); print(json.dumps(report,indent=2,sort_keys=True))'
```

Exit 0; safety `read_only_byte_comparison_no_regeneration`; full output `commands/pilot_summary_bytes.json`.

## prepared_analysis_tests_read

```sh
cat tests/test_cuda_benchmark.py scripts/analyze_cuda_results.py scripts/analyze_results.py
```

Exit 0; safety `read_only_source_inspection`; full output `commands/prepared_analysis_tests_read.json`.

## prior_failure_log_read

```sh
cat results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/commands/focused_regressions.json results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/commands/focused_regressions_final.json
```

Exit 0; safety `read_only_retained_evidence`; full output `commands/prior_failure_log_read.json`.

## project_status_docs_read

```sh
tail -n 100 README.md docs/ROADMAP.md docs/EXPERIMENT_PROTOCOL.md docs/CPU_GPU_SAFETY_REPAIR_v1.md
```

Exit 0; safety `read_only_documentation_inspection`; full output `commands/project_status_docs_read.json`.

## protocol_and_runner_read

```sh
sed -n 1,180p scripts/cpu_gpu_protocol.py
```

Exit 0; safety `read_only_source_inspection`; full output `commands/protocol_and_runner_read.json`.

## provenance_read

```sh
cat scripts/cpu_gpu_provenance.py scripts/validate_cpu_gpu_pilot.py
```

Exit 0; safety `read_only_source_inspection`; full output `commands/provenance_read.json`.

## python_tests_read

```sh
cat tests/test_environment.py tests/test_cli.py tests/test_metrics_cli.py
```

Exit 0; safety `read_only_source_inspection`; full output `commands/python_tests_read.json`.

## runner_commands_read

```sh
sed -n 1,180p scripts/run_cpu_gpu_pilot.py
```

Exit 0; safety `read_only_source_inspection`; full output `commands/runner_commands_read.json`.

## safety_tests_read

```sh
cat tests/test_cpu_gpu_safety.py
```

Exit 0; safety `read_only_source_inspection`; full output `commands/safety_tests_read.json`.

## seal_review

```sh
python3 -B results/raw/cpu_gpu_repair_review_20261010T185659333607Z/seal_review.py
```

Exit 0; safety `hash_verification_and_evidence_sealing_only`; full output `commands/seal_review.json`.

## selected_cpp_tests_read

```sh
cat tests/test_baselines.cpp tests/test_mergesort.cpp tests/test_memory.cpp tests/test_comparisons.cpp tests/test_searching.cpp
```

Exit 0; safety `read_only_source_inspection`; full output `commands/selected_cpp_tests_read.json`.

## selected_cpp_tests_read_more

```sh
cat tests/test_quicksort.cpp tests/test_pdqsort.cpp tests/test_timsort.cpp tests/test_radixsort.cpp tests/test_structures.cpp
```

Exit 0; safety `read_only_source_inspection`; full output `commands/selected_cpp_tests_read_more.json`.

## selected_helpers_read

```sh
cat tests/test_integer_sorts.hpp tests/test_support.hpp src/main.cpp src/benchmark/metrics_main.cpp src/benchmark/comparison_input_main.cpp scripts/capture_environment.py
```

Exit 0; safety `read_only_source_inspection`; full output `commands/selected_helpers_read.json`.

## static_inventory

```sh
python3 -B results/raw/cpu_gpu_repair_review_20261010T185659333607Z/static_inventory.py
```

Exit 0; safety `ast_text_and_file_hashes_only`; full output `commands/static_inventory.json`.

## timing_path_read

```sh
sed -n 85,125p tests/test_parallel_mergesort.cpp
```

Exit 0; safety `read_only_source_inspection`; full output `commands/timing_path_read.json`.

## Initial inspection and evidence creation

Before the recorder existed, the exact read-only shell command was:

```sh
pwd
cat AGENTS.md
cat results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/FINAL_AUDIT.md
cat results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/COMMANDS.md
cat results/raw/cpu_gpu_tooling_review_20261010T125855526277Z/FINAL_AUDIT.md
cat results/raw/cpu_gpu_tooling_review_20261010T125855526277Z/COMMANDS.md
```

Exit0, source/evidence reads only. Integrity manifests were parsed/read by verify_evidence scripts. A Python3 -B stdin bootstrap hashed all11391 pre-existing results and project files and exclusively created this timestamped directory, START_SNAPSHOT.json and record.py (exit0). Evidence-only apply_patch and Python exclusive-file writes created the review scripts, inert fixtures and corrected verifier v2. No historical script was executed in place. Bootstrap/initial read outputs were observed in the terminal, not copied into fabricated subprocess logs. No additional experiment or tool command was run.
