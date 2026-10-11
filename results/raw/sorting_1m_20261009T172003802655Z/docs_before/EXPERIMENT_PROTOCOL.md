# Experiment protocol

## Current baseline

The sorting timing engine now follows [sort_timing_v1](BENCHMARKING.md), using
small smoke workloads before any larger controlled experiment. Separate
sort_metrics collects key comparisons/process RSS under [METRICS.md](METRICS.md).
No large-scale timing study, memory comparison study, speedups or charts have
been established. The std::sort adapter is the installed library's
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
schemas now exist. Sorting analysis retains failures/outliers; search experiment
schemas and plotting tools remain pending. Failed runs must remain visible. Raw output must never be overwritten;
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
duplicate and boundary queries. Required query workloads and project linear,
binary and exponential search implementations remain Phase 3 work.
