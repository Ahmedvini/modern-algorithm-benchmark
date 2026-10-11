## Phase 6 — OpenMP implementation and completed scaling study (2026-10-09)

Workspace writable; no Git metadata (git status128), no repository initialized.
Inspected AGENTS.md completely, README, roadmap/audit/algorithm/benchmark/protocol/
metrics docs, existing core/registry/CLI/CMake/tests and Phase5 tooling before edits.
Baseline fresh Release configure/build/CTest exited0,22/22 groups passed17.54s.
The starting106 project-file hashes/backups and3,796 previous artifact hashes are
retained in `results/raw/openmp_validation_20261009T200852928292Z/repository_before.json`, `prior_artifacts_sha256.json`
and `build/openmp_review_20261009T200852928292Z`. All earlier raw/processed/figures and historical protocols,
including frozen1M sorting and Phase5 full study, remain unchanged.

Contract `results/raw/openmp_validation_20261009T200852928292Z/PROTOCOL_v1.md` and docs/OPENMP_PROTOCOL_v1.md were frozen
before implementation. Stable signed-int32 parallel Merge Sort uses one N-key
buffer allocated before mutation, task splits above16384, taskwait before parent
merge/copyback and a final team barrier. Requests1..64, serial for request1 or
N<32768; invalid or nested requests reject before mutation. Parent merges are
serial; O(NlogN) work/O(N) keys plus runtime/task/stack overhead. Task bodies
cannot throw/allocate; OpenMP runtime failure is runtime-defined. No fault-injection
claim. Empty/singleton safe, no arithmetic transformation of keys.

Separate configurable registry/executable preserves the old6-entry registry,
std_sort default and sequential merge_sort. The old timing loop is factored into
one shared template; copy/reference validation remain outside steady_clock ns.
Allocation, team creation, tasks/joins and deallocation are timed. New32-column
parallel_sort_timing_v1 appends version/request/actual-team/region fields; original
sort_timing_v1 CSV remains28 columns. Requested team is not busy-worker count.
Normal timing has no test observer/counting/RSS. Benchmark metadata retains
source/executable/tool/library hashes, compile commands, OpenMP flags/runtime paths
and environment. No guessed libgomp version.

Files added: include/algorithms/parallel_mergesort.hpp,
include/algorithms/detail/parallel_mergesort_impl.hpp,
src/algorithms/parallel_mergesort.cpp, include/benchmark/detail/timing_impl.hpp,
include/benchmark/parallel_timing.hpp, src/benchmark/parallel_timing.cpp,
src/benchmark/parallel_main.cpp, scripts/run_parallel_matrix.py,
scripts/analyze_parallel_results.py, tests/test_parallel_mergesort.cpp,
tests/test_parallel_benchmark.py, docs/OPENMP_PROTOCOL_v1.md and both frozen
OpenMP study launch documents in docs/studies/. Existing changes: CMakeLists.txt,
include/benchmark/timing.hpp, src/benchmark/timing.cpp, README.md and docs/
ALGORITHMS.md, BENCHMARKING.md, EXPERIMENT_PROTOCOL.md, METRICS.md, ROADMAP.md,
AUDIT.md. No vendor, generator, old algorithm/registry or old test/Python file
changes. Full final inventory and review patch are retained with this audit.

Final commands (all exit0, stdout/stderr/argv/status retained in commands/):
```sh
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_SANITIZERS=OFF -DMAB_ENABLE_OPENMP=ON
cmake --build build/release --parallel 2
ctest --test-dir build/release --output-on-failure -V
cmake -S . -B build/sanitize -DCMAKE_BUILD_TYPE=Debug -DMAB_ENABLE_SANITIZERS=ON -DMAB_ENABLE_OPENMP=ON
cmake --build build/sanitize --parallel 2
env -u ASAN_OPTIONS -u LSAN_OPTIONS UBSAN_OPTIONS=halt_on_error=1 ctest --test-dir build/sanitize --output-on-failure -V
python3 tests/test_parallel_benchmark.py build/release/parallel_sort_benchmark
```
Final corrected Release24/24 passed30.09s, ASan/UBSan24/24 passed84.51s;
13 parallel Python tests passed standalone and within each suite, including all
five distributions/zero sorted swaps. Existing Phase5 Python23 methods still pass.
No compiler warnings in fresh build logs. Leak detection enabled; no ptrace failure
or leak-disabled retry occurred. Earlier reviewed suites24/24 also passed before
the metadata correction; they are retained separately, not the final evidence.
C++ parallel tests:523 inputs,4,184 public/registry output checks at1/2/4/8threads,
ten concurrent131073-element calls; eight observed tasks and65,549 merges in
stable projected-key fixture, bounds/threshold/serialized-nesting and6 timing rows.
Exact equality to std::sort/sequential results verifies order and permutation;
stability uses projected-key identity. OpenMP-enabled team probe1:1,2:2,4:4,8:8.
OpenMP-OFF configure/build sort_benchmark/list-sorts all exited0 and retained
originalsix names; no full OFF CTest is claimed.

Concurrency limitation: TSan compilation succeeded, but both the parallel test
and independent std::thread probe exited66 before tests with `FATAL:
ThreadSanitizer: unexpected memory mapping`. This is an environment startup
failure, not evidence of an OpenMP-specific conflict or race-free execution.
Valgrind unavailable. No access-control/ASLR workaround attempted. Disjoint ranges,
barriers, atomic internal observers, concurrent-call stress and ASan/UBSan are
complementary validation, not a race-detector pass. Exact commands/diagnostics:
commands/tsan_compile.json, tsan_run.json, tsan_standalone_compile.json,
tsan_standalone_run.json.

Failures retained: initial recorder setup exited1 because commands/ did not yet
exist; its baseline child was never launched (initial_recorder_failure.json).
Initial Python fixtures emitted unclosed-file ResourceWarnings, corrected with
StringIO before final tests; no final warning. First full study command exited1:
`matrix/bundle configuration differs`. All180 child processes actually exited0
with1,800 correct measured/360 warmup rows, but analyzer incorrectly required
floor(N/100) swaps for already-sorted input, which correctly records0. This was
an analysis defect; corrected without changing datasets/timing code. The original
attempt `openmp_scaling_20261009T200852928292Z` remains FAILED, no COMPLETE or derived-success claim.
Its1,806 files are hash-protected, diagnosis in failed_attempt_diagnosis.json.
An all-five-distribution regression and fresh Release/sanitizer suites preceded
exclusive new smoke/full retry paths. No attempt pooling, overwrite or resume.
Exploratory read of nonexistent case_0004/run.json exited1 (actual name run_000004);
it did not affect execution or evidence.

Corrected smoke commands (all exit0):
```sh
python3 scripts/run_parallel_matrix.py --preset smoke --output results/raw/openmp_smoke_20261009T200852928292Z_retry1 --processed results/processed/openmp_smoke_20261009T200852928292Z_retry1 --figures results/figures/openmp_smoke_20261009T200852928292Z_retry1 --dry-run
python3 scripts/run_parallel_matrix.py --preset smoke --output results/raw/openmp_smoke_20261009T200852928292Z_retry1 --processed results/processed/openmp_smoke_20261009T200852928292Z_retry1 --figures results/figures/openmp_smoke_20261009T200852928292Z_retry1
python3 -B results/raw/openmp_validation_20261009T200852928292Z/verify_run.py smoke
```
Smoke32 configurations,N0/32767/32768/65537,uniform/duplicate_heavy,seed1729,
threads1/2/4/8,W1/R5:320 measured and64 warmup successes, zero failed/missing.
Eight figure pairs/report/summary bytes regenerated; all329 raw files unchanged.
All-distribution N100 validation additionally passes within the13-method suite.

Full retry launch frozen before execution at
`docs/studies/openmp_scaling_20261009T200852928292Z_retry1_v2.md` and RETRY_FULL_STUDY_LAUNCH_v2.md.
Original v1 remains immutable; v2 clarifies sorted swaps0 and records retry reason,
new paths, hashes/resources. No matrix change. Corrected smoke forecast199.616s
child wall (Nlog2(N+2) ratio×4), below1800s budget, plotting separate. Memory estimate
150,217,728 bytes, required available536,870,912 bytes; disk allowance419,889,152,
required free839,778,304. Actual prelaunch availableRAM6,755,241,984 and disk free
134,562,123,776 bytes. These are planning/snapshot values, not isolated memory.

Full commands (all exit0):
```sh
python3 scripts/run_parallel_matrix.py --preset full --output results/raw/openmp_scaling_20261009T200852928292Z_retry1 --processed results/processed/openmp_scaling_20261009T200852928292Z_retry1 --figures results/figures/openmp_scaling_20261009T200852928292Z_retry1 --dry-run
python3 scripts/run_parallel_matrix.py --preset full --output results/raw/openmp_scaling_20261009T200852928292Z_retry1 --processed results/processed/openmp_scaling_20261009T200852928292Z_retry1 --figures results/figures/openmp_scaling_20261009T200852928292Z_retry1
python3 -B results/raw/openmp_validation_20261009T200852928292Z/verify_run.py full
```
Full180 configurations:N32768/100000/1000000,5distributions,3seeds1729/42/2718,
threads1/2/4/8,two sorters,W1/R5,card16,sorted swaps0/defaultfloor(N/100)otherwise,
256MiB array budget. All1,800 measured/360warmup trials passed, failed/missing0;
all180 child commands and analysis exited0. Pipeline wall33.123s includes analysis.
Each input fingerprint agrees across thread configurations. Observed parallel
teams2/4/8 equal requests; request1 executes serial. Timing remains uninstrumented.
360 per-dataset algorithm groups,180 dataset ratios,60 cross-dataset groups;
20SVG/PDF figure pairs, report/summary/observations regenerated byte-for-byte.
All1,809 raw files unchanged through regeneration, all3,796 previous artifacts,
original smoke, failed attempt and frozen protocols unchanged.

Descriptive N1M,p8 results: median of three dataset-specific ratios, formed from
within-dataset five-trial medians. Efficiency divides primary ratio by actual8;
min/max is across dataset ratios, not a confidence interval. No significance claim.

| Distribution | Sequential-baseline speedup | Min–max | Efficiency | Separate parallel1 speedup |
|---|---:|---|---:|---:|
| duplicate_heavy | 3.568831 | 3.468465–3.826871 | 0.446104 | 3.893432 |
| nearly_sorted | 3.079466 | 2.492053–3.328528 | 0.384933 | 3.777703 |
| reverse_sorted | 2.603176 | 2.111693–2.929176 | 0.325397 | 4.384512 |
| sorted | 2.501757 | 2.457263–2.671667 | 0.312720 | 3.594457 |
| uniform | 3.045514 | 3.042874–3.512856 | 0.380689 | 3.355280 |

Environment: Linux6.18.7-76061807-generic x86_64/glibc2.39, Intel i5-11400H,
6physical/12logical CPUs, affinity0..11; totalRAM16,475,164,672bytes; GNU13.3.0,
CMake3.28.3,Python3.12.3,Matplotlib3.11.0. Release-O3-DNDEBUG for both algorithms,
parallel translation units additionally-fopenmp; CMake OpenMP4.5/_OPENMP201511,
actual libgomp linkage/hashes retained. Exposed cgroup memory.max=max; governors
performance at retry preflight, load3.3564/2.5723/1.9731. These are observations,
not controls; no affinity/frequency/cache/thermal/background changes imposed.
Thermal state not measured;12logical CPUs are not12physical cores.
OMP_DYNAMIC=FALSE,THREAD_LIMIT=8,MAX_ACTIVE_LEVELS=1,WAIT_POLICY=PASSIVE recorded.

Raw `results/raw/openmp_scaling_20261009T200852928292Z_retry1`, processed `results/processed/openmp_scaling_20261009T200852928292Z_retry1` and figures
`results/figures/openmp_scaling_20261009T200852928292Z_retry1` retain matrix, environments/source/compile/runtime
identities, every row/outlier, statistics, report and machine-readable plot manifest.
`results/raw/openmp_validation_20261009T200852928292Z/full_retry_verification.json` supports completion/regeneration;
smoke_retry_verification.json supports smoke. execution_tools and retry_execution_tools
archive exact pre/post-correction Python tools. COMMANDS.md/commands/ retain exact
argv, exit status, stdout/stderr, including prior failures. final_review.json,
FINAL_AUDIT.md, file_changes.json, source_after.json and changes.patch support
saved-file/integrity review. Regenerate into NEW paths with analyze_parallel_results.py;
raw files are immutable, no retries/resumption in-place.

Phase6 delivers validated OpenMP implementation **and completed scaling study**.
Limitations: TSan unavailable as above; serial parent merges and different serial
merge strategies between sequential baseline and parallel-request1; team count
not busy-worker count; one shared session with fixed matrix order/odd-R cyclic
imbalance and uncontrolled frequency/cache/thermal/load. Ratios aggregate datasets,
not independent repetitions. No isolated RSS, comparison-count experiment,
independent-session replication, statistical significance or linear/universal
scaling claim. No CUDA, learned-index/AlphaDev or100M experiment was attempted.
Next roadmap milestone: Phase7 CUDA device/runtime preflight and reproducible CUB
Colab/cloud guide with separate transfer/kernel/end-to-end semantics; do not claim
GPU results until actual verified execution. Other deferred research remains listed
in ROADMAP.md.
