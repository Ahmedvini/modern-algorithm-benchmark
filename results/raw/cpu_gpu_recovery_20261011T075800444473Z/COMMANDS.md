# Commands and exit statuses

Repository cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark

Recovery scope: source/policy repairs, focused inert Python regressions, read-only identity/log checks and Colab CLI metadata. No CTest discovery/execution, configure/build, GPU workload/resource probe, benchmark, warmup, pilot or measured trial.

## Initial unwrapped read-only inspection (each shell exit0)

Exact inspection command groups, before the recorder was established:
```sh
pwd
rg --files -g 'AGENTS.md' -g '*record.py' -g '*cpu_gpu*' -g '*validation_policy*' scripts tests docs results/raw/cpu_gpu_final_preflight_20261011T074147349659Z
cat AGENTS.md
cat results/raw/cpu_gpu_final_preflight_20261011T074147349659Z/FINAL_AUDIT.md
cat results/raw/cpu_gpu_final_preflight_20261011T074147349659Z/COMMANDS.md
cat results/raw/cpu_gpu_final_preflight_20261011T074147349659Z/FINAL_INTEGRITY.json
cat results/raw/cpu_gpu_final_preflight_20261011T074147349659Z/record.py
cat scripts/cpu_gpu_protocol.py
cat scripts/cpu_gpu_provenance.py
cat docs/CPU_GPU_VALIDATION_POLICY_v2.json
cat scripts/cpu_gpu_validation_policy.py
sed -n '1,210p' scripts/run_cpu_gpu_pilot.py
sed -n '1,150p' scripts/analyze_cpu_gpu.py
cat scripts/run_cpu_gpu_study.py
cat results/raw/cpu_gpu_final_preflight_20261011T074147349659Z/finalize_review.py
cat docs/CPU_GPU_COMPARISON_PROTOCOL_v1.md
cat docs/CPU_GPU_VALIDATION_POLICY_v2.md
cat tests/test_validation_policy.py
rg -n 'BUILD_COMPLETE|input_tool_sha256|binary_sha256|comparison_input' scripts/validate_cpu_gpu_pilot.py results/raw/bounded_resume_20261011T024034091796Z/*.py
cat README.md
cat docs/ROADMAP.md
cat docs/EXPERIMENT_PROTOCOL.md
```

Some large combined outputs were truncated at the tool display. Targeted source reads and the complete retained inspection leaf provide the policy/runner evidence. No truncated display is treated as proof of reading omitted source.

Bootstrap: `python3 -B -` used hashlib/json/pathlib to verify23 prior seal members, all original188 project files,80 protected files,65 build metadata and prior historical hashes; captured all12,261 current historical result hashes, created this unique directory and copied record.py. BEFORE.json retains exact maps. Exit0. No workload. Initial current root/AGENTS inspection also used only cat/pwd.

## colab_help.json

- Exit: 0
- Scope: documented authentication workflow inspection
- UTC: 2026-10-11T07:58:07.109544+00:00
- cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark
- Full output: [colab_help.json](colab_help.json)

```sh
colab --help
```

## colab_version.json

- Exit: 0
- Scope: CLI version only; no remote workload
- UTC: 2026-10-11T08:11:32.141526+00:00
- cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark
- Full output: [colab_version.json](colab_version.json)

```sh
colab version
```

## existing_validation_policy_tests.json

- Exit: 0
- Scope: Existing nine synthetic/static classification tests; no subprocess or GPU/timing code
- UTC: 2026-10-11T08:09:25.343217+00:00
- cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark
- Full output: [existing_validation_policy_tests.json](existing_validation_policy_tests.json)

```sh
python3 -B tests/test_validation_policy.py -v
```

## final_identity_hardening_tests.json

- Exit: 0
- Scope: 26 inert tests after strict schema/import safety review; no workload
- UTC: 2026-10-11T08:12:27.591778+00:00
- cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark
- Full output: [final_identity_hardening_tests.json](final_identity_hardening_tests.json)

```sh
python3 -B tests/test_framework_compatibility.py -v
```

## focused_compatibility_tests.json

- Exit: 1
- Scope: Inert provenance/identity regressions; subprocess and runner invocation blocked; no CTest/GPU/timing workloads
- UTC: 2026-10-11T08:04:49.373655+00:00
- cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark
- Full output: [focused_compatibility_tests.json](focused_compatibility_tests.json)

```sh
python3 -B tests/test_framework_compatibility.py -v
```

## focused_compatibility_tests_final.json

- Exit: 0
- Scope: 26 inert provenance/identity regressions; all external execution blocked
- UTC: 2026-10-11T08:09:23.101243+00:00
- cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark
- Full output: [focused_compatibility_tests_final.json](focused_compatibility_tests_final.json)

```sh
python3 -B tests/test_framework_compatibility.py -v
```

## focused_compatibility_tests_v2.json

- Exit: 0
- Scope: Inert regressions after fixture-only duplicate missing keyword correction; external execution blocked
- UTC: 2026-10-11T08:05:45.623945+00:00
- cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark
- Full output: [focused_compatibility_tests_v2.json](focused_compatibility_tests_v2.json)

```sh
python3 -B tests/test_framework_compatibility.py -v
```

## focused_compatibility_tests_v3.json

- Exit: 0
- Scope: Inert regressions with explicit current GPU command/binary binding; no external execution
- UTC: 2026-10-11T08:07:17.957497+00:00
- cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark
- Full output: [focused_compatibility_tests_v3.json](focused_compatibility_tests_v3.json)

```sh
python3 -B tests/test_framework_compatibility.py -v
```

## git_identity.json

- Exit: 128
- Scope: inspection
- UTC: 2026-10-11T07:58:07.107016+00:00
- cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark
- Full output: [git_identity.json](git_identity.json)

```sh
git status --short --branch
```

## offline_verification.json

- Exit: 0
- Scope: Offline AST, frozen provenance, static 19-name selection, intentional source-snapshot rejection and retained log review; no discovery/workload
- UTC: 2026-10-11T08:13:52.177704+00:00
- cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark
- Full output: [offline_verification.json](offline_verification.json)

```sh
python3 -B results/raw/cpu_gpu_recovery_20261011T075800444473Z/verify_recovery.py
```

## session_auth_attempt.json

- Exit: 0
- Scope: documented session connection; no GPU or benchmark
- UTC: 2026-10-11T07:58:07.106009+00:00
- cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark
- Full output: [session_auth_attempt.json](session_auth_attempt.json)

```sh
colab sessions
```

## targeted_policy_inspection.json

- Exit: 0
- Scope: read-only implementation and protocol
- UTC: 2026-10-11T07:58:07.108188+00:00
- cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark
- Full output: [targeted_policy_inspection.json](targeted_policy_inspection.json)

```sh
python3 -B -c 'from pathlib import Path
for n in ['"'"'docs/CPU_GPU_COMPARISON_PROTOCOL_v1.md'"'"','"'"'docs/CPU_GPU_VALIDATION_POLICY_v2.md'"'"','"'"'tests/test_validation_policy.py'"'"','"'"'scripts/validate_cpu_gpu_pilot.py'"'"']:
 print('"'"'\nFILE '"'"'+n+'"'"'\n'"'"'+Path(n).read_text())'
```

## Other read-only inspection and evidence assembly (exit0)

Python here-doc inspections read BUILD_COMPLETE.json, CORRECTNESS_BUNDLE.json, VALIDATION_CONTEXT.json, and baseline manifest field counts; inspected the retained pilot cuda_ctest.json lines containing Ran14/OK/framework names. No modules/test functions were executed in those inspections.

```sh
sed -n '1,180p' tests/test_cpu_gpu_safety.py
sed -n '1,120p' tests/fixtures/cpu_gpu_provenance_reproducer.py
sed -n '350,470p' tests/test_cpu_gpu_comparison.py
sed -n '1,130p' scripts/non_timing_tests.py
cat docs/CPU_GPU_DRIVER_REVIEW_v1.json
sed -n '205,270p' scripts/run_cpu_gpu_pilot.py
rg -n 'validate_retained_source|source_review|verify_source_extension' scripts/analyze_cpu_gpu.py scripts/run_cpu_gpu_pilot.py
sed -n '1,100p' scripts/validate_cuda_sort.py
cat results/raw/cpu_gpu_final_preflight_20261011T074147349659Z/COMMANDS.md
cat results/raw/cpu_gpu_recovery_20261011T075800444473Z/CHANGES.diff
cat scripts/cpu_gpu_build_identity.py
cat scripts/cpu_gpu_framework_compatibility.py
```

Evidence assembly used Python file I/O to save six original sources, construct the pinned new policy JSON, and later read (without extracting) the original run_cpu_gpu_study.py member from the sealed reviewed_source_v2.tar.gz. Its bytes matched BEFORE.json before being saved as a seventh original. difflib generated CHANGES.diff/CHANGE_INVENTORY.json. All these here-doc commands exited0. Source edits used apply_patch; final complete changes are CHANGES_FINAL.diff. No existing artifact was replaced.

## Final consolidation

```sh
python3 -B results/raw/cpu_gpu_recovery_20261011T075800444473Z/finalize_recovery.py
```

Exit0 is supported by RECOVERY_SEALED and FINAL_INTEGRITY.json. Hash/file operations only. The final seal excludes itself, and the after-seal read-only verification is a separate python3 -B - hash/manifest check with exit0; it does not alter the sealed evidence.

Failure history retained: initial focused fixture run23 methods,12 errors due duplicated missing keyword; corrected fixture23/23, then24/24, then26/26 as coverage was added. Final strict-schema/import safety26/26. Existing policy9/9. The prior review parser failure/correction remains unchanged under its original paths. No GPU access or timing failure was retried/hidden.
