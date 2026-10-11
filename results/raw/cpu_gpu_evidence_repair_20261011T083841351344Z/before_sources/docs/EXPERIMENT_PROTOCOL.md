# Experiment protocol

## Current baseline

The sorting timing engine follows [sort_timing_v1](BENCHMARKING.md). After small
smoke validation, the first [1M study](studies/sorting_1m_20261009T172003802655Z_v1.md) completed
450 measured trials and 90 warm-ups across six algorithms/five distributions/
three seeds. Its descriptive results retain every observation and environment
limitations; no universal performance conclusion or significance is established.
Separate sort_metrics collects key comparisons/process RSS under
[METRICS.md](METRICS.md); no memory comparison study has run. Phase 5 timing charts are recorded below. The std::sort adapter is the installed library's
implementation; its precise library/compiler environment must accompany runs.

Release builds use the commands in README.md. Sanitizer tests will use a separate
Debug build. Correctness checks compare full vectors with std::stable_sort or std::sort so
lost or duplicated keys cannot pass by merely producing a sorted vector.

## Requirements before measurements

Timing will use a monotonic clock, exclude generation, copying and verification,
and use identical input copies for all sorters. Comparison counting must occur
separately from timing. Sorting smoke defaults are five repetitions, one warmup,
and 1K/10K int32 matrices; the planned larger research baseline remains 1M keys.
Future search workloads use 1,000 queries with a documented hit/miss ratio. Search construction and
lookup costs must be reported separately. Maximum observed query latency is not
the theoretical worst case. Timer overhead must be assessed before reporting
individual query latencies.

Every result must retain its exact command, compiler and flags, environment,
seed, distribution parameters, input size, repetitions, algorithm identity,
status and errors. Separate versioned metric JSON and sort_timing_v1 CSV/summary
schemas now exist. Sorting and search batch analysis retain failures/outliers; Phase 5 plotting tools
are now validated. Failed runs must remain visible. Raw output must never be overwritten;
summaries and plots belong under results/processed and results/figures.

CUDA and 100M experiments remain deferred until prerequisite phases are validated.

## Dataset generator contract: mt19937_64_v1

Each generation constructs a fresh std::mt19937_64 with the supplied uint64 seed.
The element type is signed int32. Size defaults to 1000 for correctness smoke
checks, seed to 1729, and distribution to uniform. This smoke default is separate
from the planned one-million-element benchmark baseline.

- **uniform:** consume one engine output per key, retain its low 32 bits as
  uint32, subtract 2^31 using signed int64 arithmetic, then convert to int32.
  This maps the entire 32-bit domain to [-2147483648, 2147483647].
- **reverse_sorted:** generate the corresponding uniform sample with the same
  size/seed and sort it nonincreasingly; duplicates are retained.
- **nearly_sorted:** generate that uniform sample, sort ascending, then perform
  K index-pair swaps, consuming both indices sequentially from the same engine
  after key generation. K defaults to floor(N/100). Each index is sampled from
  [0,N); self-swaps and repeated indices are allowed, so K does not mean K changed
  positions or inversions. Zero swaps leaves the ascending sample. N < 2 skips
  all swaps. The output records the request, including skipped swaps.
- **duplicate_heavy:** sample an unbiased u from [0,K), then return
  u-floor(K/2), where K is duplicate_cardinality. The default K=16 gives [-8,7].
  K must lie in [1,2^32]; K=1 gives all zeros, and K=2^32 uses the full signed
  int32 domain. Domain cardinality does not guarantee every value occurs.

For bounded sampling with positive bound b, calculate t=(0-b)%b using uint64
wraparound arithmetic. Consume engine words until word>=t, then return word%b.
This rejection mapping avoids modulo bias and library-dependent
uniform_int_distribution mappings. Empty generation consumes no words. Sorting
transforms preserve the generated multiset. Dataset generation itself is outside
any future sorting timed region. Version changes must explicitly preserve or
replace the documented seed-to-input compatibility contract.

Frozen swap fixtures were independently checked with a Python implementation of
MT19937-64 initialization, twist and tempering, and compared with 15 outputs from
a separately compiled probe of the current C++ generator (five seeds, K=0,1,5).
The full-vector regressions are in tests/test_datasets.cpp:

| N | Seed | First index pair | Coverage |
| --- | --- | --- | --- |
| 4 | 11 | (0,0) | First-index self-swap |
| 4 | 28 | (3,3) | Last-index self-swap |
| 4 | 13 | (0,3) | Distinct endpoint swap |
| 4 | 8 | (1,2) | Distinct interior swap |
| 8 | 1729 | (7,1) | Another size and mixed signed keys |

The size-eight five-swap fixture uses pairs (7,1), (5,2), (0,7), (0,6), (7,1).
The supported API is int32-specific; generic object swaps are outside its scope.

## Reference search semantics

std_lower_bound_search requires ascending sorted data and returns the first
matching index, or nullopt for a miss. It has O(log N) lookup comparisons and
O(1) auxiliary space. It builds no index; sorting preprocessing is separate.
The library reference adapter is not labeled as any project search algorithm.
The correctness tests compare it with a linear std::find oracle, including
duplicate and boundary queries. Phase 3 now adds independent linear, binary and exponential search adapters
and versioned query batches; the reference adapter remains unchanged.

## Recorded 1M study and aggregation

The immutable [study protocol v1](studies/sorting_1m_20261009T172003802655Z_v1.md) freezes the requested
1M parameters before execution; protocol hashes and raw completion markers are
retained under results/raw/sorting_1m_20261009T172003802655Z. The full report lives under
results/processed/sorting_1m_20261009T172003802655Z/RESULTS.md. Per-seed groups report five successes,
zero failures, median/mean/sample SD/min/max. Cross-seed groups use three equally
weighted seed medians, each derived from five timings. Repeated trials are not
independent datasets. All outliers and warm-up observations are retained.

The shared desktop's CPU frequency, cache state, thermal state and background
load were not controlled; accessible power policy and before/after load/resource
snapshots are recorded. No primary comparison instrumentation or measured RSS
accompanied this study. No protocol deviation or correctness failure occurred.
All derived summaries regenerated exactly; the protocol and raw results stayed
unchanged. Follow-up studies require separate frozen protocols and new outputs.

## Array search protocol

[search_batch_v1](SEARCH_PROTOCOL_v1.md) was defined before the engine/matrix
implementation. Generate existing seeded signed-int32 data, sort ascending outside
lookup timing, and reuse identical data and deterministic query batches across
linear/binary/exponential search. Queries retain source positions, expected first
matching positions and explicit absence. Fixed-rank/random-hit, representable
below/interior/above misses, balanced mixed batches and empty-input misses have
precise policies and explicit unavailable-category reasons.

Use steady_clock batch measurements with out-of-timing reference validation,
exclusive raw CSV bundles and separate category/run summaries retaining outliers.
Normalized batch averages are not individual-query observations. A separate
comparison executable measures search key predicates; primary timing is uncounted.
The sorting generator compatibility contract and frozen 1M sorting study remain
unchanged. Phase 5 now validates multi-size search timing/plots through 1M; individual-query
timing remains future work.

## Phase 4 structure protocol

[structures_batch_v1](STRUCTURES_PROTOCOL_v1.md) was saved before implementation.
It fixes first-insertion ordered-map payload semantics, Skip List level generation,
B-tree order/splitting and independent oracle/invariant validation. Benchmark ranks
are prepared as first sorted positions while original insertion order is preserved.
Construction and lookup are separately measured; reference sorting/rank mapping,
queries, full validation and destruction stay outside their respective intervals.
All structures use the unchanged Phase 3 deterministic query plans. This initial
small smoke protocol authorizes no large study, isolated memory or comparative
performance conclusion. New frozen protocols and resource checks precede larger
structure studies. Earlier sorting/search protocols/results remain immutable.

## Phase 5 orchestration extension

[ORCHESTRATION_PROTOCOL_v1.md](ORCHESTRATION_PROTOCOL_v1.md) is a separate frozen
extension. Existing search/structure protocols and 1M sorting study are unchanged.
It defines an all-family development smoke, a distinct 180-configuration full
matrix, strict unified observations, hierarchical dataset statistics, serial
execution, interruption/failure/missing semantics, resource/runtime gates and
reproducible SVG/PDF/report generation. Existing data and query generation/timing
boundaries stay intact. No comparison/RSS path enters primary timing. Plot/count/
memory evidence availability and full-study status must be reported explicitly.

The Phase 5 full preset completed 180 configurations/22,020 measured trials and
4,404 warmups at sizes through1M; all correctness checks passed. Its raw data,
processed report/statistics and SVG/PDF figures are separate new artifacts under
phase5_full_20261009T191000587965Z. All derived bytes regenerated; frozen family protocols and older
sorting study stayed unchanged. No comparison/memory measurement or universal
performance conclusion is inferred from this timing study.

## Phase 6 OpenMP extension

[OPENMP_PROTOCOL_v1.md](OPENMP_PROTOCOL_v1.md) freezes separate configurable
parallel Merge Sort contracts and parallel_sort_timing_v1. Existing generator,
sort/search/structure protocols, Phase 5 presets and previous results are unchanged.
Primary sequential-merge and secondary parallel-one-thread scaling baselines remain
separate. Actual teams, compiler/runtime/flags, task threshold and environment are
recorded; construction/copies/validation follow shared sorting timing boundaries.
A separately frozen launch document follows correctness/sanitizer/smoke/regeneration
and resource review; this candidate protocol alone is not proof a full study ran.

## Cloud GPU follow-up gate

The requested cloud GPU follow-up is blocked at environment Gate 1. No GPU
sorting protocol or experiment was implemented: Gate 2 requires actual cloud
device enumeration and a checked kernel. Existing frozen protocols and studies
remain unchanged. CPU regression checks are not cloud validation.
[Gate evidence](../results/raw/gpu_cloud_gate1_20261009T211734154323Z/FINAL_AUDIT.md).

## Post-cloud validation: first CUB correctness slice

The retained archive at ../results/evidence/cloud_validation_evidence.tar.gz
matches SHA256 48b3e78360e7c0c1721c21a3879bc975b902f5b3603fa25a0c92230c695c0810.
Its reports show Tesla T4/compute7.5, driver580.82.07, nvcc13.0.88/runtime13000,
checked device0 kernel, 1/1 runtime CTest and23/23 cloud CPU tests (OpenMP OFF).
These are historical environment results, not new GPU sorting evidence. Earlier
blocked entries remain history; the roadmap table/latest entry is current.

The new correctness-only adapter cub_radix_sort sorts full-domain signed int32
via genuine CUB DeviceRadixSort::SortKeys. It uses per-call owned host/device
buffers, checked transfer/launch/synchronization/cleanup, a separate GPU registry,
and no CPU substitution. CPU sorters/defaults and timing schemas are unchanged.
CUB reference v3.0.0, commit e944297b0b51a8e9c0f1b30425370c31c1c0e0a0, BSD-3-Clause,
is identified in third_party/cub (upstream source unmodified, toolkit headers used).
The initial version/header hashes are checked; installed cloud CUB compatibility
is not known from the old runtime archive.

Build opt-in: MAB_ENABLE_CUDA=ON and MAB_ENABLE_CUDA_SORT=ON. Both default OFF;
readiness-only CUDA remains separate. cuda_sorting CTest/validate_cuda_sort.py
exercise public/registry/repeated paths against std::sort, including non-power-of-
two sizes and signed extrema. Missing hardware is explicit, never a passing sort.
The expected475 cases/1900 output checks have **not run on a GPU**. Local CUDA
configuration failed because no CUDA compiler is installed; no local driver change.
No new GPU sorting build/execution, timing/smoke study or full study is claimed.

Follow [the correctness contract](CUDA_SORT_PROTOCOL_v1.md) and
[the cloud validation handoff](CUDA_SORT_VALIDATION_GUIDE_v1.md).
Next milestone: compile/run this exact source on the validated cloud GPU, retain
and review the new sorter evidence, then define separate GPU timing methodology.
Original learned-index/AlphaDev, scaling and final research phases remain pending.

## Observed CUDA correctness and pending timing

[CUDA_SORT_PROTOCOL_v2.md](CUDA_SORT_PROTOCOL_v2.md) supersedes only the initial
CUB dependency/result identity contract; v1 remains frozen history. Reviewed
CUB3.0.1 headers match the installed Colab toolkit. Actual T4 sorter build,
475-case/1900-check direct execution and repeated1/1 CTest passed; both original
failed configure and successful retry were exported/hash-verified locally.
See [results/raw/cub_correctness_colab_20261009T223853955936Z/FINAL_AUDIT.md](../results/raw/cub_correctness_colab_20261009T223853955936Z/FINAL_AUDIT.md).
This establishes correctness only. Separate transfer/device/end-to-end timing,
allocation/reuse rules, matrix resource review and GPU experiments remain pending.


## Prepared CUB timing milestone validated

[Timing protocol v1](CUDA_TIMING_PROTOCOL_v1.md) and `cuda_sort_benchmark` now
provide separately labelled H2D/device-sort/D2H CUDA events and steady_clock
prepared end-to-end latency. Production adapter, CUB3.0.1 pin and CPU defaults are
unchanged. Allocations/context/setup, input staging, output-vector copy and oracle
validation are excluded; event units ns preserve float-ms API precision. This is
not allocation-inclusive production-adapter timing or isolated kernel active time.

Actual Colab T4 Release execution: smallest smoke5 measured/1 warmup, then48
configurations (N0/1/1025/65537, six workloads, two seeds, W1/R5),240 measured/48
warmups; zero failed/missing. Full outputs equal std::sort outside timing. GPU
framework14/14 methods pass (60 validation-only configurations), and production
correctness repeats475 inputs/1900 checks directly and through1/1 CTest. Local
CPU Release27/27 and ASan/UBSan27/27 pass with leaks enabled; GPU methods are
explicitly skipped only in host-only analysis tests. CPU sanitizers do not validate
device code. Known nvcc generated-line warnings are retained (100+161); no other
warning category or pin modification. No full GPU comparison study is claimed.

[Raw evidence/audit](../results/raw/cuda_timing_20261009T231303050084Z/FINAL_AUDIT.md),
[processed report](../results/processed/cuda_timing_20261009T231303050084Z/REPORT.md),
and [matrix statistics](../results/processed/cuda_timing_20261009T231303050084Z/matrix.json)
retain every observation, exact commands, hashes and per-dataset median/mean/sample
SD/min/max. Summary regeneration passes in both environments; local/cloud statistic
groups match, with relocated absolute provenance paths. All9,568 earlier result
files remain unchanged. Clock/thermal/background controls are unverified; post-run
probes are not timing controls. See audit for resource/timing limitations.
