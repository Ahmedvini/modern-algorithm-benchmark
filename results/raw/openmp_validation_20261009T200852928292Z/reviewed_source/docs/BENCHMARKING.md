# Reproducible sorting protocol: sort_timing_v1

## Scope and inputs

sort_benchmark calls the existing production registry: std_sort (default),
quick_sort, pdq_sort, tim_sort, merge_sort and radix_sort. It links mab_timing and mab_core, never
mab_metrics. The original correctness CLI and sort_metrics remain independent.
--sort all selects the registry; comma-separated subsets are supported.

The development smoke matrix uses N=1,000 and 10,000, seed 1729, all six sorters
and five distributions. Explicit larger experiments can use 1K/10K/100K/1M and
multiple seeds. The subsequent [frozen 1M study](studies/sorting_1m_20261009T172003802655Z_v1.md)
is complete with 450 measured trials and 90 warm-ups; the full multi-size larger
matrix below remains instructions only. Default CTest uses tiny inputs, not a
large performance matrix.

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
justify a general faster/slower conclusion. Phase 5 now supplies reproducible
plots and hierarchical descriptive summaries; independent-session uncertainty
experiments remain future work. Comparison
counts and process RSS use the independent METRICS.md path, not the timing interval.

## First recorded 1M study

See [the frozen v1 protocol](studies/sorting_1m_20261009T172003802655Z_v1.md),
[full statistics](../results/processed/sorting_1m_20261009T172003802655Z/RESULTS.md) and
[final audit](../results/raw/sorting_1m_20261009T172003802655Z/FINAL_AUDIT.md). All six algorithms,
N=1,000,000, five distributions, seeds 1729/42/2718, one warm-up and five measured
repetitions completed 15 configurations: 450 measured successes and 90 warm-up
successes with zero failures. Nearly-sorted swaps=10,000; duplicate domain=16.
The engine, CSV schema and runner order were unchanged.

The established analyzer produces 90 per-seed groups. Cross-seed statistics
use three seed medians with equal weight and report median/mean/sample SD/min/max
of those medians, avoiding pooled repeated timings as independent datasets.
Raw nanoseconds are retained; report tables convert to milliseconds and round
to three decimals. All observations/outliers remain. The retained study-specific
analysis/verification scripts reproduce all five derived JSON/CSV/Markdown files
byte-for-byte, checking raw/protocol/source/binary/earlier-evidence hashes.

This fixed-workload study ran on a shared desktop with recorded dynamic CPU
power policy and before/after resource/load snapshots; it does not establish
exclusive load, fixed frequency, fixed thermal/cache state, significance or a
universal ranking. No RSS or comparison-count experiment accompanied primary
timing. Recommended follow-up: separately freeze a 1M independent-session/seed
replication with documented affinity/power policy and counterbalanced ordering.
No study beyond 1M has run.

## Search batch engine (separate search_batch_v1 schema)

The [versioned search protocol](SEARCH_PROTOCOL_v1.md) defines nine category
policies and their availability, deterministic query identity, duplicate semantics,
preprocessing and cyclic ordering. Existing sorting binaries/schemas/tools and
std_sort default are preserved. search_benchmark links the normal search library,
existing mab_timing/output utilities and mab_core; it does not link counted code.
search_counts is the separate comparison-only executable.

```sh
python3 scripts/run_search_matrix.py --binary build/release/search_benchmark --output results/raw/new_search_smoke
python3 scripts/analyze_search_results.py results/raw/new_search_smoke --output results/processed/new_search_smoke.json
build/release/search_counts --output results/raw/new_search_counts --search all --size 64 --queries 16
```

The matrix defaults to N=0,1,64,1000; uniform/duplicate_heavy; seed 1729, query
seed 2718; all three searchers/all nine categories; 64 queries per available
category; one warm-up and five measured repetitions. Unavailable categories are
retained with reasons, not silently replaced by another category. All algorithms
share each configuration's sorted data and exact category query list. Source
ordering distributions are normalized by preprocessing and can produce identical
prepared data; the recorded distribution identifies generation, not lookup order.

| Search CLI option | Default / validation |
| --- | --- |
| --output | Required nonexistent directory; parent must exist |
| --search | linear_search; comma-separated linear_search,binary_search,exponential_search or all; unique known names |
| --size / --seed | 1000 / 1729; unsigned decimals fitting size_t / uint64; zero size allowed |
| --query-seed | 2718; unsigned decimal fitting uint64 |
| --distribution | uniform; same five generation/alias names as sort_benchmark |
| --queries | 1000; even integer in [2,100000] |
| --categories | all; comma-separated unique names from SEARCH_PROTOCOL_v1; execution uses fixed category order |
| --swaps / --distinct | floor(N/100) / 16; same bounds as sort_benchmark |
| --repetitions / --warmups | 5 / 1; ranges [1,10000] / [0,1000] |
| --memory-limit-mib | 256; [1,65536], conservative 16*N+128*queries*9 planning guard |
| --run-id | Output directory name; explicit strings are CSV/JSON escaped |
| --validation-only | Permit Debug/sanitizer tests with validation label |
| --list-searches / --help | Print registry names / usage and immediately exit 0 |

Repeated valid options use the last parsed value. Unknown names and malformed
numbers fail at parsing; resource/range checks occur before directory creation.
Unsigned numbers reject signs, whitespace, overflow and trailing characters.
Unknown/missing options, invalid configuration, allocation/write/correctness errors
exit 1 with error: on stderr. Owned incomplete bundles retain FAILED or absent
COMPLETE; existing output paths are never deleted/overwritten. search_counts
accepts dataset/query/search options but rejects timing-only options; it records
search_counts_v1, per-query predicates/answers, and no latency or RSS.

Before lookup, generate and std::sort data outside timing. The separately recorded
preprocessing_sort_ns covers only that final std::sort call, excluding generation's
own transformations and query generation; it is one setup observation, not a
repeated preprocessing benchmark. Input order is ascending for all algorithms.
Only batch loop, production function dispatch and stores into a preallocated
answer buffer are timed. Every stored result is verified against the first-match
reference after timing. queries.csv joins categories/query IDs to target, selected
rank and expected first-match rank/absence; run.json carries category counts and
fingerprints. No search preprocessing or instrumentation occurs inside lookup.

The dedicated analyzer validates 32 timing fields, query identity/hash/hit counts,
metadata agreement, phase/category/order, completion and planned totals. It reports
successful/failed/missing trials, warm-ups, availability reasons and batch latency
median/mean/sample SD/min/max. Normalized ns/query divides batch statistics by
batch_size; this is average batch cost, not an individual-query measurement.
Maximum normalized batch average is not maximum individual-query latency. Every
observation/outlier remains; incompatible runs/seeds/categories stay separate.
Default analysis rejects partial runs; --allow-incomplete reports partial/missing
status and exits 1. Derived files are exclusively created separately from raw data.

The runner adds --sizes, --seeds, --query-seeds, --distributions, --searches and
matrix limits, while forwarding queries/categories/dataset/timing options.
It retains child argv/exit/stdout/stderr, environment/tool hashes and completion
markers. A larger baseline requires an explicit new protocol/resource review:

```sh
python3 scripts/run_search_matrix.py --binary build/release/search_benchmark --output results/raw/new_1m_search_study --sizes 1000000 --seeds 1729,42,2718 --query-seeds 2718,3141 --queries 1000 --repetitions 5 --warmups 1
```

This larger command is instructions only; no 1M search study was run during Phase 3; Phase 5 extends it below. Linear
search can make large batches costly. Direct per-query timing/maxima, timer
calibration, cold caches, affinity/frequency control and search RSS/allocation
studies remain unimplemented. Smoke observations validate infrastructure and
support no performance superiority claim.

## Structure construction and lookup: structures_batch_v1

The separate [frozen Phase 4 protocol](STRUCTURES_PROTOCOL_v1.md) defines owned
indexes, insertion order, first-payload semantics, invariants, timing boundaries,
34-column CSV and failure policy. Reuse existing datasets, Phase 3 query planner,
CSV escaping, compiler/source metadata, environment capture and sample statistics.
Array-search/sorting protocols and tools are unchanged.

structure_benchmark accepts search_benchmark's dataset/query/timing/output options,
replacing --search with --structure (default skip_list), --list-searches with
--list-structures, and adding --structure-seed (1729). All five configurations
are skip_list,btree_m10,btree_m16,btree_m32,btree_m64. Numeric parsing, repeated
options, immediate help/list, validation-only build guard, exit 1/stderr errors
and exclusive raw bundles follow existing conventions. The structure planning
allowance is 512*N+128*queries*9 bytes. RSS is not sampled or isolated.

run_structure_matrix.py uses --structures and --structure-seed with the existing
matrix list/row limits; run order is size/seed/query-seed/distribution. Defaults
are N=0,1,64,1000; uniform/duplicate_heavy; seeds 1729/2718/1729; Q64; W1/R5.
The per-round row bound includes a construction row plus each eligible query
category per structure. Empty input still has construction rows; unavailable
lookup categories retain reasons and generate no invented timing.

Each round rotates structure order, builds a fresh instance and validates size,
all payloads and structural invariants. Constructor, promotion RNG initialization,
node/vector allocation and inserts are included in build timing. Prepared key/rank
entries and reference sorting are excluded. Lookup batches run on that instance;
virtual dispatch, loop and preallocated answer stores are included. Every answer
is checked outside timing. Instance destruction occurs after all lookup timers.
These are warmed structures/queries; validation touches nodes before lookup.
No cold-cache, per-operation maximum, isolated memory or end-to-end cost is claimed.

run.json records original insertion and sorted-reference fingerprints, unique-key
count, structure seed and the exact query plan. queries.csv uses the unchanged
Phase 3 six-column schema. trials.csv uses operation build/lookup; construction
has blank query fields. COMPLETE requires every planned row, successful correctness
and closed streams. The dedicated analyzer checks schema/metadata, query hashes,
exact schedule, fail-fast records and completion; default refuses incomplete data.
--allow-incomplete reports failed/missing trials and warmups/missing runs, exits 1.
Build/lookup/category/seed groups remain separate. Statistics are ns, with normalized
lookup ns/query; sample SD uses n-1 and is null below two successes. All raw outliers
remain. Summary output is exclusive and deterministically regenerable.

## Phase 5 unified pipeline

[experiment_pipeline_v1](ORCHESTRATION_PROTOCOL_v1.md) freezes serial family
orchestration and separate smoke/full presets, leaving all family engines and
schemas unchanged. run_experiments.py prints a deterministic dry-run plan or
invokes the existing runners, validates every planned child/row and then runs
analyze_experiment.py for common observations/statistics, plot_results.py and a
consolidated report. All output roots/run IDs are explicit and exclusive.

Only successful validated collection receives COLLECTED; only validated derived
artifacts receive final COMPLETE and hashes. Subprocess stdout/stderr/exits and
interruption outcomes are retained; failed/missing configurations remain visible.
No resumption is implemented. Retry with a new ID; never reuse/delete old output.
Partial analysis requires --allow-incomplete, exits1, preserves partial status;
malformed records remain rejected. Sorting/search/structure metrics are never
silently pooled, and performance runs exclude counted adapters.

summary.json preserves per-dataset success/failure/missing/warmup counts and
median/mean/sample SD/min/max ns. Cross-dataset summaries use one median per
actual ordered-input fingerprint (median of declared-dataset medians on a repeated
fingerprint), equal weight. Query seed, structure seed, policy/batch size, build,
source, flags and source distribution remain grouping dimensions. No repeated
trial is treated as an independent dataset. observations.jsonl retains every raw
row and its CSV path/row index, with required/optional/null field mappings in the
new protocol. Raw query targets/expected positions remain traceable in queries.csv.

SVG/PDF figures separate sorting/build/lookup and source distributions/policies.
Centers summarize input medians; separate min/max bars show dataset-median and
measured-trial spread. y axes start at0; x symlog explicitly labels the N<=1 linear
region. Lookup is normalized batch-average ns/query. plot_manifest.json records
source/figure hashes, filter/group identities, transforms/units/points and plotting
stack. Reports include completeness tables and unavailable comparison/memory plots.
No counts or measured memory are fabricated from timing rows. Regenerate to new
paths with analyze_experiment.py; standalone plot_results.py also revalidates raw.
Full execution status is recorded separately in AUDIT.md; smoke is not full study.

The retained Phase 5 full study is results/raw/phase5_full_20261009T191000587965Z; processed
summary/observations/REPORT.md are under results/processed/phase5_full_20261009T191000587965Z,
and SVG/PDF/plot_manifest.json under results/figures/phase5_full_20261009T191000587965Z.
All 180 configurations, 22,020 measured trials/4,404 warmups passed; 144 unavailable
category/configuration entries have explicit reasons (including empty-only policy
on nonempty data and interior misses when duplicate domain has no gaps).
4,404 per-dataset and1,468 cross-dataset groups retain all outliers and ns statistics.
177 figure pairs and all derived files regenerated byte-for-byte. This is a single
shared-machine session, not independent-session replication or significance.
The full row totals differ from upper bounds solely because policies are explicitly
unavailable, not failed/missing trials. Construction includes1,500 measured builds;
11,700 structure lookup batches are separate. Comparison/RSS paths were not run.

## Phase 6 OpenMP family: parallel_sort_timing_v1

The new parallel_sort_benchmark reuses the shared run_timing_engine template;
original run_timing_trials retains normal dispatch and the unchanged 28-field
sort_timing_v1 CSV. The new configurable path returns actual-team information
from the sorter, copying it to the row after the stop timestamp. Clock, restore,
full reference validation, seed-offset cyclic order and error handling are shared.
The new CSV is the old 28 fields with protocol=parallel_sort_timing_v1, followed
by implementation_version,requested_threads,actual_threads,parallel_region.
Sequential rows report1/1/false; parallel requests may run serial below threshold.
A failed invocation can report actual_threads=0 (unknown), never a guessed team.
Buffer allocation, OpenMP team/tasks/joins and buffer destruction belong to timing.

run.json adds parallel_threads,parallel_threshold,task_grain,openmp_macro,
openmp_version,openmp_flags and openmp_runtime_libraries. CMake/compile commands,
source hashes and upstream provenance remain sidecars. Matrix environment records
OMP/GOMP policy, actual runtime linkage paths/hashes and CPU/OS/compiler/resources;
no runtime version is invented when unavailable. Common Release optimization flags
apply; -fopenmp is required for parallel translation units and its flags are recorded.

run_parallel_matrix.py extends orchestration with a separate versioned family;
it reuses Phase 5 resource/signal/process helpers and existing environment capture,
CSV escaping, dataset generation and sample-statistics functions. Phase 5 presets
and old family scripts remain unchanged. It validates bounded matrices, prints
stable dry-run plans, runs serial children, validates raw collection, then invokes
analysis/plots/report before final completion. Failures/interruption retain exact
command diagnostics and FAILED/INTERRUPTED markers. Missing trials are explicit.
Directories are exclusively created; retry with a new ID, no resume or overwrite.
--config custom JSON follows the strict preset schema; --preset full is only the
unchanged candidate matrix, subject to separately frozen launch/resource review.

Analyzer grouping retains size/distribution/dataset/request/actual-team identities;
mixed actual teams within a cell are rejected. Default studies require actual=request
above threshold. Ratios require complete positive medians and the parallel request1
baseline. Below threshold scaling ratios are unavailable. Per-dataset timings use
median/mean/sample SD/min/max ns. Primary speedup uses the sequential cell median;
secondary speedup uses parallel request1's median on the same input. Efficiencies
divide their respective speedups by actual p. Ratios precede cross-dataset statistics;
identical fingerprints collapse, seeds are equally weighted. Outliers stay; no
confidence intervals/significance claim. Figures show dataset min/max spreads.

summary.json,observations.jsonl,REPORT.md and SVG/PDF/plot_manifest.json are separate
from raw bundles. Regeneration is byte-identical on the recorded plotting stack.
No memory/counting result is inferred from timing. See [frozen protocol](OPENMP_PROTOCOL_v1.md)
and AUDIT.md for actual smoke/full execution and sanitizer/race-detector limitations.
