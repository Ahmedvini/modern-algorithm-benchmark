# Reproducible sorting protocol: sort_timing_v1

## Scope and inputs

sort_benchmark calls the existing production registry: std_sort (default),
quick_sort, pdq_sort, tim_sort, merge_sort and radix_sort. It links mab_timing and mab_core, never
mab_metrics. The original correctness CLI and sort_metrics remain independent.
--sort all selects the registry; comma-separated subsets are supported.

The development smoke matrix uses N=1,000 and 10,000, seed 1729, all six sorters
and five distributions. Explicit larger experiments can use 1K/10K/100K/1M and
multiple seeds; those larger experiments have not been run for this milestone.
Default CTest uses tiny inputs, not a large performance matrix.

Existing mt19937_64_v1 generation is unchanged. Uniform, reverse_sorted,
duplicate_heavy and nearly_sorted retain EXPERIMENT_PROTOCOL.md's exact mapping.
The benchmark-only distribution sorted means the corresponding uniform sample
sorted ascending, implemented by the existing nearly_sorted generator with zero
swaps. It reports zero swaps even if --swaps was supplied. It does not extend the
original CLI/generator enum. Defaults are swaps floor(N/100), duplicate domain 16.

Each configuration generates one immutable original vector and records its
ordered FNV-1a64 fingerprint: uint32 key representation, low-to-high four bytes,
offset 14695981039346656037, multiplier 1099511628211, unsigned wraparound. This
is an identification aid, not a cryptographic correctness proof. The entire
sorted vector is compared with a trusted std::sort reference on every trial.

## Execution and timing

Default warmups=1 and measured repetitions=5 **per algorithm and configuration**.
Warmups may be zero; repetitions must be 1..10,000 and warmups 0..1,000. Warmup
rows are retained with phase warmup; analysis excludes them from runtime summaries.
Warmup failures stop the run. No automatic convergence or early statistical stop.

Before warmups, the engine creates the expected sorted vector and a same-sized
working vector. Before every call it copies the immutable original into the
already allocated working vector. Generation, reference sorting, input restoration,
full-vector validation, metadata, CSV writing and flushing are outside timing.
Only steady_clock::now(), the production sort call, and steady_clock::now() bracket
the timed interval. Sort-owned allocation/deallocation and function dispatch are
included. There is no end-to-end/setup metric and no comparison instrumentation.

Merge Sort and Radix Sort each allocate a single N-key workspace per nontrivial
sorting call. Those allocations and deallocations remain inside timing under
the same protocol. The existing linear-workspace planning allowance covers their
key buffers; radix's 256 size_t offsets and allocator overhead remain outside
that estimate. Radix Sort's comparison metric is unsupported in the separate
metrics CLI; it does not contribute fabricated comparison counts to timing CSV.

Elapsed durations are integer nanoseconds from duration_cast<nanoseconds>.
The clock is statically required to be monotonic; its native period numerator/
denominator are recorded. Nanosecond units do not imply nanosecond accuracy.
Clock quantization, timer-call overhead and scheduling affect tiny runs. Zero
durations are retained. No timer-overhead subtraction, batching or unsupported
precision claim is made. CTest timings are validation observations, not experiments.

Within each phase/trial, selected algorithm order rotates cyclically. Offset is
(seed % algorithm_count + trial_index % algorithm_count) % algorithm_count;
the metadata retains the selected list and each row's execution_order. This
reduces fixed position bias but is not statistical randomization. Trial indices
restart at zero for measured trials. Warmups run for all algorithms before
measured rounds. Copies touch memory before timing: this is a warmed development
protocol, not a cold-cache study. No CPU pinning, frequency control, exclusive
machine reservation, cache flushing or background-load control is implemented.

Performance execution requires Release and sanitizers OFF. --validation-only
permits Debug/sanitizer test runs and explicitly labels records validation.
Analysis keeps that label/build metadata; such records must not be interpreted
as production performance or pooled with Release experiments.

## Resource planning and CLI

```sh
build/release/sort_benchmark --output results/raw/new_single_run --sort all --size 1000 --seed 1729 --distribution uniform --repetitions 5 --warmups 1
python3 scripts/run_matrix.py --binary build/release/sort_benchmark --output results/raw/new_smoke_matrix
mkdir -p results/processed
python3 scripts/analyze_results.py results/raw/new_smoke_matrix --output results/processed/new_smoke_summary.json
```

Explicit larger experiment (instructions only; not executed here):

```sh
python3 scripts/run_matrix.py --binary build/release/sort_benchmark --output results/raw/new_cpu_experiment --sizes 1000,10000,100000,1000000 --seeds 1729,42,2718 --repetitions 5 --warmups 1 --memory-limit-mib 256
python3 scripts/analyze_results.py results/raw/new_cpu_experiment --output results/processed/new_cpu_summary.json
```

sort_benchmark requires --output NEW_DIRECTORY. Its parent must exist. Other
options: --sort NAME[,NAME...] or all (default std_sort), --size (1000), --seed
(1729), --distribution (uniform), --swaps (N/100), --distinct (16), --repetitions
(5), --warmups (1), --memory-limit-mib (256), --run-id (directory name),
--validation-only, --list-sorts and --help. Repeated options use the last parsed
value; invalid values fail immediately. Numeric arguments are unsigned decimals,
with no signs/whitespace/trailing characters or overflow. Size zero is allowed.
Sorter subsets cannot be empty/duplicated or contain unknown names. Distinct
must be 1..2^32. Swaps are bounded at 10,000,000 for this CLI.

The memory planning limit is 1..65,536 MiB. N is checked before allocation using
4*N*sizeof(int32): original, reference, working and a linear-workspace allowance.
This is a conservative planning estimate, **not measured memory or a hard RSS
limit**; allocator/runtime/vector growth overhead and OS overcommit are excluded.
Actual allocations can still fail. One configuration is resident at a time.
run_matrix bounds lists to 1,000 entries, configurations to 1,000 and total
warmup/measured rows to 1,000,000 before constructing its case list. It executes
configurations serially in size/seed/distribution order, with a new process per
configuration. Its defaults are two sizes, one seed, five distributions, all
registry names, one warmup and five measured repetitions. --sizes/--seeds and
--distributions accept comma-separated lists; --sorts selects a subset or all.

## Raw output and metadata

Directory creation is exclusive and atomic. Existing directories/files/symlinks
are rejected; no overwrite flag or cleanup removes earlier output. Within the
new owned directory, run.json describes the plan before timing; trials.csv is
streamed/flushed per observation. COMPLETE.json is created only after every
planned row passed and the CSV was closed successfully. Errors retain available
raw data, write FAILED.json where possible, print stderr and exit 1. Interrupted
runs lack a completion marker and are incomplete. Disk/write errors cannot be
made recoverable if the filesystem refuses writes; absent COMPLETE remains
authoritative. The matrix similarly retains each child's command/stdout/stderr/
exit code, stops on first failure and writes its completion marker only after all
children succeed. Partial data never masquerades as a completed matrix.

run.json stores protocol, run_id/kind, exact argv, start Unix seconds, seed,
distribution/parameters, size, selected algorithms/order policy, warmup/repetition
counts, expected row totals, input hash, planning limit and clock period. Build
metadata includes CMake compiler identity/version/path, actual build configuration,
sanitizer flag, __cplusplus, CMake global/configuration flags, platform/architecture
and compile-command availability. These flags are labeled CMake settings, not
guessed full effective flags. compile_commands.json and CMakeCache.txt are copied
when present; exact per-translation-unit compile options are in that artifact.

CMake records SHA-256 of project include/src and vendored headers/provenance in
source_hashes.json; recorded source changes trigger reconfiguration. Upstream
PDQSort/Timsort provenance is copied from configured build artifacts. Runtime
requires those configured artifacts to remain accessible, and does not fabricate
missing provenance. Direct CLI records available Linux /proc CPU/memory information
and a hardware_concurrency hint (zero means unknown). Other platform details may
be absent; there is no guessed CPU/GPU/RAM value or Git revision. run_matrix also
uses the existing environment capture for OS/kernel, CPU, RAM, compiler flags,
tool versions, Git absence and executable SHA-256. All of this is outside timing.

The raw CSV has 28 fields in this order:

```text
schema_version,protocol,run_id,run_kind,algorithm,distribution,size,seed,nearly_sorted_swaps,duplicate_cardinality,dataset_generator,input_hash_fnv1a64,phase,trial_index,execution_order,elapsed_ns,elapsed_unit,status,correctness,error,repetitions,warmups,compiler_id,compiler_version,build_type,sanitizers,platform,architecture
```

Schema=1, protocol=sort_timing_v1, generator=mt19937_64_v1, elapsed_unit=ns.
run_kind is performance/validation. phase is warmup/measure. status is ok/error;
correctness is passed/failed/not_checked. Indices/order are zero-based. Timing
exists for successful calls and correctness failures; exceptions have a blank
elapsed field. Error diagnostics are retained. Build/configuration and dataset
fields repeat in each row to permit independent grouping. CSV quotes comma,
quote, CR and LF fields, doubles embedded quotes, and uses LF record separators.
Consumers must use a CSV parser and preserve large integer seeds/hashes/times.

## Analysis and failure/outlier policy

analyze_results.py validates schema, units, metadata agreement, phase/trial/order,
unique records, correctness/status/error consistency, planned totals and completion
markers. It rejects incomplete runs by default before creating an output file.
--allow-incomplete is explicit: partial summaries retain complete=false, failed
trials/warmups, missing trials and missing planned runs, and the command still
exits 1. Invalid/malformed CSV remains an error even in that mode. Failed rows
are counted but excluded from successful timing statistics, never hidden.

The separate summary JSON uses schema_version=1, summary_kind=sort_timing_summary,
complete, source, elapsed_unit=ns, outlier_policy=retain_all, stdev_definition,
missing_runs and groups. Every run/algorithm group includes configuration/build
identity, successful_trials, failed_trials, missing_measured_trials, warmup_rows,
failed_warmups, run_complete, median_ns, mean_ns, stdev_ns, min_ns and max_ns.
Sample standard deviation uses n-1 and is null for fewer than two successes;
all statistics are null for zero successes. Medians/means may be fractional ns
as statistical summaries, without implying finer clock precision.

Groups are separated by run and algorithm; distinct seeds/distributions/builds
are not silently pooled. All successful measured observations, including outliers,
are retained. There is no rejection/clipping/trimmed-mean policy or ranking.
Summary output is exclusively created under a separate derived-data path. Raw
observations are never edited by analysis. One run or a small smoke matrix cannot
justify a general faster/slower conclusion. Publication-quality controlled
experiments, uncertainty interpretation and plots remain later work. Comparison
counts and process RSS use the independent METRICS.md path, not the timing interval.
