# Final audit: sorting_1m_20261009T172003802655Z

## Controlled one-million-element sorting study — 2026-10-09

Study `sorting_1m_20261009T172003802655Z` is complete under frozen v1 protocol
[protocol](studies/sorting_1m_20261009T172003802655Z_v1.md). No algorithms, timing/metrics implementation,
CLI, runner, analyzer, test, CMake or vendor file changed. Workspace write access
passed an anonymous temporary-file write/read/delete probe. Git metadata remains
absent: the environment probe git status --short exited 128; no Git revision is
invented. The current source, tools, build inputs and executable are SHA-256
manifested. Existing raw artifacts were inspected and hashed before new output.

### Frozen configuration, semantics and resource review

Six production sorters in registry order: std_sort, quick_sort, pdq_sort,
tim_sort, merge_sort, radix_sort. N=1,000,000 signed int32 keys; distributions
uniform, sorted, reverse_sorted, duplicate_heavy and nearly_sorted; seeds
1729,42,2718. One warm-up and five measured repetitions per algorithm/dataset.
Duplicate domain 16 ([-8,7]); nearly-sorted request exactly 10,000 index-pair
swaps, including allowed self/repeated pairs. Sorted uses the corresponding
uniform sample ordered ascending with zero swaps. Other inactive parameters
remain in the CSV as documented. mt19937_64_v1 is unchanged.

Expected and observed: 15 size/seed/distribution configurations, 90 algorithm/
dataset groups, 450 measured trials and 90 warm-ups, 540 total rows. Configurations
run serially in size/seed/distribution order; algorithm order uses the unchanged
seed_offset_cyclic_v1 rotation. Raw rows retain trial and execution indices;
five rounds do not fully balance six positions and no random shuffle occurred.
Each normal production call starts with the same restored original vector.
steady_clock times only sorting in integer ns, including sort-owned allocation/
deallocation. Generation, copying, reference sorting, full-output validation and
CSV I/O remain outside timing. Primary timing links mab_timing/mab_core, never
mab_metrics; no comparison-count experiment or process-RSS study was run.

Preflight MemTotal 16,475,164,672 bytes; MemAvailable 4,340,154,368 bytes;
free disk 134,457,196,544 bytes. Immediately before execution, available RAM
4,411,662,336 bytes and disk 134,454,919,168 bytes. The engine estimates
4*N*sizeof(int32) = 16,000,000 bytes (15.26 MiB), with unchanged planning limit
256 MiB. This excludes runtime/allocator overhead and bucket offsets and is
not measured memory or a hard RSS cap. Gates require >=256 MiB available RAM,
>=128 MiB free disk and equivalent finite-cgroup headroom if such a cap exists.
Accessible cgroup ancestors report memory.max=max and exposed cpu.max=max 100000;
address-space/data/RSS/file-size/CPU-time limits are unlimited, stack soft limit
8 MiB. Both preflight and immediate launch gates passed with matrix path absent.
No resource-driven protocol revision was necessary.

### Environment and limitations of control

Pop!_OS 24.04 LTS, Linux 6.18.7-76061807-generic, x86_64; Intel Core i5-11400H,
six physical cores and 12 logical CPUs, allowed affinity 0..11. GNU C++ 13.3.0,
CMake 3.28.3, Python 3.12.3, Release, sanitizers OFF; configured -O3 -DNDEBUG,
-Wall -Wextra -Wpedantic, C++17. Exact compile commands, cache, link command,
libstdc++ linkage, source/upstream provenance, CLI help/tool hashes are retained.
CLI/Python tools have no --version option; hashes and runtime versions identify
them instead. Benchmark executable SHA-256:
`98ae6eea14525a27241936abf4b493650a428bf6f0afcc1a94042dcfad087c7f`.

CPU policy observed before/after: intel_pstate powersave, balance_performance,
800000..4500000 kHz. No affinity, governor, priority or frequency change was made.
Preflight 1/5/15-minute load averages: 1.518/1.018/1.062; immediately before:
1.314/1.164/1.104; after: 1.286/1.176/1.109. Per-policy current-frequency,
pressure, cgroup and process-name/load snapshots are retained. A shared desktop
was used; background activity, CPU frequency, thermal and cache state were not
controlled. Thermal state was not measured. Copies touch input memory; this is
a warmed-input protocol. Timer overhead was not calibrated or subtracted.
These observations support descriptive findings for this session, not a universal
ranking, statistical significance or hardware-controlled population claim.

### Exact commands and fresh outcomes

All commands below exited 0. The full Release suite passed 15/15 CTest groups.
The build refreshed existing artifacts without source changes and emitted no
compiler warnings. The full suite includes 3,590 shared sort inputs/98,508 search
checks, 220 dataset combinations, QuickSort 3,718/PDQSort 4,027/Timsort 4,149 inputs,
4,015 inputs per new baseline, 1,404 comparison inputs across five adapters,
72 timing inputs/1,296 validated registry calls, and all CLI/memory/framework tests.
These tests are validation rather than study timings. No fresh sanitizer build
or suite was run for this documentation/experiment-only milestone; the preceding
15/15 ASan/UBSan result with leak detection enabled is historical evidence.

```sh
python3 results/raw/sorting_1m_20261009T172003802655Z/preflight_capture.py after_execution.json  # exit 0
python3 results/raw/sorting_1m_20261009T172003802655Z/analyze_study.py --self-test  # exit 0
python3 results/raw/sorting_1m_20261009T172003802655Z/preflight_capture.py before_execution.json  # exit 0
python3 results/raw/sorting_1m_20261009T172003802655Z/analyze_study.py --study /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/sorting_1m_20261009T172003802655Z  # exit 0
python3 results/raw/sorting_1m_20261009T172003802655Z/launch_review.py  # exit 0
python3 scripts/analyze_results.py /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/sorting_1m_20261009T172003802655Z/matrix --output /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/processed/sorting_1m_20261009T172003802655Z/per_seed.json  # exit 0
python3 results/raw/sorting_1m_20261009T172003802655Z/preflight_capture.py  # exit 0
cmake --build build/release --parallel 2  # exit 0
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_SANITIZERS=OFF  # exit 0
ctest --test-dir build/release --output-on-failure -V  # exit 0
python3 scripts/run_matrix.py --binary build/release/sort_benchmark --output /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/sorting_1m_20261009T172003802655Z/matrix --sizes 1000000 --seeds 1729,42,2718 --distributions uniform,sorted,reverse_sorted,duplicate_heavy,nearly_sorted --sorts std_sort,quick_sort,pdq_sort,tim_sort,merge_sort,radix_sort --repetitions 5 --warmups 1 --memory-limit-mib 256 --distinct 16 --swaps 10000  # exit 0
python3 results/raw/sorting_1m_20261009T172003802655Z/verify_study.py  # exit 0
```

Every benchmark child command is retained separately in matrix/*_command.json;
all 15 child exit codes are 0. Existing environment-capture subprocess probes
also retain their exact commands/statuses; Git 128 is the expected metadata-
absence inspection failure. There were no failed build, test, matrix, analysis,
regeneration or verification commands, and no retries or omitted configurations.

Matrix execution UTC: 2026-10-09T17:26:15.005269+00:00 through
2026-10-09T17:26:30.239307+00:00. The wrapper's 15.234 s elapsed time includes
setup/process/validation/output and is not algorithm sort time.

### Results and analysis units

All 450 measured trials and 90 warm-ups passed full-vector std::sort-reference
correctness; zero failed/missing trials. The parser validates the 28-field
sort_timing_v1 schema, units, metadata, cyclic order, row identities/totals and
completion markers. All 15 required configurations and 90 algorithm/dataset
combinations are present. All six algorithms share each configuration's input
fingerprint, and configured source manifests match the current source files.

The established analyzer emits 90 per-seed groups with five successes and zero
failures each, median/mean/sample SD/min/max in ns. Warm-ups are retained and
excluded from statistics. Cross-seed analysis computes descriptive median/mean/
sample SD/min/max of three equal-weight per-seed medians, giving 30 groups.
It does not pool 15 trials as independent datasets. Every raw observation,
including outliers, is retained; no clipping, winsorization or significance test.
Full per-seed and cross-seed tables (ms = ns/1,000,000) are saved under
results/processed/sorting_1m_20261009T172003802655Z/RESULTS.md with unrounded CSV/JSON alongside.
The study-specific analysis code and its synthetic-only known-statistic/group-
validation tests are retained in the new raw evidence directory; engine/runner/
established analyzer remain unchanged.

### Verification and immutable evidence

New raw location: results/raw/sorting_1m_20261009T172003802655Z; matrix contains 15 exclusively created
bundles and COMPLETE markers. protocol.json/PROTOCOL_v1.md match the frozen
project protocol, SHA-256
`5a684928f809f8aa373c9275697676e061595a31617bf03ea6f952f4d3a11b9b`.
preflight.json, before_execution.json, after_execution.json, repository/source/
executable manifests, exact command records and verification.json are retained.
Processed location: results/processed/sorting_1m_20261009T172003802655Z; per_seed.json/csv,
cross_seed.json/csv and RESULTS.md are derived files. FINAL_AUDIT.md is saved
separately under the new raw study path after review.

Verification regenerated all five processed files byte-for-byte in a temporary
new location. All 138 matrix files match their pre-analysis hashes; all 334
previous raw files match their pre-study hashes; frozen protocol and execution
inputs are unchanged. Raw datasets/results and earlier audit evidence were not
overwritten. No observed deviation from the frozen protocol or required matrix.
No comparison or memory results are estimated from timing; RSS remains a process-
wide lifetime measure available through a separate path, not isolated workspace.

### Status and next experiment

The requested 1M study milestone is complete. Phase 2's required sorting
implementations/metrics/repeatable timing and first 1M study are validated.
Optional allocation-specific metrics, additional sorting experiments and plots
remain future work. No dataset larger than 1M, CUDA, GPU or 100M workload was run.
Recommended next experiment: a separately frozen 1M replication across independent
sessions and more held-out seeds, with documented CPU affinity/power policy and
counterbalanced configuration order where practical; retain session/dataset units
rather than treating repeated trials as independent data. No such replication
has run. Next implementation phase is Phase 3 deterministic hit/miss queries
and search benchmarking; 10M/100M scaling remains deferred.

## Cross-seed descriptive statistics

Each row describes three dataset medians (five trials per seed). All rows have 15 successful trials, zero failed trials and three datasets. The standard deviation below is sample SD across three seed medians; min/max are the smallest/largest seed median, not the extremes of all 15 trials. Milliseconds = nanoseconds / 1,000,000; tables round to three decimals, JSON/CSV retain precision. No outliers removed and no significance test performed.

| Algorithm | Distribution | Median of medians (ms) | Mean of medians (ms) | Sample SD (ms) | Min median (ms) | Max median (ms) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| std_sort | uniform | 57.699 | 58.703 | 2.587 | 56.768 | 61.642 |
| std_sort | sorted | 8.740 | 8.716 | 0.064 | 8.643 | 8.763 |
| std_sort | reverse_sorted | 5.978 | 6.067 | 0.277 | 5.844 | 6.377 |
| std_sort | duplicate_heavy | 20.182 | 20.366 | 1.427 | 19.039 | 21.876 |
| std_sort | nearly_sorted | 10.407 | 10.542 | 0.357 | 10.272 | 10.946 |
| quick_sort | uniform | 83.771 | 86.526 | 5.076 | 83.424 | 92.384 |
| quick_sort | sorted | 74.459 | 75.527 | 1.869 | 74.436 | 77.685 |
| quick_sort | reverse_sorted | 72.090 | 72.520 | 3.892 | 68.861 | 76.610 |
| quick_sort | duplicate_heavy | 14.574 | 14.664 | 0.463 | 14.253 | 15.165 |
| quick_sort | nearly_sorted | 31.783 | 32.222 | 0.909 | 31.615 | 33.267 |
| pdq_sort | uniform | 24.457 | 25.080 | 1.477 | 24.016 | 26.767 |
| pdq_sort | sorted | 0.764 | 0.751 | 0.029 | 0.718 | 0.771 |
| pdq_sort | reverse_sorted | 1.558 | 1.523 | 0.084 | 1.427 | 1.584 |
| pdq_sort | duplicate_heavy | 4.248 | 4.383 | 0.267 | 4.211 | 4.691 |
| pdq_sort | nearly_sorted | 8.627 | 8.612 | 0.203 | 8.402 | 8.806 |
| tim_sort | uniform | 82.326 | 82.662 | 1.593 | 81.263 | 84.396 |
| tim_sort | sorted | 0.396 | 0.402 | 0.012 | 0.395 | 0.416 |
| tim_sort | reverse_sorted | 2.057 | 2.021 | 0.236 | 1.769 | 2.237 |
| tim_sort | duplicate_heavy | 40.939 | 40.833 | 1.598 | 39.185 | 42.375 |
| tim_sort | nearly_sorted | 7.693 | 7.773 | 0.269 | 7.554 | 8.073 |
| merge_sort | uniform | 75.129 | 77.611 | 4.958 | 74.384 | 83.319 |
| merge_sort | sorted | 10.942 | 10.773 | 0.316 | 10.408 | 10.969 |
| merge_sort | reverse_sorted | 10.903 | 10.442 | 1.088 | 9.199 | 11.224 |
| merge_sort | duplicate_heavy | 36.602 | 37.704 | 5.070 | 33.276 | 43.235 |
| merge_sort | nearly_sorted | 15.330 | 15.183 | 1.546 | 13.569 | 16.649 |
| radix_sort | uniform | 7.268 | 7.475 | 0.481 | 7.132 | 8.025 |
| radix_sort | sorted | 8.311 | 8.125 | 0.551 | 7.505 | 8.559 |
| radix_sort | reverse_sorted | 7.721 | 8.078 | 1.019 | 7.286 | 9.228 |
| radix_sort | duplicate_heavy | 13.286 | 13.135 | 0.373 | 12.710 | 13.410 |
| radix_sort | nearly_sorted | 8.388 | 8.195 | 0.696 | 7.423 | 8.775 |
