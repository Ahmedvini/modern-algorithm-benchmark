# Deferred GPU archive index — CPU-only release

GPU execution, CUDA/CUB performance and CPU-versus-GPU comparison are outside the
2026-10-11 CPU-only release. This is an in-place archive index: no GPU source,
protocol, pin, raw measurement or audit was deleted, moved or rewritten.

|Material|Preserved location|Release interpretation|
|---|---|---|
|Optional CUDA implementation and runtime probe|`src/cuda/`, CUDA-related public headers, `cmake/`, CUDA targets in `CMakeLists.txt`|Deferred implementation; CPU-only builds disable CUDA options|
|Reviewed dependency identity|`third_party/cub/`|CUB 3.0.1 pin unchanged; not a CPU result input|
|Cloud execution instructions|`docs/CUDA_EXECUTION_GUIDE_v1.md`, `docs/CUDA_SORT_VALIDATION_GUIDE_v2.md`|Historical/reproducibility guidance, not a current GPU allocation claim|
|CUDA correctness evidence|`results/raw/cub_correctness_colab_20261009T223853955936Z/`|Historical T4 correctness; not a full comparison|
|Prepared-buffer timing protocol and smoke|`docs/CUDA_TIMING_PROTOCOL_v1.md`, `results/raw/cuda_timing_20261009T231303050084Z/`|Earlier standalone GPU smoke measurements; excluded from CPU-only report|
|Accepted six-dataset comparison pilot|`results/raw/cpu_gpu_pilot_20261010T001232473460Z/`, `results/processed/cpu_gpu_pilot_20261010T001232473460Z/REPORT.md`|Pilot only; never presented as full-study data|
|Frozen full comparison specification|`docs/CPU_GPU_COMPARISON_PROTOCOL_v1.md`, `docs/studies/cpu_gpu_comparison_v1.matrix.json`, `.resources.csv`, `.freeze.json`|48 datasets, 1,200 measured calls, 240 warm-ups: not executed|
|Launch/evidence/selection controls|`scripts/run_cpu_gpu_study.py`, related `scripts/cpu_gpu_*` and `scripts/non_timing_tests.py`|Enforcement preserved; CPU scope is not approval or a bypass|
|Subsequent failed/blocked validation and recovery|Existing timestamped `results/raw/cpu_gpu_*`, `gpu_*`, `bounded_*`, `ctest_*`, and `isolated_colab_*` evidence|Historical record retained unchanged|

Current CPU-only tables, figures and conclusions consume no GPU summary, timing
or comparison row. Historical pilots do not establish outcomes for the frozen
48-dataset protocol. No full CPU/GPU launch, completion, speedup or acceleration
is claimed. GPU resource availability and an independently protected study
approval remain dependencies of any future GPU release, not this release.

Reopening GPU work would require an explicit scope change, genuine trusted
approval accepted by the existing guard, identity-matched build/correctness and
resource evidence, and a separate launch decision. Existing frozen inputs and
historical GPU evidence must remain immutable.
