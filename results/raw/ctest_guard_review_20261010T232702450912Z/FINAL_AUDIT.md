# Independent review of the CTest pre-discovery guard

**Verdict: NO-GO for an unqualified reusable-guard PASS.** A remaining static
path-identity defect allows the discovery callback to receive a different build
tree from the one validated when a relative path is combined with a different
callback working directory. The current prerequisite runner passes absolute
paths and avoids that case. The original hook/include repair otherwise passes
static review within its documented trusted, quiescent-tree scope.

No source repair is applied here. Stop after this review; no discovery,
prerequisites, resource checks or study are authorized.

Evidence: `results/raw/ctest_guard_review_20261010T232702450912Z/`.

## Method and scope

Read the latest repair FINAL_AUDIT.md and COMMANDS.md first, listed its directory,
and identified the actual integrity filename as FINAL_INTEGRITY.json before
reading it. Read both earlier review/repair audits requested by the user. Traced
current guard, selector, prerequisite runner, subprocess wrapper, standalone CUDA
validators, protocol/provenance imports, CMake registrations, selection policy,
inert fixtures and test wrappers. Inspected the retained failures and final logs.

`STATIC_REVIEW.json` records exact source paths, hashes, method names/lines,
initial correction diff and the static path counterexample. Full inspected text
and command statuses are retained in `commands/*.json`; `COMMANDS.md` includes
early unwrapped inspections. `EVIDENCE_VERIFICATION.json` contains independent
direct hash comparisons, not copied preservation totals from the repair audit.

This review ran only file reads, JSON parsing, hashing, AST parsing, retained-log
comparison and pure path arithmetic. It did not import repository modules, call
the selector/guard, create new test fixtures, run tests or execute any CTest binary.
Only this new exclusive review directory was written.

Evidence-authoring qualifications: the initial bootstrap stdin was not retained
verbatim before context compaction; EARLY_COMMANDS documents its hashing/write
operations and exact executable/status without claiming a byte-exact stdin
transcript. Subsequent review programs and wrapped commands are fully retained.
Two evidence-only apply_patch context errors are preserved in TOOL_FAILURE.md;
they did not run a workload or alter project/historical files. All wrapped
inspection/hash/AST commands exited0.

## A. Pre-discovery guard

### What passes static review

Actual control flow:

- `scripts/non_timing_tests.py:70` pre_discovery_gate first validates the reviewed
  source/command manifest, then calls `ctest_build_guard.validate_build_tree`.
- `select_tests:76` gates at77 even for retained JSON. It checks registry coverage,
  command identity, selected-test properties and the exact anchored serial plan.
- `selected_ctest:133` gates at138 before its discovery callback at139; selection
  revalidates the tree at141; fingerprints must agree at142; a further gate at145
  precedes execution at147.
- CLI `main:153` gates at161 before subprocess discovery at165. The retained-JSON
  branch also gates and cannot bypass validation by supplying a JSON file.
- `validate_cpu_gpu_pilot.py` prerequisite-only branches at47/56/65/83 all use
  the same selected_ctest helper. They cannot broaden its selection via a flag.

The shared guard checks contents, commands and properties, not only filenames:

- `ctest_build_guard.py:19/32` accepts a narrow literal grammar and rejects
  malformed arguments, expansions, escapes, control flow and all include/subdirs
  statements. No included CMake file is evaluated or trusted by default.
- `:117-127` scans the entire tree, rejecting CTestCustom.cmake/.ctest,
  CTestConfig.cmake, other .ctest files, symlinks, unreadable directories and
  nested CTest/Dart registries, even when unreferenced.
- `:128-151` verifies every generated declaration, command, property and backtrace
  against policy, including excluded tests. Unknown/missing/duplicate declarations,
  fixtures, dependencies and unreviewed command arguments fail closed.
- `:64-96` checks present DartConfiguration.tcl as strict reviewed key/value data;
  functional values and commands are constrained. Only documented output labels
  and Release/Debug configuration may vary. Fixed -N/-R invocations do not invoke
  its dashboard build/update commands.
- `:110` rejects CTEST_* environment overrides; selected_ctest restricts wrapper
  prefixes before calling any callback. Missing/unreadable/invalid metadata raises
  before the discovery callback in these paths.

The local installed CMake documentation for ctest_read_custom_files,
CTEST_CUSTOM_PRE_TEST/POST_TEST and TEST_INCLUDE_FILES/FILE confirms why these
files/directives matter. Documentation was read; CMake/CTest was not invoked.

### Blocking finding A1: discovery does not pin the validated absolute path

`validate_build_tree:106` computes `Path(build_dir).absolute()`, validates that
tree and returns its absolute identity at156. But `selected_ctest:139` constructs
discovery with `str(build_dir)`, the original argument, rather than that guarded
identity. No absolute-path requirement exists at the public helper boundary.

The project's real subprocess wrapper, `run_cpu_gpu_pilot.invoke:20-26`, always
launches children with `cwd=ROOT`. A caller using that wrapper from another Python
working directory can therefore validate one tree and discover another:

| Item | Static example |
|---|---|
| Python validation cwd | /tmp/REVIEW_CALLER_EXAMPLE |
| Helper argument | build/REVIEW_PATH_EXAMPLE |
| Tree validated | /tmp/REVIEW_CALLER_EXAMPLE/build/REVIEW_PATH_EXAMPLE |
| Callback child cwd | project ROOT |
| Tree interpreted by discovery | ROOT/build/REVIEW_PATH_EXAMPLE |

The second tree's hooks/includes have not passed the gate. Checks after discovery
cannot protect against code interpreted during discovery itself. This is a
static public-API counterexample, not an executed exploit or a claim that any
historical hook ran. `STATIC_REVIEW.json` retains the path arithmetic and exact
line references; no directories or callbacks were created/executed for it.

The current prerequisite runner constructs cpu/san/gpu paths under absolute ROOT,
so this finding does not establish a bypass in its present four call sites.
All retained guard fixtures also use absolute TemporaryDirectory paths and do not
cover mixed working directories. The reusable safety contract remains incomplete.

Recommended focused repair: construct discovery from the exact absolute guarded
build identity, or reject nonabsolute helper arguments before callbacks. Cover
relative/mixed-cwd behavior with inert callbacks and verify the actual argv; do
not execute CTest to demonstrate the issue. No such change is made in this review.

### Coverage and trust qualifications

The gate is not universal across all prerequisite/validation workflows. The
explicit legacy full-protocol branches in validate_cpu_gpu_pilot.py:49/58/67/85
invoke CTest directly, as do validate_cuda_sort.py:113 and validate_cuda_timing.py:49.
These are documented workflows outside the correctness-only policy, not a silent
fallback from --prerequisites-only. Thus A2 passes for the selector and its four
correctness-only call sites, but a repository-wide no-legacy-bypass claim would
be false. Those workflows must not inherit a blanket guard approval.

Boundary rechecks detect changes during discovery and after plan saving, but do
not close an atomic TOCTOU gap. Another writer can still modify files between a
gate's last read and CTest opening them. The contract explicitly requires trusted
tools and an exclusively owned quiescent tree; no locking/sandbox enforces that
assumption. A6 is verified as boundary rechecking, not unconditional race prevention.

The reviewed manifest is local policy, not signed attestation. Its 144-file source
snapshot matches actual bytes; production selection never auto-renews it. This
review does not attest arbitrary binaries, tools, or adversarial concurrent writers.
Unused compiler CMake files are outside the accepted root registry's reach because
all includes/subdirs are forbidden; ignoring them is not evidence that they were
executed or reviewed.

## B. Regression evidence

Inspected, **not rerun**:

| Retained final log | Recorded exit | Methods | Result |
|---|---:|---:|---|
| commands/inert_regressions_sealed_source.json | 0 | 28 | all pass; no errors/skips |
| commands/existing_inert_selection_tests_final.json | 0 | 11 | all pass; no errors/skips |

AST method names match every success line in those logs: 39 distinct methods,
not 39 CTest groups or fresh tests in this review.

Coverage traced in tests/test_ctest_build_guard.py:

| Requirement | Test source lines | Actual path inspected |
|---|---|---|
| Clean exact19 plan and fake helper | 55,62 | select_tests / selected_ctest |
| Directory pre/post/empty hooks | 67 | selected_ctest; zero callback assertion |
| Unreviewed include and exact prior fixture | 75,80 | selected_ctest; zero callback assertion |
| Nested subdirs and unreferenced metadata | 86,93 | selected_ctest; zero callback assertion |
| Modified command/properties/backtrace | 99,103 | selected_ctest; zero callback assertion |
| Unreadable/missing/malformed/ambiguous/UTF8 | 110,118,122 | selected_ctest; zero callback assertion |
| Duplicate/missing registry; symlinks | 133,139 | selected_ctest / pre_discovery_gate |
| Environment/wrapper/source mismatch | 145,176 | helper before callbacks |
| Changes during discovery / after plan save | 152,161,168 | helper; execution callback never reached |
| CLI rejected and valid branches | 179,188,195 | actual main with process launch blocked/faked |
| CUDA opt-in, stack, bracket syntax, Dart | 202,210,220,225,230 | select_tests and helper |
| Discovery command/properties/registry | 238 | select_tests |

These exercise production public control flow, not just a parser helper. Rejected
pre-discovery cases call assert_rejected_before_discovery:50, which asserts an
empty callback list. Inter-boundary mutations necessarily permit the fake
discovery callback but prevent the fake execution callback. The retained exact
fixture rejection is also recorded in REJECTION_PROOF.json; no hook was executed.

New-test setUp blocks run/Popen/call/check_call/check_output/os.system and clears
environment overrides. Its fake callbacks return literal JSON/text and create no
binary. The existing wrapper collects only SelectorTests (11 methods), blocks
process launch before import, and deliberately excludes the provenance reproducer
and broader framework collection. Inspected imports/helpers contain no top-level
workload invocation. The fake '0 tests failed out of19' string is not real CTest
output. A fixture generated from the same policy is not an independent CMake
interpreter check; real discovery/toolchain integration remains unexecuted here.

The exact19 selection matches policy and the retained SELECTED_TESTS.json by
independent JSON comparison, without calling selection code:

baselines, cli, comparisons, cpu_gpu_comparison_framework, cuda_benchmark_analysis,
cuda_preflight, cuda_sort_handoff, datasets, environment_manifest, memory,
memory_unsupported, mergesort, metrics_cli, pdqsort, quicksort, radixsort, searching,
structures, timsort.

parallel_mergesort and the other nine CPU timing groups remain excluded. Explicit
GPU correctness metadata adds two groups, never GPU timing. None was run here.

Failures/corrections are retained rather than relabeled successful:

- metadata_policy_review.json records exit1 for the initial Python alias comparison.
  Current generation/selection uses canonical paths; the complete first-failing
  derivation-script revision is not separately preserved, so its exact historical
  program cannot be wholly reconstructed from that log alone.
- inert_regressions.json records exit1: 26 methods, 25 passes and one Dart parser
  error. Retained attempt1 source and current source differ by the precise regex
  change allowing digits in P4Command. The next 26-method run records exit0.
- The proposed CUDA backtrace policy/script before stack correction is retained.
  Current stack shape agrees with inspected historical generated metadata and
  current source line references. No fresh CUDA metadata was generated.
- The documentation patch rejection is disclosed, with a later state inspection;
  the exact failed tool stderr is not independently retained as a command log.

## C. Independent preservation verification

Direct rehashing against retained baselines succeeded, with zero changed/missing
paths. This is independently reproduced now, not inferred from audit summaries:

| Set | Files/hash entries verified |
|---|---:|
| All files predating latest repair | 11,448 |
| Original historical subset | 11,345 |
| Earlier safety-repair directory | 46 actual; 45 sealed plus seal |
| Earlier independent-review directory | 57 actual; 56 sealed plus seal |
| Latest hook-repair directory | 68 actual; 67 sealed plus seal |
| All result files at this review's start | 11,516 |
| Reviewed source snapshot | 144 |
| Project files at review start | 177 |
| Existing build metadata | 21 |
| Protected anchors, existing pinned CMake exception applied | 26 |
| Production/header/dependency baseline | 80 |
| Frozen protocol/matrix/resources | 3, plus independently pinned freeze file |

The freeze and existing CMake-review identities match the literal protected pins.
Production adapter src/cuda/cub_sort.cu remains SHA256
`b6d7f37c7494587fc6e4a676c00c166dc322d31cce96710811e3a4cb9cd8b9cb`.
CUB remains 3.0.1/version300001, commit
`f19d875da0d8bfb2e38c109b2b40522b8abbbbc3`; UPSTREAM.json remains SHA256
`477b1ee70b0a9113c9f98b263c19a31d05ccee54f45ce8476aec4cc98965ced1`.

Repair inventory independently matches BEFORE.json versus current bytes and
FILE_REVIEW.json: exactly four added and seven modified project files, no deletion:

- Added: scripts/ctest_build_guard.py, tests/ctest_fixture.py,
  tests/test_ctest_build_guard.py, docs/CTEST_BUILD_GUARD_v1.md.
- Modified: scripts/non_timing_tests.py, tests/test_cpu_gpu_safety.py,
  tests/test_cpu_gpu_comparison.py, docs/NON_TIMING_TEST_SELECTION_v1.json,
  README.md, docs/ROADMAP.md, docs/AUDIT.md.

All 68 new repair-evidence files are disjoint from the 11,448-file prior set and
confined to that repair directory. Earlier directory membership and sealed hashes
match exactly. Seal files are verified by later baseline maps, not self-hashed.
These are retained local hash chains, not externally signed historical attestation;
they do not prove absence of arbitrary transient writes before snapshots.

Prior repair command records and inspected inert bodies support its no-CTest/
no-build/no-prerequisite/no-timing/no-GPU claim. They are not an independent OS
process trace. One read-only command record, retained_cuda_metadata_inspection,
records `python3 -B -` without the stdin program, which prevents complete command
reproduction from the archive alone. Its rendered metadata was independently
inspected in this review; no fresh discovery is inferred from that record.

For **this** review, the actual executed inspection programs are retained and
contain no repository imports, selector/helper calls or workload invocations.
CTest discovery0; tests0; builds0; prerequisites0; resource checks0; benchmarks/
pilots/studies/timing trials0; GPU commands0. No commit/push/Git initialization.
No old evidence or project file was written. FINAL_INTEGRITY.json rechecks the
11,516 starting result paths, 177 project files and 21 build metadata files after
this audit is saved, and seals only the new review evidence.

## Decision and exact next step

The original directory-hook/include finding is repaired for the reviewed flat
registry and current absolute-path, quiescent invocation flow. B and preservation
checks pass on the stated evidence basis. A is not an unqualified PASS because
the reusable helper does not bind discovery to the exact checked path; universal
legacy coverage and atomic TOCTOU protection also must not be claimed.

**Next: a separate focused non-executing repair of A1 with inert mixed-cwd/relative-
path regression coverage, followed by independent review.** No source change is
authorized or applied by this review. Fresh prerequisites/resource checks and
study authorization remain separate explicit decisions. Stop here.
