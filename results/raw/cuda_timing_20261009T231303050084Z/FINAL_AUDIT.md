# Final audit — prepared CUB GPU timing milestone

Status: **performance infrastructure/smoke milestone complete**. A full GPU/CPU
comparative study is **not run**. Correctness is separately revalidated and is not
used as a substitute for performance evidence. No commit/push/Git initialization,
local driver change, package installation, CUDA acceleration claim or100M run.

## Starting state and preserved work

Workspace writable, no Git metadata (`git status --short`128). Inspected AGENTS,
README, roadmap/protocol/metrics/benchmarking/CMake, adapter/registry/timing/tests,
and the preceding audit/CHANGES/COMMANDS/GPU completion evidence under
results/raw/cub_correctness_colab_20261009T223853955936Z. Existing CPU/default
semantics and reviewed CUB3.0.1 pin preserved. Source_before.json and private
before-copy establish the starting state; prior_artifacts_sha256.json records9568
existing raw/processed/figure/evidence files before this task.

Versioned docs/CUDA_TIMING_PROTOCOL_v1.md was saved before code/execution and its
hash still matches the cloud source. New prepared-session API is benchmark-only;
production cub_radix_sort_v1 keeps allocation-per-call/stream0 behavior. Separate
private nonblocking stream, pinned host input/output, device input/output and exact
CUB workspace are reused. CUB DeviceRadixSort::SortKeys over all32 signed-key bits,
no CPU fallback. Keys-only stability is not observable. Host5-array and device
2-array+workspace budgets are planning constraints, not isolated measured memory.

## Timing contract

| Column | Measurement | Unit |
| --- | --- | --- |
| h2d_ns | event0->1 around pinned-host to device async copy | ns |
| device_sort_ns | event1->2 around CUB GPU timeline work, possibly dispatch gaps | ns |
| d2h_ns | event2->3 around device to pinned-host output copy | ns |
| end_to_end_ns | host steady_clock before event0 record through checked event3 sync | ns |

Synchronize the private stream before timing, check every CUDA/CUB call/launch and
final event completion before reading output. Host end-to-end includes enqueue,
CUB dispatch, checks/wait, transfers and sort. It excludes context/stream/event/
buffer allocation, workspace query, prior sync, input staging, output-vector copy,
event elapsed queries, oracle/verification and I/O. This is prepared pipeline
latency, not allocation-inclusive production-adapter latency or isolated kernel
active time. Three event intervals need not sum to host time. Event API float ms
converted x1e6 to double ns; no ns resolution claim. Empty/singleton require real
device discovery but skip GPU work, record three zeros and time the trivial call.

## Actual environment and remote execution

The old configured Colab session had expired (sessions listed none). One
replacement session `mab-t4-20261009T231303050084Z` was requested and became READY.
Actual preflight checked device enumeration and a kernel, not only nvcc version.
Tesla T4, compute7.5, driver580.82.07, CUDA nvcc/toolkit13.0.88/runtime API13000,
GCC13.3.0, CMake3.31.10, Linux6.6.122+/x86_64/glibc2.39; Release -O3 -DNDEBUG,
sm75, OpenMP OFF for this isolated GPU build. See downloaded/raw/environment.json,
correctness/preflight/report.json, compile commands/cache and post_run_conditions.
CPU/RAM and discovery details are recorded rather than inferred.

Exact CUB3.0.1/CCCL revision f19d875da0d8bfb2e38c109b2b40522b8abbbbc3,
BSD-3-Clause. Original UPSTREAM.json/LICENSE and configure pin prefix unchanged.
Fresh installed dependency manifest retained at downloaded/raw/correctness/dependency_sha256.json.
Source/binary/compiler flags identities retained; final125 non-document source
files match the GPU-tested bundle. Documentation alone changed after execution.

Source bundle `cuda_timing_source_v1.tar.gz` SHA256
fa7c1d2fc131ba832a5c357498a6c1523c3eeeea99d6c7c4478df30d04ab0f73
matched both ends;147 source files checked before extraction/execution. Safe
extraction into a new directory; no old remote project overwritten. Retrieved
colab_gpu_timing_evidence.tar.gz SHA256
236b32018d74ac5be6252df130038eadcbc95169509107bd6d3e7ea323290c41 matched both ends;
1115 packaged files independently verified. Derived processed files were moved to
results/processed/cuda_timing_20261009T231303050084Z after extraction; archive is unchanged. download_verification.json and
verification.json record the mapping. Private CLI credential files stay in build,
not in source/evidence bundles. No manual user Colab step remains for this milestone.

## Commands and actual results

[COMMANDS_FINAL.md](COMMANDS_FINAL.md) lists exact argv/exit codes and links full
stdout/stderr records; it preserves initial diagnostics, all48 native matrix
commands, cloud correctness/preflight/configure/build/direct/CTest commands,
analysis/regeneration and CLI upload/execution/download. Main commands all exit0:

```bash
cmake -S . -B build/cuda_timing_20261009T231303050084Z/cpu-release -DCMAKE_BUILD_TYPE=Release -DMAB_ENABLE_CUDA=OFF -DMAB_ENABLE_CUDA_SORT=OFF
cmake --build build/cuda_timing_20261009T231303050084Z/cpu-release --parallel 2
ctest --test-dir build/cuda_timing_20261009T231303050084Z/cpu-release --output-on-failure -V
cmake -S . -B build/cuda_timing_20261009T231303050084Z/cpu-sanitize -DCMAKE_BUILD_TYPE=Debug -DMAB_ENABLE_SANITIZERS=ON -DMAB_ENABLE_CUDA=OFF -DMAB_ENABLE_CUDA_SORT=OFF
cmake --build build/cuda_timing_20261009T231303050084Z/cpu-sanitize --parallel 2
env -u ASAN_OPTIONS -u LSAN_OPTIONS UBSAN_OPTIONS=halt_on_error=1 ctest --test-dir build/cuda_timing_20261009T231303050084Z/cpu-sanitize --output-on-failure -V
python3 tests/test_cuda_benchmark.py
```

Fresh full Release27/27 and ASan/UBSan27/27 passed, zero failed/skipped CTest
groups. Leak detection enabled; no ptrace limitation recurred. Within the host
analysis group,12 methods pass and2 GPU methods explicitly skip without an
executable; actual cloud GPU framework passes all14, zero skips. Final Release
CTest was repeated after test additions; both final suites include all14 methods.
Local builds emit zero warnings. Full existing sorting/search/metrics/structure/
OpenMP regressions retained and pass. CPU sanitizers do not instrument CUDA code.

Executed remotely in the hash-verified clean checkout:

```bash
python3 scripts/validate_cuda_timing.py --output results/raw/NEW_GPU_TIMING --processed results/processed/NEW_GPU_TIMING
```

Exit0 in66.310s is runner duration, **not a sorting timing measurement**. Stages:
- Fresh minimal kernel/preflight: operational.
- Unchanged public CUB correctness:475 inputs/1900 full-vector checks, direct exit0;
  same suite repeated through cuda_sorting CTest1/1 pass, no skip.
- cuda_sort_benchmark build: exit0.
- Smallest: N1025/uniform/seed1729,W1/R5:5 measured+1 warmup, all correct.
- Actual GPU framework: targeted CTest1/1,14/14 Python methods.60 validation-only
  size/workload configurations (N0,1,2,31,32,33,1023,1024,1025,65537 across6 workloads),
  120 measured+60 warmup validation rows, excluded from primary performance samples.
- Primary matrix: N0,1,1025,65537 x uniform/sorted/reverse_sorted/duplicate_heavy/
  nearly_sorted/signed_edges x seeds1729,42, W1/R5.48 complete configurations,
  240 measured+48 warmups,0 failed/missing/skipped/unexecuted planned trials.
- Total primary smoke including smallest:245 measured+49 warmups.120 measured
  matrix trials are empty/singleton shortcuts;125 nontrivial measured GPU pipelines
  include the smallest. All results verified against std::sort outside timers.
- Strict schema/completion/nonnegative metric validation and summary regeneration:
  all exit0. All warmups/outliers retained, excluded only warmups from statistics.

Per-dataset summaries separately report median/mean/sample SD(ddof1)/min/max and
success/failure/missing counts for each metric. No pooling repeated timings into
independent dataset samples or unsupported confidence/significance claim. Signed
edges deliberately ignore seed and do not make two independent generated datasets.

[Processed report](../../processed/cuda_timing_20261009T231303050084Z/REPORT.md) includes every matrix
cell and an example in us: N65537/uniform/seed1729 five-trial medians H2D28.896,
device-sort63.904,D2H27.680,host end-to-end128.136. CSV/raw statistics retain ns;
these are descriptive smoke measurements, not CPU/GPU speedups.

## Evidence and integrity

- Raw: downloaded/raw/smallest/trials.csv; downloaded/raw/matrix/run_*/trials.csv.
- Full metadata/configurations/logs/cache/binary/source/dependency manifests:
  downloaded/raw; downloaded/transfer_verification.json and remote_execution.json.
- Strict summaries: results/processed/cuda_timing_20261009T231303050084Z/smallest.json and matrix.json,
  original/regenerated and two local regenerations for each; generated REPORT.md.
- [verification.json](verification.json): all980 measured metric values checked;
  all196 group/metric statistics independently recomputed with Python statistics.
  Remote summaries byte-regenerate; local summaries byte-regenerate; all local/
  remote groups/statistics match. Absolute source provenance differs after transfer.
- [changes.json](changes.json), [CHANGES.md](CHANGES.md), source_changes.patch:
 8 added/9 modified source/document files,0 deleted.131 protected starting files
  including CPU algorithms, production adapter, vendors/license and old protocols
  unchanged. The CMake pin prefix and new frozen protocol also match.
- All9568 prior artifact hashes pass both independent and final review;0 changed.
  No frozen study/report/plot/raw file was regenerated or overwritten.

## Warnings, failures and limitations

No actual build, correctness or benchmark failure. Recorded diagnostics:
- Git status128: no .git, so no branches/commits can be inspected.
- Expired previous session: availability blocker resolved with one replacement T4.
- Two local inventory-review helper assertions exit1: omitted existing .gitignore,
  then incorrect period/comma delimiter. Both preserved; corrected final_review_v2
  exit0 verified actual unchanged files/pin. No source change to satisfy helpers.
- Intentional unit-fixture exit9/timeouts/interruptions/collisions passed expected
  assertions; they are not actual GPU failures.
-100 production plus161 timing nvcc-generated GCC line-directive extension warnings
  under the existing -Wpedantic. All logs retained; no other warning category,
  CUB/compiler incompatibility fix, suppression or dependency-pin change.

CUDA Compute Sanitizer not run. No race-freedom inference from ordinary tests.
Frequency, cache/thermal conditions and background contention uncontrolled; only
post-run probes labelled as such. No clock-lock/governor changes. CUDA event
resolution/precision affects tiny intervals. Not allocation-inclusive adapter
latency, isolated memory or kernel active time; no CPU baseline timing collected
in this smoke. No full GPU study,100M experiment, statistical significance,
performance-superiority claim or final research deliverable completed here.

## Next milestone

Freeze a controlled <=1M GPU/CPU comparison protocol with explicit timing scopes,
identical seeded datasets, CPU std_sort/sequential Merge/OpenMP baselines as
supported, multiple seeds/repetitions and resource estimates. Keep prepared GPU
transfer-inclusive and device-only intervals clearly separated; add a separately
labelled allocation-inclusive GPU measurement only if required by the comparison.
Do not compare device-only latency with CPU end-to-end without explicit scope.
The performance infrastructure/smoke milestone passes; the full GPU comparative
study and original learned-index/AlphaDev/scaling/final report phases remain open.
