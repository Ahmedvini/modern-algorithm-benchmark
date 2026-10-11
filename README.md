# Modern Search & Sorting Benchmark — CPU-only release

This release delivers an empirical CPU study: six sequential sorters, array
search, Skip List/B-tree structures, OpenMP Merge Sort, and a learned rank index.
It retains the completed 1M, multi-size, OpenMP, and 10M/100M CPU observations;
no performance experiment was repeated for this release revision.

Read the [CPU-only methodology and acceptance scope](docs/CPU_ONLY_RELEASE_v1.md),
[final report](report/cpu_only_20261011T133332368294Z/FINAL_REPORT.md),
[report PDF](report/cpu_only_20261011T133332368294Z/REPORT.pdf), and
[12-slide presentation](report/cpu_only_20261011T133332368294Z/PRESENTATION.pdf).
The [release audit](results/raw/cpu_only_release_20261011T133332368294Z/FINAL_AUDIT.md)
records numerical reanalysis, correctness checks, and preservation.

GPU execution and CUDA/CUB comparisons are deferred and are not CPU-release
completion requirements. Their code, frozen protocols, pins, and historical
artifacts remain preserved in place; see the [deferred archive index](docs/DEFERRED_GPU.md).
No CPU-versus-GPU result is claimed. The independent CPU/GPU launch guard remains
unchanged. Local CPU correctness uses the separate [v5 procedure](docs/LOCAL_VALIDATION_v5.md);
historical v3 and inactive v4 are preserved.

This directory initially contained only `AGENTS.md`. Six C++17 sorting algorithms,
separate metrics and the reproducible timing framework are validated. The first
[1M sorting study](results/processed/sorting_1m_20261009T172003802655Z/RESULTS.md) is complete with
450 measured trials and 90 warm-ups; findings describe one recorded machine/session.
Array search and ordered-structure benchmarking have separate protocols and
executables. The additive learned rank index has passed deterministic correctness
and ASan/UBSan tests and a 48-configuration held-out CPU evaluation (24 distinct
sorted vectors). Scale/report status and limitations are recorded in the roadmap.

The default sorting adapter invokes the installed standard library's `std::sort`.
Project QuickSort, Merge Sort and signed Radix Sort, upstream PDQSort and upstream
Timsort have separate named adapters.

Build in Release mode with CUDA explicitly disabled:

```sh
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_OPENMP=ON -DMAB_ENABLE_CUDA=OFF -DMAB_ENABLE_CUDA_SORT=OFF -DMAB_ENABLE_CPU_GPU_COMPARISON=OFF
cmake --build build/release --parallel 2
```

For correctness-only validation, follow [the guarded local procedure](docs/LOCAL_VALIDATION_v5.md).
Do not invoke the full CTest registry to avoid repeating timing-bearing integration
tests. Existing report data can be audited and regenerated without running any
benchmark; see [reporting instructions](report/README.md).

Tests use explicit checks that remain enabled under `NDEBUG` and compare the
entire output with `std::stable_sort` or `std::sort`, including integer boundaries, duplicates,
empty input, and seeded randomized inputs. No external test library is needed.
The full CTest registry includes timing-bearing framework tests. For a strictly
correctness-only run use the [guarded local procedure](docs/LOCAL_VALIDATION_v5.md),
which validates source and build metadata before discovery and excludes timing tests.

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
comparison ran during that integration milestone. These 6/6 results precede
the Timsort integration below.

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
were pending at that stage. No benchmark, CUDA or 100-million-element run
was performed during that integration milestone.

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
No larger experiment, CUDA workload or 100-million-element run was performed
during that timing-framework milestone; the later 1M study is recorded below.

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

## Recorded 1M study

The [frozen v1 protocol](docs/studies/sorting_1m_20261009T172003802655Z_v1.md) uses all six algorithms,
five distributions, seeds 1729/42/2718, N=1,000,000, one warm-up and five measured
repetitions per algorithm/dataset. All 15 configurations completed: 450 measured
successes, 90 warm-up successes and zero failures. Fresh Release tests passed
15/15 groups before execution; no sanitizer suite was rerun in this experiment.

[Raw matrix](results/raw/sorting_1m_20261009T172003802655Z/matrix/matrix.json),
[verification](results/raw/sorting_1m_20261009T172003802655Z/verification.json),
[final audit](results/raw/sorting_1m_20261009T172003802655Z/FINAL_AUDIT.md) and
[full descriptive results](results/processed/sorting_1m_20261009T172003802655Z/RESULTS.md) retain the
commands, environment and all observations. Per-seed and cross-seed CSV/JSON are
separate derived files. Cross-seed statistics summarize three seed medians with
equal weight; repetitions are not independent datasets. All five derived files
regenerated byte-for-byte, with raw results/protocol/earlier evidence unchanged.

GNU 13.3.0 Release (-O3 -DNDEBUG), Pop!_OS 24.04, Intel i5-11400H were recorded.
CPU power/frequency, thermal/cache state and background load were not controlled;
no universal ranking or statistical significance is claimed. Comparisons/RSS were
not collected for this timing study. No size above 1M or CUDA workload was run.

## Search algorithms and reproducible batches

The separate registry provides linear_search, binary_search and exponential_search.
All return the first matching index or absence; binary/exponential require ascending
data, while linear supports any order. The existing std_lower_bound reference
adapter and sorting/default CLI behavior are preserved.

```sh
build/release/search_benchmark --output results/raw/new_search_run --search all --size 1000 --queries 1000
python3 scripts/run_search_matrix.py --binary build/release/search_benchmark --output results/raw/new_search_smoke
python3 scripts/analyze_search_results.py results/raw/new_search_smoke --output results/processed/new_search_summary.json
build/release/search_counts --output results/raw/new_search_counts --search all --size 64 --queries 16
```

See [the versioned search protocol](docs/SEARCH_PROTOCOL_v1.md) and
[CLI, output and analysis details](docs/BENCHMARKING.md). Data are generated using
the existing generator and sorted outside lookup timing. Nine query policies cover
fixed/random hits, range/interior misses, 50% mixed batches and empty-input misses.
Unavailable categories retain reasons, while targets/selected ranks/first-match
answers remain in raw query CSV. All algorithms receive identical batches.

steady_clock records complete batch latency; validation is outside timing.
Normalized ns/query is a batch average, not a measured individual-query duration.
Separate search_counts records per-query < and == predicates without timing.
New raw/summary paths are exclusive, failures/outliers remain visible, and smoke
runs do not establish performance superiority. No large search study has run.

Fresh full Release and ASan/UBSan suites passed **18/18 groups**, with leak detection
enabled and no final compiler warnings. The retained [search smoke summary](results/processed/search_smoke_20261009T173830593675Z.json)
has 141 groups: 705 measured successes and 141 warm-up successes across eight
configurations; 25 unavailable category/configuration pairs have explicit reasons.
All 534 earlier result artifacts and frozen sorting/search protocols remain
unchanged; the summary regenerated byte-for-byte. See [verification](results/raw/search_validation_20261009T173830593675Z/verification.json)
and [audit](docs/AUDIT.md) for exact commands, counts and limitations.
The Phase 3 batch milestone is complete; Phase 4 validation is recorded below.

## Owned search structures (Phase 4)

SkipList and BTree are ordered signed-int32 -> size_t maps: duplicate insertion
preserves the first payload, missing lookup returns nullopt, and size counts unique
keys. Copy/move, update and deletion are unsupported. The separate registry exposes
skip_list and btree_m10/m16/m32/m64 (maximum child count, minimum degree M/2).
Skip List uses seeded MT19937-64 promotion with probability 1/2 and 32 levels.
See [frozen contracts/protocol](docs/STRUCTURES_PROTOCOL_v1.md) and
[implementation details](docs/ALGORITHMS.md).

```sh
build/release/structure_benchmark --output results/raw/new_structure_run --structure all --size 1000 --queries 64
python3 scripts/run_structure_matrix.py --binary build/release/structure_benchmark --output results/raw/new_structure_smoke
python3 scripts/analyze_structure_results.py results/raw/new_structure_smoke --output results/processed/new_structure_summary.json
```

The matrix defaults to sizes 0/1/64/1000, uniform/duplicate-heavy, dataset and
structure seed 1729, query seed 2718, all five configurations, one warmup/five
measured rounds and 64 queries per available category. structure_benchmark defaults
to skip_list; --structure selects comma-separated names or all, --structure-seed
selects the Skip List RNG seed, --list-structures lists the registry. Remaining
options/bounds follow search_benchmark; defaults are 1000 keys/queries and 256 MiB.
The stronger planning estimate is 512*N+128*queries*9, not measured memory or a
hard RSS cap. Existing CLIs, std_sort default and frozen sorting results are intact.

Construction (constructor/all inserts) and lookup batches have separate rows and
statistics. Original insertion order is retained; payload ranks and exact Phase 3
queries are prepared outside timing. Every built structure and query answer is
validated outside timing. Destruction, setup, validation and I/O are excluded.
Batch ns/query is a normalized average, not individual-query latency. No structure
comparison counts, RSS or isolated allocation measurements are implemented.
New raw and summary paths are exclusive; failed/missing trials and outliers remain
visible. Larger structure experiments need their own frozen protocol/resource review.

Phase 4 insertion/lookup and development smoke validation is complete. Fresh
Release and ASan/UBSan suites passed **21/21 groups**, with leak detection enabled
and no final compiler warnings. The [smoke summary](results/processed/structures_smoke_20261009T181402878134Z.json)
contains 275 groups: 200 measured builds, 1,175 measured lookup batches and 275
warmups across eight configurations, zero failed/missing trials. It regenerated
byte-for-byte, and all 696 earlier artifacts and frozen protocols remain unchanged.
See [verification](results/raw/structures_validation_20261009T181402878134Z/verification.json),
[raw matrix](results/raw/structures_validation_20261009T181402878134Z/smoke_matrix/matrix.json)
and [audit](docs/AUDIT.md). The next milestone is Phase 5 orchestration and plots.

## Unified orchestration, statistics and plots (Phase 5)

The [versioned orchestration contract](docs/ORCHESTRATION_PROTOCOL_v1.md) adds a
serial top-level pipeline around the existing sorting/search/structure tools.
It keeps construction, sorting and lookup timings separate. Python 3 and
Matplotlib (including its NumPy/font dependencies) are required for visualization;
Matplotlib was already available on the validated machine. No pandas dependency.

```sh
mkdir -p results/figures
python3 scripts/run_experiments.py --preset smoke --run-id NEW_ID --dry-run
python3 scripts/run_experiments.py --preset smoke --run-id NEW_ID
python3 scripts/analyze_experiment.py results/raw/NEW_ID --output results/processed/NEW_REGEN_ID --figures results/figures/NEW_REGEN_ID
```

Explicit --raw-root/--processed-root/--figure-root and --build-dir are supported;
roots must exist. All output directories must be absent. No overwrite or resume:
failed/interrupted runs retain diagnostics, and retries require a new ID.
--config JSON accepts strictly validated custom matrices; use profile=custom for
changed presets. Dry-run JSON contains the configuration SHA256, exact family and
child commands, output paths and row/memory/disk estimates without executing them.

The smoke preset uses N=0/64/1000, uniform/duplicate-heavy, seeds1729/42, all
algorithms/structures/categories, Q64,W1,R5. The separate full preset uses
1K/10K/100K/1M, all five distributions, seeds1729/42/2718,Q1000,W1,R5:

```sh
python3 scripts/run_experiments.py --preset full --run-id NEW_FULL_ID --dry-run
# Execute only after the frozen protocol's validation/resource/runtime review:
python3 scripts/run_experiments.py --preset full --run-id NEW_FULL_ID
```

Raw experiment.json/family bundles/command diagnostics and COLLECTED/COMPLETE or
failure/interruption markers live under results/raw/ID. summary.json,
observations.jsonl and REPORT.md live under results/processed/ID; SVG/PDF figures
and plot_manifest.json live under results/figures/ID. The report retains failures,
missing trials, unavailable policies and environment limitations. Plot manifests
map source hashes/filters/transforms/dependency versions to output hashes.

Repeated timings are summarized per dataset before cross-dataset medians are
aggregated with equal weight; identical ordered-input fingerprints collapse to
one unit. Error bars show min/max spread, not confidence intervals. Lookup ns/query
is a normalized batch average. All outliers are retained; no universal ranking,
significance, inferred memory or fabricated comparison plots. Regeneration is
byte-identical on the same plotting stack; other font/version stacks may differ.

After validating a pilot, record a conservative resource/runtime forecast:

```sh
python3 scripts/assess_experiment.py results/raw/PILOT_ID --output results/processed/NEW_ASSESSMENT.json
```

This forecasts the unchanged full preset using overhead-inclusive family wall
time, documented complexity scaling and a factor-four allowance. It is not a
measured full runtime. Tiny smoke data can greatly overestimate fixed setup;
an explicitly labeled intermediate pilot can refine planning. The default
assessment budget is 3600 seconds of family wall time; plotting cost is separate.

Phase 5 delivered a validated pipeline **and a completed full CPU timing study**.
Final Release and ASan/UBSan suites passed **22/22 groups**, plus 23 standalone
Python pipeline tests; leak detection stayed enabled. The smoke completed 36
configurations with 3,260 measured successes and 652 warmups. The full preset
completed 180 configurations with **22,020 measured successes and 4,404 warmups**,
zero failed/missing trials. Sorting, construction and lookup remain separate.
All 177 full-study SVG/PDF figure pairs, report, summary and observation bytes
regenerated exactly. All 867 earlier artifacts and frozen studies stayed unchanged.

[Full report](results/processed/phase5_full_20261009T191000587965Z/REPORT.md),
[summary](results/processed/phase5_full_20261009T191000587965Z/summary.json),
[plot manifest](results/figures/phase5_full_20261009T191000587965Z/plot_manifest.json),
[raw plan](results/raw/phase5_full_20261009T191000587965Z/experiment.json) and
[verification](results/raw/orchestration_validation_20261009T191000587965Z/full_verification.json)
retain the evidence. Shared-machine frequency/cache/thermal/background conditions
were uncontrolled; these descriptive findings establish no universal ranking or
statistical significance. Separate comparison/memory studies, per-query latency
and independent-session replication remain deferred. At that audit, Phase 6 OpenMP was next; its completed evidence is below.

## OpenMP parallel Merge Sort (Phase 6)

The optional `MAB_ENABLE_OPENMP=ON` (default) builds separate parallel targets;
set it OFF to build the original CPU targets without OpenMP. GCC/Clang require a
supported OpenMP runtime. The original six-entry registry, std_sort default,
sequential merge_sort and frozen Phase 5 presets remain unchanged.

```sh
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_OPENMP=ON
cmake --build build/release --parallel 2
build/release/parallel_sort_benchmark --output results/raw/NEW_PARALLEL_RUN --sort all --threads 4 --size 100000
python3 scripts/run_parallel_matrix.py --preset smoke --output results/raw/NEW_OMP_ID --processed results/processed/NEW_OMP_ID --figures results/figures/NEW_OMP_ID --dry-run
# Execute only after protocol/resource review; remove --dry-run.
```

The new executable defaults to sequential merge_sort; --sort selects merge_sort,
parallel_merge_sort or all. --threads accepts unsigned decimal1..64, default1.
All existing dataset/timing options and validation-only build policy apply.
The library creates a team only for N>=32768 and request>1, with grain16384.
CSV records requested and actual team size and implementation version per trial.
Team size does not prove every worker executed a task. Above-threshold studies
require actual=request. Threads1/2/4/8 are supported by the matrix runner, which
sets and records OMP_DYNAMIC=FALSE,OMP_THREAD_LIMIT=8,OMP_MAX_ACTIVE_LEVELS=1,
OMP_WAIT_POLICY=PASSIVE. Different concurrent runs still contend; schedule serially.

The [frozen OpenMP contract](docs/OPENMP_PROTOCOL_v1.md) defines disjoint tasks,
barriers, allocation/nesting behavior and separate scaling baselines. Analysis
uses sequential Merge Sort / parallel time as primary speedup; parallel one-thread
/ parallel time is reported separately. Ratios are computed from within-dataset
medians before cross-dataset aggregation. No comparison instrumentation enters
primary timing. Counts/RSS, CUDA and 100M workloads are outside this phase.

```sh
python3 scripts/analyze_parallel_results.py results/raw/OMP_ID --output results/processed/NEW_REGEN_ID --figures results/figures/NEW_REGEN_ID
```

All paths must be absent; no overwrite/resume. The matrix analyzer requires both
baselines and a matrix manifest. Single CLI bundles retain raw CSV/metadata.
See AUDIT.md for actual test/study status; instructions alone are not results.

Phase 6 now delivers a validated implementation **and completed scaling study**.
Fresh final Release and ASan/UBSan suites passed **24/24 groups**, including
523 input cases/4,184 parallel public/registry checks and 13 Python framework tests.
Leak detection was enabled. Teams1/2/4/8 were tested. The corrected smoke passed
32 configurations,320 measured/64 warmup trials. The full study passed180
configurations,1,800 measured/360 warmup trials across32768/100K/1M elements,
five distributions and three seeds, with zero failed/missing trials. All20SVG/PDF
figure pairs and summaries/report regenerated byte-for-byte. All3,796 prior
artifacts stayed unchanged.

ThreadSanitizer could not initialize (`unexpected memory mapping`,exit66), also
on an independent non-OpenMP probe. Concurrent stress and disjoint-task review
supplement sanitizers; this is no race-freedom claim. The first full attempt is
retained FAILED because strict analysis incorrectly expected nonzero swaps for
already-sorted input. Its180 children passed, but no completion marker was created.
An all-distribution regression and fresh full suites preceded the exclusive retry;
no timings were pooled between attempts. See AUDIT.md for all failures/commands.

[Frozen retry launch](docs/studies/openmp_scaling_20261009T200852928292Z_retry1_v2.md),
[full report](results/processed/openmp_scaling_20261009T200852928292Z_retry1/REPORT.md),
[summary](results/processed/openmp_scaling_20261009T200852928292Z_retry1/summary.json),
[raw matrix](results/raw/openmp_scaling_20261009T200852928292Z_retry1/matrix.json),
[plot manifest](results/figures/openmp_scaling_20261009T200852928292Z_retry1/plot_manifest.json) and
[verification](results/raw/openmp_validation_20261009T200852928292Z/full_retry_verification.json)
retain exact configurations, statistics, compiler/runtime identity and integrity.
The shared-machine study does not establish significance or universal superiority.
Next roadmap milestone: Phase7 CUDA device/runtime preflight and reproducible
Colab/cloud guide, with GPU results explicitly not run until a device is verified.

## CUDA readiness and cloud execution (Phase 7)

**Deferred archive material.** This and the following CUDA/CPU-GPU sections
retain historical implementation and validation notes. Their milestone-local
claims are not current CPU-release completion criteria. Follow the
[archive index](docs/DEFERRED_GPU.md) for context; no frozen full comparison was
executed, and none of these GPU observations enters the CPU-only report.

CUDA support is **disabled by default** (`MAB_ENABLE_CUDA=OFF`). CPU algorithms,
registries, defaults and timing schemas are unchanged. Preflight needs only Python
standard-library modules and does not install software or change drivers/settings:

```sh
python3 scripts/cuda_preflight.py --output results/raw/NEW_CUDA_PREFLIGHT
```

The output directory must not exist. JSON diagnostics, a human summary and a
hashed discovery-completion marker are saved. Exit0 requires an actually checked
device0 kernel; exit2 with a report means CUDA unavailable/unverified, not a CPU
project failure. Exit1 is a reporting error, exit130 interruption. Missing tools,
failed commands and skipped build/runtime steps remain explicit. No environment
or whole PATH dump; allowlisted CUDA paths/visibility and redacted diagnostics only.

The [versioned readiness contract](docs/CUDA_PREFLIGHT_PROTOCOL_v1.md) and
[Colab/cloud guide](docs/CUDA_EXECUTION_GUIDE_v1.md) document classifications,
source verification, isolated builds, optional smoke commands, CPU fallback,
troubleshooting and persistent evidence export. CUDA ON requires CMake>=3.18,
NVIDIA toolkit>=11.0 with C++17 and a compatible host compiler. It currently builds
only `cuda_runtime_probe`; no GPU sorter or benchmark exists. CPU sanitizer and
CUDA builds must be separate. Existing CPU minimum CMake3.16 stays unchanged.

Local discovery found NVIDIA GA107M / GeForce RTX3050Ti Mobile PCI evidence,
but no discoverable nvcc, nvidia-smi, driver version file or CUDA libraries.
Driver usability is unverified; CUDA configure/build/kernel execution and Colab
execution are **not run**. Mocked readiness tests are not GPU execution evidence.
See the latest [audit](docs/AUDIT.md) for fresh CPU validation and integrity results.

The requested Phase7 readiness/guide milestone passed fresh **25/25 Release and
ASan/UBSan groups** with leak detection enabled, including22 preflight/isolation
methods. All8,447 earlier artifacts remain unchanged. [Local readiness evidence](results/raw/cuda_preflight_20261009T205410772326Z_reviewed/report.json)
records unavailable CUDA (exit2); optional CUDA compilation/kernel execution and
Colab steps remain unvalidated. [Audit evidence](results/raw/cuda_preflight_validation_20261009T205410772326Z/FINAL_AUDIT.md)
and COMMANDS.md retain commands/statuses. The original GPU sorting/timing goals
remain pending. Next GPU step: validate the guide on an allocated operational GPU
before CUB sorting or transfer/kernel/end-to-end measurement work.

## Cloud GPU follow-up — Gate 1 blocked (requested Phase 8)

No cloud GPU runtime or remote execution endpoint is connected to this session.
The audited Phase 7 archive and all 126 source hashes were verified locally;
its CUDA-OFF CPU fallback built and listed all six sorters. This does not validate
Colab/cloud execution. Fresh local preflight exited 2 (gpu_driver_unavailable):
RTX 3050 Ti Mobile PCI evidence, but no driver binding/module/device nodes,
nvidia-smi, nvcc or discoverable CUDA libraries. Compute capability and CUDA
versions remain unknown. CUDA build/enumeration/kernel checks were skipped.

Fresh CPU Release and ASan/UBSan passed 25/25 groups each, with leak detection
on and 22 readiness/isolation methods passing per suite. No CUB protocol/sorter,
GPU correctness test, GPU smoke or full GPU study was started. All 8,656
earlier result artifacts remain unchanged. No installation/system change.
[Gate audit](results/raw/gpu_cloud_gate1_20261009T211734154323Z/FINAL_AUDIT.md) and
[local preflight](results/raw/gpu_cloud_gate1_20261009T211734154323Z/local_preflight/report.json) retain evidence.
Next GPU step: allocate and connect a supported NVIDIA cloud development runtime,
verify the archive and run the existing guide/preflight there. Require actual
enumeration and checked kernel before Gate 2. This follow-up remains blocked;
original roadmap Phase 8 learned-index/AlphaDev retains its pending status.

## Post-cloud validation: first CUB correctness slice

The retained archive at results/evidence/cloud_validation_evidence.tar.gz
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

Follow [the correctness contract](docs/CUDA_SORT_PROTOCOL_v1.md) and
[the cloud validation handoff](docs/CUDA_SORT_VALIDATION_GUIDE_v1.md).
Next milestone: compile/run this exact source on the validated cloud GPU, retain
and review the new sorter evidence, then define separate GPU timing methodology.
Original learned-index/AlphaDev, scaling and final research phases remain pending.

Final local CPU regression:26/26 Release and26/26 ASan/UBSan, leaks enabled;11 handoff methods pass. New GPU sorting remains uncompiled/unexecuted. Evidence: results/raw/cub_sort_validation_20261009T220322089788Z/FINAL_AUDIT.md.

Latest CUB handoff revision2: dangling-symlink safety fixed;12 host methods and26/26 Release/ASan/UBSan groups pass, leaks enabled. GPU sorting still uncompiled/unexecuted. Use [v2 guide](docs/CUDA_SORT_VALIDATION_GUIDE_v2.md), cub_sort_source_v2.tar.gz and evidence at results/raw/cub_sort_final_review_20261009T222209607981Z/FINAL_AUDIT.md. Earlier candidate archive remains unchanged.

## Observed CUB GPU correctness validation

The current CUB adapter has now compiled and executed on the existing Colab Tesla
T4 (compute7.5, driver580.82.07, nvcc13.0.88, runtime API13000, GCC13.3.0).
The direct test passed475 inputs/1900 full-vector output checks; targeted
`cuda_sorting` CTest repeated the same suite and passed1/1, with zero failures or
skips. These supersede the earlier pending entries above. No CPU substitution.

The original v2 archive hash matched locally and remotely. Its configure failed
on the initial CUB3.0.0 pin: installed CUB is3.0.1. Independent upstream review
verified [CCCL commit f19d875da0d8bfb2e38c109b2b40522b8abbbbc3](https://github.com/NVIDIA/cccl/tree/f19d875da0d8bfb2e38c109b2b40522b8abbbbc3).
Only the version macro differed in that header; SortKeys and LICENSE hashes were
unchanged. The reviewed exact pin/result identity are now documented in
[correctness protocol v2](docs/CUDA_SORT_PROTOCOL_v2.md) and
[validation guide v3](docs/CUDA_SORT_VALIDATION_GUIDE_v3.md). All original bundles,
protocols and failed diagnostics remain retained.

Fresh CUDA-disabled Release and Debug ASan/UBSan suites passed26/26 each, leaks
enabled. GPU compilation emitted100 GCC-extension line-directive warnings from
nvcc-generated code under host -Wpedantic; diagnostics are retained, not suppressed.
All8,825 earlier result artifacts match their starting hashes. Downloaded evidence
contains611 hash-verified files, including both attempts, build/cache/compiler
commands and1688 installed dependency hashes. See
[final audit](results/raw/cub_correctness_colab_20261009T223853955936Z/FINAL_AUDIT.md) and
[GPU completion record](results/raw/cub_correctness_colab_20261009T223853955936Z/downloaded/retry1/NEW_CUB_CORRECTNESS/COMPLETE.json).

**The CUDA sorting correctness milestone is complete.** Original roadmap Phase7
remains open for the separate GPU timing contract/engine, transfer/device/end-to-end
smoke and study. No GPU benchmark, acceleration claim or100M run was performed.


## Prepared CUB GPU performance benchmark

The separate `cuda_sort_benchmark` target uses the unchanged CUB3.0.1 dependency
pin and requires both CUDA options. It does not time the allocation-per-call
production adapter. [Timing protocol v1](docs/CUDA_TIMING_PROTOCOL_v1.md) defines
H2D, device-sort and D2H CUDA-event intervals plus host `steady_clock` prepared
end-to-end latency. Buffers are reused; allocation, staging and oracle checks are
excluded. CUDA-event units are converted to ns without claiming ns resolution.

On a verified GPU (Release, no sanitizers):

```bash
cmake -S . -B build/cuda-performance -DCMAKE_BUILD_TYPE=Release \
  -DMAB_ENABLE_CUDA=ON -DMAB_ENABLE_CUDA_SORT=ON -DCMAKE_CUDA_ARCHITECTURES=75
cmake --build build/cuda-performance --target cuda_sort_benchmark --parallel 2
build/cuda-performance/cuda_sort_benchmark --output results/raw/NEW_GPU_SAMPLE \
  --size 1025 --distribution uniform --seed 1729 --warmups 1 --repetitions 5
python3 scripts/analyze_cuda_results.py results/raw/NEW_GPU_SAMPLE \
  --output results/processed/NEW_GPU_SAMPLE.json
```

Output directories/files must not exist; parents must exist. The sequential
`run_cuda_matrix.py` defaults to sizes0,1,1025,65537, six distributions (including
`signed_edges`) and seeds1729,42, W1/R5:48 configurations/240 measured/48 warmups.
`validate_cuda_timing.py --output results/raw/NEW_GPU_TIMING --processed
results/processed/NEW_GPU_TIMING` first reruns GPU correctness, then builds/runs
the smallest smoke, GPU framework tests, matrix and exact summary regeneration.
Strict analysis rejects incomplete runs by default; `--allow-incomplete` preserves
failure/missing counts and returns1. Raw observations and warmups are retained;
per-dataset summaries give median, mean, sample stdev, min/max for each metric.
CPU-only builds remain independent. GPU acceptance/evidence is recorded separately
below when actually executed; no broad performance study is implied by these commands.


## Prepared CUB timing milestone validated

[Timing protocol v1](docs/CUDA_TIMING_PROTOCOL_v1.md) and `cuda_sort_benchmark` now
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

[Raw evidence/audit](results/raw/cuda_timing_20261009T231303050084Z/FINAL_AUDIT.md),
[processed report](results/processed/cuda_timing_20261009T231303050084Z/REPORT.md),
and [matrix statistics](results/processed/cuda_timing_20261009T231303050084Z/matrix.json)
retain every observation, exact commands, hashes and per-dataset median/mean/sample
SD/min/max. Summary regeneration passes in both environments; local/cloud statistic
groups match, with relocated absolute provenance paths. All9,568 earlier result
files remain unchanged. Clock/thermal/background controls are unverified; post-run
probes are not timing controls. See audit for resource/timing limitations.

## Controlled CPU/GPU comparison: protocol frozen for review

The [comparison protocol v1](docs/CPU_GPU_COMPARISON_PROTOCOL_v1.md),
[exact matrix](docs/studies/cpu_gpu_comparison_v1.matrix.json),
[resource estimates](docs/studies/cpu_gpu_comparison_v1.resources.csv) and
[freeze hashes](docs/studies/cpu_gpu_comparison_v1.freeze.json) specify a future
study at N=1025/65537/1000000. It has 48 datasets, three CPU modes and two distinct
GPU paths, one warm-up and five measured repetitions: 1200 measured calls and
240 warm-ups. A separate six-dataset pilot is planned first; neither was run here.

Primary ratios will use allocation-inclusive, warm-context host-vector API calls
on the same Colab machine. Existing prepared H2D/device/D2H/end-to-end measurements
remain diagnostics and cannot be used as denominators for CPU host-call speedups.
The production CUB3.0.1 adapter and all previous protocols remain unchanged.
The comparison driver, paired analyzer and resource-query helper are still to be
implemented; no working study command is claimed. Review the protocol before that
implementation and fresh GPU/resource validation. The
[planning audit](results/raw/cpu_gpu_protocol_20261009T234954580281Z/FINAL_AUDIT.md)
distinguishes verified evidence, calculated budgets and unexecuted work.

## Controlled CPU/GPU pilot tooling

The isolated comparison driver, paired analyzer and CUB workspace diagnostic now
exist; see [the implementation guide](docs/CPU_GPU_COMPARISON_DRIVER_v1.md).
`MAB_ENABLE_CPU_GPU_COMPARISON` defaults OFF and requires CUDA sorting and OpenMP.
Existing sorters, defaults, CUB3.0.1 pin and frozen protocols are unchanged.

The pilot-only validation entry point uses new output/build directories, fresh
kernel/build/correctness prerequisites, exclusive output paths and independent
analysis before completion. It preserves attempts and failures. Primary timings
bracket unchanged host-vector API calls, including their allocations/transfers;
the four prepared-buffer metrics remain separate diagnostics. Only production
GPU host-call medians may supply paired CPU/GPU ratio denominators.

```sh
python3 scripts/validate_cpu_gpu_pilot.py \
  --output results/raw/NEW_CPU_GPU_VALIDATION \
  --pilot-output results/raw/NEW_CPU_GPU_PILOT \
  --processed results/processed/NEW_CPU_GPU_PILOT
```

This command permits only the frozen six datasets (150 measured calls and 30
warm-ups), after all prerequisites pass. It has no full-study or resume option.
Use `scripts/run_cpu_gpu_pilot.py --help` and its `--dry-run` mode to inspect the
plan without GPU execution. Fresh local Release and ASan/UBSan suites pass 29/29
groups, with leak detection enabled. Actual remote execution and failure evidence
is retained under `results/raw/cpu_gpu_pilot_20261010T001232473460Z/`; consult its
final audit for the current GPU/pilot status. No full comparative study is claimed.

The final T4 run passed cloud CPU Release 29/29, ASan/UBSan 29/29 (leaks enabled)
and GPU-enabled Release 32/32. The exact pilot completed 150 measured calls and
30 warm-ups with zero failed/interrupted/missing records. All four cloud/local
summaries are byte-identical; independent retained-row checks passed. See the
[pilot report](results/processed/cpu_gpu_pilot_20261010T001232473460Z/REPORT.md)
and [final audit](results/raw/cpu_gpu_pilot_20261010T001232473460Z/FINAL_AUDIT.md).
Earlier failed/expired attempts remain explicit; only the final v3 evidence supports
pilot acceptance. Review the pilot before authorizing the separate full study.

## Full CPU/GPU matrix tooling

`scripts/run_cpu_gpu_study.py --dry-run` now plans the unchanged48-dataset matrix;
the existing pilot command still selects only six datasets. See the
[tooling guide](docs/CPU_GPU_FULL_MATRIX_TOOLING_v1.md) for exact commands, raw
identity/completeness checks, prerequisite-only validation and analysis.
Actual execution requires fresh compatible prerequisites and an explicit
`--execute-study` latch **after separate authorization**. No resume/overwrite.
Analysis supports both recorded matrix parts; incomplete studies cannot produce
paired/cross-input comparisons, and prepared diagnostics never replace production
host-call timing. This is tooling support, not a completed comparison study.

The [safety repair](docs/CPU_GPU_SAFETY_REPAIR_v1.md) adds independent frozen-source
anchor enforcement and a reviewed, fail-closed non-timing test selector.
`python3 -B scripts/non_timing_tests.py --build-dir build/EXISTING_RELEASE` only
prints discovery/selection; it never executes tests. The prerequisite-only
validator now uses that selection and marks its result correctness-only,
`study_eligible=false`. It cannot satisfy the unchanged frozen full-study gate.
No fresh prerequisite run or study was performed by this repair.

The subsequent [CTest build guard](docs/CTEST_BUILD_GUARD_v1.md) validates reviewed
source and generated configuration **before discovery**, including retained JSON.
Hooks, includes, nested registries and unreviewed commands fail closed; metadata
is rechecked before execution. Only inert Python fixtures validated this repair.
No real discovery or selected CTest suite ran. Independent review is next;
study launch remains **NO-GO**.

The follow-up [path-identity repair](results/raw/ctest_path_repair_20261010T234224414430Z/FINAL_AUDIT.md)
pins discovery and downstream selection to the guard's exact absolute build path,
including relative caller arguments and differing callback working directories.
All47 focused inert regressions pass; no CTest, build, prerequisite, resource or
GPU command ran. The approved19 CPU selection and supported layouts are unchanged.
This repair still requires separate independent review; study launch remains NO-GO.
# Bounded CPU/GPU validation — passed; full study not authorized

The opted-in `MAB_ENABLE_VALIDATION_DIAGNOSTICS=ON` targets provide prepared-CUB
correctness without timing and an OpenMP runtime-team diagnostic. The
[v2 classification policy](docs/CPU_GPU_VALIDATION_POLICY_v2.md) keeps correctness,
timing smoke, pilot and full prerequisites distinct; it grants no study eligibility
or execution authorization. Historical protocols and production algorithms are unchanged.

The [reviewed CMake3.31 metadata alternative](docs/CTEST_COLAB_METADATA_v2.md)
preserves the original19 correctness groups plus two explicitly selected diagnostics.
Fresh isolated T4 builds and guarded suites passed: Release21/21, Debug ASan/UBSan21/21
with leak detection enabled. Prepared GPU correctness passed163 inputs/489 output
checks and489 invalid-operation rejections. Bounded resources passed all frozen sizes
(1,025/65,537/1,000,000);12 worker checks verified team1 below32,768 and team2 at/above.
Host-only analysis intentionally skipped two GPU timing Python methods in each suite;
no CTest group was skipped. Worker-team size does not prove task participation.

The initial synthetic-fixture failures, harness errors and stale Colab import rejection
are retained with the successful revision in the
[current audit](results/raw/bounded_resume_20261011T024034091796Z/FINAL_AUDIT.md).
The [earlier blocked attempt](results/raw/bounded_validation_20261011T020343203635Z/FINAL_AUDIT.md)
remains immutable. No timing smoke, pilot, warm-up, measured trial or study ran here.
Next: independent review of the consolidated validation evidence. Legacy full-study
provenance gates remain unchanged and reject the deliberately extended framework;
current correctness evidence does not establish timing validity or authorize a launch.
# CPU/GPU recovery: explicit framework compatibility

An opt-in, pinned [framework compatibility policy](docs/CPU_GPU_FRAMEWORK_COMPATIBILITY_v1.md)
now recognizes the three approved test-only framework changes while preserving
legacy rejection and all full-prerequisite coverage requirements. A read-only
build-identity snapshot includes `comparison_input` and rejects stale/mismatched
files. Focused inert regressions pass; current remote identities and full-study
eligibility remain blocked. No new timing trials ran. See the
[recovery audit](results/raw/cpu_gpu_recovery_20261011T075800444473Z/FINAL_AUDIT.md).

