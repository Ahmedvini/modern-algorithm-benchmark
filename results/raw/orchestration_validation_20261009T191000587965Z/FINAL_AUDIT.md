## Phase 5 — audited orchestration, visualization and completed CPU study (2026-10-09)

Workspace was writable: the safe temporary-file check succeeded and was removed.
AGENTS.md was read completely; README, roadmap, audit, algorithm/benchmark/metrics
references and both family protocols were inspected before implementation. Git
metadata is absent (`git status --short`: exit 128); none was created. The existing
Release baseline was freshly configured, built and passed 21/21 CTest groups.
Historical LastTest logs were copied separately; they are not fresh test evidence.

The new evidence root is
`results/raw/orchestration_validation_20261009T191000587965Z/`. Starting-state,
repository-before and prior-results manifests record 99 original project files
and 867 earlier result artifacts. Original files were backed up for a reviewable
patch. All 867 artifacts and all protected original files remain unchanged,
including the frozen 1M sorting study, search/structures protocols, vendored code,
algorithms, existing tests and existing Python family tools. No original C++
implementation or timing behavior changed. std_sort remains the default.

Before implementation, the new versioned protocol was saved and frozen as
`docs/ORCHESTRATION_PROTOCOL_v1.md`, with a retained copy PROTOCOL_v1.md and SHA256
`5bf13d60312d4958be93eb17dfe56c0be221964cf2960dec5988849d524d0d73`.
Earlier protocols were preserved. The protocol defines smoke and full presets,
serial execution, exact family outputs, query-category availability, resource
planning, missing/failure/interruption handling, aggregation and plotting.

### Implemented changes and metric definitions

Seven new files: the orchestration protocol; scripts/experiment_model.py,
run_experiments.py, analyze_experiment.py, plot_results.py, assess_experiment.py;
and tests/test_experiments.py. Eight existing files changed: CMakeLists.txt adds
one experiment_pipeline CTest group; README and docs/ROADMAP, AUDIT, ALGORITHMS,
BENCHMARKING, EXPERIMENT_PROTOCOL and METRICS describe verified behavior.
file_changes.json, changes.patch and final_source_manifest.json retain the exact
file inventory and review without Git.

The serial top-level runner invokes the unchanged sorting, array-search and
structure runners. Deterministic dry runs print exact parent/child commands,
configuration hashes, output paths and bounded resource estimates. Explicit run
IDs and exclusive directory creation prevent overwrites and collisions. Resume
is deliberately unsupported: existing paths fail fast. Child stdout/stderr,
return codes, timestamps and interruption diagnostics are retained; failed or
interrupted runs never receive successful completion markers. Process groups
are terminated on interruption. Collection and final completion markers require
strict validation, including configuration, raw schema, duplicate trial identity,
positive/nonnegative finite timing as appropriate, family protocol, build and
fingerprint consistency, expected coverage and derived-file hashes. A partial
analysis requires an explicit flag, reports omissions and exits unsuccessfully.

observations.jsonl preserves every raw observation and its file/row provenance;
unavailable metadata remains null rather than invented. Warmups and measured
rows remain distinct. Sorting and construction times are elapsed batch ns;
lookup plots show normalized batch-average ns/query, never directly measured
individual latency. Generation, copying, queries and correctness checks retain
the existing outside-timing semantics. Primary runs contain no comparison
instrumentation. No process RSS or isolated allocation value was collected in
these timing studies. Comparison/memory figures explicitly report absent matching
evidence instead of estimating measurements.

Per-dataset groups retain successful/failed/missing counts, median, mean, sample
standard deviation (ddof=1), minimum and maximum. Warmups are excluded from timing
statistics. Cross-dataset summaries first summarize repeated timings within each
dataset, collapse identical ordered-input fingerprints, then equally weight
medians of distinct inputs; repetitions do not inflate dataset sample size.
All outliers remain. Query policies, workload parameters, build/source identity
and construction versus lookup stay separate. No confidence interval or
statistical-significance claim is made.

Matplotlib Agg produces SVG/PDF figures with deterministic metadata, fixed font
and styling, zero-based linear y axes, explicitly labeled symlog size axes,
central medians, dataset-median min/max spread and separate trial variability.
Each plot manifest records source hashes, filters, transforms, points, units,
plotting stack and output hashes. Reports consolidate environment, protocol,
coverage, results, variability, limitations and regeneration instructions.
Byte identity is verified on this plotting stack, not guaranteed across versions.

### Actual failures, fixes and final validation

The initial standalone pipeline suite exited 1: 18/19 methods passed; the parent
SIGTERM test timed out. Raising InterruptedError in the signal handler allowed
Python I/O retry; it now raises KeyboardInterrupt and terminates the child process
group. Test cleanup also fixed ResourceWarnings from that failure. The initial
failure log and result remain retained. Subsequent review separated natural
SIGINT/SIGTERM interruption from other fatal child signals such as SIGABRT, and
validated exact return-code types plus interrupted parents whose child exited 0.
These handling fixes affect failure paths, not successful benchmark timings.
The exact Python execution tools used for all three studies are retained under
execution_tools/ with hashes matching each study environment. Final code includes
the handling fixes and passes the expanded 23-method suite. No study failed.

Exact final commands, each exit 0:

```sh
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_SANITIZERS=OFF
cmake --build build/release --parallel 2
ctest --test-dir build/release --output-on-failure -V
cmake -S . -B build/sanitize -DCMAKE_BUILD_TYPE=Debug -DMAB_ENABLE_SANITIZERS=ON
cmake --build build/sanitize --parallel 2
env -u ASAN_OPTIONS -u LSAN_OPTIONS UBSAN_OPTIONS=halt_on_error=1 ctest --test-dir build/sanitize --output-on-failure -V
python3 tests/test_experiments.py build/release
```

Final Release: 22/22 CTest groups, 19.32 seconds. Final Debug ASan/UBSan: 22/22,
54.94 seconds. Independent Python: 23/23 methods. Leak detection remained enabled;
the historical ptrace limitation did not recur, so no leak-disabled retry ran.
No final compiler warnings. All 21 preexisting groups passed unchanged, including
6,635 structure cases / 1,239,680 insertion attempts / 3,218,705 map-oracle lookups /
75,665 invariant checks; 3,704 search inputs / 309,996 oracle checks; existing
sorting, metrics, CLI, timing and Python framework tests. New tests cover stable
configuration/dry-run identity, malformed/duplicate records, incompatible protocols,
missing trials, failed and interrupted subprocesses, atomic directory collisions,
hand-checkable hierarchical statistics, resource estimates, exact plot points,
manifest provenance and byte-identical summary/report/figure regeneration.
Synthetic fixture timings are test data, never presented as benchmark measurements.

COMMANDS.md and commands_index.json in the new evidence root retain every recorded
configure/build/test, dry-run, smoke/calibration/full launch, runtime assessment
and independent verification command with actual exit codes and diagnostics.
The initial unwrapped failure and Git inspection failure are separately identified.
Family experiment.json and *_command.json files retain exact benchmark commands.

### Executed smoke, calibration and unchanged full preset

Smoke command (exit 0), preceded by the identical command plus --dry-run (exit 0):

```sh
python3 scripts/run_experiments.py --preset smoke --run-id phase5_smoke_20261009T191000587965Z
```

Smoke: N=0/64/1000, uniform/duplicate_heavy, dataset seeds 1729/42,
query seed 2718, structure seed 1729, Q64, one warmup and five repetitions.
All 36 configurations completed: sorting 360 measured/72 warmup;
search 975/195; structures 1,925/385. Total 3,260 measured successes and 652
warmups, zero failed/missing/interrupted trials. Its 652 per-dataset and 330
cross-dataset groups, report and 81 SVG/PDF figure pairs regenerated exactly.
Unavailable categories were explicitly recorded, not fabricated as missing trials.
verification.json retains raw immutability and prior-artifact verification.

The tiny smoke's overhead-inclusive full forecast was 22,955.803 seconds,
exceeding the 3,600-second runtime gate. A separately labeled, frozen 100K uniform
calibration used all algorithms/structures, seed 1729, Q1000, zero warmups and one
measured repetition. It did not replace or reduce the full protocol. Its exact
launch used --config with calibration_config.json and the distinct run ID
phase5_calibration_20261009T191000587965Z; exit 0. CALIBRATION_PROTOCOL_v1.md and
calibration_runtime_assessment.json retain the prelaunch contract and result.
The refined forecast was 2,745.658 seconds with a factor-four allowance; memory,
disk and runtime planning gates passed. Forecasts are estimates, not timings.
FULL_STUDY_LAUNCH_v1.md and full_launch_plan.json were saved before execution.

Full command (exit 0), preceded by identical --dry-run (exit 0):

```sh
python3 scripts/run_experiments.py --preset full --run-id phase5_full_20261009T191000587965Z
```

The frozen full preset ran N=1K/10K/100K/1M; uniform, sorted, reverse_sorted,
duplicate_heavy and nearly_sorted; seeds 1729/42/2718; query seed 2718;
structure seed 1729; Q1000; W1/R5; cardinality16; default nearly-sorted swaps;
1024 MiB per-process budget. All six sorting algorithms, three array searchers,
Skip List and B-Tree orders 10/16/32/64 ran serially. 180 configurations completed.
Before query availability checks, protocol upper bounds were 24,900 measured and
4,980 warmup rows. Exact actual availability produced:

| Family | Successful measured | Successful warmups | Failed / missing |
|---|---:|---:|---:|
| Sorting | 1,800 | 360 | 0 / 0 |
| Array search | 7,020 | 1,404 | 0 / 0 |
| Structures | 13,200 | 2,640 | 0 / 0 |
| Total | 22,020 | 4,404 | 0 / 0 |

Structure measured rows comprise 1,500 builds and 11,700 lookup batches.
No interrupted configuration. 144 category/configuration pairs were explicitly
unavailable (72 each search/structures: empty-only policy on nonempty input and
unrepresentable between-value gaps in duplicate-heavy inputs). This is expected
protocol availability, not omitted execution. Every retained row passed correctness.
The report has 4,404 per-dataset and 1,468 cross-dataset groups and 177 SVG/PDF
figure pairs. Overhead-inclusive family wall times were sorting 16.222 seconds,
search 158.112 seconds and structures 215.411 seconds; analysis 97.930 seconds.
These include setup/process/validation/I/O and are not algorithm timing statistics.

Raw, processed and figure roots respectively are:
`results/raw/phase5_full_20261009T191000587965Z/`,
`results/processed/phase5_full_20261009T191000587965Z/`,
`results/figures/phase5_full_20261009T191000587965Z/`.
REPORT.md, summary.json, observations.jsonl and plot_manifest.json are data-driven.
Independent verify_full.py exited 0: all processed bytes and 177 figure pairs
regenerated byte-for-byte in fresh temporary directories; all 1,764 full raw files
remained unchanged. full_verification.json retains this proof. All 867 earlier
artifacts and 671 smoke/calibration artifacts also remained unchanged. Final
read-only validation checks current code against retained summaries/manifests.

### Environment, limits and completion

Recorded full-launch environment: Linux 6.18.7-76061807-generic x86_64;
Intel Core i5-11400H, 12 logical CPUs; RAM 16,475,164,672 bytes,
available 3,908,259,840 bytes; disk free 134,313,807,872 bytes.
GNU C++13.3.0, CMake3.28.3, Python3.12.3, Release -O3 -DNDEBUG;
Matplotlib3.11.0, NumPy1.26.4, Agg/DejaVu Sans. Actual compile commands,
source/executable/tool/font hashes and environment/resource snapshots are retained.
Exposed cgroup memory.max=max; affinity CPUs0..11; governors powersave;
load average 1.1245/1.4868/1.4043. These are observations, not controls. No frequency,
cache, affinity, thermal or background-load control was imposed; thermal state
was not measured. Results describe this shared-machine session. No statistical
significance, universal ranking or independent-session replication is claimed.

This milestone delivers both the validated end-to-end pipeline and completed full
CPU timing study. Final review evidence is FINAL_AUDIT.md and final_review.json;
all intended changes are saved and no required test/integrity check remains open.
Limitations: no resume, Linux-specific orchestrator resource/signal policy, byte
identity tied to plotting stack, unavailable comparison/memory study figures,
uncalibrated individual-query latency and uncontrolled shared-session confounders.
No CUDA or 100M experiment was attempted. Exact next implementation milestone:
Phase 6 OpenMP parallel sorting, thread-count controls and differential validation,
then a separately frozen scaling/speedup/efficiency experiment.

Final review command initially exited 1 because the review helper reconstructed
the report from a JSON-loaded plot manifest whose sorted PDF/SVG keys differ from
the SVG/PDF insertion order used by figure generation. This was a verification
helper error, not a raw-data or production-regeneration failure. The helper now
restores the generator's explicit format order before comparing report bytes;
final_review_initial.py and commands/final_review.json retain the failure. The
corrected final_review_corrected command and final_review.json retain its result.

A second helper invocation exited 1 after the substantive data/report/hash checks
passed: it used the full verification field name when reading the smoke evidence
(the smoke field is all_derived_regenerated_byte_identical). This schema-reference
error was corrected; final_review_second.py and final_review_corrected command
record preserve it. final_review_complete is the final corrected invocation.
Neither helper failure modified an experiment or required a production-code change.
