# Analyzer provenance and non-timing selection repair audit

Evidence: `results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/`.
Recommendation: **NO-GO for study launch**. Repair validated by synthetic/static
checks only. Fresh prerequisites intentionally unexecuted. Stop after this audit.

## Starting evidence and preservation

Read instructions and the latest review FINAL_AUDIT.md, COMMANDS.md and
FINAL_INTEGRITY.json before editing. Verified its actual30 retained files,
prior tooling85 evidence files,137 source identities and four documentation
identities. BEFORE.json retains11345 pre-existing result-file hashes,137 source
hashes and four frozen hashes. Accepted pilot and N65537 workspace/resource
evidence inspected without modification. Git status exited128: no metadata;
no initialization, commit or push.

Final direct comparison: historical files **11345 before /11345 after**;
zero changed, missing, overwritten or renamed. Total results files after repair
**@TOTAL_RESULTS@**, including **@NEW_EVIDENCE@** new files confined to this
directory. Four frozen assets,26 protected anchors (with the already accepted
CMake exception),80 production/header/dependency files and the existing CMake
review match. The entire old tooling85-file and independent review30-file seals
were rechecked, not assumed from summaries. FINAL_INTEGRITY.json records exact
source/document/evidence hashes and excludes itself from its hash list.

| Frozen file | SHA256 |
|---|---|
| protocol | 7738d21ff0ea611c04a557418182ab562769b568c7dc0b898ca5d50280e21c70 |
| matrix | 29f9f2765e466a88fc3a7b6e590b1c38dd1ebe5f4f003a37e02aabc9b7074833 |
| resources | 324a67c9668d258366f738348ad853cbadd65ce4edd6f34b3ec16f4baaafeaab |
| freeze | 518ac535473e50fb61dab3a70858bdfe42dfdb43570f649174f44bffe40e1ac6 |

Production src/cuda/cub_sort.cu remains
`b6d7f37c7494587fc6e4a676c00c166dc322d31cce96710811e3a4cb9cd8b9cb`.
CUB3.0.1/version300001 commit `f19d875da0d8bfb2e38c109b2b40522b8abbbbc3`
pin remains `477b1ee70b0a9113c9f98b263c19a31d05ccee54f45ce8476aec4cc98965ced1`.
No adapter, timing worker, CMake anchor, frozen input or historical result edited.

## Root causes and repairs

1. Analysis validated mutually consistent mutable source/prerequisite/build/raw
   hashes without independently checking expected production-adapter identity.
   New cpu_gpu_provenance.py pins the accepted freeze and existing CMake review,
   verifies frozen assets, then derives expected code/pin digests from that
   verified matrix. Only the exact existing CMake exception is allowed. Missing,
   malformed, ambiguous or inconsistent anchors fail closed. Legacy code-only
   maps omit documentation; frozen documentation is checked directly, and any
   optional retained claim must agree. Both pilot/study performance paths enforce
   independent source identity.
2. Prerequisite-only validation ran broad CTests, while manually narrowed
   selections relied on names and missed embedded N32768/W1/R2 timing in
   parallel_mergesort. New non_timing_tests.py uses reviewed command/class/source
   metadata because no safety labels exist. Unknown/missing/duplicate tests,
   modified source, unreviewed commands/arguments and implicit fixture/dependency/
   environment execution fail closed. Known timing entrypoints stay blocked even
   when relabelled. Its CLI only discovers/plans; its execution helper saves a
   plan before serial exact-regex execution. Actual helper execution was mocked.

Prerequisite-only uses that helper for Release, sanitizer and explicit GPU
correctness, emitting validation_scope=non_timing_correctness_v1 and
study_eligible=false. Runner/analyzer reject this subset as unchanged full-study
prerequisites. This avoids calling19/21 groups full29/32 coverage. The original
non-flag pilot workflow retains its full scope; it was not executed. Frozen
timing-framework prerequisites still need separate authorization.

## Files changed

Modified:

- scripts/analyze_cpu_gpu.py: independent anchor enforcement and subset rejection.
- scripts/run_cpu_gpu_pilot.py: reject correctness-only prerequisites.
- scripts/validate_cpu_gpu_pilot.py: safe selector and explicit subset scope.
- tests/test_cpu_gpu_comparison.py: preserve50 methods; valid anchored fixtures,
  mocked discovery/selection assertions.
- README.md, docs/ROADMAP.md, docs/AUDIT.md and
  docs/CPU_GPU_FULL_MATRIX_TOOLING_v1.md: repair commands/results/remaining gates.

Added:

- scripts/cpu_gpu_provenance.py: trusted roots and strict source validation.
- scripts/non_timing_tests.py: reusable fail-closed discovery/selection.
- tests/test_cpu_gpu_safety.py:22 focused provenance/selector methods.
- tests/fixtures/cpu_gpu_provenance_reproducer.py: exact archived reproducer,
  SHA2561588c1ce06ded80b91d9806673b883effb7c98b0ace8d1eadb5c04688072142c;
  tests execute copies in disposable locations only.
- docs/NON_TIMING_TEST_SELECTION_v1.json:32 reviewed test classifications/commands
  and141-file source snapshot.
- docs/CPU_GPU_SAFETY_REPAIR_v1.md: trust/selection contract and limitations.
- This evidence directory only; before/ and attempt1/ preserve originals and
  the failed compatibility attempt. REVIEWED_CHANGES.patch records existing-file
  diffs. No existing test removed or weakened.

## Exact selection, inspected before executing focused tests

Actual CTest discovery from a byte-exact discovery-file copy with unchanged
absolute commands lists29 CPU groups. `ctest -N --show-only=json-v1` executed
zero tests. Both initial and final plans retained. Selected19 groups:

```text
baselines
cli
comparisons
cpu_gpu_comparison_framework
cuda_benchmark_analysis
cuda_preflight
cuda_sort_handoff
datasets
environment_manifest
memory
memory_unsupported
mergesort
metrics_cli
pdqsort
quicksort
radixsort
searching
structures
timsort
```

Excluded10: experiment_pipeline, structure_timing, structure_framework,
search_timing, search_framework, timing, benchmark_framework, parallel_mergesort,
parallel_framework, comparison_engine. Exact argv/regex/rationale retained in
SELECTED_TESTS_FINAL.json and the versioned manifest.

Reviewed source:12 selected C++ groups perform correctness/invariant/counting/
memory checks without timing engines; CLI/metrics programs are correctness/
counting only. Environment tests serialize/use failing probes. CUDA preflight/
handoff methods use doubles or CUDA-disabled configuration. cuda_benchmark_analysis
gets no GPU executable and would skip its two GPU timing methods. Comparison
framework uses synthetic records/subprocess doubles and small untimed input
generation. Unittest's elapsed test-run time is not algorithm timing evidence.

GPU selection tested synthetically only: explicit opt-in adds runtime/sorting
correctness for21 groups, never cuda_benchmark_gpu_framework. Unknown source
changes demand review and repinning. This is repository safety policy, not a
sandbox or proof about substituted binaries; future execution must establish
fresh binary/source correspondence. No19/21-group CTest run occurred here.

## Commands and actual outcomes

COMMANDS.md records exact validation argv, exits and safety classes;
commands/*.json contains full outputs. Read-only inspection/preparation failures
are separately disclosed there.

- Discovery/final selection: exit0;19 selected,10 excluded; tests_executed=false.
  Selection inspected before regression execution.
- Initial focused attempt: exit1;21 methods,17 passed,3 failures/1 error because
  legacy source maps omit documentation. Original implementation/manifest and
  full failure log retained. Fixed by directly verifying frozen documentation
  without weakening code anchors.
- Final focused suite: exit0; **22/22 passed,0 failed,0 skipped**. Covers exact
  former reproducer, consistent changed-adapter metadata, invalid/absent/ambiguous
  trust, valid baseline, changed source/commands/tests, implicit scheduling,
  known timing entrypoints, selection-before-execution and subset scope.
- Existing synthetic framework: exit0; **50/50 passed,0 failed,0 skipped**.
  Injected failure/interruption/timeout text comes from mocks. Only a small
  untimed input-generation executable runs; no sorter/timer/GPU child runs.
- Exact synthetic reproducer: exit0; unchanged baseline accepted; synthetic1200
  measured/240 warm-up records. Changed adapter rejected with
  `retained protected source differs from trusted anchor: src/cuda/cub_sort.cu`.
  Zero actual sorting/GPU calls. FULL_ANALYSIS_PROBE.json retains result.
- Read-only accepted pilot summary regeneration: exit0; byte-identical SHA256
  07e69e2e0c8853f93d3f3da895337b5e4b72e5e2dd0ff0577db3cbd1f7053a22.
  Old raw/processed results not written.
- Static syntax/provenance/manifest and integrity checks: exit0; eight changed/
  new Python files parse/compile without execution. No warning emitted by final
  focused/framework runs.
- Git inspection: exit128 (metadata absent). Read-only filename inspection: exit2
  (nonexistent test_capture_environment.py, corrected). Audit-generation heredoc:
  quoting SyntaxError followed by missing-file error, exit2; no final evidence
  created, corrected using apply_patch. These are failures, not passed checks.

No fresh configure/build, CPU Release/ASan suite, GPU suite, selected CTest suite,
prerequisite validator, timing-bearing test, GPU work, pilot/full study or100M
experiment was executed. Final passing tests comprise72 Python methods plus
offline/static checks, not fresh native/GPU validation.

## Remaining blockers and next step

Repairs pass synthetic/static checks. Study launch remains **NO-GO**. Stop here.
Next: independent repair review; then separately authorized fresh correctness
prerequisites, full frozen coverage (including timing-framework tests), all-size
execution-VM resource/environment/binary checks, and separate study authorization.
Pilot/cloud variability, SMT/shared load, thermal/frequency/cache controls and GPU
memory/race-tool limitations remain. Legacy unscoped prerequisite manifests stay
compatible; newly labelled correctness subsets are ineligible. No study
authorization follows from this audit.
