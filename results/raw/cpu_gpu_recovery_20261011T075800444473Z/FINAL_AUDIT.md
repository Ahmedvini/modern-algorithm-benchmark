# CPU/GPU recovery audit

**NO-GO — recovery repairs implemented; required validation gates remain open.**

No benchmark/timing sample, pilot, warmup, measured trial, full study,100M workload,
CTest discovery/test, native executable, build/configuration or GPU command ran.
Only the focused inert tests below executed. No commit/push/Git initialization.

## Gate decision

| Gate | Requirement | Status | Evidence / remaining condition |
| --- | --- | --- | --- |
| 1 | Framework compatibility and eligibility | BLOCKED | PASS: pinned explicit compatibility and public launch/analyzer regressions; Full evidence remains absent; new source snapshot needs independent review/reclassification. No prerequisite was upgraded. |
| 2 | Colab authentication and environment | BLOCKED | Authentication metadata command succeeds; CLI0.7.4; Server reports no active sessions. No replacement created in this recovery; current T4/toolchain/resources cannot be inspected. |
| 3 | Identity-matched GPU/framework validation | BLOCKED | No new GPU execution; retained bounded results preserved; No accessible intended build. Current production475/1900 and full GPU framework14 coverage still not established; timing runs forbidden here. |
| 4 | comparison_input identity | BLOCKED | PASS: read-only snapshot/verification and missing/stale/mismatched regressions; Actual intended remote input-tool hash unavailable; old BUILD_COMPLETE lacks it. No historical manifest rewritten or substitute binary accepted. |

All four overall gates remain BLOCKED for a subsequent launch decision. PASS
implementation subresults are not claims of current GPU or full-study eligibility.
See [GATES.json](GATES.json), [OFFLINE_VERIFICATION.json](OFFLINE_VERIFICATION.json),
[COMMANDS.md](COMMANDS.md), and [FINAL_INTEGRITY.json](FINAL_INTEGRITY.json).

## Root causes and repair

The old source guard permits only the earlier CMake integration. The bounded
framework additionally changed its prepared header and CUDA source, so the
launcher and independently frozen analyzer correctly rejected three mismatches.
The new explicit cpu_gpu_framework_compatibility_v1 path pins the exact three
already reviewed after-digests through the immutable validation-v2 policy and
original freeze/CMake trust roots. Unknown/missing/mutated roots fail closed.
Original production-CUB and dependency hashes remain independently authoritative.

Legacy default behavior and historical pilot analysis remain unchanged. The full
runner requires explicit CLI/prerequisite agreement, a full v2 nine-gate coverage
bundle, retained hashed records and current build/source/comparison/input identity.
The analyzer enforces the same opt-in requirements. Actual retained CUDA CTest
output must contain exactly one passed GPU framework group with14 methods and
no skips there; host-only skips do not count as a GPU pass. Production output must
parse as475/1900 through the established verifier. Command paths identify that
build, not a historic worker. Prepared latency never becomes primary host-call
timing. Correctness-only artifacts and partial/failed coverage remain rejected.

The old bounded BUILD_COMPLETE omitted comparison_input despite the launcher's
existing input-tool hash requirement. New cpu_gpu_build_identity.py snapshots all
11 required executable/library/metadata entries, including comparison_input,
without executing them. It rejects missing/aliased paths and wrong build settings.
The opted-in launcher rechecks exact paths/bytes against that snapshot before
execution and completion; analysis checks retained source, executable and compile
identities. A changed input binary is rejected even if its top-level prerequisite
digest is updated. A freshly captured hash is **not** proof of build provenance:
configure/build/link logs and independent review are still required. No actual
remote input hash was available; no value has been fabricated.

## Changes and review

Seven existing files modified: README.md and docs/ROADMAP.md document the blocked
recovery; cpu_gpu_protocol.py/provenance.py add the explicit pinned source path;
run_cpu_gpu_pilot.py keeps shared full prerequisites strict and retains new records;
run_cpu_gpu_study.py exposes the explicit opt-in; analyze_cpu_gpu.py independently
checks compatible evidence and disallows compatibility in historical pilot mode.

Five additions: docs/CPU_GPU_FRAMEWORK_COMPATIBILITY_v1.json and .md,
scripts/cpu_gpu_framework_compatibility.py, scripts/cpu_gpu_build_identity.py,
tests/test_framework_compatibility.py. No C++/CUDA production/test code, CMake,
selector/guard, old policy or frozen file changed. Full original-file snapshots,
[CHANGES_FINAL.diff](CHANGES_FINAL.diff) and CHANGE_INVENTORY.json are retained.
The diff was inspected, with a targeted complete reread of the two new modules
after the combined diff display truncated. Final AST/provenance checks passed.

The unchanged v3 selector has the exact original19 CPU names and no new test
registration. It intentionally rejects the new Python-source snapshot before
discovery: OFFLINE_VERIFICATION records that expected rejection. It was not
bypassed, rewritten or run against a real build. A new independently reviewed
additive selection snapshot is needed before native-suite reuse/execution.

## Fresh tests and failures

Final focused test_framework_compatibility.py:26 passed,0 failed/skipped.
Existing test_validation_policy.py:9 passed,0 failed/skipped. These35 distinct
methods are synthetic/static; fake binaries are never executed, subprocess,
shell and runner invocation are blocked. Production public launch-validation and
analyzer metadata paths are exercised, including valid legacy and compatible
fixtures, altered adapter/pin/framework/root identities, missing/failed/stale
coverage, command-path mismatches, absent/stale input-tool hashes, and diagnostic
substitution rejection. Positive full-evidence fixtures model metadata only;
they are not observed performance or GPU evidence.

Initial23-method attempt:11 passed and12 fixture-construction errors (duplicate
missing keyword from inherited pilot coverage). Its exit1/log is retained.
Fixture-only correction passed23/23; added cases passed24/24 and26/26; final
schema/import-safety review again passed26/26. No production behavior was changed
to fix a test. All attempts are additive JSON logs. The earlier preflight parser
failure and corrected v2 remain preserved and sealed, not regenerated.

Retained native Release21/21 and ASan/UBSan21/21 summaries were read and counted
again, not rerun. Their C++ sources remain unchanged, but this recovery's Python
changes do not inherit a fresh native-suite PASS. Retained prepared163/489,
workspace3 sizes and worker12 are historical current-before-repair evidence;
none establishes present-session availability or missing current full framework
coverage. No new sanitizer suppression or leak-policy change. Prior build logs
contain CPU0 warnings and CUDA367 nvcc/GCC line-marker warnings, independently
recounted here. Historical341 belongs to an earlier build. No compiler ran here.

## Session and exact remaining prerequisites

Git status returned128: repository has no Git metadata; no commit/branch identity
invented. Source identity is the before/current file maps. Colab CLI0.7.4 help and
version succeeded. Unlike the previous OAuth-blocked attempt, colab sessions
returned0 and reported that it pruned one stale local record and **no active
sessions exist on the server**. Authentication succeeds for that metadata call;
no T4 session, compiler/runtime/CUB installation, resources or worker topology was
observed remotely. No credentials were requested, supplied or retained. No new
session or replacement build was created by this recovery.

Next prerequisites: independently review this compatibility/diff and an additive
non-timing selection snapshot; establish an approved accessible T4 session;
validate/identify its exact source/build and comparison_input bytes with the new
snapshot plus original build evidence; obtain applicable current production and
framework coverage without relabeling old results. Missing timing-framework
evidence cannot be generated under this recovery's non-timing authorization.
Fresh all-size resource/cgroup/affinity/quota and untimed worker checks remain
necessary before a separately authorized final preflight. No launch authorized
or attempted here. Resource observations and future session lifetime are not
guarantees. Ordinary content seals are not external attestations of remote logs.

## Consolidated preservation

All12,261 pre-existing result files retain exact membership and SHA256 bytes.
This includes every prior failed attempt, parser version and historical study.
All80 protected production/header/dependency files,65 existing build metadata
files, four frozen inputs, selector/path guards and earlier policy remain intact.
Original26 anchor files are unchanged relative to the captured starting state;
the same three approved historical exceptions to the original freeze remain.
CUB3.0.1/CCCL f19d875da0d8bfb2e38c109b2b40522b8abbbbc3 is unchanged.
Project inventory188 before /193 after:7 intentional modifications,5 additions,
0 removals. The new code/build/test source map has153 files versus150 before.
Every other project byte matches. Prior final-preflight seal and23 members were
independently rechecked. PRESERVATION_VERIFIED.json and FINAL_INTEGRITY.json
record exact maps/counts; counts alone were not used as proof of preservation.

Stop after recovery. Full-study launch still requires a separate final preflight
and explicit authorization. No benchmark timings or trials occurred.
