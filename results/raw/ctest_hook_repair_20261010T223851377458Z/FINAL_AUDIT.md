# CTest pre-discovery hook repair

**Repair implemented and inert regressions pass. Study launch remains NO-GO.**
Stop here. The exact next action is a separate independent review of this code
and evidence; no prerequisites, resource validation or study are authorized.

Evidence: `results/raw/ctest_hook_repair_20261010T223851377458Z/`.

## Starting state and root cause

Read the independent review's FINAL_AUDIT.md, COMMANDS.md, FINAL_INTEGRITY.json
and relevant selector/prerequisite source before editing. Inspected AGENTS.md,
relevant README/roadmap/protocol sections, current generated CPU metadata, the
selection policy, tests and retained CUDA metadata. BEFORE.json records 11,448
pre-existing result files, 173 project files (excluding Python caches), and 21
build-metadata files. The expected historical breakdown matches exactly:
11,345 earlier files +46 prior repair files +57 independent-review files.

Old `selected_ctest` called its discovery callback at line110 before validating
source/JSON. The CLI did the same through subprocess.run. `select_tests` checked
test JSON but never examined CTestCustom, includes, nested configuration or Dart
settings. A name filter cannot guard code evaluated while CTest loads a tree.
The retained prior-review fixture was therefore accepted despite unreviewed hooks.

## Changes and traced paths

Added `scripts/ctest_build_guard.py`: pure static validation of the reviewed flat
root registry. It never runs CMake/CTest or reads included files by evaluating
them. Only literal single-line add_test/set_tests_properties declarations are
allowed. All names/commands/arguments/properties/source backtraces must match
reviewed metadata, including excluded timing groups. Includes, subdirs, control
flow, expansions, escapes, unknown/duplicate/missing declarations and properties
fail closed. The whole tree is scanned for custom hooks, .ctest files, nested
CTest/Dart registries, symlinks and unreadable directories. Unknown unreachable
compiler metadata is not interpreted. Present DartConfiguration data must match
the reviewed functional schema; environment labels are explicitly distinguished
from commands. Unknown CTEST environment overrides and wrappers are rejected.

Modified `scripts/non_timing_tests.py`:

- `pre_discovery_gate:70` verifies source policy, then static build metadata.
- `select_tests:76` uses that gate even for supplied discovery JSON, checks registry
  identity/commands and reviewed selected-test properties, and retains the exact
  serial anchored 19-name plan.
- `selected_ctest:133` gates before its discovery callback at139; metadata must
  still agree after discovery and at the final execution boundary at145.
- CLI `main` gates at161 before optional subprocess discovery at165. Supplying
  retained JSON cannot bypass the gate.

`validate_cpu_gpu_pilot.py` is unchanged. Its prerequisite-only Release:47,
sanitizer:56, leak retry:65 and CUDA:83 call sites already use selected_ctest and
inherit the new gate. The legacy full-protocol branch intentionally runs timing
tests and remains outside this correctness-only selector. Neither branch ran.

Modified `docs/NON_TIMING_TEST_SELECTION_v1.json`: explicit source-policy renewal
and reviewed generated-property/Dart schema. This is not a frozen protocol change
or runtime automatic enrollment. CPU source backtraces were cross-checked against
the unchanged CMake source; CUDA include-stack shape was checked against retained
real generated metadata, with current source line numbers. No CUDA build ran.

Added `tests/ctest_fixture.py` and `tests/test_ctest_build_guard.py` for inert
metadata/fake-runner coverage. Updated existing `tests/test_cpu_gpu_safety.py`
selector fixtures and the mocked prerequisite fixture in
`tests/test_cpu_gpu_comparison.py` to provide actual inert generated metadata.
The latter module was syntax-checked and reviewed, not executed as a suite.

Added `docs/CTEST_BUILD_GUARD_v1.md`; updated README.md, docs/ROADMAP.md and
docs/AUDIT.md with the contract, evidence and continuing NO-GO status. Exact
hashes, paths and available diffs: FILE_REVIEW.json and SOURCE_DIFF.patch.
Four files added, seven existing source/document files modified. No production
algorithm, analyzer, adapter, CMake target, frozen input or CUB pin was modified.

## Inert regression results and rejection proof

Final focused command:

```sh
env PYTHONDONTWRITEBYTECODE=1 python3 -B tests/test_ctest_build_guard.py -v
```

Exit0, **28/28** methods, zero failures/errors/skips. Exact output:
`commands/inert_regressions_sealed_source.json`.

Inspected existing selector class only:

```sh
env PYTHONDONTWRITEBYTECODE=1 python3 -B results/raw/ctest_hook_repair_20261010T223851377458Z/run_existing_inert_selection_tests.py
```

Exit0, **11/11** methods, zero failures/errors/skips. Exact output:
`commands/existing_inert_selection_tests_final.json`. Combined distinct final
coverage is39 methods. This is not19 native/CTest groups or fresh sanitizer/GPU
validation. Broad provenance/framework collections were not run.

The tests use temporary text files, never binaries. Real subprocess run/Popen/
call/check_call/check_output and os.system are blocked in the new collection.
The existing selector-class wrapper blocks real run/Popen/os.system. Reviewed
imports/helpers have no workload-launch side effects. Valid-path discovery and
execution callbacks are Python fakes returning literal fixture text; their
"0 tests failed out of19" string is not observed CTest output.

Coverage includes a clean19-name plan, custom pre/post/empty hooks, .ctest hooks,
unreviewed include, nested subdirs/file/hook, changed commands/backtraces,
fixtures/dependencies, unreadable/missing/malformed/invalid-UTF8 metadata, symlinks,
duplicates, environment/wrappers, source snapshot change, both CLI paths, explicit
CUDA opt-in metadata, bracket quotes, Dart settings and boundary mutation.

`REJECTION_PROOF.json` retains the exact prior-review fixture's rejection for
`unreviewed CTest hook/configuration: .../CTestCustom.cmake`, with discovery
callback count0. `SELECTED_TESTS.json` is a pure plan from UNEXECUTED_CLEAN_TREE;
that retained fixture was never interpreted by CTest. The selected names are:

baselines, cli, comparisons, cpu_gpu_comparison_framework, cuda_benchmark_analysis,
cuda_preflight, cuda_sort_handoff, datasets, environment_manifest, memory,
memory_unsupported, mergesort, metrics_cli, pdqsort, quicksort, radixsort, searching,
structures, timsort.

All ten CPU timing groups remain excluded, specifically parallel_mergesort's
N=32,768 path. The GPU timing framework remains excluded even with explicit
correctness opt-in. Rejected pre-discovery fixtures assert zero callback calls;
mutation during discovery or after saving the plan cannot reach execution.

## Failures and corrections retained

- `commands/metadata_policy_review.json`, exit1: a one-time policy-derivation
  assertion compared `/usr/bin/python3` against its resolved python3.12 path.
  Generated and discovered commands now use the established canonical path
  comparison. All command arguments still must match reviewed identities.
- `commands/inert_regressions.json`, exit1: initial26 methods,25 passes/one error.
  The Dart key grammar rejected standard P4Command. Corrected alphanumeric key
  syntax, retained attempt1/ source/policy, and reran successfully.
- Static retained-CUDA review found an incorrect proposed backtrace include-stack
  shape. The original policy/script are retained under
  metadata_policy_before_cuda_stack_review/. Corrected the shape using historical
  generated metadata and added an independent source/stack regression.
- A documentation apply_patch context mismatch was rejected atomically; the
  documentation_patch_state log confirms no partial edits. Corrected afterward.

All other recorded shell command exits are0. Earlier passing runs are retained
separately from final runs. No failed attempt was deleted or relabeled successful.

## Preservation and safety

PRESERVATION_FINAL.json records fresh direct before/after comparisons:

- All11,448 prior results unchanged, with zero missing/changed paths.
- Original11,345 historical files unchanged; prior repair46 files and independent
  review57 files unchanged, including their self-excluded seals. Their45/56
  sealed file hashes and exact directory membership are verified directly.
- All26 protected anchors match with only the existing independently pinned
  CMake exception. All80 production/header/dependency identities match history.
- Three frozen members plus the independently pinned freeze manifest match;
  the existing CMake review pin also matches. Production adapter SHA256:
  b6d7f37c7494587fc6e4a676c00c166dc322d31cce96710811e3a4cb9cd8b9cb.
  CUB3.0.1/version300001 pin SHA256:
  477b1ee70b0a9113c9f98b263c19a31d05ccee54f45ce8476aec4cc98965ced1.
- All21 pre-existing build-metadata files unchanged. Intended source/document
  differences are exactly the11 listed paths, with all other project hashes
  unchanged. New result files are confined to this exclusive evidence directory.

FINAL_INTEGRITY.json rechecks preservation after audit generation, supplies final
new/total file counts and seals this evidence (excluding the seal itself).
COMMANDS.md records exact child argv, exits, safety classes and raw log paths;
PRE_RECORDER_COMMANDS.md records early/unwrapped terminal commands honestly.

Actual CTest discovery commands0; CTest/native test groups0; fresh prerequisites0;
resource checks0; sorting/timing trials0; benchmarks/pilots/studies0; GPU commands0.
No fresh build/Release/ASan/UBSan/GPU suite is claimed. No19-test selection was
executed. No commit, push, Git initialization or historical cleanup occurred.

## Remaining limitations and next action

The guard deliberately rejects unsupported generated layouts instead of executing
them. CUDA metadata validation is inert; fresh toolchain/hardware execution is
not established. Reviewed source/command policy is local trust, not cryptographic
attestation of arbitrary binaries. Trusted tools and an exclusively owned,
quiescent tree are required: boundary rechecks cannot prevent malicious concurrent
writes between checking and CTest opening a file. This is not an OS sandbox.
Correctness-only prerequisites remain ineligible for the frozen full-study gate.

**Next: independent review of this repair and evidence only.** Study launch is
**NO-GO**. Fresh prerequisites/resources and subsequent study authorization remain
separate explicit decisions. This repair stops at this audit.
