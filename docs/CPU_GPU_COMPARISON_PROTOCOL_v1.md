# Controlled CPU/GPU comparison protocol v1

Protocol identity: `cpu_gpu_comparison_v1`. Status: **frozen for review; execution
not authorized by this deliverable**. This document specifies a future bounded
study, not measured comparative results. Its matrix, resource table and freeze
manifest are in `docs/studies/cpu_gpu_comparison_v1.{matrix.json,resources.csv,freeze.json}`.
The manifest hashes the exact document and assets. Revisions require a new version;
do not edit the frozen files to accommodate a failed gate.

## 1. Verified starting point and unresolved implementation

The reviewed evidence is
`results/raw/cuda_timing_20261009T231303050084Z/{FINAL_AUDIT.md,CHANGES.md,COMMANDS_FINAL.md,FINAL_INTEGRITY.json}`
and `results/processed/cuda_timing_20261009T231303050084Z/REPORT.md`.
It establishes actual Tesla T4 CUB correctness and prepared-buffer timing smoke
execution, not allocation-inclusive adapter performance or a CPU/GPU comparison.
The existing `CUDA_TIMING_PROTOCOL_v1.md` remains unchanged.

The current production adapter and prepared benchmark both use NVIDIA CUB
`DeviceRadixSort::SortKeys`, signed int32 keys, ascending full 32-bit sorting.
The reviewed dependency is CCCL v3.0.1, commit
`f19d875da0d8bfb2e38c109b2b40522b8abbbbc3`, `CUB_VERSION=300001`, from
<https://github.com/NVIDIA/cccl>. `third_party/cub/UPSTREAM.json` records the
version-header, SortKeys-header and retained aggregate-license hashes. Do not
change this pin. Actual installed headers and the complete include-tree manifest
must be checked again before execution; toolkit version alone is insufficient.

Existing interfaces already accept `Values&` (`std::vector<int32_t>`), so the
primary comparison needs **no public sorter-interface change**. The missing
implementation is an isolated driver coordinating the existing CPU registries,
production CUDA registry and prepared session; a shared signed-edge workload;
dual-workspace resource queries; and strict host-call/paired analysis. The existing
CPU timing CLI cannot select the CUDA registry or signed-edge workload. The GPU
matrix runner does not interleave CPU calls. Their current schemas/analyzers must
remain usable. Do not concatenate their incompatible timing rows and call that a
matched experiment. These additions and their tests are a later implementation
milestone, not implemented by this protocol.

## 2. Implementations and build

| Backend identity | Existing entry point | Scope | CPU thread policy |
|---|---|---|---|
| `cpu_std_sort` | `find_sorter("std_sort").sort` | Host-vector API call | One calling thread |
| `cpu_merge_sort` | `find_sorter("merge_sort").sort` | Host-vector API call | One calling thread |
| `cpu_parallel_merge_sort_t2` | `find_parallel_sorter("parallel_merge_sort", 2)` | Host-vector API call | Request two OpenMP team threads |
| `gpu_cub_adapter` | `find_cuda_sorter("cub_radix_sort").sort` | Host-vector API call | GPU; CPU team count not applicable |
| `gpu_cub_prepared` | `CudaTimingSession::sample` | Existing four prepared metrics | GPU; CPU team count not applicable |

`std_sort` means the recorded standard library's `std::sort`, not a universal
implementation identity. Sequential Merge Sort is the existing stable bottom-up
implementation; its N-key auxiliary vector is allocated inside each call.
Parallel Merge Sort is `parallel_merge_sort_v1`, stable, with threshold 32768 and
task grain 16384. Below the threshold it reports one actual thread; at/above it,
two are required for this study. Report actual team size, not workers observed
executing tasks. No claim about stability of indistinguishable int32 duplicates
is inferred from these timing tests.

Use one Release build on the **same Colab VM for CPU and GPU**: C++17, sanitizers
and comparison instrumentation off, `MAB_ENABLE_CUDA=ON`,
`MAB_ENABLE_CUDA_SORT=ON`, `MAB_ENABLE_OPENMP=ON`, CUDA architecture 75. Requested
Release flags are `-O3 -DNDEBUG` for C++ and CUDA. Capture the complete effective
compile/link commands and flags; reject unexpected optimization, instrumentation,
LTO, native-architecture or fast-math changes rather than silently accepting them.
Keep the CPU default `std_sort`. The future comparison target and invocation
cannot be named as working commands before implementation.

The retained T4 environment used driver 580.82.07, CUDA/nvcc 13.0.88, runtime API
13000, GCC 13.3.0 and CMake 3.31.10. These are **historical**, not current session
metadata. Fresh preflight, kernel execution, CUB compilation/correctness and CPU
fallback tests are prerequisites. Target a Tesla T4, compute capability 7.5; a
different device requires a revised protocol. Record changes in toolchain/runtime
and rerun validation; never invent unavailable versions.

Set `OMP_DYNAMIC=FALSE`, `OMP_THREAD_LIMIT=2`, `OMP_MAX_ACTIVE_LEVELS=1`,
`OMP_WAIT_POLICY=PASSIVE`, `OMP_PROC_BIND=FALSE`. Require at least two effective
logical CPUs after affinity/cpuset and CPU-quota checks. Historical Colab exposed
two logical CPUs on **one physical core with SMT**, not two physical cores. No
4/8-thread configurations are proposed. Record actual team count and reject an
unexpected one-thread team on N >= 32768. Passive waiting reduces, but does not
prove absence of, interference during GPU calls. No affinity or frequency control
is claimed. Do not run other workloads concurrently.

## 3. Inputs, matrix and identities

All values are signed int32. Sizes are **1025, 65537, 1000000**: the first exposes
fixed launch/transfer costs, the second crosses common boundaries, and the last is
the cap. Five seeded distributions use seeds **1729, 42, 2718**:

* `uniform`: generator `mt19937_64_v1`, low 32 bits minus 2^31 in signed 64-bit
  arithmetic, as specified in `EXPERIMENT_PROTOCOL.md`.
* `sorted`: the corresponding uniform sample ordered ascending outside timing.
* `reverse_sorted`: the corresponding uniform sample ordered descending.
* `duplicate_heavy`: generator-v1 bounded sampling into a 16-value domain,
  translated by minus floor(16/2); occurrence of every value is not guaranteed.
* `nearly_sorted`: uniform sample sorted ascending followed by exactly floor(N/100)
  generator-v1 pair swaps; self-swaps and repeated indices are allowed.

The sixth workload, `signed_edges_v1`, repeats
`[INT32_MIN, INT32_MAX, -1, 0, 1, INT32_MIN+1, INT32_MAX-1, 0]` and truncates to N.
Its recorded seed is 1729 but is **unused**; only one edge dataset per size is
included. Do not manufacture three independent datasets by repeating this pattern
with different seed labels. The existing prepared benchmark constructs this
pattern; a future shared helper must preserve its exact values.

Recipes explicitly record swaps=0 for non-nearly-sorted workloads and cardinality
16 throughout (not applicable parameters remain recorded). Construct one original
vector, one oracle sorted with `std::sort`, and one reusable working/output vector
per dataset, all outside timing. Every backend receives exactly the same original
contents before every call; compare the complete resulting vector to the oracle
afterward. This proves order and multiset preservation for that trial. Generation,
input restoration, checksums and oracle construction/verification are excluded
from primary measurements. Keep input restoration policy identical across CPU and
production GPU calls; prepared pinned staging remains separately excluded.

The main bounded study contains `3 * (5 * 3 + 1) = 48` datasets and five modes:

| Planned set | Datasets | Mode configurations | Measured calls | Warm-up calls | Total calls |
|---|---:|---:|---:|---:|---:|
| Pilot: N=1025/1000000, uniform/duplicate_heavy/signed_edges, seed 1729 | 6 | 30 | 150 | 30 | 180 |
| Main study | 48 | 240 | 1200 | 240 | 1440 |

For each mode/dataset use **one warm-up and five measured repetitions**. Main study
primary host-call rows: 960 measured + 192 warm-ups; prepared rows: 240 measured +
48 warm-ups, each containing four metrics. Four metrics are not four independent
trials. Pilot primary rows: 120 + 24; prepared rows: 30 + 6. Pilot observations
must not be reused as main-study observations. These are planned counts; none
were executed for this protocol deliverable.

Serialize recipes as sorted-key JSON, ASCII, no whitespace separators, no NaN;
`dataset_id` is SHA-256 of those bytes. Hash actual input bytes with SHA-256 over
each key cast to uint32 and encoded low byte first, independent of host endian.
Also retain existing FNV-1a64. Recipes identify configurations; content hashes prove
equivalent generated contents. Matrix identity is SHA-256 of its exact frozen
file bytes, recorded with protocol and freeze hashes, source manifest, executable
hashes, build/environment IDs and unique run ID in every run manifest. Do not
generate a fresh timestamp into configuration serialization. Actual runtime
metadata is explicitly null in the planned matrix until collected.

## 4. Timing scopes and fair comparisons

### Primary: `host_vector_api_call_v1`

Start with an ordinary caller-owned working `Values` containing restored input.
After a device synchronization outside timing confirms no outstanding work, take
`steady_clock::now()`, invoke the **unchanged** public sorter, then take the stop
timestamp immediately after successful return. The vector now contains the full
host-visible sorted result. Do not add per-call events, counting comparators,
CPU fallbacks or extra synchronization inside the production adapter. Resolve
registry entries and prepare thread configuration before timing. Record elapsed
nanoseconds as `host_call_e2e_ns` (CSV column `elapsed_ns`, unit `ns`).

This is a **warm-context, allocation-inclusive API-call latency**, not cold-process
latency, dataset-generation latency or a complete application lifecycle. CUDA
context initialization, module first-use and all mode warm-ups occur before
measured calls. The adapter's own device/property checks remain inside its call.

| Included within this identical logical boundary | Excluded |
|---|---|
| CPU algorithm work and internal temporary-buffer allocation/destruction | Caller input restoration, generation, oracle and correctness checks |
| OpenMP team/task creation, synchronization and auxiliary buffer | Process/context initialization and preflight |
| Production GPU host-output allocation, device input/output allocation, CUB workspace query/allocation | Prepared session creation/destruction and retained pinned/device buffers |
| Production pageable H2D, CUB dispatch/device execution, checked launch/synchronization, pageable D2H | CSV I/O, metadata, analysis, all comparison-count instrumentation |
| Production checked device-buffer frees, vector swap and destruction of old host storage before return | Timer calibration and pre-call device synchronization |

The adapter synchronizes its default stream and completes blocking D2H before
return. The stop timestamp therefore does not merely time asynchronous enqueue.
The host clock includes relevant host overhead; CUDA events cannot substitute for
this metric. CPU/GPU warm-up and prepared-path residency affect allocator/cache
state; record this deliberate interleaving rather than claiming a cold allocator.

Only **matched primary host-call medians** may form CPU/GPU ratios. They compare
complete implementations, including different algorithms and allocation policies;
they do not isolate hardware acceleration. Never pair local-machine CPU results
with Colab GPU results. Never divide CPU host-call time by device-sort-only or
prepared end-to-end time. Label ratios by baseline backend, N and distribution;
no universal ranking or significance claim is authorized.

### Diagnostics: unchanged `cuda_sort_timing_v1`

`CudaTimingSession` owns reusable two pinned host buffers, two device key buffers,
CUB workspace, four CUDA events and a private nonblocking stream. Before timing it
stages the original vector to pinned input and drains prior stream work. Within
the timed pipeline it records event 0, async H2D, event 1, CUB SortKeys, event 2,
async D2H, event 3 and waits on event 3. Output is then copied from pinned output
to the caller's vector **outside** timing.

| Existing field | Measurement and boundaries |
|---|---|
| `h2d_ns` | CUDA event 0 to 1, pinned H2D interval |
| `device_sort_ns` | CUDA event 1 to 2, CUB device-sort timeline interval |
| `d2h_ns` | CUDA event 2 to 3, pinned D2H interval |
| `end_to_end_ns` | Host steady clock immediately before event 0 record through event 3 synchronization: **prepared end-to-end** |

CUDA-event float milliseconds are multiplied by 1e6 to express nanoseconds; this
conversion adds no precision. Events can include idle gaps caused by host dispatch;
`device_sort_ns` is not a sum of isolated kernel active times. Host prepared E2E
includes enqueue/wait overhead but excludes all allocation/free/context/setup,
pinned staging, final output-vector copy, event elapsed-time queries and validation.
Component sums need not equal host E2E. Keep all four diagnostics separate from
the primary scope. Retain the old protocol/schema identity and 22-column raw CSV;
do not relabel its E2E field as allocation-inclusive latency.

## 5. Scheduling and recording

Use serial execution, preferably one process per dataset with all five modes in
that process. No concurrent datasets, builds, transfers, analysis or plots during
timings. Order seed is **314159**. Sort datasets by SHA-256 of ASCII
`314159|<dataset_id>`, tie-break by dataset ID. For each dataset, sort backend IDs
by SHA-256 of `314159|<dataset_id>|<backend_id>`, tie-break by backend ID. Run one
warm-up for each in that base order. Measured rounds r=0..4 left-rotate the base
order by r. Thus every mode occupies every order position exactly once. The matrix
enumerates these exact orders. This reduces simple order bias; it does not control
temperature, caches, frequency or background interference.

Before every backend call restore input outside timing; before GPU/CPU primary
calls drain outstanding GPU work outside timing. After each call validate the
entire output. The prepared session may stay resident across all calls for this
dataset; include its residency in resource estimates. Destroy it before advancing
to the next dataset. Record actual order, per-dataset execution index and global
call index (zero-based, including warm-ups), trial index and warm-up/measured phase.

The proposed primary CSV is **specified, not implemented**:

```text
schema_version,protocol,run_id,matrix_sha256,build_id,environment_id,dataset_id,input_sha256,input_hash_fnv1a64,size,distribution,seed,dataset_generator,nearly_sorted_swaps,duplicate_cardinality,backend_id,algorithm,implementation_identity_ref,scope,phase,trial_index,execution_order,global_trial_index,requested_cpu_threads,actual_cpu_threads,parallel_region,elapsed_ns,elapsed_unit,status,correctness,error
```

Use primary schema 1, protocol `cpu_gpu_host_call_v1`, scope
`host_vector_api_call_v1`; a run manifest links the outer protocol
`cpu_gpu_comparison_v1` and exact frozen matrix. CPU requested/actual threads are
1/1 for sequential modes; parallel actual comes from `ParallelSortInfo`; GPU
thread fields are blank/not applicable, not invented worker counts. Resolve
`implementation_identity_ref` through hashed source/build/stdlib/CUB metadata.
Success requires full oracle equality. Failed calls have explicit error/status and
blank timing rather than a fabricated duration. Prepared rows keep their existing
schema, with an order sidecar mapping each row to dataset ID, backend, phase,
round, configuration and global execution index. Raw warm-ups remain retained.

Create an exclusive new output directory; collisions, including symlinks, fail.
Preserve protocol, matrix, environment/source/build/binary manifests, commands,
stdout/stderr, exit codes, raw rows, failures, order sidecar and raw hashes. No
automatic retry, resumption or overwrite. A failed/interrupted dataset stops the
run and leaves subsequent trials explicitly missing in the completion audit.
Per-dataset timeout 60s, pilot total 300s, main study 1800s; timeout/interruption
must not create a completion marker. Any revised run gets a new output path.

## 6. Resource estimates and launch gates

These are calculated payloads and **planning allowances, not measured allocations
or RSS**. One int32 array is 4N bytes. The future driver holds original, oracle and
working vectors (12N); prepared pinned buffers add 8N; either CPU Merge Sort's
auxiliary vector or production GPU's output vector adds 4N, not both concurrently.
Known peak host payload is therefore **24N bytes**. Allocator/runtime, CUDA pageable
staging, stack/OpenMP tasks, metadata and context overhead are additional/unmeasured.

With a retained prepared session, device peak while the production adapter runs is
**16N + max(W_prepared,1) + max(W_adapter,1)** bytes: both paths' input/output
buffers coexist. Workspace sizes are queried separately with the corresponding
stream/API parameters before allocating performance buffers. Do not assume the
private-stream and default-stream requirements are identical. Query helpers must
clean up their temporary buffers outside measurement and record actual results.

| N | One array bytes | Known host peak bytes | Both device key pairs bytes | Device planning cap including two 64MiB workspace allowances |
|---:|---:|---:|---:|---:|
| 1025 | 4100 | 24600 | 16400 | 134234128 |
| 65537 | 262148 | 1572888 | 1048592 | 135266320 |
| 1000000 | 4000000 | 24000000 | 16000000 | 150217728 |

At 1M this is 22.89MiB known host payload and a 143.26MiB device planning cap.
The 64MiB **per workspace** allowance is an acceptance policy, not a proven CUB
upper bound. Historical prepared allocations were 1 byte at N1025 and 279295
bytes at N65537; N1M and default-stream adapter requirements are unknown. Query
both again. Stop/revise if either exceeds 64MiB, combined device payload exceeds
256MiB, or it exceeds half of fresh `cudaMemGetInfo` free memory measured before
persistent allocations. Do not quietly raise the cap. Require at least 1GiB host
headroom under both MemAvailable and applicable cgroup limits, and 1GiB free disk.
One dataset at a time bounds residency. Record actual workspace/pinned/device
allocations separately from process peak RSS; RSS never isolates the sorter.

The machine-readable resource CSV covers every proposed size and explicitly marks
unknown current workspaces. Planning at 1KiB per raw row gives 1474560 bytes
(1.41MiB) for 1440 rows. Reserve 512MiB for raw logs/build products, with the 1GiB
disk gate above; these are budgets, not measured artifact sizes.

### Execution-time estimate, not a performance prediction

The historical prepared-run process durations were approximately 0.25s/configuration
at N1025/65537. There are **no measured allocation-inclusive GPU timings**. The
historical local CPU 1M std/merge maximum sample is B=0.091878472s from
`results/processed/sorting_1m_20261009T172003802655Z/per_seed.json`; it is from a
different CPU host and can only anchor a conservative planning proxy.

The matrix records a transparent model:
`CPU(N)=max(0.001, 4*B*(N*log2(N))/(1000000*log2(1000000)))` seconds per CPU call,
with **no assumed OpenMP speedup**. Assume 0.05s per production GPU call, 0.01s
per prepared call, 0.5s setup/dataset and 0.01s validation/call at 1M scaled linearly.
For each dataset, cost is
`0.5 + 6*(3*CPU(N)+0.05+0.01) + 30*0.01*N/1000000` seconds.
These GPU, setup, validation and multiplier values are unmeasured allowances.

The resulting model is **25.96s pilot / 158.10s main**, with fourfold contingency
**103.84s / 632.40s**, excluding build, full regressions, preflight, session
provisioning and evidence transfer. Budget a further 5–20 minutes for build and
validation, also an assumption. Fresh pilot wall times and memory must replace
these proxies before study authorization. Stop for review if the pilot fails or
the observed projection cannot fit the 1800s main limit with headroom. No cloud
session readiness or runtime estimate has been empirically established here.

## 7. Statistics, uncertainty and run quality

Within each dataset/backend/scope, require five successful measured calls; report
success/failure/interruption/missing counts, median, mean, sample SD (ddof=1),
minimum and maximum in ns. Keep warm-ups and every outlier, excluding only warm-ups
and explicitly failed observations from timing statistics. Do not drop slow valid
rows. Failed/incomplete configurations cannot support a complete-study claim.

Compute each primary CPU/GPU descriptive ratio as that dataset's CPU median
divided by its production-GPU host-call median. Aggregate within each N/workload
across distinct input datasets with equal weights: report median/mean/sample
SD/min/max of dataset medians, and separately of paired ratios. Do not pool 15
trials as 15 independent datasets. If two seeds produce the same input SHA-256,
retain all rows but collapse their dataset weight and report the reduced distinct
count. Sorted/reverse/uniform transformations are separate workload groups, not
additional independent seeds. Signed-edge groups have one dataset, so cross-dataset
SD and confidence intervals are unavailable. No confidence interval or statistical
significance test is proposed for these three-seed descriptive groups.

Measure 1000 empty host-clock pairs outside primary timing as a diagnostic;
never subtract an estimated timer overhead. Flag medians below ten times the
calibration median as resolution-limited and omit their ratios; nonpositive
denominators also have no ratio. Prepared event precision limitations remain
explicit. Show uncertainty as sample spread/SD, not an unsupported inferential CI.

Fresh environment capture must include OS/kernel/architecture, CPU model and
physical/logical topology, affinity/cpuset/quota, RAM/cgroup limits, disk free,
compiler/stdlib/CMake/Python, effective flags, OpenMP linked runtime and environment,
CUDA compiler/runtime/driver/headers, GPU model/UUID/compute capability/device
selection/memory, source and binary hashes. Capture GPU temperature/clocks/power
policy and CPU governor/frequency where accessible before/after runs, background
load and visible competing processes. Unavailable metadata is null with a reason.
Visible competing benchmarking/GPU work requires stopping, not silently continuing.
No thermal, cache, frequency, exclusivity or background-load control may be claimed
without evidence. Shared-cloud SMT, virtualization and undetectable interference
remain confounders even if visible checks pass.

## 8. Validation checklist and acceptance criteria

**Protocol deliverable (this task):** inspect retained source/evidence; verify old
hashes; save versioned design, exact matrix and resource formulas; independently
validate counts, identities, order balance, deterministic regeneration and freeze
hashes; document missing implementation. This does not authorize execution.

**Before pilot:** review this freeze; implement the isolated driver, strict schema/
sidecar validator, paired analyzer and dual-workspace query without changing
production adapter behavior. Test exact order, dataset equivalence, edge fixtures,
malformed/duplicate/nonfinite rows, protocol/scope mismatch, failed/interrupted and
missing trials, exclusive output safety, thread metadata and summary regeneration.
Fresh CPU Release and ASan/UBSan suites must pass; preserve the sanitizer policy.
On the actual T4, rerun CUDA correctness (475 inputs/1900 output checks), prepared
GPU framework tests and CUB-header verification. Verify complete build metadata,
source changes against this freeze and all historical artifact hashes. Only
additive reviewed comparison code may extend the source manifest; otherwise revise
the protocol. Check resource and CPU-team gates before timing.

**Pilot acceptance:** all six datasets/five modes present; exactly 150 measured
and 30 warm-up calls in the frozen order; no failed/interrupted/missing/duplicate
records; full oracle equality every call; primary scope/units and four prepared
metrics correct, finite and nonnegative; actual CPU team sizes correct. Raw content
identities must agree across modes. Regenerate summaries twice byte-for-byte;
verify formulas independently on retained rows and preserve their hashes. Record
observed memory/time and revise the planning estimate before main-study review.
Do not infer performance superiority from pilot values.

**Main-study acceptance, only after separate review/authorization:** same checks,
48 datasets, 240 mode configurations, 1200 measured + 240 warm-ups, 960 primary
measured + 240 prepared measured rows, all complete and correct. Validate schema,
phase/order identities, hash/config/source/build/environment compatibility and
ratios restricted to matched scopes. Regenerate per-dataset and cross-dataset
summaries from immutable raw data; retain failed attempts and outliers. Verify
all frozen/historical artifacts before a completion marker. Report uncertainty,
limitations and descriptive scope-specific observations, never a universal winner.

Exact next step: review the frozen protocol and matrix, then implement/test the
missing comparison driver and analyzer; run the six-dataset pilot only when those
checks and fresh resource/runtime gates pass. No full comparative experiment,
100M workload, CUDA dependency update or performance ranking is part of this task.
