# Frozen 1M sorting study — sorting_1m_20261009T172003802655Z — v1

Frozen UTC: 2026-10-09T17:25:43.282869+00:00. This document is saved and hashed before
execution. Results go in separate derived reports; do not edit this protocol.
A change to parameters requires a new version before any revised execution.

## Parameters and expected counts

N = 1,000,000 signed int32 keys only. Algorithms, in registry order:
std_sort, quick_sort, pdq_sort, tim_sort, merge_sort, radix_sort.
Distributions, in runner order: uniform, sorted, reverse_sorted,
duplicate_heavy, nearly_sorted. Seeds, in runner order: 1729, 42, 2718.
One warm-up and five measured repetitions per algorithm/dataset.
15 configurations = 1 size × 3 seeds × 5 distributions.
90 algorithm/dataset groups = 15 × 6 algorithms.
450 measured trials = 90 × 5; 90 warm-ups = 90 × 1; total 540 rows.
No algorithm, distribution, seed or repetition will be silently omitted.

## Input definition and equivalence

Use unchanged mt19937_64_v1 from docs/EXPERIMENT_PROTOCOL.md, fresh engine per
configuration. Uniform maps low uint32 engine bits minus 2^31 with int64
arithmetic. Sorted is that uniform sample ascending via nearly_sorted with zero
swaps. Reverse is the corresponding sample descending. Nearly sorted is the
ascending sample followed by exactly 10,000 unbiased independently sampled
index-pair swaps, allowing self/repeated swaps. Duplicate-heavy samples unbiased
integers in [0,16), shifted by -8; every domain value is not guaranteed to occur.
Rejection threshold uses unsigned (0-bound)%bound, not library distributions.
Explicit --swaps 10000 is inactive for other distributions; sorted records zero.
All other configurations record 10000 and duplicate cardinality 16 even when
inactive, consistent with the existing schema. Generation is outside timing.

Each configuration generates one immutable original vector; all six algorithms
receive restored copies of that exact vector. Every raw row records size, seed,
distribution/parameters, mt19937_64_v1 and ordered FNV-1a64 input fingerprint.
The fingerprint is identification rather than a collision-proof correctness
check; each full output must equal a std::sort reference outside timing.

## Timing, warm-ups and ordering

Use the existing build/release/sort_benchmark, Release with sanitizers OFF.
The binary links mab_timing/mab_core, not mab_metrics. Comparison counts are
not executed. steady_clock brackets only the normal sort call, recording integer
nanoseconds. Input restoration, generation, reference sorting, full correctness
validation and output I/O are outside timing. Algorithm-owned allocation,
deallocation and dispatch are included, consistent across algorithms. Inputs
are restored even for warm-ups; all six warm-ups precede measured rounds.
No timer-overhead subtraction; units do not claim nanosecond clock accuracy.

Configurations execute serially: size, then seed, then distribution. One new
process per configuration. Within each phase/trial the selected algorithm list
rotates by (seed%6 + trial_index%6)%6. execution_order records zero-based position;
trial_index restarts for the measured phase. This is cyclic ordering, not
randomization or fully balanced position exposure over five repetitions.
Retain selected lists, argv, every row and warm-up duration.

## Preflight resource review

Recorded preflight MemTotal = 16475164672 bytes,
MemAvailable = 4340154368 bytes,
disk free = 134457196544 bytes. The generator allocates N keys;
the timing engine retains original/reference/working plus a linear workspace
allowance: 4 × N × 4 = 16,000,000 bytes (about 15.26 MiB).
Keep the existing --memory-limit-mib 256 planning guard. This is neither measured
memory nor a hard RSS cap: it excludes runtime/allocator overhead and radix
bucket offsets. No measured process RSS or auxiliary-allocation study will run
with these primary timings; the separate metrics API is process-lifetime peak
RSS and cannot isolate algorithm workspace. The user study is timing only.

Available RAM exceeds a 256 MiB headroom check; disk free exceeds 128 MiB.
Accessible cgroup ancestors have memory.max=max and exposed cpu.max=max 100000;
there is no finite observed memory/CPU quota. Address-space/data/RSS/file-size/CPU
time limits are unlimited; stack soft limit is 8 MiB. Full limits are retained.
These checks pass for the planned serial N=1M study. Recheck available resources
immediately before launching, stop on a failed gate rather than reduce N or rows.
The proposed matrix output path is absent and will be created exclusively.

## Environment and controls

Pop!_OS 24.04 LTS, Linux 6.18.7-76061807-generic, x86_64.
Intel Core i5-11400H, six physical cores reported by lscpu, 12 logical CPUs;
allowed affinity mask 0..11. Compiler GNU 13.3.0; CMake 3.28.3;
Python 3.12.3; project version 0.1.0. Configured Release flags -O3 -DNDEBUG,
with -Wall -Wextra -Wpedantic and C++17; actual translation-unit commands and
link command are recorded. std_sort uses the installed libstdc++ implementation.
No --version exists for this CLI or Python tools: record their source SHA-256,
Python/runtime version, help text and exact command instead of inventing versions.
Benchmark SHA-256: 98ae6eea14525a27241936abf4b493650a428bf6f0afcc1a94042dcfad087c7f.
No Git metadata: git status exits 128; source SHA-256 manifests replace a revision.

Observed frequency policy: intel_pstate, powersave, balance_performance,
800000..4500000 kHz. No governor/frequency/affinity/priority setting is changed.
Preflight load averages (1/5/15 min): [1.517578125, 1.01806640625, 1.06201171875].
Record CPU policy/load/memory/resource snapshots immediately before and after
execution. This is a shared desktop: no exclusive machine reservation, background
load control, frequency lock, thermal stabilization or cache flushing. Restoring
input touches memory; this is a warmed-input protocol. Those limitations restrict
conclusions. Snapshot frequencies are not fixed frequencies or effective whole-run
measurements. Thermal state is not measured or controlled.

## Failure and output policy

All outputs exclusively use new paths under results/raw/sorting_1m_20261009T172003802655Z and
results/processed/sorting_1m_20261009T172003802655Z. Earlier raw results remain unchanged.
The matrix uses existing COMPLETE/FAILED markers and per-child command records.
A failed child stops the matrix; interrupted or missing-marker runs are incomplete.
Do not treat partial output as completed; preserve available rows and diagnostics.
No automatic retries or observation selection. Every warm-up and measured output
must pass full-reference correctness. Primary execution stops on failure.

## Analysis frozen before execution

Reuse scripts/analyze_results.py for 90 per-seed algorithm groups: success/failure
counts, median, mean, sample standard deviation (n-1), minimum, maximum in ns.
Warm-ups are retained but excluded from runtime statistics. Retain all successful
observations including outliers. No deletion, winsorization, clipping or ranking.

Cross-seed unit = one five-trial median per seed. For each algorithm/distribution,
compute median, arithmetic mean, sample SD and min/max of the three seed medians,
weighting seeds equally. Report three datasets, 15 successful trials (if all pass),
and explicit failed counts. Do not pool repetitions as independent datasets.
The mean of seed medians is explicitly labeled and differs from pooled runtime
mean. Only descriptive statistics: no significance test, confidence interval,
population-generalization or universal performance ranking is claimed.
CSV/JSON retain ns; report tables use ms = ns / 1,000,000, rounded to 3 decimals.
The retained analyze_study.py checks known synthetic statistics without writing
synthetic observations to study results; it produces cross-seed and full per-seed
tables using the existing strict parser.

Verify all 15 required configurations, 90 groups, 450 measured and 90 warm-up
rows, 28-field schema, cyclic order, Release/sanitizers-off metadata, no failures,
identical per-configuration fingerprints and matching source/binary manifests.
Hash matrix/protocol artifacts before analysis; independently regenerate and
compare summaries, verify those hashes and every prior raw file afterward.

## Exact execution and analysis commands

Run from /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark. Logging wrappers retain argv, stdout, stderr, UTC interval
and actual exit code in commands/, outside timed benchmark calls.

```sh
python3 scripts/run_matrix.py --binary build/release/sort_benchmark --output /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/sorting_1m_20261009T172003802655Z/matrix --sizes 1000000 --seeds 1729,42,2718 --distributions uniform,sorted,reverse_sorted,duplicate_heavy,nearly_sorted --sorts std_sort,quick_sort,pdq_sort,tim_sort,merge_sort,radix_sort --repetitions 5 --warmups 1 --memory-limit-mib 256 --distinct 16 --swaps 10000
python3 scripts/analyze_results.py /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/sorting_1m_20261009T172003802655Z/matrix --output /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/processed/sorting_1m_20261009T172003802655Z/per_seed.json
python3 /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/sorting_1m_20261009T172003802655Z/analyze_study.py --study /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/sorting_1m_20261009T172003802655Z
```

Fresh preflight Release configure/build/full CTest pass 15/15 groups, exit 0.
No sanitizer timing or new sanitizer study is planned; prior ASan/UBSan results
are historical, not rerun evidence. No sizes above 1M, CUDA, GPU or 100M workloads.
After completion, save a separate final audit; preserve this protocol unchanged.
