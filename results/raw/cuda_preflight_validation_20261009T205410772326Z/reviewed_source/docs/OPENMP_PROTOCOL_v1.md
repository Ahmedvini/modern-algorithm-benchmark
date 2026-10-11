# Phase 6: parallel_merge_sort_v1 and parallel_sort_timing_v1

Frozen before the parallel implementation. This adds a separate configurable
sorting family; sort_timing_v1 and all Phase 5 presets/results remain unchanged.

## Algorithm and public contract

Signed int32 Values, ascending, stable (left wins equal keys), deterministic full
output. Public parallel_merge_sort(values, requested_threads) returns the actual
OpenMP team size and whether a parallel region was entered. Requests are integers
in [1,64]; invalid requests and invocation inside an existing OpenMP region throw
invalid_argument before mutation. Empty/singleton input returns actual_threads=1.
The old bottom-up merge_sort and six-entry sorting registry/default are preserved.
A separate configurable registry has merge_sort and parallel_merge_sort.

One N-key buffer is allocated per nontrivial call before task creation. Allocation
failure propagates before mutation; no allocations or throwing operations occur
inside task bodies. The comparator and optional internal test observer must be
nothrow and copied by value; keys are never arithmetically transformed. OpenMP
runtime allocation/creation failure is runtime-defined, not converted to a C++
exception or claimed recoverable. No allocation-failure injection is promised.

For requested=1 or N<32768, perform stable serial merging using that workspace;
actual_threads=1 and parallel_region=false. Otherwise enter exactly one parallel
region with num_threads(requested); a single thread records omp_get_num_threads
and starts sorting. Lengths >16384 split at begin+(end-begin)/2, create two tied
child tasks, then taskwait before merging into the same-range workspace and
copying back. Leaves use allocation-free serial bottom-up merges. Child ranges
and their buffers are disjoint; parents access them only after taskwait. The
parallel-region final barrier completes all work. Merges themselves are serial
within each node, so this is not a linear-scaling or parallel-merge claim.

Expected work O(N log N), auxiliary O(N), bounded O(log N) range recursion plus
OpenMP runtime task/team memory (not measured). Default tasks cannot throw.
No global mutable state, counter, omp_set_num_threads or omp_set_dynamic call.
Independent external calls own their buffers; nested OpenMP calls are rejected.
Team size is observable, not evidence every team member executed a task. Test-only
observers track tasks, merge boundaries and worker IDs; primary timing has no
such counters. Public stability follows merge ordering; a projected-int32
internal fixture makes equal-key identity observable without a generic public API.

## Benchmark and compatibility

parallel_sort_benchmark defaults to merge_sort, N1000, seed1729, uniform,
threads=1,W1,R5,memory_limit_mib=256. --sort accepts merge_sort,parallel_merge_sort
or all; --threads [1,64] configures the parallel entry only. Existing dataset,
list/help, numeric validation, build guard, exclusive output and failure behavior
follow sort_benchmark. The same shared timing loop restores inputs outside timing,
uses steady_clock integer ns, checks full std::sort output outside timing, retains
warmups and cyclic seed/trial algorithm ordering. Buffer allocation, team creation,
tasks, joins and deallocation are inside the sorting interval; dataset generation,
copying, metadata and verification are excluded. Normal counters/RSS are absent.

Raw schema is sort_timing_v1's 28 fields with protocol=parallel_sort_timing_v1,
plus implementation_version,requested_threads,actual_threads,parallel_region.
The sequential entry reports requested/actual=1/1; run.json records configured
parallel_threads separately. Actual team size is measured each invocation; below
threshold/request1 reports serial1 even when configured request>1. Runtime may
contract teams: record it, never silently substitute the request. Strict analysis
separates actual-team identities; full study requires actual=request above threshold.

run.json retains compiler/build/platform, source/dataset/executable identities,
OpenMP _OPENMP and CMake OpenMP version/flags/libraries, clock and invocation.
Matrix environment retains CPU/OS/RAM/limits/governor/load, relevant OMP variables,
ldd runtime paths and SHA256 hashes (runtime version unavailable unless recorded).
No guessed runtime version. CMake MAB_ENABLE_OPENMP enables only separate targets;
OFF leaves previous targets/tests available. No vendored source modification.

## Correctness and concurrency gates

Differential public/configurable registry/serial/std::sort tests: empty/singleton,
extrema/equal/negative, exhaustive small arrays, five distributions, fixed seeds,
boundaries around16384/32768 and larger ranges; requests1/2/4/8 and repeated calls.
Assert tasks/merges through internal test-only observers, check range bounds and
projected stability. Stress independent simultaneous invocations and repeated
runtime scheduling; these tests do not prove absence of data races.
Attempt ThreadSanitizer with the available toolchain/runtime and retain diagnostics.
If unsupported, record the exact failure and use disjoint-range/synchronization
review, concurrent-call/observer tests and ASan/UBSan as complementary checks;
never call ordinary tests a race-detector pass.

Before study: fresh full Release and sanitizer tests, Python tests, every-thread
smoke, byte-identical summary/figure regeneration and all prior-artifact hashes.
Leak detection disabled only on the documented ptrace failure. No large run until
these pass. Record any failure, missing configuration or interruption; never COMPLETE
on partial output. Exclusive outputs and new IDs; no overwrite or resume.

## Scaling design and statistical units

Candidate full matrix (freeze a separate launch protocol after smoke resource
planning): N32768/100000/1000000, all five distributions, seeds1729/42/2718,
threads1/2/4/8,W1,R5,cardinality16,default swaps. 180 configurations (45 datasets
x4 requests), two algorithms:1800 measured/360 warmup rows. Maximum N1M.
Smoke: N0/32767/32768/65537,uniform/duplicate_heavy,seed1729,all four requests,W1,R5:
32 configurations,320 measured/64 warmup rows. No smoke leaderboard claim.

Run serially in size,seed,distribution,thread order; preserve cyclic algorithm
order in each child. Set OMP_DYNAMIC=FALSE,OMP_THREAD_LIMIT=8,OMP_MAX_ACTIVE_LEVELS=1
for declared studies, record remaining affinity/scheduling policy. Do not silently
alter application global settings. Requested threads1/2/4/8 are subject to preflight
team probes and available CPU affinity. Warn in report about unbalanced odd-R
cyclic positions, warmed copies, serial merge span and fixed configuration order.

Per dataset/configuration/algorithm: successful/failed/missing/warmup counts,
median/mean/sample SD(ddof1)/min/max ns, retain every outlier. Primary algorithmic
speedup=median(sequential merge_sort in the same cell)/median(parallel at p).
Efficiency=speedup/actual p, reported only above threshold with actual=request.
Separately implementation speedup=median(parallel request1 for same dataset)/
median(parallel requestp); do not call these the same baseline. Per-dataset ratios
are computed before equal-weight cross-dataset aggregation; collapse identical
input fingerprints. Report medians/means/sample SD/min/max of dataset ratios,
not ratios of pooled trial means or independent-trial confidence intervals.
No significance test or universal speed/linear scaling claim.

Resource forecast from validated smoke: overhead-inclusive wall durations scaled
by N*log2(N+1), same configuration/round counts, conservative allowance; record
model and uncertainty. Memory max16*N (array planning) plus runtime/analysis
allowance; >=512MiB available memory and>=128MiB free disk and accessible cgroup
headroom, stronger gates if estimates require it. These are estimates, not RSS or
hard caps. Record compiler/runtime/flags/hardware/power/load; no cache, thermal,
frequency or exclusive-background-control claim without evidence. A full launch
requires its own frozen protocol and justified forecast; no CUDA/learned/100M work.
