# Exact commands and statuses

Authorization: reviewed-source transfer and isolated build/narrow correctness validation only. No study, performance smoke, warm-up or measured trials.
The local wrapper is `python3 -B results/raw/isolated_colab_build_20261011T010417197263Z/record.py NAME SCOPE TIMEOUT CHILD_ARGV...`; individual JSON files retain full argv/cwd/status/stdout/stderr.
Initial direct read/search commands and exclusive baseline creation are retained in EARLY_COMMANDS.json. All had overall shell exit 0; the first compound Git check printed missing-repository diagnostics. The isolated recorded Git command below independently returned 128.

## bundle.json

```text
python3 -B results/raw/isolated_colab_build_20261011T010417197263Z/make_bundle.py
```
Exit 0. Read/hash reviewed source and create allowlisted archive only.

## download.json

```text
colab download /content/mab_isolated_20261011T010417197263Z/validation_evidence.tar.gz results/raw/isolated_colab_build_20261011T010417197263Z/downloaded_validation.tar.gz --session cpu-gpu-validation
```
Exit 0. Download new isolated validation logs/metadata archive; no historical evidence overwritten.

## extract.json

```text
colab exec --session cpu-gpu-validation --file /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/isolated_colab_build_20261011T010417197263Z/remote_extract.py --timeout 120
```
Exit 0. Verify remote archive, inspect regular safe members, exclusively extract, verify frozen/source hashes.

## git_status.json

```text
git status --short
```
Exit 128. Read-only source revision check; absent Git metadata is retained, no Git initialization.

## isolated_build_validation.json

```text
colab exec --session cpu-gpu-validation --file /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/isolated_colab_build_20261011T010417197263Z/remote_build_validate.py --timeout 1500
```
Exit 0. Authorized isolated Release configure/build, direct CPU/CUB correctness tests, metadata-only describe; no timing trials.

## remote_destination_check.json

```text
colab exec --session cpu-gpu-validation --file /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/isolated_colab_build_20261011T010417197263Z/remote_check.py --timeout 90
```
Exit 0. GPU/tool metadata and absence of unique destination; no CUDA execution.

## session_status.json

```text
colab status --session cpu-gpu-validation
```
Exit 0. Session metadata only.

## upload.json

```text
colab upload results/raw/isolated_colab_build_20261011T010417197263Z/reviewed_source.tar.gz /content/mab_source_20261011T010417197263Z.tar.gz --session cpu-gpu-validation
```
Exit 0. Transfer only the verified 153-file reviewed source bundle; no results/credentials.

## Remote build/validation commands

```text
cmake -S /content/mab_isolated_20261011T010417197263Z/source -B /content/mab_isolated_20261011T010417197263Z/build-release -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS= '-DCMAKE_CXX_FLAGS_RELEASE=-O3 -DNDEBUG' -DMAB_ENABLE_OPENMP=ON -DBUILD_TESTING=ON -DMAB_ENABLE_CUDA=ON -DMAB_ENABLE_CUDA_SORT=ON -DMAB_ENABLE_CPU_GPU_COMPARISON=ON -DMAB_ENABLE_SANITIZERS=OFF -DCMAKE_CUDA_ARCHITECTURES=75 -DCMAKE_CUDA_FLAGS= '-DCMAKE_CUDA_FLAGS_RELEASE=-O3 -DNDEBUG'
```
cwd: /content/mab_isolated_20261011T010417197263Z/source; exit 0.

```text
cmake --build /content/mab_isolated_20261011T010417197263Z/build-release --target cpu_gpu_comparison comparison_input test_cuda_sorting test_mergesort --parallel 2
```
cwd: /content/mab_isolated_20261011T010417197263Z/source; exit 0.

```text
/content/mab_isolated_20261011T010417197263Z/build-release/test_mergesort
```
cwd: /content/mab_isolated_20261011T010417197263Z/source; exit 0.

```text
/content/mab_isolated_20261011T010417197263Z/build-release/test_cuda_sorting
```
cwd: /content/mab_isolated_20261011T010417197263Z/source; exit 0.

```text
/content/mab_isolated_20261011T010417197263Z/build-release/cpu_gpu_comparison --describe
```
cwd: /content/mab_isolated_20261011T010417197263Z/source; exit 0.

No CTest was invoked. Tests are existing direct executable targets audited for timing behavior before execution. comparison --describe returns before input parsing, allocation, workspace diagnostics or trial invocation.
Remote control scripts are retained verbatim alongside these logs. They write only the new isolated /content directory, its new evidence archive, and the explicitly uploaded source archive.
Finalization: `python3 -B results/raw/isolated_colab_build_20261011T010417197263Z/finalize.py` (exit 0 when this final seal is present). It validates/extracts new evidence, compares preservation hashes and writes only this new local evidence directory. Polling awaited the recorded CLI commands. apply_patch authored only evidence-control files.
