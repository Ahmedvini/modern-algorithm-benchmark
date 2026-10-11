# Sorting metric definitions

The current [CPU-only release methodology](CPU_ONLY_RELEASE_v1.md) distinguishes
within-dataset repetitions from cross-dataset summaries, minima from medians,
and RSS from auxiliary space. Existing CPU timing/count/memory observations are
retained. GPU metric definitions later in this document are
[deferred historical specifications](DEFERRED_GPU.md), not current release
measurements or completion criteria.

## Completed separate metrics matrix

The [count/RSS protocol](COUNT_MEMORY_STUDY_v1.md) was executed separately from
timing:240 `sort_metrics` invocations, five counted adapters, four distributions,
four sizes through1M and three seeds. All returned exit0 after oracle validation.
The first collector attempt failed while parsing the memory wire schema; its
single successful native record and failure are retained. The corrected retry
uses a new directory and the actual seven-field JSON schema (`value`, not the
C++ API member name `peak_rss_bytes`). Eight focused parser regressions pass.

Raw data is in
`results/raw/autonomous_completion_20261011T095554571762Z/count_memory_retry1/`;
regenerable statistics and eight figures are in
`results/processed/count_memory_20261011T095554571762Z/`. Counts retain every
dataset observation. RSS is Linux `getrusage` process-lifetime peak in bytes,
including input/runtime/allocator/instrumentation. It is not isolated auxiliary
memory; small-N high-water marks can be dominated by startup. Radix comparison
counting remains unsupported, with no fabricated zero count.

Learned-index diagnostics independently report prediction error, fallback,
executed key predicates, vector capacity bytes and object bytes. Its process RSS
is also lifetime-wide. Query timing excludes these diagnostics; no individual
query maximum is inferred from normalized batch averages.

sort_metrics and mab_metrics provide separate instrumented validation. The
original algorithm_benchmark CLI, eleven-field schema, registry and std_sort
default are preserved. The normal executable links only mab_core. This milestone
adds no timer, repetition matrix, timing CSV or performance comparison.

## Key comparisons: key_less_than_v1

One comparison means one executed binary signed-int32 less-than evaluation in
the counting comparator. True and false results each count once. Equal/self keys,
copied pivots and temporary-buffer keys follow the same rule. A three-way decision
that evaluates a < b and b < a counts twice. Pivot, insertion, partition, merge,
galloping and heapsort comparisons are included. Swaps, assignments, iterator/index
tests, run/depth/stack bookkeeping, generation and later verification are excluded.

Each adapter creates a uint64 counter initialized to zero. Comparator copies
refer to that run-local counter throughout the synchronous sort. No counters
survive the call or are shared across independent calls. A single counted run
does not execute its comparator in parallel. Overflow throws before wrapping;
no successful count is returned, and input may already be partially rearranged.

| Sorter | Instrumented identity | Relationship to production |
| --- | --- | --- |
| std_sort | std_sort_counting_less | std::sort with an ascending counting comparator; library/compiler dependent |
| quick_sort | project_quick_sort_counting_less | Shared project template and depth budget; includes pivot/partition and both heap calls |
| pdq_sort | upstream_pdqsort_branchless_counting_less | Explicit upstream branchless entry point preserves production int32/std::less policy |
| tim_sort | upstream_gfx_timsort_counting_less | gfx::timsort with identity projection and counting comparator |
| merge_sort | project_merge_sort_counting_less | Shared bottom-up merge template with right < left counting predicate |

Five comparison sorters support counting. Radix Sort performs digit extraction,
histograms and scatter without key comparisons, so comparison complexity is not
represented by a fabricated zero. It is absent from counted_sorters; requesting
find_counted_sorter("radix_sort") throws an explicit unsupported invalid_argument.
The metrics CLI exits 1, prints that diagnostic to stderr and emits no JSON or
RSS record for this unsupported request. This preserves the existing schema
without treating an unavailable metric as a successful count. The process-memory
API itself remains algorithm independent; allocation-specific radix memory is
not measured. Tests require coverage of all other production registry names.
Unknown counted names still throw the existing error. No count is estimated.
QuickSort's internal template accepts a comparator, defaulting to empty
std::less<Key> in normal execution. Its public adapter, pivot policy, boundaries,
depth and observer semantics are preserved. Normal execution has no counter
updates or runtime instrumentation switch.

PDQSort's automatic trait recognizes std::less/std::greater but not a custom
comparator. Passing a counter to ordinary pdqsort would choose a different
partition policy. The counted adapter uses public pdqsort_branchless and a
compile-time check that production still chooses branchless for int32/default
comparison. No upstream trait or source is modified. Counting side effects may
change generated instructions; this metric counts key predicates, not CPU branches.

Timsort forwards ordering through its comparator, including upper_bound and
galloping. Its post-sort audit is disabled in the established configuration;
the counted translation unit rejects GFX_TIMSORT_ENABLE_AUDIT to prevent counting
verification work. Checked/debug standard-library modes can add comparator
checks and need separate metric review; the validated flags do not enable them.
Vendored sources, licenses and provenance are unchanged.

All adapters use the same signed-int32 predicate unit on identical inputs, so
counts describe predicate work under those recorded implementations. Counts do
not rank elapsed time or machine instructions. Comparator instantiation can
change generated code, and std::sort counts are not portable across libraries.
Exact tests use manually checked project QuickSort and Merge Sort traces and comparator
semantics; upstream/library counts are checked for repeatability within a build
without hardcoding implementation-specific expected numbers. Counted runs must
never substitute for normal timing runs.

## Measured memory

The metric is process peak resident set size, normalized to bytes. On Linux,
getrusage(RUSAGE_SELF).ru_maxrss returns KiB; checked multiplication by 1024
converts it. See [Linux getrusage documentation](https://man7.org/linux/man-pages/man2/getrusage.2.html).
This interpretation requires Linux 2.6.32 or newer. Other platforms explicitly
return unsupported, method none and a null value. macOS's different ru_maxrss
units are not interpreted as Linux data.

The scope is process lifetime up to sampling: a high-water mark, not current
RSS, a resettable interval or an allocation delta. RUSAGE_SELF covers process
threads, not children. Resource-usage history can survive exec, so a new CLI
invocation does not establish an isolated algorithm-memory baseline.

sort_metrics samples immediately after instrumented sorting and before creating
reference/normal-sort validation vectors. Generation (including sorting inside
some distributions) is part of the earlier process history. Output occupies the
input vector. Resident input/output, algorithm workspace, stack, allocator
metadata/retained pages, runtime/library/loader and counting overhead can all
contribute. Sanitizer runs include sanitizer overhead. Only resident pages count;
this is not virtual memory or allocated bytes. Later verification/output occur
after the captured sample. Values can vary between launches/builds.

RSS does not isolate algorithm auxiliary memory. No temporary-buffer allocation
metric is implemented: upstream vectors retain their existing allocators, with
no global allocation interposition. QuickSort's O(log N) stack and Timsort's O(N)
workspace remain theoretical descriptions, separate from measured memory. No
cross-algorithm memory study or performance conclusion is claimed.

getrusage failure reports error/null/errno. Negative or unrepresentable results
report EOVERFLOW instead of wrapping. The CLI emits a partial JSON record retaining
comparisons, writes an error to stderr and exits 1. Unsupported memory permits a
successful count record with unsupported/null, never a fabricated zero. Formatting
rejects inconsistent reports.

## CLI and schema

```sh
build/release/sort_metrics --sort quick_sort --size 2 --distribution duplicate_heavy --distinct 1
```

This validation input yields seven QuickSort key comparisons; RSS is read at
runtime and has no fixed expected value. Dataset/sorter options and defaults
match the correctness CLI: size 1000, seed 1729, uniform, swaps floor(N/100),
distinct 16, std_sort. Strict unsigned decimal parsing, bounds, repeated options,
immediate --help and allocation exception behavior follow README's CLI rules.
No search workload is run. Unknown sorter errors say "unknown counted sorter".
Argument/counter/correctness errors exit 1 with error: on stderr and no success
JSON. Memory failure uses the partial-record behavior above.

After full equality to std::sort and the corresponding normal registry sorter,
the command emits one JSON object plus newline. It has 15 top-level fields:

| Field | Meaning |
| --- | --- |
| schema_version | Integer 1 for this independent metric schema |
| mode | sort_metrics |
| status | ok, or partial for memory measurement failure |
| sort_algorithm | Registered sorter name |
| instrumented_implementation | Identity from the adapter table |
| comparison_convention | key_less_than_v1 |
| key_comparisons | uint64 count from this sort alone |
| dataset_generator | mt19937_64_v1 |
| size, seed, distribution | Resolved dataset configuration |
| nearly_sorted_swaps, duplicate_cardinality | Requested/resolved parameters, including inactive ones |
| memory_sample_point | after_instrumented_sort_before_validation |
| process_memory | Object below |

process_memory has seven fields: status (ok/unsupported/error), metric (peak_rss),
scope (process_lifetime), unit (bytes), method (getrusage_ru_maxrss/none), value
(uint64/null), error_code (errno/null). Value exists only for ok, error_code only
for error; method none means unsupported. No timing or theoretical space is
encoded as measured data. JSON consumers must preserve large integer precision.

## Validation limits

Tests cover exact QuickSort traces, exhaustive arrays, deterministic distributions,
extrema, sorted/reverse/equal/patterned inputs, counted/normal/reference equality,
copied comparators, overflow, repeated/interleaved reset and heap forwarding.
Memory JSON fixtures are explicitly synthetic values, including zero, error and
unsupported. Real Linux probes check units/high-water behavior without requiring
a specific RSS. A separate build tests the actual unsupported source branch on
Linux; Windows/macOS were not run. No actual getrusage failure is induced;
error-object formatting uses a fixture. CLI tests cover schema, identities,
parameters, invalid arguments and repeated counts while allowing RSS to vary.
Raw records are metric validation evidence, not a performance experiment matrix.

## Relationship to the recorded 1M timing study

The [first 1M protocol](studies/sorting_1m_20261009T172003802655Z_v1.md) runs normal production sorts
without comparison counting. No separate process RSS or algorithm-allocation
study was performed in that milestone. Its 16,000,000-byte array/workspace
planning estimate is not measured memory. Existing process peak RSS remains
a process-lifetime metric available through the independent metrics path; it
must not be inferred from sort timing or interpreted as isolated auxiliary space.

## Separate search counts: key_predicate_v1

search_counts shares the deterministic sorted-input/query plan with search_benchmark
but performs separate per-query counted execution and records no lookup timing.
One executed binary signed-int32 < or == predicate counts once, irrespective of
its Boolean result. Linear counts equality checks; binary/exponential include
lower-bound and expansion predicates plus final equality checks. Bookkeeping,
index arithmetic, query construction and reference validation are excluded.
This unit differs from sorting's key_less_than_v1; do not silently equate them.
Production and counted adapters instantiate the same project templates, but
normal paths have no counters or instrumentation flag. Counter copies refer to
a checked run-local uint64; independent calls share no mutable state.

search_counts uses exclusive bundles with search_counts_v1 metadata, queries.csv,
counts.csv and COMPLETE/FAILED markers. counts.csv fields are algorithm,
query_category,query_id,target,expected_position,actual_position,key_comparisons,
comparison_convention,correctness. Empty positions mean absent; successful counts
must agree with the first-match oracle. Timing-only options are rejected; the
primary timing analyzer refuses count bundles. No process-memory or search-specific
allocation metric is added. Sorting's Linux RSS API and limitations are unchanged.
Normalized search batch ns/query is not directly measured individual-query latency;
no maximum per-query duration is reported without future timer calibration.

## Phase 4 structure metrics

structures_batch_v1 reports construction ns and lookup-batch ns separately.
Construction includes fresh constructor/RNG initialization and all insert attempts,
including duplicates; destruction is excluded. Lookup uses no counting path or
sorted-input preprocessing. Normalized batch ns/query is an average, never directly
observed individual latency. No new comparison metric is supported for the indexes;
no count is estimated from timing or algorithm complexity. All size/invariant/rank
validation is outside timers. Diagnostic split/level counts in tests are structural
coverage evidence, not comparison counts or benchmark performance metrics.

Owned-storage complexity is theoretical O(U) for B-trees and expected O(U) for
Skip List (hard O(32U)), with U unique keys. The 512*N+128*queries*9 planning guard
is neither measured memory nor a process cap. No index-specific allocation or RSS
experiment ran here. Existing Linux process-lifetime peak RSS remains available
only through its independent API; it cannot isolate one index's memory, be reset
between structures, or be inferred from this study's timings.

## Phase 5 statistical/visual units

The unified pipeline stores integer ns observations and traceable raw metadata.
Sorting/construction plots convert to ms; lookup plots normalize batch ns by Q
and explicitly label batch-average ns/query. Neither normalization nor maximum
batch average is a directly measured individual-query maximum. Cross-dataset
statistics aggregate distinct-input medians with equal weight after per-dataset
repetitions; min/max error bars are descriptive spread, not confidence intervals.
Identical prepared fingerprints do not provide independent search datasets.
Source/flags/build/policy/seed grouping definitions are in the new orchestration
protocol. Separate comparison and process-RSS implementations are unchanged;
no count/memory experiment is inferred from timing or theoretical complexities.
Unsupported count/memory plots remain explicitly listed as missing evidence.

## Phase 6 parallel sorting metrics

parallel_sort_timing_v1 records normal sorting ns and requested/actual OpenMP team
size per row; it does not count comparisons or process RSS. Team size means members
of the created team, not observed busy workers. Below threshold or request1 executes
serially and reports actual1. Unknown failed invocation team size is0. Task/merge/
worker observers exist only in correctness tests. Mixed actual-team cells are rejected
from analysis rather than pooled. Common sorting validation remains outside timing.

Algorithmic speedup uses the sequential merge_sort cell median / parallel median;
implementation speedup uses the separate parallel-request1 median / parallel median.
Their efficiencies divide by actual p. Compute ratios per dataset, then summarize
equally weighted distinct-input ratios with sample SD/min/max. These are descriptive
ratios, not significance or a promise of linear scaling. No parallel counted adapter,
isolated buffer tracking or measured OpenMP runtime memory is implemented.


## Prepared GPU timing metrics

`cuda_sort_timing_v1` records H2D/device-sort/D2H event intervals in ns converted
from CUDA float milliseconds, plus host steady_clock end_to_end_ns. Event intervals
can include dispatch gaps; these are GPU timeline measurements, not isolated kernel
active time or host allocation measurements. Prepared buffers/workspace/events are
reused. The host interval includes submission/checking/wait/transfers/sort, excludes
allocation/context setup, staging, output-vector copy, oracle/verification and I/O.
Three event durations need not sum to host elapsed. Empty/singleton skip GPU work
and record three zeros. Full correctness is verified outside all timers.

Warmups remain in raw CSV but are excluded from per-dataset median/mean/sample SD
(ddof1)/min/max. Four metrics from a trial are not four independent observations.
No cross-seed pooling or confidence interval; signed_edges ignores seed. Failed
metrics are blank, never zero-filled. Strict analysis retains failed/missing counts
and rejects incomplete runs by default. No comparison count, isolated measured
memory, allocation-inclusive latency or speedup is inferred. Payload budgets are
planning only, excluding runtime/allocator overhead. See CUDA_TIMING_PROTOCOL_v1.md
and the latest audit for the validated smoke and API-resolution/cloud limitations.
