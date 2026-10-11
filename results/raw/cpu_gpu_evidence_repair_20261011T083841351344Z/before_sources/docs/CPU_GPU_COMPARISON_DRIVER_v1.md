# Controlled CPU/GPU pilot implementation

This is an implementation guide for the unchanged frozen
[comparison protocol](CPU_GPU_COMPARISON_PROTOCOL_v1.md). The frozen matrix's
planning-time status remains historical; runtime implementation/evidence are
recorded separately. The full study is not enabled by this pilot runner.

## Architecture and timing

`mab_comparison` implements canonical int32 input I/O, the signed-edge pattern and
W1/R5 cyclic scheduling. `comparison_input` calls the existing seeded generator,
writing canonical low-to-high uint32 bytes outside all sort timing. Python hashes
the retained input with SHA-256; the worker checks its existing FNV-1a identity.
Original/oracle/working vectors are constructed before timing and shared logically
across all five modes. Every result is compared in full with the std::sort oracle
outside timing. No normal sorting implementation or registry was modified.

The explicitly enabled `cpu_gpu_comparison` worker executes the unchanged std_sort,
Merge Sort, OpenMP Merge Sort and production CUB registry functions. Steady-clock
timestamps immediately bracket public host-vector calls, including internal
allocation/free and the production adapter's pageable transfers and checked
synchronization. Before calls, input restoration and device synchronization occur
outside timing. Prepared samples call the existing `CudaTimingSession::sample`
unchanged, retaining the separate four metrics and old CSV/protocol identity.
Its pinned staging, allocation and final vector copy remain excluded. No comparison
counter is used. Registry lookup, metadata and serialization are outside timing.

The driver writes an attempt record before each operation and flushes each raw
sample afterward. Exceptions emit blank metrics with error details and stop.
Timeouts/interruptions preserve logs, attempted/missing identities and incomplete
markers. Existing output directories, including dangling symlinks, are rejected.
No resume, overwrite, retry or full-study option exists.

## Workspace and memory diagnostic

The unchanged production adapter queries CUB with null temporary storage on the
default stream, allocates `max(requirement,1)` bytes, sorts, synchronizes, transfers
back and checks frees within every public call. Its host output vector and device
input/output buffers are also allocated per call. It is not instrumented here.

`src/cuda/comparison_resources.cu` separately creates representative device key
buffers, queries default-stream and private nonblocking-stream requirements using
the same signed int32/full32-bit/int item-count parameters, and checks successful
temporary allocation requests for both workspaces. It frees its resources before
performance buffers are constructed. Those are **isolated diagnostic queries and
successful cudaMalloc request sizes**, not observations of every production call,
allocator-rounded physical allocation or process memory. The production path and
reviewed CUB3.0.1 pin remain unchanged.

`workspace_queries.json` records fresh results for both pilot sizes before timing.
Each dataset's `resources.json` repeats the gate and verifies the prepared session's
actual sizing result agrees. It records successful session buffer/workspace request
sizes separately. Frozen resource tables are not updated with runtime values.
The 64MiB-per-workspace/256MiB-combined/half-free-device/host/disk gates remain in
force. Root resource files and any inaccessible cgroup controls are retained;
unknown controls are not described as controlled/unlimited resources.

`process_memory.json` uses existing Linux getrusage peak RSS, captured outside
timing after all modes in a dataset process. It includes process/context/runtime,
input/oracle/output, allocator and all modes' history; it cannot isolate any one
algorithm or represent device memory. Units are bytes. Unsupported/error status
is explicit through the existing memory API.

## Build and validated execution entry point

The new `MAB_ENABLE_CPU_GPU_COMPARISON` option defaults OFF. It requires
`MAB_ENABLE_CUDA=ON`, `MAB_ENABLE_CUDA_SORT=ON` and `MAB_ENABLE_OPENMP=ON`.
Existing CPU-only and CUDA-without-comparison builds retain their behavior.
`docs/CPU_GPU_DRIVER_REVIEW_v1.json` hashes the additive CMake integration against
the frozen source anchor; every run checks this extension and all protected
source/dependency anchors. New source hashes, complete compile commands and linked
OpenMP/runtime metadata are retained.

On a freshly verified T4 with the pinned CUB headers:

```sh
python3 scripts/validate_cpu_gpu_pilot.py \
  --output results/raw/NEW_CPU_GPU_VALIDATION \
  --pilot-output results/raw/NEW_CPU_GPU_PILOT \
  --processed results/processed/NEW_CPU_GPU_PILOT
```

All output paths and their build-directory names must be new. This command first
verifies the freeze and executes a fresh kernel preflight, new CPU Release and
ASan/UBSan builds/full tests, new CUDA/OpenMP Release build/full tests, actual CUB
correctness475 inputs/1900 checks, dependency-tree capture and source checks.
Leak detection is disabled only after the documented ptrace limitation reproduces;
other sanitizer failures stop validation. Only then does it permit the six-dataset
pilot (150 measured +30 warm-up calls), strict analysis and duplicate deterministic
summary generation. Any failed prerequisite prevents the pilot. This command was
created for this milestone; actual execution results belong in the latest audit.

To inspect the exact plan without GPU execution/output creation:

```sh
python3 scripts/run_cpu_gpu_pilot.py --dry-run \
  --executable build/NEW_GPU_BUILD/cpu_gpu_comparison \
  --input-tool build/NEW_GPU_BUILD/comparison_input \
  --output results/raw/NEW_CPU_GPU_PILOT
```

The dry-run prints frozen commands/orders/counts and resource formulas. Runtime
input/build/environment IDs are explicitly shown as placeholders. Actual direct
runner execution requires a compatible `--prerequisites` manifest generated by
the validator; stale source/binary/command hashes are rejected.

## Raw data, analysis and limitations

Root metadata: run/build/environment/source-review/prerequisite manifests, exact
commands and exit statuses, workspace queries, frozen-asset copies, completion or
failure/interruption marker and raw hashes. Per-dataset directory: retained
input.bin/input.json, recipe/content identity, then measurement primary.csv
(frozen31 fields), prepared/trials.csv (unchanged22 fields) and prepared/run.json,
prepared_order.csv, attempts.jsonl, calibration, resources, process RSS and markers.
The output record identities include backend, dataset, phase, trial and global
order. Four prepared values count as one invocation, never four trials.

```sh
python3 scripts/analyze_cpu_gpu.py results/raw/EXISTING_CPU_GPU_PILOT \
  --output results/processed/NEW_SUMMARY.json
```

The independent analyzer checks hashes, frozen recipes/identities/order, actual
threads, scopes, warm-ups, schema, finite timings, diagnostic workspace caps,
duplicates/missing/failed/interrupted rows and contradictory completion. Incomplete
runs are rejected by default; `--allow-incomplete` retains counts and exits1,
without paired ratios. Malformed raw data is rejected. Synthetic unit fixtures are
explicitly labelled and rejected by the public analysis CLI as performance evidence.

Summaries retain all outliers, report within-dataset median/mean/sample SD/min/max
in ns, then equally weight distinct input medians. Identical-input seed medians
collapse by their median into one input weight. Pilot groups each have one input,
so cross-dataset SD is null. Paired ratios use production GPU host-call medians
only; prepared device/transfer/E2E values never supply denominators. Resolution-
limited/nonpositive ratios are null; calibration is never subtracted. Reports are
descriptive, not rankings or significance tests. CPU/GPU run on the same VM; CPU
SMT, cloud load, frequency, cache/allocator state and thermal controls remain
confounders. No100M, broad CPU/GPU study or universal performance claim follows
from successful pilot execution.
