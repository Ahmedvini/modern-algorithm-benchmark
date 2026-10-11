# CTest pre-discovery build guard v1

This repairs the directory-hook finding in
`results/raw/cpu_gpu_repair_review_20261010T185659333607Z/FINAL_AUDIT.md`.
Study launch remains **NO-GO**. The next action is a separate independent review;
this repair does not authorize discovery, prerequisites, resource probes or a study.

## Trust and supported metadata

`non_timing_tests.pre_discovery_gate` first verifies the reviewed complete source
snapshot, then calls the static `ctest_build_guard.validate_build_tree`. Neither
function executes CMake/CTest. `NON_TIMING_TEST_SELECTION_v1.json` records exact
reviewed commands and generated properties, including backtraces tied to unchanged
CMake sources. This is a reviewed repository policy, not a signed attestation or
automatic trust-on-first-use enrollment. Only the explicit repair workflow renews
the source snapshot; production code never renews it.

The current project has a flat registry of 29 CPU or 32 CUDA-enabled tests. Only
literal single-line `add_test` and `set_tests_properties` statements are supported,
with ordinary quotes or `[=[...]=]` quotes. Every command, argument, name, property
and backtrace must match policy, including excluded timing tests. Duplicates and
missing declarations fail. Expressions, escapes, control flow, arbitrary commands,
includes and `subdirs` are rejected rather than evaluated. No included CMake
program or nested registry has been reviewed, so none is allowed.

The whole build tree is inspected for `CTestCustom.cmake`, `CTestCustom.ctest`,
`CTestConfig.cmake`, other `.ctest` files, nested CTest/Dart registries, symlinks
and unreadable directories. These are rejected even if unreferenced or empty.
Unreachable ordinary compiler `.cmake` files are not interpreted. Missing,
nonregular, oversized, unreadable or unparseable metadata fails closed.

When present, `DartConfiguration.tcl` must match the reviewed key/value schema.
Source/build paths, command settings and functional defaults are checked. Four
output-only labels and Release/Debug configuration may vary. Dashboard commands
are limited to literal reviewed CMake arguments and never invoked by the fixed
discovery/test commands. Arbitrary `CTEST_*` environment overrides and unreviewed
wrappers are rejected. Only the existing two sanitizer `env` prefixes are allowed.

## Entry points and boundary checks

- `select_tests`, including supplied discovery JSON, gates the actual tree first.
- The CLI gates before its discovery subprocess. `--discovery-json` avoids
  discovery but cannot bypass build validation.
- `selected_ctest` gates before discovery, checks returned registry/commands,
  saves a plan, then repeats source/build validation before execution. Metadata
  fingerprints must agree.
- All four prerequisite-only call sites (Release, sanitizer, leak retry, CUDA
  correctness) already use this helper. The legacy full-protocol branch runs
  timing-framework tests intentionally and is outside this selection policy.

The CPU plan is exactly: baselines, cli, comparisons,
cpu_gpu_comparison_framework, cuda_benchmark_analysis, cuda_preflight,
cuda_sort_handoff, datasets, environment_manifest, memory, memory_unsupported,
mergesort, metrics_cli, pdqsort, quicksort, radixsort, searching, structures, timsort.
`parallel_mergesort` and its N=32,768 timing path remain excluded. Explicit CUDA
correctness opt-in adds two tests; GPU timing is always excluded.

## Validation and limitations

Evidence: `results/raw/ctest_hook_repair_20261010T223851377458Z/`. Tests use inert
temporary files and Python fake callbacks, with real process launch blocked. The
exact previously accepted hook fixture fails before any discovery callback.
Coverage includes hooks/includes/nesting, malformed/changed/unreadable files,
command/property/identity changes, both CLI paths and inter-boundary changes.
No real discovery, CTest group, prerequisite validator, build, timing or GPU ran.

The grammar is intentionally narrow. Different generator layouts/backtraces,
multi-configuration trees or dashboard defaults require review and policy changes.
CUDA stack shape was checked against retained metadata, not a fresh CUDA build.
Fresh CPU/GPU execution is unvalidated by this repair.

Use exclusively owned, quiescent build trees and trusted tools. Boundary rechecks
cannot prevent an external concurrent writer changing files between validation
and CTest opening them. This is not an OS sandbox or executable attestation.
Fresh build/validation remains a separate decision. Correctness-only prerequisite
output still has `study_eligible=false` and cannot satisfy the frozen study gate.
