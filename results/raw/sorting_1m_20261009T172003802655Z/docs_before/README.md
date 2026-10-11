# Modern Search & Sorting Benchmark

This directory initially contained only `AGENTS.md`. The C++17 correctness core
is validated; required algorithms and measurement infrastructure are still being
developed. The timing framework supports small reproducible smoke measurements;
no comparative performance conclusions or large-scale results are established.

The default sorting adapter invokes the installed standard library's `std::sort`.
Project QuickSort, Merge Sort and signed Radix Sort, upstream PDQSort and upstream
Timsort have separate named adapters.

Build and test in Release mode:

```sh
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release
cmake --build build/release --parallel 2
ctest --test-dir build/release --output-on-failure
```

Tests use explicit checks that remain enabled under `NDEBUG` and compare the
entire output with `std::stable_sort` or `std::sort`, including integer boundaries, duplicates,
empty input, and seeded randomized inputs. No external test library is needed.

See [roadmap](docs/ROADMAP.md) and [experiment protocol](docs/EXPERIMENT_PROTOCOL.md).

Phase 0 completed with 2/2 CTest tests passing. The initial inventory and build
failure are documented in [audit](docs/AUDIT.md). Record an environment snapshot
without overwriting previous raw data:

```sh
python3 scripts/capture_environment.py --build-dir build/release --output results/raw/environment_new_run.json
```

Python 3 is required for tests and environment capture. Git metadata was absent
in the original directory; no commits have been created.

## Correctness CLI

```sh
build/release/algorithm_benchmark --size 1000 --seed 1729 --distribution nearly_sorted --swaps 10
```

This CLI generates one signed int32 dataset, checks the selected sorter against the full
std::stable_sort output, and checks std::lower_bound lookups against a linear
oracle. It produces correctness records, not benchmark performance measurements.
The six CLI search probes do not constitute a fixed-ratio benchmark query set.

| Option | Default | Accepted values |
| --- | --- | --- |
| `--size N` | `1000` | Unsigned decimal fitting size_t; zero allowed |
| `--sort NAME` | `std_sort` | std_sort, quick_sort, pdq_sort, tim_sort, merge_sort or radix_sort; selects the sorting registry entry |
| `--seed S` | `1729` | Unsigned decimal fitting uint64_t |
| `--distribution NAME` | `uniform` | uniform, nearly_sorted, reverse_sorted, duplicate_heavy |
| `--swaps K` | floor(N/100) | Unsigned decimal fitting size_t; applied only to nearly_sorted |
| `--distinct K` | `16` | Domain cardinality in [1, 4294967296]; used by duplicate_heavy |
| `--help` | — | Print usage and exit 0 immediately |

Use separate option and value arguments. Repeated valid options use the last
value. Malformed numeric values fail immediately when parsed; distribution names
are also checked immediately. Cardinality is checked after parsing, including
when another distribution is selected. `--swaps` and `--distinct` remain in the
record even when inactive. There is no implicit memory cap: excessive size
requests can fail, and this CLI is not a large-scale experiment orchestrator.

Unknown options, missing values, invalid sorters/distributions/cardinalities, and numeric
signs, whitespace, fractions, scientific notation, hexadecimal notation, trailing
characters or overflow cause exit 1 and an `error: ...` line on stderr. Caught
allocation/length exceptions and correctness failures have the same exit behavior.
No success JSON is printed on these failures. Operating-system termination is
outside this exception handling. `--help` stops parsing; later arguments are ignored.

Successful checks exit 0 and emit one JSON object plus newline on stdout:

```json
{"schema_version":1,"mode":"correctness","status":"ok","sort_algorithm":"std_sort","search_algorithm":"std_lower_bound","dataset_generator":"mt19937_64_v1","size":1000,"seed":1729,"distribution":"uniform","nearly_sorted_swaps":10,"duplicate_cardinality":16}
```

The numeric fields are schema version, size, seed, resolved requested swap count,
and domain cardinality. Identity/configuration fields are mode, status, sort and
search algorithm, dataset generator and distribution. For inputs shorter than
two elements, swaps are skipped but the requested count is still reported.
All eleven fields are checked by the CLI regression suite.

## Sanitizer checks

```sh
cmake -S . -B build/sanitize -DCMAKE_BUILD_TYPE=Debug -DMAB_ENABLE_SANITIZERS=ON
cmake --build build/sanitize --parallel 2
env -u ASAN_OPTIONS -u LSAN_OPTIONS UBSAN_OPTIONS=halt_on_error=1 ctest --test-dir build/sanitize --output-on-failure -V
```

The sanitizer option supports GCC/Clang toolchains and rejects unsupported
configurations. The environment-variable commands above use a POSIX shell.
Historically, the restricted execution runtime made LeakSanitizer fail with
"does not work under ptrace". Retry without leak detection only if that specific
limitation recurs; ASan and UBSan remain enabled:

```sh
ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1 ctest --test-dir build/sanitize --output-on-failure -V
```

See [audit](docs/AUDIT.md) for actual validation results and environment limitations.

Project QuickSort is selectable with `--sort quick_sort`. It uses median-of-three
pivots, three-way partitioning, a `2*floor(log2(N))` depth budget, and heapsort
fallback. See [algorithm details](docs/ALGORITHMS.md). The output's sort_algorithm
field reports the selected name; the eleven-field schema and default stay unchanged.

After QuickSort integration, fresh full Release and Debug ASan/UBSan suites
passed 5/5 groups each. QuickSort's 3,718 dedicated differential cases and its
forced/default-budget fallback checks passed; see the audit for exact counts.

Phase 1 passed fresh full Release and Debug ASan/UBSan suites (4/4 groups each).
Leak detection was enabled; the historical ptrace limitation did not recur.

## Upstream PDQSort

`--sort pdq_sort` selects Orson Peters' official
[orlp/pdqsort](https://github.com/orlp/pdqsort), pinned to commit
`b1ef26a55cdb60d236a5cb199c4234c704f46726` under the Zlib license. Original source
and license notices are retained without modifications. See
[vendored attribution and hashes](third_party/pdqsort/README.md) and
[algorithm details](docs/ALGORITHMS.md). Builds use the local vendored header and
need no network access. std_sort remains the default; the JSON schema is unchanged.

```sh
build/release/algorithm_benchmark --sort pdq_sort --size 1000 --seed 1729 --distribution uniform
```

PDQSort integration passed fresh full Release and Debug ASan/UBSan suites (6/6
CTest groups each), with leak detection enabled and no compiler warnings. Its
4,027 dedicated differential input cases passed through the public interface
and registry; shared sorting/dataset tests also cover it. No performance
comparison has run. These 6/6 results precede the Timsort integration below.

## Upstream Timsort

`--sort tim_sort` selects genuine [cpp-TimSort](https://github.com/timsort/cpp-TimSort),
pinned to commit `99b612d9826e8387a30008f2b21be206181ad890` from its C++11-compatible
2.x.y branch. The current upstream 3.x branch requires C++20. The selected older
branch is not actively maintained; its exact revision is recorded rather than
claimed to be the v2.1.0 release tag. The MIT license and all header attribution
notices are preserved; upstream code is unchanged. See
[source hashes and attribution](third_party/timsort/README.md), machine-readable
[provenance](third_party/timsort/UPSTREAM.json) and [algorithm details](docs/ALGORITHMS.md).

```sh
build/release/algorithm_benchmark --sort tim_sort --size 1000 --seed 1729 --distribution nearly_sorted
```

The adapter sorts signed int32 keys ascending and accepts empty/singleton inputs.
std_sort remains the default and the eleven-field correctness JSON schema is
unchanged. Builds use the vendored header with no network dependency.

Fresh Release and Debug ASan/UBSan suites passed 7/7 CTest groups each, including
4,149 dedicated Timsort differential inputs through both public and registry
paths, and ten CLI test methods. Leak detection remained enabled and no compiler
warnings were emitted. Exact commands and immutable logs are recorded in
[the audit](docs/AUDIT.md). Timsort integration is complete; Phase 2 remains in
progress because additional sorters and comparison/memory/timing infrastructure
were pending at that stage. No benchmark, CUDA or 100-million-element run was performed.

## Separate comparison and memory metrics

```sh
build/release/sort_metrics --sort quick_sort --size 2 --distribution duplicate_heavy --distinct 1
```

sort_metrics accepts the same dataset/sorter options and defaults listed above,
including std_sort. It verifies counted output against std::sort and the normal
registry sorter. The original CLI, eleven-field schema and registry are unchanged.
Five comparison sorters support run-local counts of executed signed-int32 less-than
predicates, including pivot/partition/merge/fallback work. Generation and later
verification are excluded. PDQSort explicitly preserves production's branchless
policy. Counted runs are separate from normal execution and future timing runs.

On Linux, getrusage(RUSAGE_SELF).ru_maxrss supplies process peak RSS, normalized
from KiB to bytes. It includes input/runtime/allocator/instrumentation memory
and does not isolate algorithm workspace. Sampling follows counted sorting and
precedes validation copies. Other platforms report unsupported/null. No temporary
buffer allocation measurement is implemented; theoretical space remains separate.

The independent 15-field metrics JSON includes key_comparisons, its convention,
adapter identity, dataset parameters and process_memory status/method/unit/scope/
value/error_code. Memory errors emit a partial record, stderr diagnostic and
exit 1; unsupported memory permits successful counting. See [metric definitions
and schema](docs/METRICS.md) for exact fields and limitations. No timing is
collected. Radix Sort has no key-comparison metric: sort_metrics --sort radix_sort
exits 1 with an explicit unsupported diagnostic and no JSON, rather than reporting
zero. Merge Sort uses project_merge_sort_counting_less with the same predicate
convention. Fresh validation and milestone status are recorded in the audit/roadmap.

The comparison/memory milestone passed fresh full Release and Debug ASan/UBSan
suites (11/11 groups each), including 1,404 inputs across all four counted sorters,
six manually verified QuickSort count fixtures, reset/isolation/overflow checks,
counted heap fallback, real/unsupported memory paths and seven metrics CLI methods.
Leak detection remained enabled; no compiler warnings were emitted. These are
metric validation runs, not benchmark performance measurements.

## Reproducible timing engine

```sh
python3 scripts/run_matrix.py --binary build/release/sort_benchmark --output results/raw/new_smoke_matrix
mkdir -p results/processed
python3 scripts/analyze_results.py results/raw/new_smoke_matrix --output results/processed/new_smoke_summary.json
```

The default smoke matrix uses 1K/10K inputs, seed 1729, all six production
sorters and uniform/sorted/reverse/duplicate-heavy/nearly-sorted distributions.
It performs one warmup and five measured repetitions per sorter/configuration.
steady_clock measures only the normal sorting call, in integer nanoseconds;
generation, input restoration, reference checks and CSV output are excluded.
Every result is checked against the full std::sort output outside timing.

For a single run, use sort_benchmark --output NEW_DIRECTORY; std_sort remains
its default. Existing CLIs and algorithms are unchanged. Performance requires
Release without sanitizers. Framework trials use --validation-only; a zero-size
test probe verifies the Release guard. Test artifacts are temporary validation
data. New directories and derived summary files are exclusively created.
Failure/partial records are retained and never treated as completed runs.

See [protocol, all options, 28-field CSV schema and summary format](docs/BENCHMARKING.md).
Separate JSON analysis reports success/failure counts, median, mean, sample
standard deviation, minimum and maximum; it retains outliers and excludes only
labeled warmups and unsuccessful timings from successful-trial statistics.

Explicit larger experiment, not executed in this milestone:

```sh
python3 scripts/run_matrix.py --binary build/release/sort_benchmark --output results/raw/new_cpu_experiment --sizes 1000,10000,100000,1000000 --seeds 1729,42,2718 --repetitions 5 --warmups 1 --memory-limit-mib 256
```

Metadata includes configuration/argv, input fingerprint, compiler/build/platform,
source hashes, upstream provenance and available environment/compile commands.
The memory planning guard is not a measured process-memory cap. CPU frequency,
affinity, cache state, timer overhead and background load are not controlled.
Smoke results validate infrastructure and do not establish a performance ranking.

Fresh full Release and ASan/UBSan suites passed 13/13 groups, including 72 timing
input configurations/864 registry trials and 11 Python framework tests. The actual
1K/10K Release smoke matrix completed 200 measured trials and 40 warmups across
ten configurations. Its 40-group [statistical summary](results/processed/benchmark_smoke_20261009T160450529409Z.json)
is separate from [raw observations](results/raw/benchmark_validation_20261009T160450529409Z/smoke_matrix/matrix.json).
No larger experiment, CUDA workload or 100-million-element run was performed.

## Project Merge Sort and signed Radix Sort

`--sort merge_sort` and `--sort radix_sort` work in the correctness CLI and
sort_benchmark, including --sort all and the matrix runner's automatic discovery.
std_sort remains the default and existing output schemas are unchanged.

Merge Sort performs stable bottom-up merges with one N-key auxiliary buffer per
nontrivial call, O(N log N) work and O(N) auxiliary space. Its separate counted
adapter counts exactly the right-key < left-key predicates used while merging.
Radix Sort uses four stable LSD passes of eight bits each. Converting a signed
key to uint32 and flipping bit 31 maps the entire signed domain into unsigned
order without overflowing INT32_MIN. It scatters original keys into one N-key
buffer with 256 bucket offsets; no comparison-sort fallback is used.
Both return immediately for empty/singleton inputs. Algorithm-owned allocation
is included in normal sorting time; these space descriptions are theoretical,
not isolated memory measurements. See [algorithm details](docs/ALGORITHMS.md).

```sh
build/release/algorithm_benchmark --sort radix_sort --size 1000 --seed 42
build/release/sort_metrics --sort merge_sort --size 4 --distribution duplicate_heavy --distinct 1
python3 scripts/run_matrix.py --binary build/release/sort_benchmark --output results/raw/new_six_sort_smoke --sizes 1000,10000 --seeds 1729 --repetitions 5 --warmups 1
python3 scripts/analyze_results.py results/raw/new_six_sort_smoke --output results/processed/new_six_sort_smoke.json
```

Fresh Release and Debug ASan/UBSan suites pass 15/15 groups, with leak detection
enabled and no compiler warnings. Each new sorter passes 4,015 dedicated
differential inputs; eleven exact Merge Sort count fixtures also pass. The fresh
all-six-sorter Release smoke completed 300 measured trials and 60 warmups with
no failures, producing 60 summary groups that regenerated exactly from raw CSV.
See [audit](docs/AUDIT.md) for commands and evidence. Historical counts above
describe earlier milestones. No performance-superiority claim is established.
