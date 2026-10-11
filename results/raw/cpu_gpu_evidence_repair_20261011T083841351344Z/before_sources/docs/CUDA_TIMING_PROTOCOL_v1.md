# CUB GPU timing protocol v1

Frozen before implementation/execution for the first performance smoke milestone.
Protocol/result identity: cuda_sort_timing_v1, schema1. CUB3.0.1 exact reviewed
header pin/commit/license and correctness contract cuda_sort_correctness_v2 remain
unchanged. Production cub_radix_sort_v1 remains allocation-per-call, stream0 and
uninstrumented. No existing CPU protocol/result is changed.

## Prepared execution and timing boundaries

A separate benchmark-only prepared session invokes the same genuine CUB
DeviceRadixSort::SortKeys on full-domain signed int32 over all32 bits. This is
not timing the public adapter's allocation-per-call contract. No CPU fallback.
Allocate two pinned host buffers, two device key buffers, CUB-sized workspace,
one nonblocking CUDA stream and four timing-enabled events once per dataset.
Copy the identical original input into pinned input before each trial, outside
all timers. Build std::sort oracle and output storage before trials.

For each nontrivial trial, synchronize the private stream before timing. On that
stream enqueue event0, async H2D, event1, SortKeys, event2, async D2H, event3.
Check CUDA/CUB return codes and launch status. Synchronize event3 before reading
output or event durations. No concurrent operations are submitted by this runner.

| Metric/CSV column | Timer and exact interval | Unit |
| --- | --- | --- |
| h2d_ns | CUDA elapsed event0->event1: pinned host input to device | ns |
| device_sort_ns | CUDA elapsed event1->event2: CUB GPU timeline interval, potentially including launch/dispatch-induced idle gaps | ns |
| d2h_ns | CUDA elapsed event2->event3: device output to pinned host output | ns |
| end_to_end_ns | host steady_clock immediately before event0 record until event3 synchronization returns | ns |

End-to-end includes event enqueue/checking, transfer submission, CUB host dispatch,
GPU work/transfers and completion wait. Excludes prior synchronization, context/
stream/event creation, host/device allocation, workspace sizing, input staging,
output copying to a vector, event-duration queries, CPU oracle/validation and I/O.
Buffers/events/workspace are reused. End-to-end is a prepared pipeline latency,
not allocation-inclusive adapter latency. The three event intervals need not sum
to host end-to-end. They do not measure host allocation or isolated kernel active
time. Event API float milliseconds are converted to double nanoseconds (x1e6),
retaining API precision rather than asserting nanosecond resolution. NVIDIA
[documents approximately0.5us resolution and stream/interference limitations](https://docs.nvidia.com/cuda/cuda-runtime-api/group__CUDART__EVENT.html).
No negative/nonfinite timings accepted. Zero allowed at timer resolution.

Empty/singleton require a real usable device but skip transfers/CUB; three event
metrics are exactly0 and host elapsed measures the trivial prepared call. A keys-only
API cannot observe equal-key payload stability. Current device fixed at session
construction; external concurrent/multi-device use is outside this contract.
All buffers use RAII; cleanup synchronizes before freeing pending storage, logs
secondary errors, and explicit successful close checks every resource release.
Exceptions never cause CPU substitution. A failing trial records status/error,
blank metrics and correctness not_checked/failed; stop and preserve partial rows.

## Workloads, limits and output

Single-run CLI cuda_sort_benchmark defaults N1000, seed1729, uniform, one warmup,
five measured repetitions. Existing generator/make_timing_input/FNV fingerprint
reused for uniform, sorted, reverse_sorted, duplicate_heavy and nearly_sorted;
existing --swaps/--distinct definitions preserved. Extra signed_edges workload
cycles INT32_MIN, INT32_MAX,-1,0,1,MIN+1,MAX-1,0 (seed recorded, not used).
Warmups use identical paths and are recorded/validated but excluded from summaries.
Validate full output against oracle after every trial, outside alltimers.

Initial smallest smoke: N1025/uniform/seed1729, one warmup/five measures. Only after
it passes, matrix N0/1/1025/65537, six workloads above, seeds1729/42, W1/R5:
48 configurations,240 measured and48 warmup rows. No size above65537 in this smoke.
An explicit configured run is capped at1M keys in this milestone. Host payload
planning reserves five N-key arrays, device planning two N-key arrays plus exact
CUB workspace; each is bounded by --memory-limit-mib (default256). Also require
device request <=half current free CUDA memory. These are allocation planning,
not RSS/isolation claims; driver/runtime/allocator overhead is not isolated.

Require Release without sanitizers for primary timing. Separate executable and
CUDA timing library exist only on explicit MAB_ENABLE_CUDA/SORT opt-in. CPU-only
builds remain independent. Output directory atomically claimed, never overwritten,
including symlink collisions. Per-run run.json, trials.csv and COMPLETE.json or
FAILED.json; crash/interruption without COMPLETE is incomplete. Python orchestrator
retains exact subprocess logs and FAILED/INTERRUPTED markers; fail-fast, no resume.

CSV columns: schema_version,protocol,run_id,algorithm,implementation_version,
distribution,size,seed,nearly_sorted_swaps,duplicate_cardinality,dataset_generator,
input_hash_fnv1a64,phase,trial_index,h2d_ns,device_sort_ns,d2h_ns,end_to_end_ns,
elapsed_unit,status,correctness,error. Four metrics per trial, not four independent
trials. Metadata required in run.json: all shared dataset/run fields, repetitions,
warmups, expected_rows, requested/actual device ordinal, GPU name/capability/memory,
runtime/driver API versions,CUB version,C++ compiler/build/platform,CUDA compiler/
toolkit/build flags, allocation/stream/clock policy, exact invocation. Copy CMake
cache/compile commands/source manifests/CUB attribution to each bundle; cloud
runner captures source/dependency/binary hashes, fresh preflight/driver/nvcc and
CPU/RAM/OS environment. Unknown environment/control values are not invented.

## Analysis and acceptance

Strict analyzer rejects malformed schema, identity/protocol mismatch, duplicate/
misordered/missing trials, nonfinite/negative timings and contradictory completion.
Default rejects incomplete runs; --allow-incomplete retains failed/missing counts
and never marks them complete. Summaries separately aggregate each metric within
each dataset: successes/failures/missing, median/mean/sample stdev (null if<2),
min/max; retain every outlier. Matrix summaries retain dataset/seed identity;
no pooled cross-seed independence or significance/speedup claim. Derived summaries
live separately, regenerate byte-for-byte from identical retained raw inputs.

Acceptance: host fixtures/regressions, fresh Release and ASan/UBSan, real GPU
correctness rerun, smallest smoke then complete matrix, strict raw/schema/count
validation and deterministic summary regeneration, original artifact hashes intact.
Expired/missing GPU is a blocker to GPU acceptance, not a CPU test failure. Preserve
all failed attempts. This is a smoke performance infrastructure milestone, not a
full study, leaderboard,100M experiment or allocation-inclusive CPU comparison.
