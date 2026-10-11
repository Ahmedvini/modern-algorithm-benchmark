# Full frozen CPU/GPU matrix tooling v1

This implementation note extends tooling, not the frozen experiment protocol.
`CPU_GPU_COMPARISON_PROTOCOL_v1.md`, its matrix/resource CSV/freeze, CUB3.0.1
pin, public adapters and timing worker remain unchanged. No study authorization
is granted by this document or by an execution flag.

The matrix's stored study-cell order contains48 datasets: N1025/65537/1000000,
five seeded workloads x seeds1729/42/2718 plus one signed-edge dataset per size.
Each cell uses its exact stored SHA-based base order and cyclic measured orders:
five modes, W1/R5,30 calls/cell,1440 total,1200 measured/240 warm-ups.
Primary rows960 measured/192 warm-ups; prepared rows240/48, four diagnostics per
call. Prepared values are not four calls and cannot supply primary ratio denominators.

## Planning and future execution

```sh
python3 scripts/run_cpu_gpu_study.py --dry-run \
  --executable build/NEW_GPU_RELEASE/cpu_gpu_comparison \
  --input-tool build/NEW_GPU_RELEASE/comparison_input \
  --output results/raw/NEW_FULL_COMPARISON
```

Dry-run is deterministic, creates no output and launches no child process. It
prints all48 input/worker command pairs, offsets0..1410, expected counts,
resource formulas and frozen timeout policy. Runtime identities remain labelled
placeholders. The existing pilot CLI remains pilot-only.

The prerequisite-only command now selects the reviewed correctness subset:

```sh
python3 scripts/validate_cpu_gpu_pilot.py --prerequisites-only \
  --output results/raw/NEW_FULL_PREREQUISITES
```

That command builds and runs the fail-closed non-timing CTest selection, together
with its explicit CUDA runtime/correctness checks. It does not launch a pilot or
study. Its manifest is labelled `non_timing_correctness_v1`, `study_eligible=false`;
it **cannot satisfy the frozen full-study prerequisite gate**. The runner and
analyzer reject that subset as study prerequisites. Full protocol coverage, which
includes timing-framework tests, still requires separately authorized validation.
This repair does not execute either prerequisite workflow. See
[the safety repair](CPU_GPU_SAFETY_REPAIR_v1.md) for discovery-only commands and
the reviewed selection manifest. Actual commands and omissions belong in the audit.

After separately obtaining and reviewing a complete, current-source/current-binary,
full-protocol PREREQUISITES.json (not the correctness-only subset above), future
execution requires both that manifest and an explicit CLI latch:

```sh
# Future authorized execution only; not run for this milestone.
python3 scripts/run_cpu_gpu_study.py --execute-study \
  --executable build/NEW_FULL_PREREQUISITES/gpu-release/cpu_gpu_comparison \
  --input-tool build/NEW_FULL_PREREQUISITES/gpu-release/comparison_input \
  --prerequisites results/raw/NEW_FULL_PREREQUISITES/PREREQUISITES.json \
  --output results/raw/NEW_FULL_COMPARISON
```

No retry, resume or overwrite: the frozen protocol forbids them. Existing paths
and symlink collisions fail before subprocesses or writes inside user outputs.
All child return codes/timeouts/interruptions are retained; the same worker
restores input, validates each result and flushes attempts/results. Work remains
serial. The60s per-dataset deadline covers input generation and worker; the1800s
study deadline covers all cells. Failed/interrupted runs stop, retain the complete
planned identity list and attempt logs, and emit a partial analysis if parsable;
malformed partial evidence emits an analysis-error record instead of guessed totals.

The runner checks current source/binary prerequisite hashes, Release flags/CUB
identity, OpenMP/environment gates and **all three fresh resource queries before
any worker**. Gates retain64MiB/workspace,256MiB combined, half fresh device-free
memory,1GiB host/disk headroom and the frozen CPU quota/affinity requirements.
Logical allocation requests remain distinct from physical allocator footprint.
Current N65537 evidence is historical for any later execution VM.

## Raw evidence and independent analysis

Study metadata uses existing schema1 and matrix_part=study. It retains frozen
asset copies, plan.json, prerequisite command copies, build/source/environment
identities, compile commands/cache, all attempts/CSV/sidecars and raw hashes.
Each input's retained bytes/SHA256, generator metadata/recipe and FNV identity must
agree across modes. No clock, adapter, CUB API, transfer scope or CSV column changed.
Completion requires independent full validation, environment/source recheck and
a raw hash manifest. A contradictory/partial run cannot pass public analysis.

```sh
python3 scripts/analyze_cpu_gpu.py results/raw/EXISTING_FULL_COMPARISON \
  --output results/processed/NEW_FULL_SUMMARY.json
```

The analyzer selects pilot/study from the recorded matrix_part, never infers a
smaller matrix from available rows. It rejects wrong frozen copies/identities,
schemas, missing or duplicate trials/attempts, incorrect phases/order/threads,
nonfinite/negative metrics, contradictory correctness/markers, unsafe links and
workspace violations. Completed studies require exact raw-manifest coverage and
hashes; performance evidence additionally validates build/environment/provenance,
hashed prerequisite commands and consistency of prepared and primary build/device
metadata. Synthetic fixtures require explicit API opt-in and are rejected by the
public performance CLI.

Retained source claims are also checked against independently pinned frozen
anchors, including the production CUB adapter and dependency pin. Mutually
consistent retained source/prerequisite/build/raw hashes cannot redefine those
anchors. The existing pinned CMake review is the only permitted exception. Legacy
code-only source maps remain supported; their omitted frozen documentation is
verified directly against its frozen hash. Missing or ambiguous trust roots fail
closed.

`--allow-incomplete` reports failed/interrupted/missing measured and warm-up counts,
exits1, and suppresses all paired/cross-input comparisons for an incomplete study.
Malformed evidence is rejected rather than repaired. No stale count can establish
completion; actual rows, attempts, per-dataset/root markers must agree.

Five repeats yield per-input median/mean/sampleSD/min/max in ns; all outliers and
warm-ups remain in raw evidence. Complete studies yield144 paired host-call ratios,
using production CUB only; timer-resolution-limited ratios are null. Cross-input
summaries equally weight distinct input medians, collapsing identical fingerprints;
they do not pool repeated timings as independent datasets. Signed-edge groups have
one input. Prepared H2D/device/D2H/prepared E2E remain diagnostics. No significance,
inferential confidence intervals or universal ranking is claimed.

## Validation status and limits

Synthetic tests exercise the complete1440-record model, failure/interrupt/missing/
duplicate cases, identity/schema/thread/scope/resource gates, compatible legacy
pilot analysis, deterministic planning and summary regeneration. Orchestrator
subprocess doubles never execute a sorter; their console completion messages are
explicitly labelled synthetic, not experimental results.

See the latest AUDIT.md entry for observed CPU/GPU test totals, omissions, warnings,
integrity and the inadvertent embedded timing test deviation. No pilot or full
study is run for this milestone. Shared-cloud load/SMT/frequency/thermal/cache
confounders and device-memory safety-tool limitations remain. Full-study launch
stays **NO-GO** until tooling review, separate authorization and fresh complete
study prerequisites/resource gates on the actual execution VM.
