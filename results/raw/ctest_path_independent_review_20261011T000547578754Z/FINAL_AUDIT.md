# Independent review: CTest path-identity repair

**Verdict: PASS.** This applies to the focused path-identity repair under the
existing trusted-tool, exclusively owned, quiescent-tree contract. It does not
authorize fresh prerequisites, resource checks, discovery, tests, or study execution.
No new blocking defect was found in the repaired caller/callback path binding.

Review evidence: `results/raw/ctest_path_independent_review_20261011T000547578754Z/`.
See [commands/statuses](COMMANDS.md), [independent comparisons](INDEPENDENT_VERIFICATION.json),
[complete starting result inventory](BEFORE_ALL_RESULTS.json), and
[final preservation/seal](FINAL_INTEGRITY.json).

## Method and inspected evidence

Read the specified path-repair audit, command log and integrity manifest, previous
guard-review audit, actual source diff, retained before/reviewed/candidate source,
and recorded initial/final test output. Earlier safety-repair and independent
review audits supplied context. Full read outputs are retained in this directory's
inspection command JSON files; some terminal renderings were truncated, so the
path tests and retained failure/success logs were inspected separately in bounded
reads. No repair author's checker, repository module, selector or test was run.

Content inspection covered:

- `scripts/non_timing_tests.py`, `scripts/ctest_build_guard.py`;
- `scripts/validate_cpu_gpu_pilot.py`, `scripts/run_cpu_gpu_pilot.py`, and relevant
  `scripts/cpu_gpu_protocol.py` definitions;
- `tests/test_ctest_build_guard.py`, `tests/ctest_fixture.py`, and the
  `SelectorTests` class and surrounding imports in `tests/test_cpu_gpu_safety.py`;
- `docs/CTEST_BUILD_GUARD_v1.md`, the selection policy, frozen comparison inputs,
  CMake review pin, `third_party/cub/UPSTREAM.json`;
- direct CTest sites in `scripts/validate_cuda_sort.py` and
  `scripts/validate_cuda_timing.py` (static text search only);
- repair `SOURCE_DIFF.patch`, `FILE_REVIEW.json`, `run_inert_tests.py`, all three
  relevant retained test records and candidate policy/source; the prior audit and
  seal chains named below.

Additional files were read for SHA-256 comparison, not claimed to receive a full
semantic code review. Exact hash maps, changed-file inventory, test method names,
line numbers, source pins and entry-point search results are in
`INDEPENDENT_VERIFICATION.json` and the retained inspection records.

This review performed only text/directory reads, JSON parsing, SHA-256 hashing,
and AST comparison. Its own verifier imports standard-library modules only and
does not evaluate parsed repository ASTs. Only this new exclusive evidence
directory was written. There was no CTest invocation, test run, configure/build,
prerequisite/resource check, benchmark, pilot, timing trial, GPU command, commit,
push, or study authorization.

## A. Path identity

The earlier defect was real: the guard returned an absolute identity while the
helper/CLI passed the original relative input onward; the subprocess wrapper's
fixed cwd could reinterpret it. Current code closes that specific defect:

| Stage | Actual source and behavior |
|---|---|
| CLI parsing | `non_timing_tests.py:155-163`: argparse retains the caller Path only until the first gate |
| Initial validation | `non_timing_tests.py:70-73` validates source policy then calls the shared static tree guard |
| Guard identity | `ctest_build_guard.py:106-110,156`: makes the caller path absolute, rejects missing/aliased/symlinked trees, returns the checked absolute spelling |
| Helper discovery | `non_timing_tests.py:138-141`: replaces the original argument with `Path(guarded['build_dir'])` before constructing discovery argv |
| CLI discovery | `non_timing_tests.py:163-171`: retains the same guard return at164 and uses it in subprocess argv at168 and selection at171 |
| Direct selection | `non_timing_tests.py:76-78`: retains its guard return immediately; no later resolution of the original relative input |
| Selection checks/plan | `non_timing_tests.py:85-127`: registry, commands and working-directory checks, and generated `--test-dir`, use the retained absolute build variable |
| Helper boundary checks | `non_timing_tests.py:143-149`: selection and final gate take the retained absolute path; complete metadata fingerprints must match before execution-command construction/use |
| Real callback wrapper | `validate_cpu_gpu_pilot.py:34-37` delegates to `run_cpu_gpu_pilot.invoke:20-26`, whose Popen uses `cwd=ROOT`; an absolute `--test-dir` is independent of that cwd |

The CLI's retained-JSON branch at165 also retains the same build identity; it
cannot bypass static validation. CLI output is only a plan. The direct selector
does not execute discovery or tests. The helper's actual future execution argv
comes from that same validated plan, with the constrained optional env prefix.

The four correctness-only prerequisite call sites at
`validate_cpu_gpu_pilot.py:47,56,65,83` use the shared helper. Its build directories
are already absolute children of ROOT (`:29-32`). Static search finds no alternate
selector/discovery entry point bypassing the repaired assignment. The legacy
full-protocol branches (`:49,58,67,85`) and standalone CUDA validators remain
outside this policy. They are unchanged and receive no blanket approval here.

The original relative path is validated before adopting the returned identity,
so the repair does not erase evidence of a symlink alias by resolving it early.
`expected_command` still resolves absolute build-derived command paths for
comparison; it no longer gets the original relative build input after the gate.
Changing callback cwd cannot retarget these absolute paths. Absolute inputs follow
the same flow. The exact retained string and fingerprints, not a freshly resolved
original argument, govern discovery/selection/execution construction.

Qualification: these are checked absolute path strings, not open directory
handles or atomic locks. A concurrent writer or mount change can still replace
metadata/files between a final check and a future CTest open. Boundary rechecks
detect the tested inter-boundary changes but do not prove race freedom. The
existing documented quiescent-tree/trusted-executable assumption remains necessary
(`docs/CTEST_BUILD_GUARD_v1.md:72`). No real discovery/toolchain behavior was tested
in this review.

## B. Regression coverage and retained failures

Inspected eight added methods in `tests/test_ctest_build_guard.py`; none rerun:

| Line | Coverage |
|---:|---|
| 67 | Relative and absolute helper inputs, different callback cwd and unsafe inert decoy; checks exact guard-return path in both callback commands and all three validations |
| 95 | Callback changes Python cwd after discovery; later selection/recheck/execution remain absolute |
| 109 | Actual CLI main with relative input and explicitly fake discovery that changes cwd |
| 124 | Retained-JSON CLI branch with cwd changed immediately after actual guard validation |
| 142 | Actual direct selector with cwd changed immediately after actual guard return |
| 154 | Unsafe relative caller tree rejected before callback despite another clean tree at the relative callback location |
| 163 | Relative symlink alias still rejected before any callback |
| 169 | Unsafe relative CLI tree rejected before mocked subprocess discovery |

Positive tests call production public paths. Their gate wrappers call the actual
guard and record its result; they do not fabricate a successful fingerprint.
The first test checks both discovery and execution argv against that result,
compares all three guard fingerprints and checks later gate arguments. Its
absolute subcase complements the relative case and existing absolute CLI cases
at297/304. Rejection cases assert no callback/subprocess is reached.

Test setup at31-41 blocks subprocess run/Popen/call/check_call/check_output and
os.system, clears the environment, and writes temporary inert literal metadata.
The fixture writer creates no executable. The retained wrapper blocks process
launch before importing the two test classes; its `new` scope selects exactly
eight methods and `all` scope exactly36 guard plus11 selector methods. It does
not collect the separate provenance or native/timing suites. Callback responses
such as '0 tests failed out of19' are fake Python strings, not real CTest output.
The temporary callback cwd models the real wrapper's different cwd; the real
Popen wrapper itself is inspected, not exercised by these tests.

Retained records, independently checked against source method names and sealed
bytes, show:

| Repair command record | Recorded exit | Recorded outcome |
|---|---:|---|
| `commands/inert_reproducer_before_fix.json` | 1 | 8 methods:3 pass,4 failures,1 error |
| `commands/inert_regressions_after_repair.json` | 0 | 8/8 pass |
| `commands/all_inert_selector_regressions.json` | 0 | 47/47 pass; no failures/errors/skips |

All paths in this table are relative to
`results/raw/ctest_path_repair_20261010T234224414430Z/`.
These are historical execution results, not fresh tests performed in this review.
The47 includes the eight new methods, rather than55 distinct methods.

The preserved candidate selector equals the retained pre-fix selector bytes;
its test file equals current new-test bytes and its candidate policy points to
that retained old selector. Before-fix logs show the relative discovery argument
failing the absolute assertion, helper/CLI argv containing 'build', retained-JSON
revalidation selecting a missing tree after cwd change, and direct-selection
command mismatch after re-resolution. The absolute helper subcase and three
fail-closed methods already succeeded. Thus the initial failure is attributable
to the intended path defect, not weak assertions or real CTest execution.

Fixtures derive generated metadata from the policy; they do not independently
validate a CMake interpreter. Recorded logs and mocks support the stated inert
scope, but are not an independent OS process trace of the past repair session.

## C. Selection and unchanged protections

Independent JSON comparison confirms every policy field other than the reviewed
source map is byte-equivalent in value to the retained pre-repair policy. Source
keys remain144; exactly two digests changed, for the selector and new guard tests.
All144 hashes match current source bytes. This is explicit reviewed local policy
renewal, not automatic production enrollment or a frozen-study update.

The approved CPU list remains exactly:

`baselines, cli, comparisons, cpu_gpu_comparison_framework, cuda_benchmark_analysis,
cuda_preflight, cuda_sort_handoff, datasets, environment_manifest, memory,
memory_unsupported, mergesort, metrics_cli, pdqsort, quicksort, radixsort, searching,
structures, timsort`.

The ten excluded CPU groups remain benchmark_framework, comparison_engine,
experiment_pipeline, parallel_framework, parallel_mergesort, search_framework,
search_timing, structure_framework, structure_timing and timing. The known32768
timing path is therefore excluded. GPU correctness remains explicit opt-in; GPU
timing is excluded. No selection was executed or regenerated here.

The diff changes only path retention in the three selector entry paths. The
shared guard, wrapper restrictions, strict source/command/properties validation,
exact anchored regex, serial execution argv, hook/include/subdirs/symlink rejection
and boundary fingerprints are unchanged. AST comparison confirms all28 existing
guard test bodies unchanged, with eight additions; all11 existing selector methods
also retain their earlier source identity. Seven project files changed in the
repair, exactly matching its inventory and before/reviewed copies. No unrelated
behavior was weakened by this repair.

## D. Independently reproduced preservation

These are fresh SHA-256 comparisons of actual files against available retained
baselines, not conclusions copied from the previous audit:

| Set | Entries/files verified | Differences |
|---|---:|---:|
| All files predating the path repair | 11,556 | 0 |
| Original historical subset | 11,345 | 0 |
| Safety repair evidence directory | 46 actual,45 sealed plus seal | 0 |
| Earlier safety independent-review directory | 57 actual,56 sealed plus seal | 0 |
| Hook repair evidence directory | 68 actual,67 sealed plus seal | 0 |
| Path-defect review directory | 40 actual,39 sealed plus seal | 0 |
| Latest path repair evidence directory | 48 actual,47 sealed plus seal | 0 |
| Frozen protocol/matrix/resource members | 3 plus pinned freeze | 0 |
| Protected anchors (existing pinned CMake exception) | 26 | 0 |
| Production/header/dependency baseline | 80 | 0 |
| Build metadata | 21 | 0 |
| Project files at this review's start | 177 | 0 |

Seal membership is checked along with every sealed digest. The48 repair files
are additive to the11556 prior paths. Earlier seals are themselves covered by
later retained hash inventories; the current seal is pinned by this review's
own starting snapshot. Local hash chains are not external signed attestation.

The freeze and independent CMake-review literal pins match; current CMake uses
the previously documented reviewed exception, not an unreported new alteration.
Production adapter remains SHA256
`b6d7f37c7494587fc6e4a676c00c166dc322d31cce96710811e3a4cb9cd8b9cb`.
CUB UPSTREAM pin remains SHA256
`477b1ee70b0a9113c9f98b263c19a31d05ccee54f45ce8476aec4cc98965ced1`,
release3.0.1/version300001, commit
`f19d875da0d8bfb2e38c109b2b40522b8abbbbc3`. This verifies retained project pin
metadata, not a fresh installed GPU dependency or runtime.

This review's initial generic snapshot accidentally excluded one historical
__pycache__ file along with project caches and reported11603. The complete scan
found11604, with no missing file: the excluded
`results/raw/cpu_gpu_protocol_20261009T234954580281Z/__pycache__/build_protocol_assets.cpython-312.pyc`
matches its repair-before digest. Both initial and supplemental inventories are
retained. Final preservation includes all11604, including this file, without
forcing counts or deleting caches.

One static rg invocation named nonexistent `third_party/cub/cub_version.cuh` and
reported a read error (enclosing multi-read shell exit0; the individual rg status
was not separately captured). Its stderr is
retained in `static_call_boundaries.json`. A subsequent `rg --files third_party/cub`
exit0 confirmed only LICENSE, README.md and UPSTREAM.json are present. The
review therefore verifies the actual pin rather than pretending the version
header is vendored. No workload or project file change resulted.

The final seal repeats exact result/project/build membership and hash comparisons
after this audit and command inventory are written. All new files must be
confined to this review directory. Matching counts alone are never used as
content-preservation proof.

## Limitations and next permitted action

No blocking gap remains for the focused original defect. Existing limits remain:
quiescent-tree and trusted-tool assumptions, no executable attestation/atomic
filesystem lock, narrow supported metadata layouts, unguarded legacy workflows
outside this policy, and no fresh real CTest/CPU/GPU integration evidence here.
Past no-workload claims are supported by recorded commands and inspected mocks,
not a complete independent process trace or proof against transient writes.

This review stops here. The next permitted action is a separate explicit
authorization decision specifying whether and how to run fresh validation under
the reviewed policy. Such validation and any eventual study execution are separate
gates. This PASS does not grant either authorization.
