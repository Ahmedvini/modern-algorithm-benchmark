# CPU-only release scope and methodology v1

## Scope and acceptance

On 2026-10-11 the user explicitly dropped GPU execution, CUDA and CUB comparisons
from this release. This document defines an additive release scope; it does not
alter any frozen experiment protocol. CPU acceptance comprises implementations,
correctness evidence, retained completed CPU studies, raw-audited analysis,
reproducible figures, an academic report and a 12-slide presentation. It does not
require a GPU session, CPU/GPU approval artifact or GPU performance result.

Six sequential sorters remain registered: `std_sort` (unchanged default),
`quick_sort`, `pdq_sort`, `tim_sort`, `merge_sort`, `radix_sort`. Linear, binary
and exponential search, Skip List, B-tree orders 10/16/32/64, OpenMP Merge Sort,
and the standalone learned rank index remain available. Upstream source and
licenses, production adapters, CMake defaults and selection/launch guards are
unchanged. [Deferred GPU material](DEFERRED_GPU.md) is preserved in place.

## Retained experiments

These are existing measurements, not experiments rerun for the CPU-only revision.
Each timing study used one warm-up and five measured repetitions per configuration.

|Study|Measured observations|Warm-ups|Raw evidence|
|---|---:|---:|---|
|1M sorting: six sorters, five distributions, three seeds|450 sorts|90|`results/raw/sorting_1m_20261009T172003802655Z/matrix/`|
|Multi-size CPU orchestration|1,800 sorts; 7,020 search batches; 13,200 structure operations|360; 1,404; 2,640 respectively|`results/raw/phase5_full_20261009T191000587965Z/`|
|OpenMP: 32,768/100,000/1M keys, five distributions, three seeds, 1/2/4/8 teams and sequential baseline|1,800 sorts|360|`results/raw/openmp_scaling_20261009T200852928292Z_retry1/`|
|10M sorting: six sorters, five distributions, three seeds|450 sorts|90|`results/raw/autonomous_completion_20261011T095554571762Z/sorting_10m/`|
|100M sorting: six sorters, five distributions, seed 1729|150 sorts|30|`results/raw/autonomous_completion_20261011T095554571762Z/sorting_100m/`|
|Learned rank vs binary search: 48 workload configurations, 24 distinct sorted inputs|480 lookup batches; 240 builds|96 lookup; 48 build|`results/raw/autonomous_completion_20261011T095554571762Z/learned_study/`|
|Separate comparison/RSS matrix: five counted sorters, four sizes, four distributions, three seeds|240 instrumented executions|Not applicable|`results/raw/autonomous_completion_20261011T095554571762Z/count_memory_retry1/`|

Validated timing records in these completed studies have zero failed/missing trials.
Earlier failed attempts remain separate; they are not folded into completed runs.
The exact sizes, order, seeds and generator parameters are recorded in each
study's matrix/run manifests and original protocol. Studies are not pooled as
one machine session or one independent statistical sample.

## Inputs, timing and semantics

The immutable [generator specification](EXPERIMENT_PROTOCOL.md) defines seeded
signed-int32 uniform, reverse, nearly sorted and duplicate-heavy data. Sorting
studies also construct ascending data by sorting the corresponding sample outside
timing. Every compared sorter receives an identical restored original input.
Dataset generation, copying to restore input, reference construction, full-vector
oracle validation, and serialization are excluded from sorting timing. Internal
sorter allocation remains part of the normal call where the implementation
allocates per call. Release builds use `steady_clock` and report nanoseconds.
Comparison counters are never enabled in primary timing.

Search and index lookup results are batch latency and normalized batch average,
not individually timed queries. Identical logical queries are used across
implementations, and the reported mixed workloads have exactly 500 hits and
500 misses per 1,000-query batch. Build/construction and lookup are separate
operations. Binary/exponential/learned lookup returns the first equal array
index or absence. Ordered structures implement unique-key maps preserving the
first-inserted payload. Sorted-input validation and reference checking remain
outside timed lookup. See [search](SEARCH_PROTOCOL_v1.md),
[structures](STRUCTURES_PROTOCOL_v1.md), and [learned index](LEARNED_INDEX_PROTOCOL_v1.md)
contracts for all query policies and edge conditions.

## Statistics and interpretation

Retain every raw observation, including slow trials. First compute statistics
within each dataset's repetitions. Cross-seed summaries equally weight dataset
medians; a minimum runtime is never substituted for a median. Report mean,
sample standard deviation, min/max and successful/failed/missing counts in the
machine-readable source summaries. Error bars show cross-dataset spread, not
confidence intervals. No significance test or universal ranking is claimed.
100M uses one seed and supports only within-dataset variability.

OpenMP primary speedup is sequential Merge Sort median divided by parallel Merge
Sort median for the same dataset. Efficiency divides that ratio by observed
team size. Summarize dataset ratios before cross-dataset aggregation; keep the
parallel implementation's one-thread baseline separate. Requested/actual team
size does not prove task participation, physical-core concurrency or race freedom.

For learned evaluation, seeds 42/2718/314159 are held out from performance tuning;
they are not claimed absent from all correctness tests. Different distribution
labels can collapse to the same sorted vector (24 distinct inputs in 48 workload
configurations); do not count those labels as independent datasets.

Separate key counts measure executed key predicates, not moves or instructions.
Radix counting is unsupported. Linux `getrusage` RSS is process-lifetime peak in
bytes, includes input/runtime/allocator/instrumentation, and does not isolate
auxiliary or structure memory. Three seed RSS observations are not repeated
measurements of one process/dataset. Planning buffer budgets are estimates;
they are never labeled measured allocation or RSS. See [metrics](METRICS.md).

## Environment and threats to validity

Retained local studies identify Intel i5-11400H, 6 physical/12 logical CPUs,
Linux kernel 6.18.7-76061807-generic with glibc 2.39, GCC 13.3.0, CMake 3.28.3,
Release `-O3 -DNDEBUG`, and MemTotal 16,089,028 KiB (approximately 16.48 GB decimal).
The OpenMP sweep records libgomp/OpenMP 4.5, dynamic teams disabled, thread limit
8, one active level and passive wait policy. Each historical run retains its own
source/compiler/configuration/environment snapshot. The release's
`RAW_VERIFICATION.json` cites two original environment manifests by path and hash.

Power policy, background load, thermals, caches and frequency were not controlled.
Shared-machine and SMT behavior limit causal/general performance conclusions.
Passing concurrency tests are not a race-detector proof; earlier TSan/runtime
limitations remain. Individual-query maximum latency, isolated structure
allocations/comparison counts and independent-hardware replication are not
measured. AlphaDev is a primary-source research review, not a reproduced training
system. The optional learned sorting selector is not implemented.

## Validation, reporting and security boundaries

Use the existing [guarded local v5 correctness workflow](LOCAL_VALIDATION_v5.md).
It retains the 19 approved default names and permits two explicitly opted-in
untimed diagnostics. Build-tree static validation precedes discovery, preserves
canonical path identity and rechecks metadata before execution. Full CTest also
contains timing-bearing integration tests; do not rerun it for this revision.

The unchanged engine's earlier Release and ASan/UBSan evidence is retained. This
release checks the existing CPU-only Release build, reruns its guarded correctness
selection, tests reporting with synthetic fixtures, audits summary values against
raw records, and regenerates new assets twice for byte comparison. No completed
performance trial is repeated. All earlier report/plot/presentation assets remain.

No independent approval gate applies to local CPU analysis/correctness. The
independently protected approval required by the frozen CPU/GPU launcher still
applies to that deferred workflow and remains fail-closed; CPU-only scope does
not grant it eligibility. No security policy or trusted anchor is changed.

See [report regeneration](../report/README.md) and the
[release audit](../results/raw/cpu_only_release_20261011T133332368294Z/FINAL_AUDIT.md).
