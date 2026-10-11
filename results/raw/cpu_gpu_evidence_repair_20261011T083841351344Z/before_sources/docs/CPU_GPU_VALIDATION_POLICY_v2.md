# Bounded correctness validation policy v2

This separately authorized extension preserves the frozen comparison protocol,
matrix, resources, v1 selection manifest and historical artifacts. It does not
authorize measurements or change the legacy analyzer/launch gates.

`CPU_GPU_VALIDATION_POLICY_v2.json` records exact approved identities for the
minimal prepared-framework access and additive CMake registration. Its digest is
pinned in `scripts/cpu_gpu_validation_policy.py`. Production CUB and dependency
identities still come from the independently protected v1 freeze. The new selector
snapshot is `NON_TIMING_TEST_SELECTION_v2.json`; unknown source or build metadata
still fails closed through the existing pre-discovery/path-identity guard.

`MAB_ENABLE_VALIDATION_DIAGNOSTICS=ON` adds opt-in `validation_policy`,
`parallel_workers_correctness`, and, when CUDA sorting is enabled,
`cuda_prepared_correctness`. The default selector preserves the original 19 CPU
names. `--allow-diagnostics` explicitly includes the new correctness targets;
GPU selection additionally requires `--allow-gpu-correctness`. Timing targets,
including `parallel_mergesort` and `cuda_benchmark_gpu_framework`, remain excluded.
Review the returned plan and metadata before executing its guarded selection.

The prepared test uses the actual session's H2D/CUB/D2H helpers without clocks,
event records, event elapsed queries, warm-ups or timed repetitions. The existing
sample event/host boundaries are unchanged. Expected coverage is 163 inputs,
489 oracle output checks and 489 invalid-operation rejections. Event creation in
the existing constructor remains setup, not performance measurement. GPU
unavailability returns77 and leaves the gate open.

The worker test makes 12 untimed public/registry calls at N=0,1,32767,32768,32769,
65537. It checks full-vector equality and the runtime-reported team1 below / team2
at or above the threshold. A team count is neither task participation nor physical
CPU count. The launcher must capture the canonical executable's SHA256, linked
build/source identity, runtime and CPU topology; the test does not self-hash.

Four evidence kinds are distinct: correctness validation, timing smoke, pilot
measurements and full-study prerequisites. The offline classifier requires an
independently supplied current session/source/build/binary context, retained
record hashes and explicit complete per-gate coverage. The evidence assembler
must parse actual command logs before supplying those assertions; the classifier
alone does not prove execution. Missing, stale, failed, skipped or mismatched
evidence is rejected. Correctness alone never satisfies timing-framework coverage.

Every assessment keeps `study_eligible=false` and `execution_authorized=false`.
A full-prerequisite candidate additionally requires production-GPU correctness,
current compatible timing smoke/pilot evidence and independent review. Those
timing workloads are not authorized by the bounded validation task. Existing v1
artifacts retain their original identities and classification; the old launcher
cannot use this revision without a separate reviewed policy integration.

Separate sanitizer builds keep CUDA disabled. Start with leak detection enabled;
disable it only on the documented LeakSanitizer/ptrace failure. Retain all other
failures and stop the affected gate. No performance or race-freedom claim follows
from correctness or sanitizer success.
