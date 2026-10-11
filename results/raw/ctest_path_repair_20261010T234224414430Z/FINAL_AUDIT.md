# Guarded CTest path-identity repair

**Repair implemented; focused inert validation passes. Separate independent
review is still required before any prerequisite checks or study launch.**
Study launch remains **NO-GO**. Stop after this audit.

Evidence: `results/raw/ctest_path_repair_20261010T234224414430Z/`.
[Exact commands/statuses](COMMANDS.md), [final integrity](FINAL_INTEGRITY.json),
[before snapshot](BEFORE.json), [preservation checks](AFTER_VERIFIED.json),
[file review](FILE_REVIEW.json), [exact diff](SOURCE_DIFF.patch).

## Inspection, defect and root cause

Read AGENTS.md, current README/roadmap/experiment-protocol sections, the latest
independent review FINAL_AUDIT.md, COMMANDS.md and actual FINAL_INTEGRITY.json.
Inspected scripts/non_timing_tests.py, scripts/ctest_build_guard.py,
scripts/validate_cpu_gpu_pilot.py, scripts/run_cpu_gpu_pilot.py, protocol/provenance
helpers, tests/ctest_fixture.py, tests/test_ctest_build_guard.py and the inspected
existing selector-class wrapper. The earlier review had already inspected the
existing SelectorTests source; its source identity is unchanged. No Git metadata
exists; no repository was initialized or destructive Git operation performed.

The static guard converts its input to an absolute path, rejects aliased/symlinked
trees, and returns the checked path as build_dir. The helper formerly discarded
that returned identity when building discovery argv and used the original caller
argument instead. The project's invoke wrapper launches children with cwd=ROOT,
so a relative input validated from another cwd could name a different discovery
tree. The CLI also reused its original argument after the guard. Direct selection
resolved the original argument again later, after validation. A change in cwd
could therefore retarget subsequent interpretation even without a changed file.

No CTest or hook was run to establish this defect. The retained pre-fix regression
uses actual production static-validation/selection paths with inert callbacks.

## Exact repair and complete call paths

Only scripts/non_timing_tests.py behavior changed:

1. `select_tests:76` first calls pre_discovery_gate with the original argument,
   then takes `Path(guard['build_dir'])` at78. It no longer resolves the original
   relative argument later. Command validation, working-directory validation and
   generated execution argv all use that checked identity.
2. `selected_ctest:133` first checks allowed wrappers and gates the original path
   at138. At140 it takes `Path(guarded['build_dir'])`. Discovery at141, the second
   static validation via select_tests at143 and final recheck at147 use that path.
   The full metadata fingerprints must still match. The execution callback at149
   receives the exact plan's absolute --test-dir, serial --parallel1 and anchored
   approved-name regex. No path is derived again from the original relative input.
3. CLI argparse still accepts --build-dir as Path. Its gate at163 validates the
   original argument; at164 it retains the guard's returned identity. Discovery
   at168 and select_tests at171 use it. --discovery-json still avoids discovery
   and still passes through validation. The CLI only prints/saves a plan.

The shared gate itself is unchanged: load_manifest verifies the complete reviewed
source snapshot, then validate_build_tree statically validates the original tree.
Canonicalization is not moved before this check, so relative symlink aliases and
unsafe trees still fail closed before any discovery callback. Flat-layout grammar,
hook/include/subdirs rejection, properties, environment restrictions, wrapper
policy and boundary-fingerprint checks are unchanged.

Prerequisite runner tracing (inspection only): its parser constructs a new build
root under absolute ROOT; correctness-only Release:47, sanitizer:56, leak retry:65
and CUDA:83 call selected_ctest. Its callback delegates to invoke, which sets
cwd=ROOT. The checked absolute path now remains independent of that child cwd.
The runner was not executed. Legacy full-protocol CTest branches remain unchanged
and outside this correctness-only selector; this repair does not approve them.

## Files changed

Exactly seven existing project files modified; no project file added/deleted:

| File | Purpose |
|---|---|
| scripts/non_timing_tests.py | Retain returned guard identity in helper, CLI and direct selection |
| tests/test_ctest_build_guard.py | Add eight inert path/cwd and rejection regressions |
| docs/NON_TIMING_TEST_SELECTION_v1.json | Explicitly renew only the two changed source digests |
| docs/CTEST_BUILD_GUARD_v1.md | Document path identity and inert validation scope |
| README.md | Link repair and continuing independent-review gate |
| docs/ROADMAP.md | Record repaired path handling; retain study NO-GO |
| docs/AUDIT.md | Record actual commands/results and preservation evidence |

The local source-policy renewal is an explicit repair-time operation, not runtime
auto-enrollment or a frozen-protocol update. Every classification, command,
metadata policy field and all other source digests remain unchanged. FILE_REVIEW
and SOURCE_DIFF retain exact before/after bytes/hashes. Static AST comparison
confirms all 28 pre-existing guard test bodies are unchanged; eight methods added.

## Regression coverage and actual results

Executed only the inspected inert test wrapper under this new evidence directory.
It blocks subprocess run/Popen/call/check_call/check_output and os.system before
test imports. New guard-test setUp also blocks them. CLI subprocess paths are
replaced with explicit Python fakes; callbacks return literal fixture JSON/text.
No binary is created or invoked. cwd changes occur only inside temporary-fixture
contexts and are restored. The fixed-cwd callback is modeled in temporary paths;
the real invoke wrapper is inspected, not launched.

Eight new methods in tests/test_ctest_build_guard.py cover:

| Lines | Coverage |
|---|---|
| 67 | Relative and absolute helper arguments; different callback cwd and inert unsafe decoy tree; exact returned guard path in both commands and all three gates |
| 95 | Callback changes Python cwd after discovery; selection/recheck/execution stay bound |
| 109 | Actual CLI main with relative --build-dir and fake discovery changing cwd |
| 124 | Retained-JSON CLI branch; cwd changes after actual static validation |
| 142 | Direct select_tests; cwd changes after actual gate return |
| 154 | Unsafe relative caller tree rejected before a differently rooted callback |
| 163 | Relative symlink alias remains rejected before any callback |
| 169 | Unsafe relative CLI tree rejected before mocked discovery |

The positive tests compare commands/plan identities against the actual guard
return. They do not mock away source/metadata validation. Original unsupported
layouts and unsafe trees are not accepted to make these cases pass.

| Command (recorder prefix and full output in COMMANDS.md) | Exit | Result |
|---|---:|---|
| python3 -B results/raw/ctest_path_repair_20261010T234224414430Z/run_inert_tests.py new, before fix | 1 | 8 methods: 3 pass, 4 failures, 1 error |
| Same `new` command, after fix | 0 | 8/8 pass, zero failures/errors/skips |
| python3 -B results/raw/ctest_path_repair_20261010T234224414430Z/run_inert_tests.py all | 0 | 47/47 pass: 36 guard +11 existing selector methods; zero failures/errors/skips |

The full47 include the eight new methods; these are not55 distinct tests.
The old-code failure is deliberately retained, not called a successful command:
[failure output](commands/inert_reproducer_before_fix.json), candidate source,
tests and source policy under reproducer_before_fix/. Four failures identify
unbound relative discovery/CLI arguments and retained-JSON revalidation; the
direct-selection error identifies later re-resolution from a changed cwd.
The absolute helper subcase passes even in that old-code run. The three existing
fail-closed cases among the new methods pass before and after the repair.

[Focused repaired output](commands/inert_regressions_after_repair.json) and
[all inert output](commands/all_inert_selector_regressions.json) retain full logs.
No unexpected repair/test/inspection command failed. Unit-runner elapsed duration
is not a sorting measurement. No broad framework/provenance collection, native
test group or CUDA test was run. No compiler warnings can be assessed here because
no build occurred; no warning was emitted by the final inert runs.

## Approved selection and preservation

Static policy comparison and mocked selection both preserve exactly:

baselines, cli, comparisons, cpu_gpu_comparison_framework, cuda_benchmark_analysis,
cuda_preflight, cuda_sort_handoff, datasets, environment_manifest, memory,
memory_unsupported, mergesort, metrics_cli, pdqsort, quicksort, radixsort, searching,
structures, timsort.

parallel_mergesort and all other timing groups remain excluded. The GPU opt-in
metadata test remains inert and cannot select GPU timing. No19-test plan ran.

BEFORE_VERIFIED.json and AFTER_VERIFIED.json are fresh direct byte/hash checks:

| Set | Before/after verified | Differences |
|---|---:|---:|
| All pre-existing result files | 11,556 /11,556 | 0 |
| Original historical subset | 11,345 /11,345 | 0 |
| Earlier safety repair | 46 actual files, 45 sealed plus seal | 0 |
| Earlier independent review | 57 actual files, 56 sealed plus seal | 0 |
| Earlier hook repair | 68 actual files, 67 sealed plus seal | 0 |
| Latest path-defect review | 40 actual files, 39 sealed plus seal | 0 |
| Frozen protocol/matrix/resource members | 3 plus independently pinned freeze | 0 |
| Protected anchors with existing pinned CMake exception | 26 | 0 |
| Production/header/dependency files | 80 | 0 |
| Existing build metadata | 21 | 0 |

The original frozen manifest and CMake review pins match their independently
retained literal identities. Production adapter SHA256 remains
`b6d7f37c7494587fc6e4a676c00c166dc322d31cce96710811e3a4cb9cd8b9cb`.
CUB3.0.1/version300001 pin SHA256 remains
`477b1ee70b0a9113c9f98b263c19a31d05ccee54f45ce8476aec4cc98965ced1`.
No protocol/matrix/resource file, production adapter, CUB pin, CMake source,
build-tree metadata or prior result was modified. Earlier seal membership is
verified as well as hashes. These are local retained baselines, not externally
signed attestations or proof of arbitrary process behavior before snapshots.

The 177-file project inventory differs only in the seven listed paths; the
144-file reviewed source set has exactly two renewed digests. Newly retained
results are confined to this exclusive evidence directory. FINAL_INTEGRITY.json
rechecks every prior result and final project/build inventory after audit creation,
then records exact added evidence/total counts and seals new evidence only.

## Safety, limitations and next gate

Actual CTest discovery0; CTest/native tests0; configure/build0; prerequisite/
resource checks0; timing-bearing tests0; benchmarks/pilots/studies0; GPU commands0.
Only focused inert Python unit methods and static/hash checks ran. No commit,
push, Git initialization, historical cleanup or destructive operation occurred.

The repair binds path strings to a validated absolute identity; it does not lock
the filesystem or attest executable binaries. Trusted tools and an exclusively
owned quiescent tree are still required; external concurrent changes between
validation and a future CTest open remain possible. Unsupported generated layouts
still fail closed. Legacy full-protocol workflows remain outside this policy.
Fresh CPU/GPU execution and prerequisite eligibility are not established by mocks.

**Exact next gate: separate independent review of this repair and evidence.**
No prerequisite/resource checks or study launch may proceed on this repair audit.
Full-study authorization remains NO-GO and requires a separate explicit decision.
