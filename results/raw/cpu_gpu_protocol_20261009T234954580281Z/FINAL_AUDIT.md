# CPU/GPU comparison protocol preparation audit

Deliverable: a frozen-for-review specification and bounded experiment matrix.
**No pilot or comparative study was executed.** No remote session was queried,
no GPU program was compiled/run, and no performance ranking was generated here.
This does not complete the broader CUDA comparison milestone.

## Starting state and evidence verification

Workspace is writable; no Git metadata exists (`git status --short` exit128).
No repository was initialized, no commit/push performed, no user files removed.
Read AGENTS.md completely and inspected README, roadmap, audit, experiment and
benchmarking/metrics documentation; reviewed CMake, registries, CPU Merge Sort,
OpenMP Merge Sort, production CUB adapter, prepared CUDA timing session, dataset
generation, CPU timing engine, GPU CLI/matrix and analysis tools.

Verified all six user-specified evidence paths exist:

* `results/raw/cuda_timing_20261009T231303050084Z/FINAL_AUDIT.md`
* `results/raw/cuda_timing_20261009T231303050084Z/CHANGES.md`
* `results/raw/cuda_timing_20261009T231303050084Z/COMMANDS_FINAL.md`
* `results/processed/cuda_timing_20261009T231303050084Z/REPORT.md`
* `results/raw/cuda_timing_20261009T231303050084Z/FINAL_INTEGRITY.json`
* `docs/CUDA_TIMING_PROTOCOL_v1.md`

`existing_evidence_verification.json` records the initial successful hash review:
10755 prior result files, the previous sealed 1186-file GPU-smoke manifest and
148 source/documentation files matched. Its final-manifest SHA-256 is
`8cc3b50f5aea82932faa36662844cb61799f04a5f7fd0d3e6803a152abc5dfef`.
Final re-verification is recorded in `FINAL_INTEGRITY.json`, with exact checker
output/exit status in `commands/final_integrity.json`.

Historical (not fresh) evidence proves Tesla T4 correctness475 inputs/1900 output
checks, prepared timing smallest5 measured/1 warm-up plus48 configurations/240
measured/48 warm-ups, zero failed/missing; GPU framework14/14 and local CPU
Release27/27/ASan-UBSan27/27 with leaks enabled. The initial checks read the actual
completion/command/summary records and hashes, not only prose reports.

Historical cloud metadata: Tesla T4 compute7.5, driver580.82.07, CUDA/nvcc13.0.88,
runtime API13000, GCC13.3.0, CMake3.31.10, two logical CPUs on one physical SMT
core. Current session readiness is unknown. `local_planning_environment.json`
records this task's local Linux/i5-11400H/12-logical-CPU environment separately;
it is not Colab metadata and cannot support a cross-host CPU/GPU ratio.

## Contract and proposed experiment

Freeze: `docs/CPU_GPU_COMPARISON_PROTOCOL_v1.md` and
`docs/studies/cpu_gpu_comparison_v1.{matrix.json,resources.csv,freeze.json}`.
The freeze manifest stores exact SHA-256 hashes and `execution_authorized=false`.

The primary matched scope is a warm-context complete host-vector sorter API call,
including algorithm-internal allocations/destruction and production GPU pageable
H2D/sort/synchronization/D2H/cleanup. Dataset generation, original restoration,
context initialization and oracle verification remain outside the timer. Existing
prepared H2D/device/D2H/host end-to-end metrics retain their old scopes/identity
and serve as diagnostics only, never CPU speedup denominators. No public sorter
interface or production behavior change is required.

Five modes: std_sort, sequential Merge Sort, two-thread OpenMP Merge Sort,
production CUB adapter host-call, and prepared CUB four-metric diagnostics. Main
plan: N1025/65537/1000000, five seeded distributions, seeds1729/42/2718 and one
nonrandom signed-edge dataset per size. That is48 distinct recipes,240 mode
configurations,1200 measured calls and240 warm-ups. Four prepared metric values
are not four trials. Pilot plan: six datasets,150 measured calls and30 warm-ups;
it must be separately validated and cannot be reused as main-study observations.
SHA-256 recipe IDs and seeded hash permutations plus five cyclic order rotations
make the exact schedule reproducible. Content hashes are collected at execution.

Within-dataset five-trial summaries precede equal-weight distinct-input summaries
and paired ratios of matched medians. All outliers retained; no significance/CI
claims. Record actual OpenMP team counts; historical Colab SMT is not two physical
cores. The common primary schema, interleaved driver, paired analyzer, shared edge
helper and dual CUB workspace-query helper are **specified but unimplemented**.

The reviewed CUB3.0.1 pin remains CCCL commit
`f19d875da0d8bfb2e38c109b2b40522b8abbbbc3`, CUB_VERSION300001; license, pin and
production adapter hashes are unchanged. Source anchors are in the frozen matrix.

## Resource and runtime planning, not measurements

At 1M: known peak host payload24,000,000bytes (three vectors, two pinned buffers,
plus one active algorithm workspace/output vector). Combined device key buffers
16,000,000bytes plus unknown prepared/default-stream CUB workspaces, since the
prepared session remains resident. A 64MiB **policy allowance per workspace**
gives a150,217,728byte device planning cap; it is not a measured/proven bound.
Require fresh dual workspace queries, <=256MiB combined device payload and <=half
fresh free GPU memory, >=1GiB host headroom and >=1GiB disk. Runtime/context/
allocator/staging/OpenMP overhead remains additional, and RSS is not isolation.

Historical prepared workspace:1byte at1025 and279295bytes at65537; current values,
1M workspace and production default-stream workspace remain unknown. Table covers
every size with formulas and explicit unknowns. No allocation-inclusive GPU timing
has been measured in this task or the previous prepared-only smoke.

Planning model:25.96s pilot/158.10s main, fourfold budget103.84s/632.40s, plus
assumed5–20min build/regression/preflight. It uses a different-host historical CPU
sample with4x multiplier and unmeasured GPU/setup/validation allowances, all
documented in protocol/matrix. It is not a forecast or CPU/GPU measurement. The
fresh pilot must replace it before main-study review/authorization.

## Fresh validation and failures

Relevant unchanged Release binaries were executed, not rebuilt:

```bash
ctest --test-dir build/cuda_timing_20261009T231303050084Z/cpu-release \
  --output-on-failure -V -R '^(datasets|timing|cuda_benchmark_analysis)$'
```

Exit0,3/3 groups passed, zero failed groups. Dataset output:220 distribution/
size/seed cases, five exact one-swap fixtures, one five-swap fixture, empty/
singleton and existing fixtures. Timing output:72 inputs/1296 validated registry
trials. CUDA-analysis Python output:14 methods ran,12 passed,2 GPU methods skipped
because no GPU executable is supplied in this CPU-only run. Fixture messages
exit9/timeouts/collisions are intentional failure-handling tests, not actual
benchmark failures. Full output is retained in `commands/targeted_cpu_ctest.json`.

`validate_protocol_assets.py`: exit0,14/14 host-only methods pass. Checks complete
matrix and independent manual totals, identities, balanced order, pilot subset,
resource arithmetic/unknowns, source/freeze hashes, schema, uncertainty policy,
planning-estimate labels and byte-for-byte asset regeneration. Negative fixtures
reject duplicate/missing datasets, oversize/wrong protocol/repetition counts,
incompatible scopes/ratios, pin changes, false readiness and order changes.
This is static protocol validation, not tests of the nonexistent comparison driver.

No fresh configure/build/full CTest/sanitizer or CUDA execution was necessary for
these documentation/planning changes; none is claimed. All performance calls in
both proposed matrices remain unexecuted. No new compiler-warning assessment was
possible without compiling; previous100+161 generated nvcc line-directive warnings
remain historical and preserved.

Nonzero/failed operations: Git status128 because metadata is absent, and two
README apply_patch context-match failures (neither changed files). Exact editor
diagnostics are in `editor_diagnostics.json`; corrected append succeeded. All
recorded validation commands exit0; see `COMMANDS.md` and `commands/*.json` for
full argv, cwd, output, timestamps, durations and statuses.

## Changes, integrity and handoff

`CHANGES.md` enumerates four new protocol assets and four updated documentation
files. No algorithm, build configuration, CLI, vendor source/license, historical
protocol or prior result artifact changed. Existing documentation is preserved
as a prefix, except one roadmap status-row update. The final integrity checker
verifies10755 prior files,1186 sealed GPU-smoke files and144 protected original
source/doc files, all new freeze hashes and26 selected source anchors.

Unresolved: comparison implementation/tooling tests, fresh T4 availability and
correctness, actual dual-workspace sizes, fresh CPU regressions for future code,
pilot timing/resources and cloud confounders. No local driver installation or
configuration change was attempted. No100M workload, performance ranking or new
comparative study was run.

**Next step:** review the frozen protocol/matrix, then implement and test the
isolated comparison driver, primary schema/paired analyzer and resource query.
After fresh gates pass, separately authorize/execute the six-dataset pilot. Only
its validated output and revised estimates can support main-study authorization.
The protocol-preparation milestone is delivered; the CPU/GPU experiment is pending.

Final observed integrity result: checker exit0;10755 prior result files,1186
sealed smoke files,144 protected original source/doc files and26 selected source
anchors all match. The exact three frozen asset hashes and freeze-manifest hash
match; only the four documented existing documentation files changed.
