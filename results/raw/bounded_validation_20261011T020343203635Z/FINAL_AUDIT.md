# Bounded CPU/GPU validation audit

Date: 2026-10-11 UTC. Repository: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`.
This report closes the authorized coordinated preparation attempt, not the outstanding CPU/sanitizer gates. No study execution is authorized.

| Stage | Result | Current evidence |
|---|---|---|
| 0 — baseline | PASS | Latest blocker seal, frozen inputs and baseline source/build hashes verified before changes; Git unavailable (child128); manifest identity used. |
| 1 — test-only diagnostics | PASS | Minimal source changes statically reviewed, isolated builds passed, actual prepared-GPU/public-registry worker diagnostics passed. |
| 2 — eligibility classification | PASS | Version2 policy, strict independent anchors and explicit framework exceptions;9 policy tests passed; incomplete current bundle rejected. Legacy launch policy unchanged. |
| 3 — replacement T4 and build | PASS | One replacement created, reviewed185-file source bundle verified on both sides;3 fresh configurations/builds passed. |
| 4A — guarded CPU regression | BLOCKED | Static gate rejected new Dart metadata before discovery. No CPU CTest suite executed. |
| 4B — ASan/UBSan correctness | BLOCKED | Debug sanitizer build passed; same unsupported Dart metadata. No sanitizer tests executed. |
| 4C — prepared GPU correctness | PASS |163 inputs;489 output checks;489 invalid-operation rejections;0 failures/skips. |
| 4D — all-size resources | PASS |3 frozen sizes, prepared/default-parameter workspace queries and bounded diagnostic allocation checks; limits passed. |
| 4E — actual workers | PASS |12 untimed public/registry calls, correct output; actual team1 below32768 and2 at/above threshold. |
| 5 — consolidated evidence/integrity | PASS | Final seal records exact preservation, explicit exceptions, additive files and downloaded remote evidence. |

## Baseline, review and protected identities

The latest plan reviewed was `results/raw/cpu_gpu_blocker_plan_20261011T015333577826Z/{FINAL_AUDIT.md,COMMANDS.md,FINAL_INTEGRITY.json}`. AGENTS, README, roadmap, experiment protocol, provenance/analyzer/selector/guard, CMake registrations, prepared implementation, public parallel API and bounded-resource implementation were inspected. Two parallel read-only reviewers inspected diagnostics and policy paths; neither executed workloads or edited files.

The authoritative frozen inputs are:

- `docs/CPU_GPU_COMPARISON_PROTOCOL_v1.md`: `7738d21ff0ea611c04a557418182ab562769b568c7dc0b898ca5d50280e21c70`.
- `docs/studies/cpu_gpu_comparison_v1.matrix.json`: `29f9f2765e466a88fc3a7b6e590b1c38dd1ebe5f4f003a37e02aabc9b7074833`.
- `docs/studies/cpu_gpu_comparison_v1.resources.csv`: `324a67c9668d258366f738348ad853cbadd65ce4edd6f34b3ec16f4baaafeaab`.
- `docs/studies/cpu_gpu_comparison_v1.freeze.json`: `518ac535473e50fb61dab3a70858bdfe42dfdb43570f649174f44bffe40e1ac6`.

The26 trusted anchors retain their v1 meanings. Exactly3 current framework exceptions are explicitly recorded and independently pinned in the new policy: CMake, prepared header and prepared implementation. The80-file production/header/dependency baseline likewise differs only at those3 paths. No production sorting algorithm changed. `src/cuda/cub_sort.cu` remains `b6d7f37c7494587fc6e4a676c00c166dc322d31cce96710811e3a4cb9cd8b9cb`; CUB3.0.1/300001 commit `f19d875da0d8bfb2e38c109b2b40522b8abbbbc3` pin file remains `477b1ee70b0a9113c9f98b263c19a31d05ccee54f45ce8476aec4cc98965ced1`.

## Changes and design

Seven original files modified; eight project files added. Per-file before/after hashes and final diffs are in [PRESERVATION_VERIFIED.json](PRESERVATION_VERIFIED.json) and `*.final.diff`.

- `include/benchmark/cuda_timing.hpp`, `src/cuda/cub_timing.cu`: explicit `execute_untimed` using the actual prepared transfer/CUB/output helpers and final synchronization. Existing `sample()` invokes those helpers with identical timing boundaries; mechanical helper expansion equals the old sample body exactly. No production adapter changes. Constructor event creation remains setup; the new call makes no timing measurements.
- `CMakeLists.txt`: additive, default-off `MAB_ENABLE_VALIDATION_DIAGNOSTICS`; separately selectable correctness registrations and an output-only supporting library. No dependency on timing-bearing integration tests.
- `scripts/non_timing_tests.py`: versioned source/selection manifest, explicit diagnostic opt-in; existing static build guard, canonical path identity, callback checks and rechecks preserved.
- `tests/test_cpu_gpu_comparison.py`: historical synthetic fixture uses independently trusted historical source anchors, rather than misrepresenting the intentionally extended current source as historical. Legacy analyzer and launch rules unchanged.
- `README.md`, `docs/ROADMAP.md`: actual bounded status and remaining metadata-review blocker. These two informational updates followed source transfer; all149 reviewed executable-source files remain identical to the transferred version.
- Added `tests/test_cuda_prepared_correctness.cpp`, `tests/test_parallel_workers.cpp`, `tests/test_validation_policy.py`, `tests/test_validation_selection.py`.
- Added `scripts/cpu_gpu_validation_policy.py`, `docs/CPU_GPU_VALIDATION_POLICY_v2.{json,md}`, `docs/NON_TIMING_TEST_SELECTION_v2.json`.

The separate classifier distinguishes correctness, timing smoke, pilot and full-prerequisite artifacts; validates independently supplied current context, exact protected identities, record hashes/status and coverage. All assessments retain `study_eligible=false` and `execution_authorized=false`. It is not an execution attestation by itself: a trusted launcher must parse command output before asserting coverage. Historical classifications and v1 analyzer/launcher are unchanged; those launch paths intentionally cannot approve this extended source revision. Full-prerequisite candidates still require compatible additional evidence and independent review. No such candidate was produced. [PARTIAL_CLASSIFICATION.json](PARTIAL_CLASSIFICATION.json) shows rejection of this incomplete run.

## Selection and test results

Static/mocked evidence preserves the exact default19 names:

`baselines, cli, comparisons, cpu_gpu_comparison_framework, cuda_benchmark_analysis, cuda_preflight, cuda_sort_handoff, datasets, environment_manifest, memory, memory_unsupported, mergesort, metrics_cli, pdqsort, quicksort, radixsort, searching, structures, timsort`.

Explicit diagnostic opt-in adds `validation_policy` and `parallel_workers_correctness`; GPU opt-in additionally permits `cuda_prepared_correctness`. Timing-bearing `parallel_mergesort`, GPU benchmark integration, and other timing targets remain excluded. [TEST_INVENTORY.json](TEST_INVENTORY.json) classifies every registration and the resource diagnostic. Mocked clean fixtures verify selection without CTest. No actual discovery was performed.

| Focused local test | Command | Child exit | Outcome |
|---|---|---|---|
| Policy initial attempt | `python3 -B tests/test_validation_policy.py` |1|9 methods;1 fixture-construction error (duplicate keyword); retained. |
| Policy corrected fixture | same |0|9/9 passed; production requirements unchanged. |
| Inert selection | `python3 -B tests/test_validation_selection.py` |0|3/3 passed; subprocess/discovery mocked. |
| Existing inert guard/path | `python3 -B tests/test_ctest_build_guard.py` |0|36/36 passed; all external subprocess entry points mocked. |

The Release and sanitizer suites were intended to execute21 approved CPU groups each, but **0 groups were discovered/executed** because the pre-discovery gate rejected metadata. Thus no suite pass, skip count, sanitizer runtime success, leak-detection result or race-freedom claim is made. Leak detection was not disabled; no sanitizer test was run.

## Replacement environment and builds

Original session was previously documented unrecoverable; current `colab sessions` reported none before creation. Exactly one authorized replacement was created by `colab new --session cpu-gpu-bounded-validation --gpu T4` (child0, semantic READY), actual session `gpu-t4-s-kkb-usw4b1-2i9q6dkvjw07d`.

Observed environment: Tesla T4 CC7.5; UUID `GPU-cd5085b4-b6d1-d004-07cc-6f1b32e3a0a2`; driver580.82.07; CUDA compiler13.0.88, runtime API13000; GCC13.3.0; CMake3.31.10; Python3.13.15; libgomp/OpenMP4.5. Linux6.6.122+/glibc2.39. Two logical CPUs, one reported physical core, Intel Xeon@2GHz. Initial RAM available12,565,610,496 B of13,605,822,464 B; disk available75,467,313,152 B; GPU free14913MiB of15360MiB. These snapshots do not guarantee later availability or control over contention/frequency/thermal behavior.

Exclusive root: `/content/mab_bounded_20261011T020343203635Z`; source and three new build directories inside. Existing remote content inspected; no overwritten project. Only reviewed source/build inputs and frozen documents transferred; results/builds/credentials excluded.185 members verified before/after extraction. Archive SHA256 `03de3a45743206244c480195de4629b8d440139f0fc5e236981f1f9cecac7fa5`.

All3 fresh configure/build pairs exited0. Exact argv/cwd/logs are under `downloaded/evidence/build_commands/` and expanded in [COMMANDS.md](COMMANDS.md): CPU Release/CUDA-OFF, CPU Debug/ASan+UBSan/CUDA-OFF, GPU Release/CUDA-ON/comparison-ON/architecture75, all OpenMP-ON and diagnostics-ON; build `--parallel 2`. No previous build was reused or replaced. Current executable/build hashes and shared parallel library identity are recorded in `BUILD_COMPLETE.json`, `LINK_BINDINGS.json`, and direct command records.

## Blocking metadata mismatch — no workaround

`remote_static_selection.json` retains `ValueError: unknown/missing Dart setting` from the shared static pre-discovery gate. The Colab transport exited0 despite the traceback; **the operation failed semantically** and produced no approved plan. No discovery callback, CTest invocation or selected test followed. `remote_validate.py` was prepared but never executed.

Read-only snapshots of all3 build trees show new empty `TLSVerify` and `TLSVersion` keys from CMake3.31; `MemoryCheckCommand` is `/usr/local/cuda/bin/compute-sanitizer` rather than reviewed `MEMORYCHECK_COMMAND-NOTFOUND`. The latter would also violate the exact metadata policy. Site and absolute CMake-path differences are retained as observations, not additionally asserted blockers where existing rules already allow them. [DART_GUARD_BLOCKER.json](downloaded/evidence/DART_GUARD_BLOCKER.json) and raw Dart files support this diagnosis. The guard and old policy were not broadened. CPU/sanitizer execution stopped as required; independent reviewed direct diagnostics continued.

## Direct untimed diagnostics

Every direct command below exited0; logs retain full stdout/stderr and executable hashes before/after in `downloaded/evidence/direct_commands/`.

- `gpu-release/cpu_gpu_comparison --describe`: metadata only.
- `gpu-release/test_cuda_prepared_correctness`:163 bounded inputs,489 full-vector oracle checks and489 expected invalid-operation rejections. Empty/small/extrema/duplicates and deterministic distributions through65537; actual prepared transfer/CUB/output path;0 failures/skips. No event timing, warmups or benchmark repetitions.
- `gpu-release/cpu_gpu_comparison --resources N` for1025,65537,1000000: isolated same-parameter workspace queries and bounded allocation checks; no sorting execution. Production adapter itself not instrumented.
- `gpu-release/test_parallel_workers`:12 public/registry calls at0,1,32767,32768,32769,65537; all full-vector comparisons correct. Runtime team1 below32768; team2 at/above32768. Request2, `OMP_DYNAMIC=FALSE`, `OMP_THREAD_LIMIT=2`, `OMP_MAX_ACTIVE_LEVELS=1`, `OMP_PROC_BIND=FALSE`, `OMP_WAIT_POLICY=PASSIVE`. Team size does not prove task participation or independent physical cores. Binary path/hash and common linked `libmab_parallel.a` resolve historical executable ambiguity.

No current production-GPU475/1900 rerun or broad regression suite is claimed. Direct prepared/worker diagnostics are independent of unsupported CTest metadata.

## Workspace/resource results

| N | Prepared query/request B | Production-parameter query/request B | Diagnostic key-buffer request B | Conservative combined device estimate B | Host payload estimate B |
|---:|---:|---:|---:|---:|---:|
|1025|1|1|8200|16402|24600|
|65537|279295|279295|524296|1607182|1572888|
|1000000|4178687|4178687|8000000|24357374|24000000|

Each diagnostic key request total is8N. Workspace requests succeeded on both paths. Conservative full-study device estimate is16N+both queried workspace sizes; host known payload estimate24N excludes runtime/allocator overhead. Physical GPU allocation footprint was **not measured**. The diagnostic allocates two key buffers and two workspaces, not the complete benchmark workload. CUB SortKeys with null temporary storage queries sizing; no sort trial follows. Workspace cap each67,108,864 B and combined planning cap268,435,456 B remained unchanged and passed. During checks GPU free15,527,116,800 B; host available12,503,564,288 B; disk free75,301,515,264 B; host/disk required headroom1GiB passed. cgroup/affinity retained in [WORKSPACE_RESOURCES.json](downloaded/evidence/WORKSPACE_RESOURCES.json). Point-in-time feasibility is not launch approval or guaranteed future capacity.

## Warnings, failures and integrity

CPU/sanitizer configure/build warning counts0. Fresh GPU configure0 warnings; GPU build**367** diagnostics, all `warning: style of line directive is a GCC extension` in nvcc-generated preprocessing/generated sources and mapped source locations. No suppression added; no other warning category detected. Historical341 is not this run's count. Detailed counts/source prefixes and examples retained in [WARNING_CLASSIFICATION.json](WARNING_CLASSIFICATION.json). No unsupported explanation of the count difference or performance claim is made.

Initial synthetic policy fixture error and subsequent correction remain retained. Missing optional guessed local source paths during read-only inspection are documented in command inventory; actual interfaces were subsequently located. No credentials/tokens/codes/cookies were requested or intentionally written; diagnostic environment capture was allowlisted and CLI URLs/credential-shaped outputs redacted by the recorder.

All11,910 pre-existing results retain identical membership/content (new evidence directory excluded), not merely matching counts. All65 existing local build-metadata hashes unchanged. All177 original project paths present, exactly7 authorized modifications;8 new project files. Frozen inputs, v1 manifests, old source anchors, production adapter/CUB pin, historical studies and earlier review evidence preserved. The3 explicit framework exceptions are not described as unchanged. Downloaded remote archive SHA256 `46dc7fc6bd00b95125995f1e8427a07dc714750976e5ae373462f6cfc059989e`; all43 sealed members plus remote seal verified. Source/build identities were also rechecked remotely before sealing. [FINAL_INTEGRITY.json](FINAL_INTEGRITY.json) seals this run's evidence; `BEFORE.json` and `PRESERVATION_VERIFIED.json` retain before/after maps.

## Next gate and authorization boundary

Independently review the exact CMake3.31 Dart additions and discovered memory-check command; if approved, implement a narrowly versioned metadata extension with inert fail-closed regressions. Then obtain/pass a new guarded CPU Release and ASan/UBSan correctness run. Do not bypass the pre-discovery gate or infer CPU/sanitizer success from the successful builds or direct GPU diagnostics. Any later legacy study-policy integration and final authorization remain separate.

Benchmark samples, pilot measurements, warmups, timing-bearing CTest executions and full-study trials in this attempt: **0**. No100M, study launch, commits, pushes, Git initialization, destructive cleanup or driver installation.

NO-GO — one or more required validation gates remain open
