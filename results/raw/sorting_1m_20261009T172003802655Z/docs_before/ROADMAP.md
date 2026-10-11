# Implementation roadmap

Work follows the phase order in `AGENTS.md`. Completion requires code, tests,
documentation, and actual validation; scaffolding alone is insufficient.

| Phase | Status |
| --- | --- |
| 0 — audit and baseline | Complete: Release build, differential tests, immutable environment manifest |
| 1 — correctness-first core | Complete: saved CLI/generator docs and swap regressions; fresh Release and sanitizer suites passed 4/4 |
| 2 — required sorting algorithms and metrics | In progress: six sorters, five counted adapters (radix unsupported), RSS and timing CSV/statistics validated; larger controlled studies pending |
| 3 — search benchmarks | Pending |
| 4 — search data structures | Pending |
| 5 — orchestration and analysis | Pending |
| 6 — OpenMP | Pending |
| 7 — CUDA | Pending; not run |
| 8 — learned index and AlphaDev study | Pending |
| 9 — 100M scale | Pending; not run |
| 10 — report and presentation | Pending |

Phase 0 validation: 2/2 CTest tests passed (310 differential sort cases and three
Python environment-manifest tests). See AUDIT.md for the initial missing-build
failure and exact environment artifact. Phase 1 validation passed 4/4 tests in
both Release and Debug ASan/UBSan builds, with leak detection enabled. The next
step was bounded project QuickSort. It now passes fresh 5/5 Release and sanitizer
suites, including observed forced/default-budget heapsort fallback. Phase 2
remains incomplete. Upstream PDQSort is now pinned with retained license and
attribution and passed fresh 6/6 Release/sanitizer suites before Timsort integration.
Timsort is now integrated from a pinned C++17-compatible upstream commit with
unchanged MIT-licensed source, hashes and attribution. Fresh full Release and
Debug ASan/UBSan suites pass 7/7 groups, including 4,149 dedicated Timsort inputs
through public/registry paths and ten CLI methods. Leak detection was enabled.
Separate comparison-count instrumentation and documented process memory reporting
are now complete: all four sorters have counted adapters, and Linux process peak
RSS is reported with explicit scope/units and unsupported/null elsewhere. Original
CLI and registry behavior are preserved. Fresh Release and Debug ASan/UBSan pass
11/11 groups, including 1,404 comparison inputs and real/forced-unsupported memory
paths, with leak detection enabled. See METRICS.md and AUDIT.md for actual evidence.

Repeatable timing/CSV infrastructure and separate statistics are now implemented
and validated. sort_timing_v1 uses normal registry calls, identical restored input,
one warmup/five repetitions by default, monotonic nanoseconds, out-of-timing full
validation, deterministic cyclic ordering, exclusive raw bundles and explicit
failure/completion records. All 13 CTest groups pass in Release and ASan/UBSan,
with leak detection enabled. The actual 1K/10K smoke matrix passed ten configurations,
200 measured trials plus 40 warmups; 40 separate algorithm groups were summarized
without outlier removal. This is not a general performance ranking.

The optional Merge Sort and signed Radix Sort milestone is now complete. Stable
bottom-up Merge Sort uses one N-key buffer and a separate counted comparator.
Stable four-pass radix-256 sorting maps signed keys by flipping the high unsigned
bit and uses one N-key buffer plus 256 offsets; comparison counts are explicitly
unsupported rather than fabricated. Both public adapters join the normal registry
and automatic matrix discovery, preserving std_sort as the default.

Fresh Release and Debug ASan/UBSan suites pass 15/15 groups with leak detection
enabled and no compiler warnings. Each new sorter passes 4,015 differential input
cases through public/registry/repeated paths; shared comparisons cover five
adapters, including eleven exact Merge Sort fixtures. The timing tests validate
1,296 registry calls. A fresh 1K/10K all-six-sorter smoke matrix completed ten
configurations, 300 measured trials and 60 warmups; its 60-group summary regenerated
exactly from retained raw CSV without removing outliers. See AUDIT.md for evidence.

Phase 2's sorting implementations and infrastructure are validated; larger
controlled sorting studies remain unfinished. Algorithm-specific temporary
allocation tracking is not implemented; supported memory is process RSS, not
isolation. Next Phase 2 step: document a controlled 1M study configuration and
collect/analyze its repeated Release trials before drawing comparisons. The next
implementation phase after sorting experiments is Phase 3's deterministic
hit/miss query sets and search benchmarking. No 1M/10M performance study, plots,
CUDA or 100M run has occurred. See BENCHMARKING.md and AUDIT.md.
