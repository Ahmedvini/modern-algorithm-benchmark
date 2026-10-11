# Exact commands and statuses

Authorization: reviewed-source transfer and isolated build/narrow correctness validation only. No study, performance smoke, warm-up or measured trials.
The local wrapper is `python3 -B results/raw/isolated_colab_revalidation_20261011T011459127026Z/record.py NAME SCOPE TIMEOUT CHILD_ARGV...`; individual JSON files retain full argv/cwd/status/stdout/stderr.
Exclusive baseline creation and evidence-script authoring commands are retained in EARLY_COMMANDS.json (exit0). All inspection commands are individually captured. Git status/revision returned128; the initial source checker returned1 due to seal path conventions, diagnosed and corrected in a new v2 checker before transfer.

## download.json

```text
colab download /content/mab_isolated_20261011T011459127026Z/validation_evidence.tar.gz results/raw/isolated_colab_revalidation_20261011T011459127026Z/downloaded_validation.tar.gz --session cpu-gpu-validation
```
Exit 0. Retrieve only new isolated validation logs/metadata archive into absent local evidence path.

## extract.json

```text
colab exec --session cpu-gpu-validation --file /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/isolated_colab_revalidation_20261011T011459127026Z/remote_extract.py --timeout 120
```
Exit 0. Remote archive digest, safe member inspection, exclusive extraction and source/frozen hash verification.

## git_revision.json

```text
git rev-parse HEAD
```
Exit 128. Read-only Git revision check; no initialization.

## independent_audit.json

```text
cat results/raw/ctest_path_independent_review_20261011T000547578754Z/FINAL_AUDIT.md
```
Exit 0. Read-only independent-review conclusions and limitations.

## instructions_and_evidence.json

```text
cat AGENTS.md README.md docs/ROADMAP.md docs/EXPERIMENT_PROTOCOL.md results/raw/ctest_path_independent_review_20261011T000547578754Z/FINAL_AUDIT.md results/raw/ctest_path_independent_review_20261011T000547578754Z/COMMANDS.md results/raw/ctest_path_independent_review_20261011T000547578754Z/FINAL_INTEGRITY.json results/raw/cpu_gpu_readiness_20261011T004018152238Z/FINAL_AUDIT.md results/raw/cpu_gpu_readiness_20261011T004018152238Z/COMMANDS.md results/raw/cpu_gpu_readiness_20261011T004018152238Z/FINAL_INTEGRITY.json results/raw/colab_t4_diagnostics_20261011T005409276199Z/FINAL_AUDIT.md results/raw/isolated_colab_build_20261011T010417197263Z/FINAL_AUDIT.md results/raw/isolated_colab_build_20261011T010417197263Z/COMMANDS.md results/raw/isolated_colab_build_20261011T010417197263Z/FINAL_INTEGRITY.json
```
Exit 0. Read-only instructions, latest readiness/build and independent-review evidence.

## isolated_build_validation.json

```text
colab exec --session cpu-gpu-validation --file /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/isolated_colab_revalidation_20261011T011459127026Z/remote_build_validate.py --timeout 1500
```
Exit 0. Fresh isolated configure/build; existing direct Merge Sort and CUB correctness tests; comparison --describe only; no CTest or timing trials.

## pre_transfer_gate.json

```text
python3 -B results/raw/isolated_colab_revalidation_20261011T011459127026Z/pre_transfer_gate.py
```
Exit 0. Fresh pre-upload source/archive, exact session/GPU identity and absent exclusive destination verification.

## remote_destination_check.json

```text
colab exec --session cpu-gpu-validation --file /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/isolated_colab_revalidation_20261011T011459127026Z/remote_check.py --timeout 90
```
Exit 0. Read-only destination absence, T4 driver/tool versions; no overwrites or workloads.

## repository_status.json

```text
git status --porcelain=v1
```
Exit 128. Read-only Git working-tree check; no initialization.

## result_gate.json

```text
python3 -B results/raw/isolated_colab_revalidation_20261011T011459127026Z/result_gate.py
```
Exit 0. Read retained remote completion/individual command statuses and narrow correctness outputs; no workloads.

## seal_format_diagnostic.json

```text
python3 -B -c 'import json,hashlib;from pathlib import Path;r=Path.cwd();names=["ctest_path_independent_review_20261011T000547578754Z","cpu_gpu_readiness_20261011T004018152238Z","colab_t4_diagnostics_20261011T005409276199Z","isolated_colab_build_20261011T010417197263Z"]
for name in names:
 d=r/"results/raw"/name;s=json.loads((d/"FINAL_INTEGRITY.json").read_text());m=s["evidence_sha256"];print(name,"keys",list(m)[:2]);bad=[]
 for p,h in m.items():
  candidates=[(d/p),(r/p)];matches=[str(x) for x in candidates if x.is_file() and hashlib.sha256(x.read_bytes()).hexdigest()==h]
  if not matches:bad.append(p)
 print("unmatched_entries",bad)'
```
Exit 0. Read-only diagnosis of retained manifest path conventions after failed pre-transfer verification; no transfer/build.

## session_identity.json

```text
colab status --session cpu-gpu-validation
```
Exit 0. Read-only existing session identity; no provisioning.

## source_review.json

```text
python3 -B results/raw/isolated_colab_revalidation_20261011T011459127026Z/verify_reviewed_source.py
```
Exit 1. Static trusted-hash, exact source membership, previous independent-review and evidence-seal verification; no workload.

## source_review_v2.json

```text
python3 -B results/raw/isolated_colab_revalidation_20261011T011459127026Z/verify_reviewed_source_v2.py
```
Exit 0. Static verification with explicit existing seal path conventions; original failed verifier/log retained.

## transferred_source_gate.json

```text
python3 -B results/raw/isolated_colab_revalidation_20261011T011459127026Z/transfer_gate.py
```
Exit 0. Verify complete remote source identity and frozen markers before any configure/build.

## upload.json

```text
colab upload results/raw/isolated_colab_revalidation_20261011T011459127026Z/reviewed_source.tar.gz /content/mab_source_20261011T011459127026Z.tar.gz --session cpu-gpu-validation
```
Exit 0. Transfer only hash-verified allowlisted source/build files to absent unique remote archive path.

## validation_scope_inspection.json

```text
cat CMakeLists.txt cmake/cuda.cmake cmake/benchmark_metadata.cmake src/benchmark/cpu_gpu_main.cpp src/cuda/cub_sort.cu tests/test_cuda_sorting.cpp tests/test_mergesort.cpp tests/test_integer_sorts.hpp docs/CPU_GPU_DRIVER_REVIEW_v1.json docs/CUDA_SORT_VALIDATION_GUIDE_v2.md
```
Exit 0. Read-only approved direct test sources, helpers, CLI early-return path and existing CMake integration.

## Remote build/validation commands

```text
cmake -S /content/mab_isolated_20261011T011459127026Z/source -B /content/mab_isolated_20261011T011459127026Z/build-release -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS= '-DCMAKE_CXX_FLAGS_RELEASE=-O3 -DNDEBUG' -DMAB_ENABLE_OPENMP=ON -DBUILD_TESTING=ON -DMAB_ENABLE_CUDA=ON -DMAB_ENABLE_CUDA_SORT=ON -DMAB_ENABLE_CPU_GPU_COMPARISON=ON -DMAB_ENABLE_SANITIZERS=OFF -DCMAKE_CUDA_ARCHITECTURES=75 -DCMAKE_CUDA_FLAGS= '-DCMAKE_CUDA_FLAGS_RELEASE=-O3 -DNDEBUG'
```
cwd: /content/mab_isolated_20261011T011459127026Z/source; exit 0.

```text
cmake --build /content/mab_isolated_20261011T011459127026Z/build-release --target cpu_gpu_comparison comparison_input test_cuda_sorting test_mergesort --parallel 2
```
cwd: /content/mab_isolated_20261011T011459127026Z/source; exit 0.

```text
/content/mab_isolated_20261011T011459127026Z/build-release/test_mergesort
```
cwd: /content/mab_isolated_20261011T011459127026Z/source; exit 0.

```text
/content/mab_isolated_20261011T011459127026Z/build-release/test_cuda_sorting
```
cwd: /content/mab_isolated_20261011T011459127026Z/source; exit 0.

```text
/content/mab_isolated_20261011T011459127026Z/build-release/cpu_gpu_comparison --describe
```
cwd: /content/mab_isolated_20261011T011459127026Z/source; exit 0.

No CTest was invoked. Tests are existing direct executable targets audited for timing behavior before execution. comparison --describe returns before input parsing, allocation, workspace diagnostics or trial invocation.
Remote control scripts are retained verbatim alongside these logs. They write only the new isolated /content directory, its new evidence archive, and the explicitly uploaded source archive.
Finalization: `python3 -B results/raw/isolated_colab_revalidation_20261011T011459127026Z/finalize.py` (exit 0 when this final seal is present). It validates/extracts new evidence, compares preservation hashes and writes only this new local evidence directory. Polling awaited the recorded CLI commands. apply_patch authored only evidence-control files.
