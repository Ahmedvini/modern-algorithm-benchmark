# Sorting metric definitions

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
