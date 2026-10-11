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
| 7 — CUDA | Correctness, prepared timing smoke and isolated controlled CPU/GPU driver/pilot validated on T4; full comparative study remains pending separate review/authorization |
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
[Gate audit](../results/raw/gpu_cloud_gate1_20261009T211734154323Z/FINAL_AUDIT.md) and
[local preflight](../results/raw/gpu_cloud_gate1_20261009T211734154323Z/local_preflight/report.json) retain evidence.
Next GPU step: allocate and connect a supported NVIDIA cloud development runtime,
verify the archive and run the existing guide/preflight there. Require actual
enumeration and checked kernel before Gate 2. This follow-up remains blocked;
original roadmap Phase 8 learned-index/AlphaDev retains its pending status.

## Post-cloud validation: first CUB correctness slice

The retained archive at ../results/evidence/cloud_validation_evidence.tar.gz
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

Follow [the correctness contract](CUDA_SORT_PROTOCOL_v1.md) and
[the cloud validation handoff](CUDA_SORT_VALIDATION_GUIDE_v1.md).
Next milestone: compile/run this exact source on the validated cloud GPU, retain
and review the new sorter evidence, then define separate GPU timing methodology.
Original learned-index/AlphaDev, scaling and final research phases remain pending.

Final local CPU regression:26/26 Release and26/26 ASan/UBSan, leaks enabled;11 handoff methods pass. New GPU sorting remains uncompiled/unexecuted. Evidence: results/raw/cub_sort_validation_20261009T220322089788Z/FINAL_AUDIT.md.

Latest CUB handoff revision2: dangling-symlink safety fixed;12 host methods and26/26 Release/ASan/UBSan groups pass, leaks enabled. GPU sorting still uncompiled/unexecuted. Use [v2 guide](CUDA_SORT_VALIDATION_GUIDE_v2.md), cub_sort_source_v2.tar.gz and evidence at results/raw/cub_sort_final_review_20261009T222209607981Z/FINAL_AUDIT.md. Earlier candidate archive remains unchanged.

## Colab CUB correctness execution — current status

The existing T4 session executed the actual CUB sorter under
[correctness protocol v2](CUDA_SORT_PROTOCOL_v2.md): configure/build/direct test/
CTest all exit0,475 input cases and1900 output checks per execution,1/1 CTest
passed with no skip. CUB3.0.1 is pinned to reviewed CCCL commit
f19d875da0d8bfb2e38c109b2b40522b8abbbbc3; the original3.0.0 mismatch attempt remains
preserved. No algorithm behavior, CPU defaults or historical protocol changed.

Fresh Release26/26 and ASan/UBSan26/26 passed, leak detection enabled. All8,825
prior result files and16 protected source/protocol/license files remain unchanged.
Downloaded evidence/archive hashes,100 generated-line-directive build warnings,
CLI connection interruption/recovery and exact commands are retained in
[results/raw/cub_correctness_colab_20261009T223853955936Z/FINAL_AUDIT.md](../results/raw/cub_correctness_colab_20261009T223853955936Z/FINAL_AUDIT.md).

Correctness is complete; the entire CUDA phase is **not complete**. Exact next
milestone: freeze GPU timing protocol defining checked synchronization, reusable
buffers/allocation scope, H2D/device/D2H CUDA-event timing and monotonic host
end-to-end timing, then implement/test an isolated benchmark and run a small smoke
matrix. GPU timing/full study, learned-index/AlphaDev,100M and final research
deliverables remain pending. No performance conclusion follows from correctness.


## Prepared GPU timing milestone — implementation under validation

New `cuda_sort_timing_v1` contract is frozen in CUDA_TIMING_PROTOCOL_v1.md.
Benchmark-only prepared CUB session, four timing fields, strict CSV summaries,
exclusive sequential matrix and staged cloud validation are implemented; actual
GPU build/execution and final integrity audit are still required before acceptance.
The reviewed CUB3.0.1 pin, production adapter and CPU protocols/defaults remain
unchanged. This is the separate smoke performance milestone, not a full GPU study.


## Prepared CUB timing milestone validated

[Timing protocol v1](CUDA_TIMING_PROTOCOL_v1.md) and `cuda_sort_benchmark` now
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

[Raw evidence/audit](../results/raw/cuda_timing_20261009T231303050084Z/FINAL_AUDIT.md),
[processed report](../results/processed/cuda_timing_20261009T231303050084Z/REPORT.md),
and [matrix statistics](../results/processed/cuda_timing_20261009T231303050084Z/matrix.json)
retain every observation, exact commands, hashes and per-dataset median/mean/sample
SD/min/max. Summary regeneration passes in both environments; local/cloud statistic
groups match, with relocated absolute provenance paths. All9,568 earlier result
files remain unchanged. Clock/thermal/background controls are unverified; post-run
probes are not timing controls. See audit for resource/timing limitations.

Exact next CUDA milestone: a separately frozen <=1M controlled CPU/GPU comparison
study, with matched/explicit timing scopes and resource estimates. No full GPU
study or100M run has completed. Learned-index/AlphaDev and final research phases
remain pending. Earlier pending entries are historical, superseded by this audit.

## Controlled CPU/GPU comparison protocol frozen for review

[Protocol v1](CPU_GPU_COMPARISON_PROTOCOL_v1.md),
[matrix](studies/cpu_gpu_comparison_v1.matrix.json),
[resource table](studies/cpu_gpu_comparison_v1.resources.csv) and
[freeze manifest](studies/cpu_gpu_comparison_v1.freeze.json) now specify 48 datasets
at 1025/65537/1000000 elements, five modes, 1200 measured calls and 240 warm-ups.
The separately planned pilot has six datasets, 150 measured calls and 30 warm-ups.
No pilot or study was executed. Primary CPU/GPU comparisons require matched
allocation-inclusive host-vector API calls on the same cloud host; the prepared
four-metric path remains diagnostic only.

The protocol passed 14 static validation methods and byte-for-byte asset
regeneration. Reused Release binaries passed three relevant CTest groups; fresh
full builds/sanitizers/GPU execution were not needed for these documentation-only
changes. All 10755 previous result files were verified before editing; the final
[planning audit](../results/raw/cpu_gpu_protocol_20261009T234954580281Z/FINAL_AUDIT.md)
records the final integrity result. The pin and production adapter are unchanged.

Exact next step: review this freeze, then implement the isolated five-mode driver,
host-call schema/paired analyzer and dual-workspace resource query; validate them
and run the six-dataset pilot before considering the main study. N1M CUB workspace
requirements, current cloud readiness and full-call performance remain unknown.
This is a completed protocol deliverable, not a completed comparative experiment.


## Controlled CPU/GPU driver and six-dataset pilot — validated

The isolated five-mode driver, independent paired analyzer and dual-workspace
query are implemented under unchanged cpu_gpu_comparison_v1. Existing production
sorters, CUB3.0.1 pin, timing families and frozen protocol/matrix/resources remain
unchanged; only reviewed additive CMake integration extends protected sources.
The pilot-only validator has no full-study/resume option, rejects collisions and
requires fresh kernel/build/correctness prerequisites before timing.

Fresh local CPU Release29/29 and ASan/UBSan29/29 pass; cloud CPU Release29/29,
ASan/UBSan29/29 and GPU-enabled Release32/32 pass. Leak detection stayed enabled.
The new engine covers60 inputs/3600 trial checks;22 framework methods pass.
Actual T4 CUB correctness475 inputs/1900 checks passes directly and through CTest.
The final pilot completed exactly150 measured +30 warm-up calls across the frozen
six datasets, with zero failed/interrupted/missing/duplicate records. Two cloud
and two local summaries match byte-for-byte;48 metric groups/18 permitted host-call
ratios were independently checked. Prepared timings remain diagnostic-only.

Both N1M isolated workspace queries and successful cudaMalloc request sizes are
4,178,687 bytes; N1025 reports1 byte. These are not instrumented production calls
or allocator-rounded measurements. Frozen estimates are not updated. CPU builds
have zero warnings; CUDA retains341 nvcc-generated GCC line-directive extension
warnings, with no other category or suppression. Earlier failed/expired attempts
remain explicit; the expired attempt's final outcome is unverified and excluded.
All10,791 previous result artifacts and protected source/protocol/pin hashes match.

[Implementation guide](CPU_GPU_COMPARISON_DRIVER_v1.md),
[pilot report](../results/processed/cpu_gpu_pilot_20261010T001232473460Z/REPORT.md),
[audit](../results/raw/cpu_gpu_pilot_20261010T001232473460Z/FINAL_AUDIT.md) and
[independent verification](../results/raw/cpu_gpu_pilot_20261010T001232473460Z/INDEPENDENT_VERIFICATION.json)
retain commands, raw data, statistics and limitations.

Exact next step: review the accepted pilot and observed resources, then separately
authorize the frozen48-dataset/1200-measurement comparative study. Its N65537
workspace queries must be fresh; a dataset-count-only runtime proxy is about59s
plus fresh prerequisites, not a measured prediction. CPU SMT, cloud background,
frequency/thermal/cache state and one seed per pilot workload limit interpretation.
No full comparative study,100M run, ranking or statistical significance is claimed.
Learned-index/AlphaDev, gradual scaling and final research deliverables stay pending.

## Fresh N=65537 CUDA resource gate — passed

New Colab T4 session, unchanged reviewed source/CUB3.0.1 and fresh Release diagnostic
build: prepared/private-stream and production-parameter/default-stream queries
both require279295 bytes; both diagnostic cudaMalloc requests and checked cleanup
succeed. Calculated combined device payload1607182 bytes satisfies unchanged
64MiB/workspace,256MiB combined and half-free-device limits; host/disk1GiB gates
also pass. These are logical requests/payload formulas, not physical allocations
or instrumented production calls. No sorting, pilot, full study or fresh CTest run.

Resource feasibility: **GO**. Full-study launch: **NO-GO now**, pending separate
authorization, a reviewed/tested full-matrix runner/analyzer extension (current
tools enforce pilot-only coverage), and fresh study prerequisites/all-size gates
on the actual execution VM. Keep the frozen matrix/protocol unchanged. The pilot's
single input per workload, repeated-timing variability, one SMT core/two logical
CPUs and uncontrolled cloud conditions limit inference. Evidence and exact next
step: [resource audit](../results/raw/cub_workspace_65537_20261010T110457531249Z/FINAL_AUDIT.md).

## Full CPU/GPU matrix tooling — implemented and validated without study execution

The separate study runner consumes all48 frozen cells/five modes, stored ordering,
W1/R5 and unchanged resource/time limits. Pilot behavior remains separately
selectable; no resume/overwrite. New prerequisite-only validation avoids automatically
launching a pilot. Analysis validates full coverage, three-size resources, identities,
actual teams, timing scopes, prerequisite/build provenance and sealed raw hashes;
incomplete studies cannot produce paired/cross-input comparisons. No production
algorithm, CMake anchor, CUB pin or frozen input was changed.

Fresh selected non-timing CPU Release19/19 and ASan/UBSan19/19 groups passed, leaks
enabled; final framework50/50 methods passed with both input binaries. Fresh T4
GPU-enabled Release21/21 selected groups passed, framework50/50, actual CUB475
inputs/1900 checks and runtime smoke. Timing groups were excluded. An initial
correctness selection inadvertently ran parallel_mergesort's embedded6 CPU timing
rows (4 measured/2 warm-ups atN32768); the deviation is retained, and that group
was excluded thereafter. No pilot, full comparison or GPU benchmark ran.

Legacy pilot summary regenerated byte-for-byte; all11228 prior result files,
protected source/pin and four frozen hashes remain unchanged. New tests use
explicit synthetic records/subprocess doubles, never fabricated observations.
[Tooling guide](CPU_GPU_FULL_MATRIX_TOOLING_v1.md) and
[final audit](../results/raw/cpu_gpu_full_tooling_20261010T121208603276Z/FINAL_AUDIT.md)
record commands, omissions, known warnings and limits.

Full-study launch remains **NO-GO** pending review, separate authorization and fresh
complete frozen prerequisites/all-size gates on the execution VM. Exact next step:
review this tooling and its validation/deviation, then authorize prerequisite-only
validation and the unchanged48-dataset study separately. No main study,100M,
learned-index/AlphaDev or final research deliverable is claimed complete.

## CPU/GPU validation safety repair — synthetic validation passed

Independent frozen-anchor enforcement now rejects the exact mutually rehashed
adapter-digest reproducer. The unchanged synthetic baseline and legacy accepted
pilot remain analyzable. A reviewed source/command manifest supplies a reusable
non-timing selector: 19 CPU correctness groups, excluding all ten timing groups
and the embedded N32768 parallel-mergesort timing case. Unknown sources, tests,
commands and implicit fixture/dependency execution fail closed.

Repair validation: 22 focused provenance/selector methods and all 50 existing
synthetic framework methods pass; no CTest group, prerequisite validator, timing
trial or GPU execution ran. Prerequisite-only manifests are now explicitly
correctness-only and cannot authorize the unchanged frozen full-study gate.
See [repair audit](../results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/FINAL_AUDIT.md)
and [selection contract](CPU_GPU_SAFETY_REPAIR_v1.md).

Full-study launch remains **NO-GO**. Next: independently review this repair, then
separately authorize fresh validation on the execution VM. Full frozen coverage
(including timing-framework tests) and all-size resource gates remain required
before separate study authorization. No fresh prerequisite validation was run.

## CTest pre-discovery hook repair — awaiting independent review

The shared selector now verifies reviewed flat build metadata before discovery
and rechecks its fingerprint before execution. Hooks, includes, subdirectories,
unknown commands/properties and unreadable metadata fail closed. The approved
19 CPU names remain unchanged. This is a source repair with inert fixture
validation, not fresh native/prerequisite/GPU validation.

See [guard contract](CTEST_BUILD_GUARD_v1.md) and
[repair audit](../results/raw/ctest_hook_repair_20261010T223851377458Z/FINAL_AUDIT.md).
Exact next action: independent review of this implementation and evidence.
Study launch remains **NO-GO**. No prerequisites or resource checks are authorized
by this repair. Historical protocols, production adapters and CUB pin are unchanged.

## CTest guarded path identity — repaired, awaiting independent review

The independent guard review found that a relative discovery argument could refer
to a different tree under the callback's cwd. The helper, CLI and direct selector
now retain the exact absolute identity returned by static validation throughout
discovery, rechecks and execution command construction. Aliases remain rejected.

Eight new inert regressions reproduce the old defect and pass after repair; all39
existing inert guard/selector regressions also pass (47 total). No CTest discovery,
native test, build, prerequisite/resource check, benchmark or GPU work ran. The
approved19 CPU plan, frozen inputs, production adapters and CUB3.0.1 remain unchanged.
See [repair audit](../results/raw/ctest_path_repair_20261010T234224414430Z/FINAL_AUDIT.md).
Exact next gate: separate independent review only. Study launch remains **NO-GO**.
