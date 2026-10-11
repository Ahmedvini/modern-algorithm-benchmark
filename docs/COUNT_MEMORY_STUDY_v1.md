# Separate count and process-memory collection v1

Use the existing Release sort_metrics executable, never the primary timing engine.
Five comparison-based adapters: std_sort, quick_sort, pdq_sort, tim_sort, merge_sort.
Radix Sort remains explicitly unsupported for key-comparison counts. No count0 is
fabricated for it. Upstream sources and production adapters are unchanged.

Matrix: sizes1000/10000/100000/1000000; distributions uniform/nearly_sorted/
reverse_sorted/duplicate_heavy; seeds1729/42/2718. Exactly240 independent process
invocations, one deterministic key-count execution per configuration. Each uses
the existing defaults: floor(N/100) swaps and duplicate cardinality16. No timing,
warm-ups, or performance ratios are collected. Input is regenerated using the
existing generator-v1 contract and output is fully checked by the executable.

Retain exact commands, exit status, stdout JSON and stderr per invocation. Require
matching algorithm/type/configuration, statusok and nonnegative key_comparisons.
The CLI has no explicit correctness field: its successful exit follows full
equality checks against std::sort and the normal adapter, as verified in source.
Memory must report its actual supported/error/unsupported status;
do not replace unavailable values. Stop on correctness failure. Treat interrupted
collections as incomplete. Use a new exclusive output directory.

Aggregate deterministic comparison counts across three distinct seed datasets;
median and min/max describe workload sensitivity, not noisy repetitions. Plot
count/N with signed-int32 key_less_than_v1 semantics from METRICS.md.

Linux process peak RSS uses getrusage(RUSAGE_SELF), KiB converted to bytes,
sampled after counted sort before validation. It includes inputs, sorting buffers,
counting code, runtime and allocator overhead from the lifetime of that child
process. It is not algorithm-specific temporary allocation. Each configuration
uses a separate process, but there is still no subtraction of a baseline or
isolation of auxiliary memory. Plot only supported observations in MiB, with
unavailable counts retained in the processed report. One RSS observation per
configuration does not establish repeatability; seed spread is descriptive only.

No GPU data, frozen CPU/GPU protocol change or significance claim is part of
this collection. Run it after timed CPU studies to avoid benchmark contention.
