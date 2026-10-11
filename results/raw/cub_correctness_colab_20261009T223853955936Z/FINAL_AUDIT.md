# Colab CUB sorting correctness — final audit

The CUDA sorting correctness milestone passed on the existing authorized Colab
Tesla T4. Original roadmap Phase7 remains incomplete for GPU timing and studies.
No primary GPU benchmark measurement or speedup was collected.

## Starting state and preservation

Workspace writable; no Git metadata (git status --short exit128), so branches,
commits and Git change status are unavailable. No Git repository initialized.
All138 starting source hashes matched the reviewed local state before edits.
The original corrected v2 bundle SHA256 matched locally and remotely:
e155579bf9f9847ae1ced84c07f6e179d98215962076d1c0aea8133de00a190f.
Archive139 safe members;138 source hashes verified before execution. Extraction
used a fresh directory, preserving /content/modern-algorithm-benchmark.

All8,825 earlier results/evidence files retain their starting SHA256 values;
16 protected versioned protocols/guides/studies/vendor/license files also match.
Original source archives, cloud readiness evidence and CPU studies remain intact.
No drivers/packages/system policy changed, new GPU allocated, commit or push.

## Session and environment

Existing session: gpu-t4-s-kkb-ass1b1-aq78qx2sgfal. CLI0.7.4 listed the assignment
but initially lacked a local alias: status printed not found despite exit0.
Registered the existing assignment through the installed client's authenticated
assignment API in a private isolated build-state file, never included in evidence.
Attached status reported IDLE. No new GPU runtime was created.

Observed Tesla T4, compute7.5, device0; total device memory15637086208 bytes.
NVIDIA driver580.82.07, nvcc13.0.88, runtime/driver API13000, GCC13.3.0,
CMake3.31.10, Python3.13.15, Linux6.6.122+/x86_64/glibc2.39.
Both attempts include a fresh operational preflight and checked device0 kernel
result1729. Metadata is in remote_environment.json and downloaded preflight reports.
No frequency/thermal/background-load control claim; these are correctness runs.

## Failure, reviewed fix and retry

Original source runner exit1: configure exit1, rejected installed version.cuh hash
316819d3be158deebcf40e96dde6d8d08e7910e9740a69b111677d0c5a21c124 versus
initial3.0.0 pin. SortKeys hash matched. Sorter compilation/tests did not start.
CLI transport exited0; the retained inner runner/configure status is authoritative.
See downloaded/attempt1/NEW_CUB_CORRECTNESS/FAILED.json and configure.json.

Independent canonical NVIDIA/cccl tag resolution and commit-qualified downloads
verified v3.0.1 at f19d875da0d8bfb2e38c109b2b40522b8abbbbc3. Version header
matches installed bytes; its only difference from reviewed3.0.0 is macro300001.
SortKeys and aggregate LICENSE hashes unchanged. CUB remains BSD-3-Clause.
upstream_v3_0_1/review.json retains URLs, HTTP statuses, hashes and tag resolution;
version_difference.patch retains the exact comparison. No upstream source/license
was edited. CMake and compile assertions still enforce an exact reviewed pin.
Two matching reference headers are not a claim that every transitive toolkit file
matches upstream: all1688 installed cub/thrust/cuda files are separately hashed.

New frozen CUDA_SORT_PROTOCOL_v2.md records the pin and protocol identity change;
v1/old guides are unchanged. Result protocol cuda_sort_correctness_v2;
implementation cub_radix_sort_v1 unchanged except compile-time version assertion.
Fixtures and expected475/1900 totals unchanged. Host regression rejects old and
unreviewed dependency/result identities. Retry bundle140 source files SHA256:
e4a5e21c02c6f5611b5577caac88abaa35856270af61b335bcf57a923e73dee1.
This matched remotely before fresh extraction into a separate retry1 checkout.

One retry CLI connection stalled in its automatic prelude, before the runner.
Remote HTTP kernel status was idle; filesystem/process inspection found no runner
marker, output or validation process. A new local WebSocket connection to the same
kernel worked. Only the stalled local CLI process was terminated: recorded child
exit-15 (outer recorder shell241); no kernel/runtime interrupt or reset. The
following reconnected CLI/runner both exited0. A progress listing exited1 because
the not-yet-created output directory was absent. These are connection/diagnostic
failures, not sorter correctness failures. Exact records and traceback retained.

## Actual GPU validation

From /content/mab_cub_20261009T223853955936Z_retry1/modern-algorithm-benchmark:

```sh
python3 scripts/validate_cuda_sort.py --output results/raw/NEW_CUB_CORRECTNESS
```

Runner exit0. Fresh preflight, Release CUDA configuration, target build,
test_cuda_sorting direct execution and targeted CTest all exited0. Full absolute
argv/cwd/stdout/stderr are retained in downloaded/retry1/NEW_CUB_CORRECTNESS/*.json
and COMMANDS.md. CMake CUDA architecture75 comes from actual device0 preflight.
CUDA ON/SORT ON, OpenMP OFF, sanitizers OFF, BUILD_TESTING ON, C++/CUDA17.
Actual CUB DeviceRadixSort::SortKeys compiled and ran; no CPU fallback or substituted
sorting algorithm. Direct test:475 input cases/1900 full-vector output checks,
zero failed/skipped/unexecuted required correctness cases. CTest reran the same
suite:1/1 passed,475/1900 again. Across two executions3800 checks, not950 distinct
fixtures. Includes signed extrema, duplicates, exhaustive small inputs, all
supported distributions/seeds, sorted/all-equal, repeated/registry calls and
boundary-adjacent/non-power-of-two sizes through65537. No internal tile coverage
or payload stability claim. Retry contains COMPLETE and no FAILED/INTERRUPTED.
Original attempt has one unexecuted GPU sorting group due configure failure.

Build emitted100 warnings, all `style of line directive is a GCC extension`.
Diagnostics reference nvcc-generated cudafe/stub files and line mappings under
host -Wpedantic. GCC accepts these GNU preprocessor line markers; this is generated
code diagnostic noise, not an observed sorting defect. No suppression or source
rewrite was applied. Full build.json retained. CPU build logs contain no warnings.

## Fresh CPU regressions

CUDA and CUDA-SORT disabled; GNU13.3.0/OpenMP4.5, isolated build directories.
First pre-fix Release configure/build/CTest exit0/0/0:26/26,28.86s.
After pin/schema changes Release configure/build/CTest exit0/0/0:26/26,28.36s.
Fresh Debug ASan/UBSan configure/build/CTest exit0/0/0:26/26,80.21s.
Leak detection enabled; env -u ASAN_OPTIONS -u LSAN_OPTIONS,
UBSAN_OPTIONS=halt_on_error=1. No ptrace failure or detect_leaks=0 retry.
Zero failed/skipped groups in each suite. Twelve host handoff methods pass standalone
and in both final suites;22 readiness methods pass. These host sanitizers are not
GPU memory/race validation. Exact individual test counts remain in CTest logs.
CPU defaults, registry, implementations and historical timing outputs unchanged.

## Evidence export and integrity

Remote export contains611 files including both complete/failed validation bundles,
CMake caches/compile commands, sorter binary, source/dependency manifests, runtime
probe and exact command/runner diagnostics. No symlinks skipped. Both attempts'
files were hashed before export and checked unchanged after packaging.
Downloaded colab_evidence.tar.gz SHA256 matches the remote export:
fda8f0107e04975068a5db5217d5996984c4a6e92a2b267f5910acd8308a7a4b.
Size2618050 bytes. Safe member inspection/extraction; all611 member hashes/sizes
verified. COMPLETE's source/preflight/dependency hashes verified, direct result
strictly revalidated, CTest confirmed actual pass rather than skip.
Source139 runner files match the140-file source bundle (runner excludes.gitignore).
Actual downloaded paths:
- downloaded/attempt1/NEW_CUB_CORRECTNESS/{FAILED,configure}.json
- downloaded/retry1/NEW_CUB_CORRECTNESS/{COMPLETE,sorting,ctest,build}.json
- downloaded/retry1/NEW_CUB_CORRECTNESS/preflight/{report.json,SUMMARY.txt}
- downloaded/retry1/NEW_CUB_CORRECTNESS/build/{CMakeCache.txt,compile_commands.json,test_cuda_sorting}
- downloaded/EVIDENCE_SHA256.json
- download_verification.json; integrity_after_validation.json; final_review.json
- commands/*.json; COMMANDS.md; source_after.json; final_changes.patch; SHA256SUMS

Early retry_changes.patch used an incorrect backup prefix; retained as debugging
history, do not apply it. retry_changes_reviewed.patch and final_changes.patch use
the verified original backup. A read-only cat inspection used nonexistent
upstream_review/version.cuh (exit1); corrected to actual cub_version.cuh.
No failure was interpreted as a successful test.

## Scope, status and next step

The CUDA sorting correctness milestone is complete on observed T4 hardware. Entire
CUDA phase remains open. Device-memory sanitization, allocation-failure injection,
other GPU/toolkit coverage and larger GPU correctness workloads were not run.
The retained host-vector oracle establishes the tested outputs, not exhaustive
absence of device errors or race freedom. No GPU timing infrastructure, performance
smoke/full study, comparison run, CUDA speedup or100M workload is claimed.

Next: freeze a GPU timing contract with checked synchronization, buffer reuse and
allocation scope; implement an isolated CUB benchmark reusing datasets/validation,
separate H2D/device/D2H CUDA-event metrics and host steady_clock end-to-end timing;
validate tests and a small smoke matrix before a study. No further user Colab command
is needed for this completed correctness validation. Learned-index/AlphaDev,
resource scaling and final research deliverables remain later roadmap work.
