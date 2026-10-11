# Exact command and status ledger

All paths below are relative to this evidence directory. argv is shell-rendered with shlex.join; JSON retains the exact argument array, cwd, UTC start and full output. Local recorder exit1 means its child failed; use the child exit field. Colab CLI exit0 is not a semantic pass: inspect markers and tracebacks. Remote leaf commands are separately listed. No timing-bearing workload was authorized or executed.

Baseline hash-only command: `python3 -B -` with literal stdin in [BASELINE_COMMAND.py](BASELINE_COMMAND.py), exit0. Initial Git inspection reported absent metadata; no Git mutations occurred.

Independent read-only reviewer commands/statuses: [AGENT_COMMANDS.md](AGENT_COMMANDS.md). Source edits used apply_patch or evidence-local assembly scripts; the exact final source diffs are under final_diffs/.

Evidence-only final consolidation/seal command: `python3 -B results/raw/bounded_resume_20261011T024034091796Z/consolidate_audit.py`, run from repository root; success is established by FINAL_INTEGRITY and the terminal completion marker. It invokes no subprocess/workload.

## FAILED_CPU_RELEASE.json

- UTC: 2026-10-11T02:49:00.453380+00:00
- cwd: `/content/mab_bounded_resume_20261011T024034091796Z/source`
- exit: `8`
- scope: Inherited from enclosing bounded launcher; see exact command and source.
- full retained record: [FAILED_CPU_RELEASE.json](FAILED_CPU_RELEASE.json)

```sh
ctest --test-dir /content/mab_bounded_resume_20261011T024034091796Z/cpu-release --output-on-failure -V --parallel 1 -R '^(baselines|cli|comparisons|cpu_gpu_comparison_framework|cuda_benchmark_analysis|cuda_preflight|cuda_sort_handoff|datasets|environment_manifest|memory|memory_unsupported|mergesort|metrics_cli|parallel_workers_correctness|pdqsort|quicksort|radixsort|searching|structures|timsort|validation_policy)$'
```

## archive_upload.json

- UTC: 2026-10-11T02:44:40.059109+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Transfer reviewed source-only archive to exclusive destination; no secrets/results/builds
- full retained record: [archive_upload.json](archive_upload.json)

```sh
colab upload results/raw/bounded_resume_20261011T024034091796Z/reviewed_source.tar.gz /content/mab_bounded_resume_20261011T024034091796Z/source.tar.gz --session cpu-gpu-bounded-validation-v3
```

## archive_upload_v2.json

- UTC: 2026-10-11T02:54:33.323772+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Transfer revised reviewed source only to new root; original source/bundle immutable
- full retained record: [archive_upload_v2.json](archive_upload_v2.json)

```sh
colab upload results/raw/bounded_resume_20261011T024034091796Z/reviewed_source_v2.tar.gz /content/mab_bounded_resume_20261011T024034091796Z_revision2/source.tar.gz --session cpu-gpu-bounded-validation-v3
```

## dart_regressions.json

- UTC: 2026-10-11T02:42:57.107089+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Focused inert regressions; inspected subprocess/shell entry points mocked, no CTest/timing/GPU
- full retained record: [dart_regressions.json](dart_regressions.json)

```sh
python3 -B tests/test_ctest_dart_compatibility.py
```

## downloaded/evidence/FINAL_GPU_SNAPSHOT.json

- UTC: 2026-10-11T03:02:49.263447+00:00
- cwd: `see parent remote script`
- exit: `0`
- scope: Inherited from enclosing bounded launcher; see exact command and source.
- full retained record: [downloaded/evidence/FINAL_GPU_SNAPSHOT.json](downloaded/evidence/FINAL_GPU_SNAPSHOT.json)

```sh
nvidia-smi --query-gpu=name,uuid,driver_version,memory.total,memory.free,temperature.gpu,clocks.sm,clocks.mem --format=csv
```

## downloaded/evidence/build_commands/cpu-release_build.json

- UTC: 2026-10-11T02:55:54.800072+00:00
- cwd: `/content/mab_bounded_resume_20261011T024034091796Z_revision2/source`
- exit: `0`
- scope: Build/configuration only; no test or benchmark invocation.
- full retained record: [downloaded/evidence/build_commands/cpu-release_build.json](downloaded/evidence/build_commands/cpu-release_build.json)

```sh
cmake --build /content/mab_bounded_resume_20261011T024034091796Z_revision2/cpu-release --parallel 2
```

## downloaded/evidence/build_commands/cpu-release_configure.json

- UTC: 2026-10-11T02:55:53.756978+00:00
- cwd: `/content/mab_bounded_resume_20261011T024034091796Z_revision2/source`
- exit: `0`
- scope: Build/configuration only; no test or benchmark invocation.
- full retained record: [downloaded/evidence/build_commands/cpu-release_configure.json](downloaded/evidence/build_commands/cpu-release_configure.json)

```sh
cmake -S /content/mab_bounded_resume_20261011T024034091796Z_revision2/source -DCMAKE_CXX_FLAGS= '-DCMAKE_CXX_FLAGS_RELEASE=-O3 -DNDEBUG' -DMAB_ENABLE_OPENMP=ON -DBUILD_TESTING=ON -DMAB_ENABLE_VALIDATION_DIAGNOSTICS=ON -DPython3_EXECUTABLE=/usr/bin/python3.13 -B /content/mab_bounded_resume_20261011T024034091796Z_revision2/cpu-release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_CUDA=OFF -DMAB_ENABLE_CPU_GPU_COMPARISON=OFF
```

## downloaded/evidence/build_commands/cpu-sanitize_build.json

- UTC: 2026-10-11T02:56:46.182519+00:00
- cwd: `/content/mab_bounded_resume_20261011T024034091796Z_revision2/source`
- exit: `0`
- scope: Build/configuration only; no test or benchmark invocation.
- full retained record: [downloaded/evidence/build_commands/cpu-sanitize_build.json](downloaded/evidence/build_commands/cpu-sanitize_build.json)

```sh
cmake --build /content/mab_bounded_resume_20261011T024034091796Z_revision2/cpu-sanitize --parallel 2
```

## downloaded/evidence/build_commands/cpu-sanitize_configure.json

- UTC: 2026-10-11T02:56:44.897612+00:00
- cwd: `/content/mab_bounded_resume_20261011T024034091796Z_revision2/source`
- exit: `0`
- scope: Build/configuration only; no test or benchmark invocation.
- full retained record: [downloaded/evidence/build_commands/cpu-sanitize_configure.json](downloaded/evidence/build_commands/cpu-sanitize_configure.json)

```sh
cmake -S /content/mab_bounded_resume_20261011T024034091796Z_revision2/source -DCMAKE_CXX_FLAGS= '-DCMAKE_CXX_FLAGS_RELEASE=-O3 -DNDEBUG' -DMAB_ENABLE_OPENMP=ON -DBUILD_TESTING=ON -DMAB_ENABLE_VALIDATION_DIAGNOSTICS=ON -DPython3_EXECUTABLE=/usr/bin/python3.13 -B /content/mab_bounded_resume_20261011T024034091796Z_revision2/cpu-sanitize -DCMAKE_BUILD_TYPE=Debug -DMAB_ENABLE_CUDA=OFF -DMAB_ENABLE_CPU_GPU_COMPARISON=OFF -DMAB_ENABLE_SANITIZERS=ON
```

## downloaded/evidence/build_commands/gpu-release_build.json

- UTC: 2026-10-11T02:57:46.941144+00:00
- cwd: `/content/mab_bounded_resume_20261011T024034091796Z_revision2/source`
- exit: `0`
- scope: Build/configuration only; no test or benchmark invocation.
- full retained record: [downloaded/evidence/build_commands/gpu-release_build.json](downloaded/evidence/build_commands/gpu-release_build.json)

```sh
cmake --build /content/mab_bounded_resume_20261011T024034091796Z_revision2/gpu-release --parallel 2
```

## downloaded/evidence/build_commands/gpu-release_configure.json

- UTC: 2026-10-11T02:57:39.123785+00:00
- cwd: `/content/mab_bounded_resume_20261011T024034091796Z_revision2/source`
- exit: `0`
- scope: Build/configuration only; no test or benchmark invocation.
- full retained record: [downloaded/evidence/build_commands/gpu-release_configure.json](downloaded/evidence/build_commands/gpu-release_configure.json)

```sh
cmake -S /content/mab_bounded_resume_20261011T024034091796Z_revision2/source -DCMAKE_CXX_FLAGS= '-DCMAKE_CXX_FLAGS_RELEASE=-O3 -DNDEBUG' -DMAB_ENABLE_OPENMP=ON -DBUILD_TESTING=ON -DMAB_ENABLE_VALIDATION_DIAGNOSTICS=ON -DPython3_EXECUTABLE=/usr/bin/python3.13 -B /content/mab_bounded_resume_20261011T024034091796Z_revision2/gpu-release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_CUDA=ON -DMAB_ENABLE_CUDA_SORT=ON -DMAB_ENABLE_CPU_GPU_COMPARISON=ON -DMAB_ENABLE_SANITIZERS=OFF -DCMAKE_CUDA_ARCHITECTURES=75 -DCMAKE_CUDA_FLAGS= '-DCMAKE_CUDA_FLAGS_RELEASE=-O3 -DNDEBUG'
```

## downloaded/evidence/validation_commands/actual_workers_untimed.json

- UTC: 2026-10-11T03:02:30.753080+00:00
- cwd: `/content/mab_bounded_resume_20261011T024034091796Z_revision2/source`
- exit: `0`
- scope: Untimed public/registry worker correctness.
- full retained record: [downloaded/evidence/validation_commands/actual_workers_untimed.json](downloaded/evidence/validation_commands/actual_workers_untimed.json)

```sh
/content/mab_bounded_resume_20261011T024034091796Z_revision2/gpu-release/test_parallel_workers
```

## downloaded/evidence/validation_commands/comparison_description.json

- UTC: 2026-10-11T03:02:29.085979+00:00
- cwd: `/content/mab_bounded_resume_20261011T024034091796Z_revision2/source`
- exit: `0`
- scope: Metadata-only --describe.
- full retained record: [downloaded/evidence/validation_commands/comparison_description.json](downloaded/evidence/validation_commands/comparison_description.json)

```sh
/content/mab_bounded_resume_20261011T024034091796Z_revision2/gpu-release/cpu_gpu_comparison --describe
```

## downloaded/evidence/validation_commands/cpu_release_ctest.json

- UTC: 2026-10-11T03:00:35.108689+00:00
- cwd: `/content/mab_bounded_resume_20261011T024034091796Z_revision2/source`
- exit: `0`
- scope: Exact21 non-timing correctness groups; sequential CTest execution.
- full retained record: [downloaded/evidence/validation_commands/cpu_release_ctest.json](downloaded/evidence/validation_commands/cpu_release_ctest.json)

```sh
ctest --test-dir /content/mab_bounded_resume_20261011T024034091796Z_revision2/cpu-release --output-on-failure -V --parallel 1 -R '^(baselines|cli|comparisons|cpu_gpu_comparison_framework|cuda_benchmark_analysis|cuda_preflight|cuda_sort_handoff|datasets|environment_manifest|memory|memory_unsupported|mergesort|metrics_cli|parallel_workers_correctness|pdqsort|quicksort|radixsort|searching|structures|timsort|validation_policy)$'
```

## downloaded/evidence/validation_commands/cpu_release_ctest_discovery.json

- UTC: 2026-10-11T03:00:34.886295+00:00
- cwd: `/content/mab_bounded_resume_20261011T024034091796Z_revision2/source`
- exit: `0`
- scope: Guarded ordinary CTest discovery only, after static validation.
- full retained record: [downloaded/evidence/validation_commands/cpu_release_ctest_discovery.json](downloaded/evidence/validation_commands/cpu_release_ctest_discovery.json)

```sh
ctest --test-dir /content/mab_bounded_resume_20261011T024034091796Z_revision2/cpu-release -N --show-only=json-v1
```

## downloaded/evidence/validation_commands/cpu_sanitize_ctest.json

- UTC: 2026-10-11T03:01:07.723724+00:00
- cwd: `/content/mab_bounded_resume_20261011T024034091796Z_revision2/source`
- exit: `0`
- scope: Exact21 non-timing correctness groups; sequential CTest execution.
- full retained record: [downloaded/evidence/validation_commands/cpu_sanitize_ctest.json](downloaded/evidence/validation_commands/cpu_sanitize_ctest.json)

```sh
env -u ASAN_OPTIONS -u LSAN_OPTIONS UBSAN_OPTIONS=halt_on_error=1 ctest --test-dir /content/mab_bounded_resume_20261011T024034091796Z_revision2/cpu-sanitize --output-on-failure -V --parallel 1 -R '^(baselines|cli|comparisons|cpu_gpu_comparison_framework|cuda_benchmark_analysis|cuda_preflight|cuda_sort_handoff|datasets|environment_manifest|memory|memory_unsupported|mergesort|metrics_cli|parallel_workers_correctness|pdqsort|quicksort|radixsort|searching|structures|timsort|validation_policy)$'
```

## downloaded/evidence/validation_commands/cpu_sanitize_ctest_discovery.json

- UTC: 2026-10-11T03:01:07.498786+00:00
- cwd: `/content/mab_bounded_resume_20261011T024034091796Z_revision2/source`
- exit: `0`
- scope: Guarded ordinary CTest discovery only, after static validation.
- full retained record: [downloaded/evidence/validation_commands/cpu_sanitize_ctest_discovery.json](downloaded/evidence/validation_commands/cpu_sanitize_ctest_discovery.json)

```sh
ctest --test-dir /content/mab_bounded_resume_20261011T024034091796Z_revision2/cpu-sanitize -N --show-only=json-v1
```

## downloaded/evidence/validation_commands/gpu_prepared_untimed.json

- UTC: 2026-10-11T03:02:29.092628+00:00
- cwd: `/content/mab_bounded_resume_20261011T024034091796Z_revision2/source`
- exit: `0`
- scope: Untimed GPU correctness only, no event samples.
- full retained record: [downloaded/evidence/validation_commands/gpu_prepared_untimed.json](downloaded/evidence/validation_commands/gpu_prepared_untimed.json)

```sh
/content/mab_bounded_resume_20261011T024034091796Z_revision2/gpu-release/test_cuda_prepared_correctness
```

## downloaded/evidence/validation_commands/resources_1000000.json

- UTC: 2026-10-11T03:02:30.476781+00:00
- cwd: `/content/mab_bounded_resume_20261011T024034091796Z_revision2/source`
- exit: `0`
- scope: Non-sorting bounded workspace/allocation diagnostic.
- full retained record: [downloaded/evidence/validation_commands/resources_1000000.json](downloaded/evidence/validation_commands/resources_1000000.json)

```sh
/content/mab_bounded_resume_20261011T024034091796Z_revision2/gpu-release/cpu_gpu_comparison --resources 1000000
```

## downloaded/evidence/validation_commands/resources_1025.json

- UTC: 2026-10-11T03:02:29.822580+00:00
- cwd: `/content/mab_bounded_resume_20261011T024034091796Z_revision2/source`
- exit: `0`
- scope: Non-sorting bounded workspace/allocation diagnostic.
- full retained record: [downloaded/evidence/validation_commands/resources_1025.json](downloaded/evidence/validation_commands/resources_1025.json)

```sh
/content/mab_bounded_resume_20261011T024034091796Z_revision2/gpu-release/cpu_gpu_comparison --resources 1025
```

## downloaded/evidence/validation_commands/resources_65537.json

- UTC: 2026-10-11T03:02:30.185656+00:00
- cwd: `/content/mab_bounded_resume_20261011T024034091796Z_revision2/source`
- exit: `0`
- scope: Non-sorting bounded workspace/allocation diagnostic.
- full retained record: [downloaded/evidence/validation_commands/resources_65537.json](downloaded/evidence/validation_commands/resources_65537.json)

```sh
/content/mab_bounded_resume_20261011T024034091796Z_revision2/gpu-release/cpu_gpu_comparison --resources 65537
```

## downloaded_failed/evidence/FINAL_GPU_SNAPSHOT.json

- UTC: 2026-10-11T02:53:03.563052+00:00
- cwd: `see parent remote script`
- exit: `0`
- scope: Inherited from enclosing bounded launcher; see exact command and source.
- full retained record: [downloaded_failed/evidence/FINAL_GPU_SNAPSHOT.json](downloaded_failed/evidence/FINAL_GPU_SNAPSHOT.json)

```sh
nvidia-smi --query-gpu=name,uuid,driver_version,memory.total,memory.free,temperature.gpu,clocks.sm,clocks.mem --format=csv
```

## downloaded_failed/evidence/build_commands/cpu-release_build.json

- UTC: 2026-10-11T02:45:26.769298+00:00
- cwd: `/content/mab_bounded_resume_20261011T024034091796Z/source`
- exit: `0`
- scope: Build/configuration only; no test or benchmark invocation.
- full retained record: [downloaded_failed/evidence/build_commands/cpu-release_build.json](downloaded_failed/evidence/build_commands/cpu-release_build.json)

```sh
cmake --build /content/mab_bounded_resume_20261011T024034091796Z/cpu-release --parallel 2
```

## downloaded_failed/evidence/build_commands/cpu-release_configure.json

- UTC: 2026-10-11T02:45:25.101516+00:00
- cwd: `/content/mab_bounded_resume_20261011T024034091796Z/source`
- exit: `0`
- scope: Build/configuration only; no test or benchmark invocation.
- full retained record: [downloaded_failed/evidence/build_commands/cpu-release_configure.json](downloaded_failed/evidence/build_commands/cpu-release_configure.json)

```sh
cmake -S /content/mab_bounded_resume_20261011T024034091796Z/source -DCMAKE_CXX_FLAGS= '-DCMAKE_CXX_FLAGS_RELEASE=-O3 -DNDEBUG' -DMAB_ENABLE_OPENMP=ON -DBUILD_TESTING=ON -DMAB_ENABLE_VALIDATION_DIAGNOSTICS=ON -DPython3_EXECUTABLE=/usr/bin/python3.13 -B /content/mab_bounded_resume_20261011T024034091796Z/cpu-release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_CUDA=OFF -DMAB_ENABLE_CPU_GPU_COMPARISON=OFF
```

## downloaded_failed/evidence/build_commands/cpu-sanitize_build.json

- UTC: 2026-10-11T02:46:16.464361+00:00
- cwd: `/content/mab_bounded_resume_20261011T024034091796Z/source`
- exit: `0`
- scope: Build/configuration only; no test or benchmark invocation.
- full retained record: [downloaded_failed/evidence/build_commands/cpu-sanitize_build.json](downloaded_failed/evidence/build_commands/cpu-sanitize_build.json)

```sh
cmake --build /content/mab_bounded_resume_20261011T024034091796Z/cpu-sanitize --parallel 2
```

## downloaded_failed/evidence/build_commands/cpu-sanitize_configure.json

- UTC: 2026-10-11T02:46:15.401045+00:00
- cwd: `/content/mab_bounded_resume_20261011T024034091796Z/source`
- exit: `0`
- scope: Build/configuration only; no test or benchmark invocation.
- full retained record: [downloaded_failed/evidence/build_commands/cpu-sanitize_configure.json](downloaded_failed/evidence/build_commands/cpu-sanitize_configure.json)

```sh
cmake -S /content/mab_bounded_resume_20261011T024034091796Z/source -DCMAKE_CXX_FLAGS= '-DCMAKE_CXX_FLAGS_RELEASE=-O3 -DNDEBUG' -DMAB_ENABLE_OPENMP=ON -DBUILD_TESTING=ON -DMAB_ENABLE_VALIDATION_DIAGNOSTICS=ON -DPython3_EXECUTABLE=/usr/bin/python3.13 -B /content/mab_bounded_resume_20261011T024034091796Z/cpu-sanitize -DCMAKE_BUILD_TYPE=Debug -DMAB_ENABLE_CUDA=OFF -DMAB_ENABLE_CPU_GPU_COMPARISON=OFF -DMAB_ENABLE_SANITIZERS=ON
```

## downloaded_failed/evidence/build_commands/gpu-release_build.json

- UTC: 2026-10-11T02:47:18.144272+00:00
- cwd: `/content/mab_bounded_resume_20261011T024034091796Z/source`
- exit: `0`
- scope: Build/configuration only; no test or benchmark invocation.
- full retained record: [downloaded_failed/evidence/build_commands/gpu-release_build.json](downloaded_failed/evidence/build_commands/gpu-release_build.json)

```sh
cmake --build /content/mab_bounded_resume_20261011T024034091796Z/gpu-release --parallel 2
```

## downloaded_failed/evidence/build_commands/gpu-release_configure.json

- UTC: 2026-10-11T02:47:09.241107+00:00
- cwd: `/content/mab_bounded_resume_20261011T024034091796Z/source`
- exit: `0`
- scope: Build/configuration only; no test or benchmark invocation.
- full retained record: [downloaded_failed/evidence/build_commands/gpu-release_configure.json](downloaded_failed/evidence/build_commands/gpu-release_configure.json)

```sh
cmake -S /content/mab_bounded_resume_20261011T024034091796Z/source -DCMAKE_CXX_FLAGS= '-DCMAKE_CXX_FLAGS_RELEASE=-O3 -DNDEBUG' -DMAB_ENABLE_OPENMP=ON -DBUILD_TESTING=ON -DMAB_ENABLE_VALIDATION_DIAGNOSTICS=ON -DPython3_EXECUTABLE=/usr/bin/python3.13 -B /content/mab_bounded_resume_20261011T024034091796Z/gpu-release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_CUDA=ON -DMAB_ENABLE_CUDA_SORT=ON -DMAB_ENABLE_CPU_GPU_COMPARISON=ON -DMAB_ENABLE_SANITIZERS=OFF -DCMAKE_CUDA_ARCHITECTURES=75 -DCMAKE_CUDA_FLAGS= '-DCMAKE_CUDA_FLAGS_RELEASE=-O3 -DNDEBUG'
```

## downloaded_failed/evidence/validation_commands/cpu_release_ctest.json

- UTC: 2026-10-11T02:49:00.453380+00:00
- cwd: `/content/mab_bounded_resume_20261011T024034091796Z/source`
- exit: `8`
- scope: Exact21 non-timing correctness groups; sequential CTest execution.
- full retained record: [downloaded_failed/evidence/validation_commands/cpu_release_ctest.json](downloaded_failed/evidence/validation_commands/cpu_release_ctest.json)

```sh
ctest --test-dir /content/mab_bounded_resume_20261011T024034091796Z/cpu-release --output-on-failure -V --parallel 1 -R '^(baselines|cli|comparisons|cpu_gpu_comparison_framework|cuda_benchmark_analysis|cuda_preflight|cuda_sort_handoff|datasets|environment_manifest|memory|memory_unsupported|mergesort|metrics_cli|parallel_workers_correctness|pdqsort|quicksort|radixsort|searching|structures|timsort|validation_policy)$'
```

## downloaded_failed/evidence/validation_commands/cpu_release_ctest_discovery.json

- UTC: 2026-10-11T02:49:00.135673+00:00
- cwd: `/content/mab_bounded_resume_20261011T024034091796Z/source`
- exit: `0`
- scope: Guarded ordinary CTest discovery only, after static validation.
- full retained record: [downloaded_failed/evidence/validation_commands/cpu_release_ctest_discovery.json](downloaded_failed/evidence/validation_commands/cpu_release_ctest_discovery.json)

```sh
ctest --test-dir /content/mab_bounded_resume_20261011T024034091796Z/cpu-release -N --show-only=json-v1
```

## evidence_verify_v2.json

- UTC: 2026-10-11T03:03:31.127919+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Verify remote archive hash and safe exact-member extraction only
- full retained record: [evidence_verify_v2.json](evidence_verify_v2.json)

```sh
python3 -B results/raw/bounded_resume_20261011T024034091796Z/verify_remote_archive.py validation_evidence.tar.gz 7339833e631df7f5dda203b6a4ef9a42a7714682331ac558d4a25e2a798780a9 downloaded
```

## failed_archive_download.json

- UTC: 2026-10-11T02:53:50.786592+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Retrieve sealed failed-attempt archive only; no execution or overwrites
- full retained record: [failed_archive_download.json](failed_archive_download.json)

```sh
colab download /content/mab_bounded_resume_20261011T024034091796Z/validation_evidence_failed.tar.gz results/raw/bounded_resume_20261011T024034091796Z/validation_evidence_failed.tar.gz --session cpu-gpu-bounded-validation-v3
```

## failed_archive_verify.json

- UTC: 2026-10-11T02:56:20.957067+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Hash/safe member/content verification of retained failed evidence; no execution
- full retained record: [failed_archive_verify.json](failed_archive_verify.json)

```sh
python3 -B results/raw/bounded_resume_20261011T024034091796Z/verify_remote_archive.py validation_evidence_failed.tar.gz 7ee768cfb4dd2cad9c97d5f0866176dd1a71c89b7431ad6d0bf561519651d3a7 downloaded_failed
```

## failure_inspection.json

- UTC: 2026-10-11T02:50:02.570123+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Read-only actual retained Release output; no tests/CTest/workload execution
- full retained record: [failure_inspection.json](failure_inspection.json)

```sh
python3 -B -c 'import json
from pathlib import Path
d=json.loads(Path('"'"'results/raw/bounded_resume_20261011T024034091796Z/FAILED_CPU_RELEASE.json'"'"').read_text());print('"'"'EXIT'"'"',d['"'"'exit_code'"'"']);print(d['"'"'stdout'"'"']);print(d['"'"'stderr'"'"'])'
```

## failure_sealer_assembly.json

- UTC: 2026-10-11T02:53:00.893456+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Evidence-only script assembly; original failure/source/build retained
- full retained record: [failure_sealer_assembly.json](failure_sealer_assembly.json)

```sh
python3 -B -c 'from pathlib import Path
E=Path("results/raw/bounded_resume_20261011T024034091796Z")
s=(E/'"'"'remote_seal.py'"'"').read_text()
s=s.replace("assert (e/'"'"'BOUNDED_COMPLETE.json'"'"').is_file() and json.loads((e/'"'"'BOUNDED_COMPLETE.json'"'"').read_text())['"'"'complete'"'"'] is True","assert json.loads((e/'"'"'validation_commands/cpu_release_ctest.json'"'"').read_text())['"'"'exit_code'"'"'] == 8")
s=s.replace('"'"'all_validation_complete=True'"'"','"'"'all_validation_complete=False'"'"').replace("root/'"'"'validation_evidence.tar.gz'"'"'","root/'"'"'validation_evidence_failed.tar.gz'"'"'")
with (E/'"'"'remote_seal_failed.py'"'"').open('"'"'x'"'"') as f:f.write(s)
print('"'"'Failure-only evidence sealer; no tests/workloads'"'"')
'
```

## fixture_before.json

- UTC: 2026-10-11T02:52:07.050397+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Evidence-only preservation of pre-fix test and initial v3 manifest; no workloads
- full retained record: [fixture_before.json](fixture_before.json)

```sh
python3 -B -c 'from pathlib import Path
E=Path('"'"'results/raw/bounded_resume_20261011T024034091796Z'"'"')
for n in ['"'"'tests/test_cpu_gpu_comparison.py'"'"','"'"'docs/NON_TIMING_TEST_SELECTION_v3.json'"'"']:
 p=E/'"'"'before'"'"'/n;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('"'"'xb'"'"') as f:f.write(Path(n).read_bytes())
print('"'"'Pre-fix files preserved'"'"')'
```

## fixture_focus.json

- UTC: 2026-10-11T02:52:17.673224+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `1`
- scope: Only synthetic StudyOrchestrationTests; invoke/snapshot/analyze mocked, no measurements/GPU/real CTest
- full retained record: [fixture_focus.json](fixture_focus.json)

```sh
python3 -B tests/test_cpu_gpu_comparison.py StudyOrchestrationTests
```

## fixture_focus_corrected.json

- UTC: 2026-10-11T02:53:36.115087+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `1`
- scope: Corrected unittest-loader invocation; exactly9 synthetic tests, all subprocess/shell entry points blocked; no CTest/GPU/timings
- full retained record: [fixture_focus_corrected.json](fixture_focus_corrected.json)

```sh
python3 -B -c 'import contextlib,importlib.util,sys,unittest
from pathlib import Path
from unittest import mock
path=Path('"'"'tests/test_cpu_gpu_comparison.py'"'"').resolve();sys.argv=[str(path)]
spec=importlib.util.spec_from_file_location('"'"'reviewed_fixture_tests'"'"',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
with contextlib.ExitStack() as stack:
 for name in ['"'"'run'"'"','"'"'Popen'"'"','"'"'call'"'"','"'"'check_call'"'"','"'"'check_output'"'"']:stack.enter_context(mock.patch('"'"'subprocess.'"'"'+name,side_effect=AssertionError('"'"'external execution forbidden'"'"')))
 stack.enter_context(mock.patch('"'"'os.system'"'"',side_effect=AssertionError('"'"'shell forbidden'"'"')))
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(module.StudyOrchestrationTests)
 result=unittest.TextTestRunner(verbosity=2).run(suite)
 assert result.testsRun==9
 sys.exit(0 if result.wasSuccessful() else 1)
'
```

## fixture_focus_final.json

- UTC: 2026-10-11T02:53:50.057790+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Exactly9 synthetic fixture tests with normal test module path; all subprocess/shell entry points blocked
- full retained record: [fixture_focus_final.json](fixture_focus_final.json)

```sh
python3 -B -c 'import contextlib,importlib.util,sys,unittest
from pathlib import Path
from unittest import mock
path=Path('"'"'tests/test_cpu_gpu_comparison.py'"'"').resolve();sys.argv=[str(path)];sys.path.insert(0,str(path.parent))
spec=importlib.util.spec_from_file_location('"'"'reviewed_fixture_tests'"'"',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
with contextlib.ExitStack() as stack:
 for name in ['"'"'run'"'"','"'"'Popen'"'"','"'"'call'"'"','"'"'check_call'"'"','"'"'check_output'"'"']:stack.enter_context(mock.patch('"'"'subprocess.'"'"'+name,side_effect=AssertionError('"'"'external execution forbidden'"'"')))
 stack.enter_context(mock.patch('"'"'os.system'"'"',side_effect=AssertionError('"'"'shell forbidden'"'"')))
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(module.StudyOrchestrationTests)
 result=unittest.TextTestRunner(verbosity=2).run(suite)
 assert result.testsRun==9
 sys.exit(0 if result.wasSuccessful() else 1)
'
```

## fixture_snapshot_update.json

- UTC: 2026-10-11T02:52:17.581627+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Current unsealed v3 review snapshot only; original transferred revision preserved; no production/policy changes
- full retained record: [fixture_snapshot_update.json](fixture_snapshot_update.json)

```sh
python3 -B -c 'from pathlib import Path
import json,sys
sys.path.insert(0,str(Path('"'"'scripts'"'"').resolve()))
from cpu_gpu_protocol import source_manifest
p=Path('"'"'docs/NON_TIMING_TEST_SELECTION_v3.json'"'"');m=json.loads(p.read_text());m['"'"'reviewed_source_sha256'"'"']=source_manifest()
p.write_text(json.dumps(m,indent=2,sort_keys=True)+'"'"'\n'"'"')
print(Path('"'"'tests/test_cpu_gpu_comparison.py'"'"').read_text().split('"'"'ROOT='"'"')[0][:1200])
print('"'"'New reviewed source snapshot retained; initial manifest remains in source archive and before/'"'"')
'
```

## guard_regressions.json

- UTC: 2026-10-11T02:42:58.157301+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Focused inert regressions; inspected subprocess/shell entry points mocked, no CTest/timing/GPU
- full retained record: [guard_regressions.json](guard_regressions.json)

```sh
python3 -B tests/test_ctest_build_guard.py
```

## legacy_fixture_inspection.json

- UTC: 2026-10-11T02:50:12.627076+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Read-only traceback-directed synthetic test/legacy policy inspection; no execution
- full retained record: [legacy_fixture_inspection.json](legacy_fixture_inspection.json)

```sh
python3 -B -c 'from pathlib import Path
for n,start,end in [('"'"'tests/test_cpu_gpu_comparison.py'"'"',325,505),('"'"'scripts/run_cpu_gpu_study.py'"'"',1,110),('"'"'scripts/validate_cpu_gpu_pilot.py'"'"',30,108),('"'"'scripts/cpu_gpu_protocol.py'"'"',100,155)]:
 lines=Path(n).read_text().splitlines();print('"'"'\nFILE '"'"'+n);print('"'"'\n'"'"'.join(str(i+1)+'"'"': '"'"'+lines[i] for i in range(start-1,min(end,len(lines)))))
'
```

## manifest_upload.json

- UTC: 2026-10-11T02:44:47.981657+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Transfer reviewed SHA256 manifest only to exclusive destination
- full retained record: [manifest_upload.json](manifest_upload.json)

```sh
colab upload results/raw/bounded_resume_20261011T024034091796Z/SOURCE_MANIFEST.json /content/mab_bounded_resume_20261011T024034091796Z/source_manifest.json --session cpu-gpu-bounded-validation-v3
```

## manifest_upload_v2.json

- UTC: 2026-10-11T02:54:34.484849+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Transfer revision2 reviewed source SHA256 manifest only
- full retained record: [manifest_upload_v2.json](manifest_upload_v2.json)

```sh
colab upload results/raw/bounded_resume_20261011T024034091796Z/SOURCE_MANIFEST_V2.json /content/mab_bounded_resume_20261011T024034091796Z_revision2/source_manifest.json --session cpu-gpu-bounded-validation-v3
```

## manifest_v3.json

- UTC: 2026-10-11T02:42:45.393432+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Evidence-reviewed source snapshot and new versioned selection manifest only; no workloads
- full retained record: [manifest_v3.json](manifest_v3.json)

```sh
python3 -B -c 'from pathlib import Path
import hashlib,json,sys
sys.path.insert(0,str(Path('"'"'scripts'"'"').resolve()))
from cpu_gpu_protocol import source_manifest
p=Path('"'"'docs/NON_TIMING_TEST_SELECTION_v2.json'"'"');m=json.loads(p.read_text())
m['"'"'schema_version'"'"']=3;m['"'"'policy'"'"']='"'"'non_timing_correctness_v3'"'"'
m['"'"'review_method'"'"']='"'"'Versioned exact CMake3.31 Colab Dart literal alternative, reviewed fixed ordinary CTest commands; all v2 registrations/source safeguards retained.'"'"'
m['"'"'build_metadata'"'"']['"'"'policy'"'"']='"'"'flat_literal_ctest_v2'"'"';m['"'"'build_metadata'"'"']['"'"'dart_compatibility_profile'"'"']='"'"'cmake331_colab_t4_v1'"'"'
m['"'"'reviewed_source_sha256'"'"']=source_manifest()
m['"'"'evidence'"'"']="results/raw/bounded_resume_20261011T024034091796Z"
target=Path('"'"'docs/NON_TIMING_TEST_SELECTION_v3.json'"'"')
with target.open('"'"'x'"'"') as out:json.dump(m,out,indent=2,sort_keys=True);out.write('"'"'\n'"'"')
print('"'"'Reviewed source files'"'"',len(m['"'"'reviewed_source_sha256'"'"']))
'
```

## metadata_test_inspection.json

- UTC: 2026-10-11T02:40:48.412379+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Read-only source/test/configuration inspection; no execution
- full retained record: [metadata_test_inspection.json](metadata_test_inspection.json)

```sh
python3 -B -c 'from pathlib import Path
for n in ['"'"'tests/ctest_fixture.py'"'"','"'"'tests/test_ctest_build_guard.py'"'"','"'"'README.md'"'"','"'"'docs/ROADMAP.md'"'"']:
 print('"'"'\nFILE '"'"'+n+'"'"'\n'"'"'+Path(n).read_text())
'
```

## policy_regressions.json

- UTC: 2026-10-11T02:42:59.558594+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Focused inert regressions; inspected subprocess/shell entry points mocked, no CTest/timing/GPU
- full retained record: [policy_regressions.json](policy_regressions.json)

```sh
python3 -B tests/test_validation_policy.py
```

## prebuild_review_bundle.json

- UTC: 2026-10-11T02:43:47.110143+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Static reviewed diff, versioned manifest, exclusive source bundle and evidence-script assembly only
- full retained record: [prebuild_review_bundle.json](prebuild_review_bundle.json)

```sh
python3 -B -c 'from pathlib import Path
import difflib,hashlib,json,tarfile
E=Path("results/raw/bounded_resume_20261011T024034091796Z");old=Path('"'"'results/raw/bounded_validation_20261011T020343203635Z'"'"')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=json.loads((E/'"'"'BEFORE.json'"'"').read_text())
allowed={'"'"'scripts/ctest_build_guard.py'"'"','"'"'scripts/non_timing_tests.py'"'"'}
assert {p for p,h in b['"'"'project_sha256'"'"'].items() if sha(Path(p))!=h}==allowed
v2=json.loads(Path('"'"'docs/NON_TIMING_TEST_SELECTION_v2.json'"'"').read_text());v3=json.loads(Path('"'"'docs/NON_TIMING_TEST_SELECTION_v3.json'"'"').read_text())
assert all(v2[k]==v3[k] for k in ['"'"'tests'"'"','"'"'cpu_build_tests'"'"','"'"'cuda_additional_tests'"'"'])
assert v2['"'"'build_metadata'"'"']['"'"'test_properties'"'"']==v3['"'"'build_metadata'"'"']['"'"'test_properties'"'"']
for p in allowed:
 diff='"'"''"'"'.join(difflib.unified_diff((E/'"'"'before'"'"'/p).read_text().splitlines(True),Path(p).read_text().splitlines(True),fromfile='"'"'before/'"'"'+p,tofile=p))
 with (E/(p.replace('"'"'/'"'"','"'"'_'"'"')+'"'"'.diff'"'"')).open('"'"'x'"'"') as f:f.write(diff)
names=sorted(set(b['"'"'project_sha256'"'"'])|{'"'"'tests/test_ctest_dart_compatibility.py'"'"','"'"'docs/NON_TIMING_TEST_SELECTION_v3.json'"'"','"'"'docs/CTEST_COLAB_METADATA_v2.md'"'"'})
files={p:sha(Path(p)) for p in names}
with (E/'"'"'SOURCE_MANIFEST.json'"'"').open('"'"'x'"'"') as f:json.dump(files,f,indent=2,sort_keys=True);f.write('"'"'\n'"'"')
with tarfile.open(E/'"'"'reviewed_source.tar.gz'"'"','"'"'x:gz'"'"') as t:
 for p in names:t.add(p,arcname=p,recursive=False)
review=dict(modified=sorted(allowed),added=sorted(set(names)-set(b['"'"'project_sha256'"'"'])),production_CMake_and_protocol_unchanged=True,tests_registrations_unchanged=True,default_selected=19,diagnostic_selected=21,independent_static_review='"'"'metadata_safety_review PASS; focused9+36+3+9 inert tests passed'"'"',source_files=len(files),archive_sha256=sha(E/'"'"'reviewed_source.tar.gz'"'"'),manifest_sha256=sha(E/'"'"'SOURCE_MANIFEST.json'"'"'))
with (E/'"'"'PREBUILD_REVIEW.json'"'"').open('"'"'x'"'"') as f:json.dump(review,f,indent=2);f.write('"'"'\n'"'"')
for name in ['"'"'remote_environment.py'"'"','"'"'remote_prepare.py'"'"','"'"'remote_build.py'"'"','"'"'remote_selection_review.py'"'"','"'"'remote_extract.py'"'"','"'"'remote_independent_diagnostics.py'"'"','"'"'remote_seal.py'"'"']:
 text=(old/name).read_text().replace('"'"'/content/mab_bounded_20261011T020343203635Z'"'"',"/content/mab_bounded_resume_20261011T024034091796Z").replace('"'"'cpu-gpu-bounded-validation'"'"','"'"'cpu-gpu-bounded-validation-v3'"'"')
 text=text.replace('"'"'03de3a45743206244c480195de4629b8d440139f0fc5e236981f1f9cecac7fa5'"'"',review['"'"'archive_sha256'"'"']).replace('"'"'52dfe8d47d83ccba8e520dc79dc24465fdeaf88cdbd8c9bce4036c848e6b936b'"'"',review['"'"'manifest_sha256'"'"'])
 text=text.replace('"'"'gpu-t4-s-kkb-usw4b1-2i9q6dkvjw07d'"'"',"gpu-t4-s-kkb-usw1b1-zafww0nxdtgf")
 with (E/name).open('"'"'x'"'"') as f:f.write(text)
print(json.dumps(review,indent=2))
'
```

## release_failure_download.json

- UTC: 2026-10-11T02:49:46.651164+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Read-only retrieval of actual failed correctness-suite record; no rerun/repair
- full retained record: [release_failure_download.json](release_failure_download.json)

```sh
colab download /content/mab_bounded_resume_20261011T024034091796Z/evidence/validation_commands/cpu_release_ctest.json results/raw/bounded_resume_20261011T024034091796Z/FAILED_CPU_RELEASE.json --session cpu-gpu-bounded-validation-v3
```

## remote_bounded_validation.json

- UTC: 2026-10-11T02:48:57.354352+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Explicit authorized guarded21 CPU Release,21 sanitizer, untimedGPU163/489,3 bounded resources,12 workers; no benchmarks/pilot/warmups/measured trials
- full retained record: [remote_bounded_validation.json](remote_bounded_validation.json)

```sh
colab exec --session cpu-gpu-bounded-validation-v3 --file results/raw/bounded_resume_20261011T024034091796Z/remote_validate.py --timeout 1200
```

## remote_bounded_validation_v2_isolated.json

- UTC: 2026-10-11T03:00:31.830048+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Bounded guarded CPU Release and ASan/UBSan21, untimed prepared GPU correctness, workspace queries and worker correctness; zero timing trials
- full retained record: [remote_bounded_validation_v2_isolated.json](remote_bounded_validation_v2_isolated.json)

```sh
colab exec --session cpu-gpu-bounded-validation-v3 --file results/raw/bounded_resume_20261011T024034091796Z/remote_validate_v2_isolated.py --timeout 1200
```

## remote_environment.json

- UTC: 2026-10-11T02:43:47.302989+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Replacement non-benchmark environment checks only
- full retained record: [remote_environment.json](remote_environment.json)

```sh
colab exec --session cpu-gpu-bounded-validation-v3 --file results/raw/bounded_resume_20261011T024034091796Z/remote_environment.py --timeout 120
```

## remote_evidence_download_v2.json

- UTC: 2026-10-11T03:02:58.048428+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Download new sealed bounded evidence; no workloads
- full retained record: [remote_evidence_download_v2.json](remote_evidence_download_v2.json)

```sh
colab download /content/mab_bounded_resume_20261011T024034091796Z_revision2/validation_evidence.tar.gz results/raw/bounded_resume_20261011T024034091796Z/validation_evidence.tar.gz --session cpu-gpu-bounded-validation-v3
```

## remote_evidence_seal_v2.json

- UTC: 2026-10-11T03:02:46.984352+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Hash source/build identities and archive bounded validation evidence; final nvidia-smi diagnostic only
- full retained record: [remote_evidence_seal_v2.json](remote_evidence_seal_v2.json)

```sh
colab exec --session cpu-gpu-bounded-validation-v3 --file results/raw/bounded_resume_20261011T024034091796Z/remote_seal_v2.py --timeout 120
```

## remote_extract.json

- UTC: 2026-10-11T02:44:52.595180+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Verify remote archive/manifest hashes, inspect safe regular members, exclusive extraction and source/freeze checks only
- full retained record: [remote_extract.json](remote_extract.json)

```sh
colab exec --session cpu-gpu-bounded-validation-v3 --file results/raw/bounded_resume_20261011T024034091796Z/remote_extract.py --timeout 120
```

## remote_extract_v2.json

- UTC: 2026-10-11T02:55:13.534466+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Verify revision2 remote archive/member/source/frozen identities then exclusive extraction; no workloads
- full retained record: [remote_extract_v2.json](remote_extract_v2.json)

```sh
colab exec --session cpu-gpu-bounded-validation-v3 --file results/raw/bounded_resume_20261011T024034091796Z/remote_extract_v2.py --timeout 120
```

## remote_failure_seal.json

- UTC: 2026-10-11T02:53:00.969941+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Read-only source/build/hash checks, metadata capture, GPU status only; archive failed attempt exclusively; no tests/workloads
- full retained record: [remote_failure_seal.json](remote_failure_seal.json)

```sh
colab exec --session cpu-gpu-bounded-validation-v3 --file results/raw/bounded_resume_20261011T024034091796Z/remote_seal_failed.py --timeout 120
```

## remote_isolated_builds.json

- UTC: 2026-10-11T02:45:22.736433+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Authorized fresh CPU Release, CPU sanitizer Debug, GPU Release configure/build only; no tests/timing/workloads
- full retained record: [remote_isolated_builds.json](remote_isolated_builds.json)

```sh
colab exec --session cpu-gpu-bounded-validation-v3 --file results/raw/bounded_resume_20261011T024034091796Z/remote_build.py --timeout 1200
```

## remote_isolated_builds_v2.json

- UTC: 2026-10-11T02:55:50.912971+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Fresh isolated revision2 CPU Release, sanitizer Debug, GPU Release configure/build; no tests/workloads
- full retained record: [remote_isolated_builds_v2.json](remote_isolated_builds_v2.json)

```sh
colab exec --session cpu-gpu-bounded-validation-v3 --file results/raw/bounded_resume_20261011T024034091796Z/remote_build_v2.py --timeout 1200
```

## remote_prepare.json

- UTC: 2026-10-11T02:44:14.368104+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Inspect /content and create exclusive isolated destination only; no existing content overwritten
- full retained record: [remote_prepare.json](remote_prepare.json)

```sh
colab exec --session cpu-gpu-bounded-validation-v3 --file results/raw/bounded_resume_20261011T024034091796Z/remote_prepare.py --timeout 60
```

## remote_prepare_v2.json

- UTC: 2026-10-11T02:54:18.285884+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Inspect destination and create isolated revision2 root only; preserve first failed source/build/evidence
- full retained record: [remote_prepare_v2.json](remote_prepare_v2.json)

```sh
colab exec --session cpu-gpu-bounded-validation-v3 --file results/raw/bounded_resume_20261011T024034091796Z/remote_prepare_v2.py --timeout 60
```

## remote_static_selection.json

- UTC: 2026-10-11T02:48:48.207482+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Shared static pre-discovery guard only; retain exact19+2 plan for all fresh builds; no CTest execution/discovery yet
- full retained record: [remote_static_selection.json](remote_static_selection.json)

```sh
colab exec --session cpu-gpu-bounded-validation-v3 --file results/raw/bounded_resume_20261011T024034091796Z/remote_selection_review.py --timeout 120
```

## remote_static_selection_v2.json

- UTC: 2026-10-11T02:59:48.789615+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Static shared guard only; no CTest discovery or workloads
- full retained record: [remote_static_selection_v2.json](remote_static_selection_v2.json)

```sh
colab exec --session cpu-gpu-bounded-validation-v3 --file results/raw/bounded_resume_20261011T024034091796Z/remote_selection_review_v2.py --timeout 120
```

## remote_static_selection_v2_isolated.json

- UTC: 2026-10-11T03:00:18.944723+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Static guard in fresh Python process; no CTest discovery or workloads
- full retained record: [remote_static_selection_v2_isolated.json](remote_static_selection_v2_isolated.json)

```sh
colab exec --session cpu-gpu-bounded-validation-v3 --file results/raw/bounded_resume_20261011T024034091796Z/remote_selection_review_v2_isolated.py --timeout 120
```

## replacement_create.json

- UTC: 2026-10-11T02:40:58.469090+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Explicitly authorized single replacement T4 creation; prior replacement pruned/no active sessions; no workloads
- full retained record: [replacement_create.json](replacement_create.json)

```sh
colab new --session cpu-gpu-bounded-validation-v3 --gpu T4
```

## review_evidence_assembly.json

- UTC: 2026-10-11T02:46:00.403019+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Evidence-only retention of observed parallel read-only review findings
- full retained record: [review_evidence_assembly.json](review_evidence_assembly.json)

```sh
python3 -B -c 'from pathlib import Path
import json
E=Path("results/raw/bounded_resume_20261011T024034091796Z")
reports={
'"'"'metadata_safety_review'"'"':{'"'"'result'"'"':'"'"'PASS for exact compatibility extension before real discovery, conditioned on focused inert tests (now passed)'"'"','"'"'inspected'"'"':['"'"'scripts/ctest_build_guard.py'"'"','"'"'scripts/non_timing_tests.py'"'"','"'"'tests/test_ctest_dart_compatibility.py'"'"','"'"'docs/NON_TIMING_TEST_SELECTION_v3.json'"'"','"'"'docs/CTEST_COLAB_METADATA_v2.md'"'"'],'"'"'findings'"'"':['"'"'Exact old or paired-empty TLS schema only; literal compute-sanitizer path only.'"'"','"'"'Old commands/properties/registrations, canonical path and boundary checks unchanged.'"'"','"'"'MemoryCheckCommand is dashboard-only, fixed ordinary selector commands never execute it.'"'"','"'"'No production code or frozen inputs changed.'"'"'],'"'"'commands'"'"':["diff -u results/raw/bounded_resume_20261011T024034091796Z/before/scripts/ctest_build_guard.py scripts/ctest_build_guard.py","diff -u results/raw/bounded_resume_20261011T024034091796Z/before/scripts/non_timing_tests.py scripts/non_timing_tests.py"],'"'"'execution'"'"':'"'"'Read-only inspections only; no tests/CTest/cloud/GPU/workloads. Agent command batches completed0; diff reports expected content differences.'"'"'},
'"'"'validation_resume_review'"'"':{'"'"'result'"'"':'"'"'Reuse safe with exact metadata extension and bounded dedicated launcher'"'"','"'"'findings'"'"':['"'"'Default19 and explicit21 preserved.'"'"','"'"'CPU selection includes temporary CUDA-OFF configure-only checks, not workload execution.'"'"','"'"'Host-only CUDA analysis intentionally skips two timing integration Python methods; distinguish from CTest skips.'"'"','"'"'Old pilot validator default path unsafe; do not invoke.'"'"','"'"'Complete source/build/binary digests needed; generated source_hashes alone insufficient.'"'"'],'"'"'execution'"'"':'"'"'Read-only inspection; no edits/tests/CTest/cloud/GPU/workloads.'"'"'}}
with (E/'"'"'INDEPENDENT_REVIEWS.json'"'"').open('"'"'x'"'"') as f:json.dump(reports,f,indent=2);f.write('"'"'\n'"'"')
print('"'"'Retained independent review findings, not test results'"'"')
'
```

## review_retained_remote_scripts.json

- UTC: 2026-10-11T02:43:09.634782+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Read-only reuse review of prior authorized bounded build/transfer/diagnostic source
- full retained record: [review_retained_remote_scripts.json](review_retained_remote_scripts.json)

```sh
python3 -B -c 'from pathlib import Path
p=Path('"'"'results/raw/bounded_validation_20261011T020343203635Z'"'"')
for name in ['"'"'remote_environment.py'"'"','"'"'remote_prepare.py'"'"','"'"'remote_build.py'"'"','"'"'remote_selection_review.py'"'"','"'"'remote_extract.py'"'"']:
 print('"'"'\nFILE '"'"'+name+'"'"'\n'"'"'+(p/name).read_text())
'
```

## revised_bundle.json

- UTC: 2026-10-11T02:54:18.122348+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Static review/test-only diff and exclusive revision2 source bundle; preserve first bundle/source/build/failure
- full retained record: [revised_bundle.json](revised_bundle.json)

```sh
python3 -B -c 'from pathlib import Path
import difflib,hashlib,json,tarfile
E=Path("results/raw/bounded_resume_20261011T024034091796Z")
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
first=json.loads((E/'"'"'SOURCE_MANIFEST.json'"'"').read_text())
changed={p for p,h in first.items() if sha(Path(p))!=h}
assert changed=={'"'"'tests/test_cpu_gpu_comparison.py'"'"','"'"'docs/NON_TIMING_TEST_SELECTION_v3.json'"'"'},changed
files={p:sha(Path(p)) for p in first}
with (E/'"'"'SOURCE_MANIFEST_V2.json'"'"').open('"'"'x'"'"') as f:json.dump(files,f,indent=2,sort_keys=True);f.write('"'"'\n'"'"')
with tarfile.open(E/'"'"'reviewed_source_v2.tar.gz'"'"','"'"'x:gz'"'"') as t:
 for p in sorted(files):t.add(p,arcname=p,recursive=False)
diff='"'"''"'"'.join(difflib.unified_diff((E/'"'"'before/tests/test_cpu_gpu_comparison.py'"'"').read_text().splitlines(True),Path('"'"'tests/test_cpu_gpu_comparison.py'"'"').read_text().splitlines(True),fromfile='"'"'before/tests/test_cpu_gpu_comparison.py'"'"',tofile='"'"'tests/test_cpu_gpu_comparison.py'"'"'))
with (E/'"'"'tests_test_cpu_gpu_comparison.py.diff'"'"').open('"'"'x'"'"') as f:f.write(diff)
review={'"'"'source_files'"'"':len(files),'"'"'archive_sha256'"'"':sha(E/'"'"'reviewed_source_v2.tar.gz'"'"'),'"'"'manifest_sha256'"'"':sha(E/'"'"'SOURCE_MANIFEST_V2.json'"'"'),'"'"'changed_since_attempt1'"'"':sorted(changed),'"'"'production_CMake_frozen_policy_unchanged'"'"':True,'"'"'independent_review'"'"':'"'"'validation_resume_review PASS test-only fixture fix'"'"','"'"'focused_synthetic_methods_passed'"'"':9}
with (E/'"'"'PREBUILD_REVIEW_V2.json'"'"').open('"'"'x'"'"') as f:json.dump(review,f,indent=2);f.write('"'"'\n'"'"')
for name in ['"'"'remote_environment.py'"'"','"'"'remote_prepare.py'"'"','"'"'remote_extract.py'"'"','"'"'remote_build.py'"'"','"'"'remote_selection_review.py'"'"','"'"'remote_validate.py'"'"','"'"'remote_seal.py'"'"']:
 text=(E/name).read_text().replace("/content/mab_bounded_resume_20261011T024034091796Z","/content/mab_bounded_resume_20261011T024034091796Z_revision2")
 text=text.replace('"'"'320bc0a2574993efba0609c22d572551184ccafac9b8b3b41cb70d41297a72cc'"'"',review['"'"'archive_sha256'"'"']).replace('"'"'2a647c5f37ad1803d4f06e4e322d404236a7434ca99971f03a13aac171f8e49f'"'"',review['"'"'manifest_sha256'"'"'])
 with (E/name.replace('"'"'.py'"'"','"'"'_v2.py'"'"')).open('"'"'x'"'"') as f:f.write(text)
print(json.dumps(review,indent=2))
'
```

## runner_assembly.json

- UTC: 2026-10-11T02:45:19.094016+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Evidence script assembly only; reviewed correctness-only runner, no execution at assembly
- full retained record: [runner_assembly.json](runner_assembly.json)

```sh
python3 -B -c 'from pathlib import Path
E=Path("results/raw/bounded_resume_20261011T024034091796Z");old=Path('"'"'results/raw/bounded_validation_20261011T020343203635Z'"'"')
s=(old/'"'"'remote_validate.py'"'"').read_text().replace('"'"'/content/mab_bounded_20261011T020343203635Z'"'"',"/content/mab_bounded_resume_20261011T024034091796Z").replace('"'"'gpu-t4-s-kkb-usw4b1-2i9q6dkvjw07d'"'"',"gpu-t4-s-kkb-usw1b1-zafww0nxdtgf")
# The complete bounded runner remains the earlier reviewed correctness-only flow.
with (E/'"'"'remote_validate.py'"'"').open('"'"'x'"'"') as f:f.write(s)
p=E/'"'"'remote_seal.py'"'"';s=p.read_text().replace("assert (e/'"'"'DIRECT_DIAGNOSTICS_COMPLETE.json'"'"').is_file()","assert (e/'"'"'BOUNDED_COMPLETE.json'"'"').is_file() and json.loads((e/'"'"'BOUNDED_COMPLETE.json'"'"').read_text())['"'"'complete'"'"'] is True").replace('"'"'GPU-cd5085b4-b6d1-d004-07cc-6f1b32e3a0a2'"'"','"'"'GPU-5d327ac4-2d0a-4a11-6bd7-97474ba6359c'"'"').replace('"'"'all_validation_complete=False'"'"','"'"'all_validation_complete=True'"'"')
# Preserve all generated configuration metadata without running CMake/CTest again.
insert="""for name,b in builds['"'"'builds'"'"'].items():
    dest=e/('"'"'metadata_'"'"'+name);dest.mkdir()
    base=Path(b)
    for rel in ['"'"'CMakeCache.txt'"'"','"'"'CTestTestfile.cmake'"'"','"'"'DartConfiguration.tcl'"'"','"'"'compile_commands.json'"'"']:
        target=dest/rel
        with target.open('"'"'xb'"'"') as out:out.write((base/rel).read_bytes())
    for f in sorted((base/'"'"'generated'"'"').rglob('"'"'*'"'"')):
        if f.is_file():
            target=dest/f.relative_to(base);target.parent.mkdir(parents=True,exist_ok=True)
            with target.open('"'"'xb'"'"') as out:out.write(f.read_bytes())
"""
s=s.replace("gpu=Path(builds['"'"'builds'"'"']['"'"'gpu-release'"'"'])",insert+"gpu=Path(builds['"'"'builds'"'"']['"'"'gpu-release'"'"'])")
p.write_text(s)
assert '"'"'.sample('"'"' not in (E/'"'"'remote_validate.py'"'"').read_text()
print('"'"'Bounded runner and evidence sealer assembled; no execution'"'"')
'
```

## selector_regressions.json

- UTC: 2026-10-11T02:42:59.316966+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Focused inert regressions; inspected subprocess/shell entry points mocked, no CTest/timing/GPU
- full retained record: [selector_regressions.json](selector_regressions.json)

```sh
python3 -B tests/test_validation_selection.py
```

## session_snapshot.json

- UTC: 2026-10-11T02:40:48.406563+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Documented session availability only; no GPU workload/session creation
- full retained record: [session_snapshot.json](session_snapshot.json)

```sh
colab sessions
```

## session_status.json

- UTC: 2026-10-11T02:43:08.580899+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Replacement identity/health only; no workloads
- full retained record: [session_status.json](session_status.json)

```sh
colab status --session cpu-gpu-bounded-validation-v3
```

## validation_progress_read.json

- UTC: 2026-10-11T03:02:33.486065+00:00
- cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`
- exit: `0`
- scope: Read existing remote validation logs only; no new workload
- full retained record: [validation_progress_read.json](validation_progress_read.json)

```sh
colab exec --session cpu-gpu-bounded-validation-v3 --file results/raw/bounded_resume_20261011T024034091796Z/remote_progress_read.py --timeout 60
```

## Remote environment leaf diagnostics

```sh
nvidia-smi --query-gpu=name,uuid,driver_version,memory.total,memory.free --format=csv
```

Exit 0; environment/resource observation only. Full output: remote_environment.json.

```sh
nvcc --version
```

Exit 0; environment/resource observation only. Full output: remote_environment.json.

```sh
c++ --version
```

Exit 0; environment/resource observation only. Full output: remote_environment.json.

```sh
cmake --version
```

Exit 0; environment/resource observation only. Full output: remote_environment.json.

```sh
python3 --version
```

Exit 0; environment/resource observation only. Full output: remote_environment.json.

```sh
lscpu
```

Exit 0; environment/resource observation only. Full output: remote_environment.json.

```sh
free -b
```

Exit 0; environment/resource observation only. Full output: remote_environment.json.

```sh
df -B1 /content
```

Exit 0; environment/resource observation only. Full output: remote_environment.json.

## Read-only final inspection and retained harmless lookup errors

Read-only inspection used cat/sed/rg, JSON parsing and SHA-256 over evidence/source; no external workload calls. One compound lookup attempted nonexistent `src/cpu_gpu_comparison_main.cu` and `metadata_cpu-sanitize/generated/build_metadata.hpp`; rg/cat reported missing paths, final ls exited0. Corrected inspected paths were `src/cuda/comparison_resources.cu` and generated/Debug/{benchmark_build.hpp,parallel_build.hpp,source_hashes.json}. These errors did not trigger execution or alter files.

The first v2 static review used a persistent Colab kernel and returned CLI0 with a ValueError. The isolated retry retained that failure, launched a fresh python3 -B process and passed. No discovery occurred during the rejected check.

The two local fixture harness errors are retained in fixture_focus.json and fixture_focus_corrected.json; corrected fixture_focus_final.json passed9/9 with subprocess/shell entry points blocked. Initial real Release group failure is preserved in downloaded_failed/evidence/validation_commands/cpu_release_ctest.json (exit8).
