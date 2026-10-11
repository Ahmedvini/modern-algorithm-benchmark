# Implementation roadmap

Work follows the phase order in `AGENTS.md`. Completion requires code, tests,
documentation, and actual validation; scaffolding alone is insufficient.

| Phase | Status |
| --- | --- |
| 0 — audit and baseline | Complete: Release build, differential tests, immutable environment manifest |
| 1 — correctness-first core | Complete: saved CLI/generator docs and swap regressions; fresh Release and sanitizer suites passed 4/4 |
| 2 — required sorting algorithms and metrics | Complete for required CPU core: six sorters, five counted adapters (radix unsupported), process RSS, timing CSV/statistics and first 1M study validated; further studies optional |
| 3 — search benchmarks | Complete for batch mode: three array searches, deterministic queries, separate counts, CSV/statistics; individual-query timing deferred |
| 4 — search data structures | Complete: Skip List and B-tree orders 10/16/32/64, differential/invariant tests, separate build/lookup smoke and verified immutable evidence |
| 5 — orchestration and analysis | Complete for CPU timing: strict all-family orchestration, hierarchical statistics, SVG/PDF variability plots/report, validated smoke and full multi-size study |
| 6 — OpenMP | Complete: stable task Merge Sort, team metadata, fresh 24/24 Release/sanitizer groups and validated 1/2/4/8-thread scaling study; TSan startup limitation retained |
| 7 — CUDA | Preflight/guide milestone complete: 25/25 CPU Release/sanitizer groups; local GPU detected but driver/toolkit unavailable; CUDA target/GPU sorting/timing and Colab execution not run |
| 8 — learned index and AlphaDev study | Pending |
| 9 — 100M scale | Pending; not run |
| 10 — report and presentation | Pending |

The entries below record milestone history; the status table and latest phase entry describe the current state.

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

The first 1M Release study is now complete under
[the frozen v1 protocol](studies/sorting_1m_20261009T172003802655Z_v1.md): all six algorithms, five
distributions, three seeds, one warm-up and five measured repetitions completed
15 configurations, 450 successful measured trials and 90 successful warm-ups,
zero failures/omissions. Preflight Release CTest passed 15/15 groups; earlier
sanitizer results are historical, not a fresh run for this experiment. All raw
observations are retained. All five derived files regenerated byte-for-byte,
and raw files, frozen protocol and earlier evidence remain unchanged.

Phase 2's required CPU sorting milestone is complete; these descriptive timings
represent one shared-machine session with dynamic frequency/background activity,
not universal performance or significance. Cross-seed summaries use three
seed medians with equal weight. Algorithm-specific temporary allocation tracking
and larger/replicated experiments remain optional future work; process RSS is
not isolation and was not measured in this timing study. Recommended next sorting
experiment: separately freeze a 1M replication across independent sessions/more
held-out seeds with documented affinity/power policy and counterbalanced order.
Next implementation milestone: Phase 3 deterministic hit/miss query sets and
search benchmarks. No size above 1M, plots, CUDA or 100M run has occurred.
See BENCHMARKING.md and AUDIT.md for actual evidence and limitations.

Phase 3 array search/batch infrastructure is now implemented and validated.
linear_search, binary_search and exponential_search return first-match positions
or absence. The unchanged std_lower_bound adapter is the reference; sorted
preconditions are checked by the engine outside timing. search_batch_v1 fixes
deterministic category/query semantics, normalized batch averages and explicit
unavailable categories; search_counts separately measures key predicates.

Fresh full Release and Debug ASan/UBSan suites pass 18/18 groups, with leak
detection enabled. New search tests pass 3,704 inputs/309,996 oracle checks,
72 reproducible configurations/4,266 validated batches and 12 Python framework
methods. The retained Release smoke covers eight configurations and all nine
policies where applicable: 705 measured successes, 141 warm-up successes, zero
failures; 25 unavailable category/configuration pairs retain explicit reasons.
Its 141-group summary regenerates byte-for-byte. All 534 earlier raw/processed
artifacts and both frozen protocols remain unchanged; see AUDIT.md for evidence.

The batch benchmark milestone is complete. No direct individual-query maximum
is measured; calibration/individual latency, large search studies and search
memory experiments remain future work. Next implementation milestone: Phase 4
Skip List then B-Tree/M-way structures, with first-duplicate semantics, separate
build costs and differential tests before benchmark integration. A controlled
1M search study needs a separately frozen protocol/resource review; it has not
run. No CUDA or 100M experiment was attempted.

Phase 4's insertion/lookup milestone is complete under the frozen
[structures protocol](STRUCTURES_PROTOCOL_v1.md). First-payload maps own their
storage; deletion/update and copy/move are deliberately unsupported. Fresh full
Release and Debug ASan/UBSan suites passed 21/21 groups, with leak detection enabled
and no final compiler warnings. Structure tests passed 6,635 cases, 1,239,680
insertion attempts, 3,218,705 oracle lookups and 75,665 invariant validations.
Timing tests validated 72 workloads/8,190 rows; 11 Python methods passed.

The development smoke completed eight configurations: 200 measured builds,
1,175 measured lookup batches and 275 warmups, zero failed/missing trials. Its
275-group summary regenerated byte-for-byte; all 696 earlier artifacts, frozen
sorting/search protocols, existing implementations/tests/vendors and the new
structures protocol remain unchanged. See AUDIT.md for commands and evidence.

Next roadmap milestone: Phase 5 full experiment orchestration and reproducible
plots with variability. A larger structure/search study requires a new frozen
protocol and resource review; it has not run. Structure comparison counting,
isolated allocation tracking, calibrated individual-query latency and allocation-
failure injection remain deferred. No CUDA or 100M workload was attempted.

Phase 5 delivered both a validated pipeline and the frozen full CPU timing study.
experiment_pipeline_v1 serially wraps the existing family runners; no C++
algorithm/timing/source or previous family tool changed. Exclusive paths, stable
configuration hashes, deterministic dry-run plans, strict observations and
interruption/failure diagnostics are implemented. Resumption is unsupported.

Final Release and Debug ASan/UBSan suites pass 22/22 groups; 23 new Python methods
also pass independently. Leak detection remained enabled. The smoke completed
36 configurations, 3,260 measured successes/652 warmups, zero failed/missing trials;
81 SVG/PDF figure pairs and all processed bytes regenerated exactly.

Resource planning, smoke integrity and a separately labeled 100K calibration
preceded the full preset. All 180 configurations completed at 1K/10K/100K/1M,
five distributions/three seeds/Q1000/W1/R5: 22,020 measured successes and 4,404
warmups, zero failed/missing trials. Its 4,404 per-dataset/1,468 cross-dataset groups,
177 figure pairs and consolidated report regenerated byte-for-byte. All 867 earlier
artifacts, frozen protocols/studies and 671 pilot artifacts remain unchanged.
Construction and lookup stay separate; batch averages are not individual latencies.

Count/memory figures lack a matching experimental study and are explicitly
unavailable; no such values are inferred. Independent-session replication,
calibrated per-query latency and structure allocation/count experiments remain
future work. The full results are descriptive for one uncontrolled shared-machine
session, not significance or a universal ranking. No CUDA or 100M run occurred.
Exact next implementation milestone: Phase 6 OpenMP parallel sorting with separate
thread-count configuration, differential validation and reproducible scaling.

Phase 6 is complete for the documented OpenMP scope: separate stable
parallel_merge_sort_v1, shared timing loop and32-column parallel_sort_timing_v1,
actual-team metadata, strict exclusive matrix orchestration, paired dataset-level
speedup/efficiency, min/max variability plots and reproducible report. The original
six algorithms/default and all prior frozen artifacts remain unchanged.
Final Release24/24 and ASan/UBSan24/24 groups passed; leak detection stayed enabled.
523 inputs/4,184 outputs, ten concurrent large calls, observed task/merge/stability
checks and13 Python methods passed. ThreadSanitizer startup failed even without
OpenMP (exit66); no race-freedom claim. The all-distribution metadata regression
corrected the first full attempt's analysis failure before fresh tests and retry.

The exclusive retry smoke completed320 measured/64 warmups in32 configurations;
the full study completed1,800 measured/360 warmups in180 configurations, zero
failed/missing trials, N32768/100K/1M, all five distributions, three seeds and
threads1/2/4/8. Twenty SVG/PDF pairs/report/summary regenerated exactly.
All3,796 prior artifacts and the failed attempt remain unchanged. Evidence:
[protocol](OPENMP_PROTOCOL_v1.md), [frozen launch](studies/openmp_scaling_20261009T200852928292Z_retry1_v2.md),
[report](../results/processed/openmp_scaling_20261009T200852928292Z_retry1/REPORT.md),
[audit](AUDIT.md) and [results/raw/openmp_validation_20261009T200852928292Z](../results/raw/openmp_validation_20261009T200852928292Z).

Next implementation milestone: **Phase7 CUDA** — verify actual device/runtime,
freeze transfer/kernel/end-to-end semantics, and provide a reproducible CUB Colab/
cloud notebook or guide. No GPU result is implied. Learned-index/AlphaDev,
100M/resource scaling and final research report/presentation remain pending.
Independent-session CPU replication, direct per-query latency calibration and
separate comparison/memory experiment figures remain deferred research work.

Phase7's **requested readiness/guide milestone is complete**, distinct from the
original roadmap's GPU sorting and timing objectives. MAB_ENABLE_CUDA defaults OFF;
CUDA discovery and the isolated tiny runtime target exist only on explicit opt-in.
The versioned [readiness contract](CUDA_PREFLIGHT_PROTOCOL_v1.md) and
[Colab/cloud guide](CUDA_EXECUTION_GUIDE_v1.md) cover verified source snapshots,
readiness classification, optional builds/smoke, CPU fallback and persistent export.

Fresh final CPU Release25/25 and ASan/UBSan25/25 groups passed (leaks enabled),
including22 preflight/build-isolation methods. Default/explicit CUDA OFF ignore an
unavailable CUDACXX; separate CPU fallback configure/build/registry passed. Local
PCI shows NVIDIA GA107M/GeForce RTX3050Ti Mobile, but no bound kernel driver,
NVIDIA module/device nodes, driver version file, discoverable CUDA libraries,
nvidia-smi or nvcc. Preflight exited2 (unavailable/unverified), not a CPU failure.
CUDA ON configure/build/kernel and Colab execution were **not run**; mocked
operational fixtures are not hardware evidence. All8,447 earlier artifacts match.
Evidence: [results/raw/cuda_preflight_20261009T205410772326Z_reviewed/report.json](../results/raw/cuda_preflight_20261009T205410772326Z_reviewed/report.json),
[results/raw/cuda_preflight_validation_20261009T205410772326Z](../results/raw/cuda_preflight_validation_20261009T205410772326Z) and AUDIT.md.

Next GPU milestone: run the source-verified guide/preflight and isolated target
on an actually allocated GPU, then separately implement pinned/licensed CUB
sorting, CPU differential validation and synchronized H2D/algorithm/D2H/end-to-end
metrics under a new protocol. Original Phase7 GPU experiments remain pending;
Phase8 learned-index/AlphaDev, Phase9 scaling and Phase10 research deliverables
also remain pending. No CUDA performance or100M execution is claimed.
