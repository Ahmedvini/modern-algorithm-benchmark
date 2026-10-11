"""Consolidated recovery audit/seal: file operations only, no subprocess/workload."""
import datetime
import difflib
import hashlib
import json
from pathlib import Path
import shlex

r = Path.cwd(); e = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
def save(name, value):
    with (e / name).open('x') as f: json.dump(value, f, indent=2, sort_keys=True); f.write('\n')

before = read(e / 'BEFORE.json'); inventory = read(e / 'CHANGE_INVENTORY.json')
historical = {str(p.relative_to(r)): sha(p) for p in sorted((r / 'results').rglob('*'))
              if p.is_file() and not p.is_relative_to(e)}
assert historical == before['historical_results_sha256'], 'historical content/membership changed'
for field in ['protected_sha256', 'build_metadata_sha256', 'frozen_sha256']:
    assert all(sha(r / p) == digest for p, digest in before[field].items()), field
names = {'CMakeCache.txt', 'CTestTestfile.cmake', 'DartConfiguration.tcl', 'Makefile', 'compile_commands.json'}
build = {str(p.relative_to(r)): sha(p) for p in sorted((r / 'build').rglob('*')) if p.is_file() and p.name in names}
assert build == before['build_metadata_sha256']
paths = [r / 'AGENTS.md', r / 'README.md', r / 'CMakeLists.txt']
for directory in ['cmake', 'docs', 'include', 'scripts', 'src', 'tests', 'third_party']:
    paths.extend(p for p in (r / directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
project = {str(p.relative_to(r)): sha(p) for p in sorted(set(paths))}
modified = sorted(p for p, digest in before['project_sha256'].items() if project.get(p) != digest)
added = sorted(set(project) - set(before['project_sha256']))
assert modified == sorted(inventory['modified']) and added == inventory['added'] and not inventory['removed']
assert set(before['project_sha256']) <= set(project)
for p in ['scripts/ctest_build_guard.py', 'scripts/non_timing_tests.py', 'docs/NON_TIMING_TEST_SELECTION_v3.json',
          'docs/CPU_GPU_VALIDATION_POLICY_v2.json', 'docs/CPU_GPU_DRIVER_REVIEW_v1.json']:
    assert project[p] == before['project_sha256'][p]
previous = r / 'results/raw/cpu_gpu_final_preflight_20261011T074147349659Z'
assert sha(previous / 'FINAL_INTEGRITY.json') == before['verified_prior_seal_sha256']
for p, digest in read(previous / 'FINAL_INTEGRITY.json')['evidence_sha256'].items():
    assert sha(previous / p) == digest
diff = []
for name in modified + added:
    old = (e / 'before_sources' / name).read_text().splitlines(True) if name in modified else []
    if name in modified: assert sha(e / 'before_sources' / name) == before['project_sha256'][name]
    diff.extend(difflib.unified_diff(old, (r / name).read_text().splitlines(True), fromfile='before/' + name, tofile='after/' + name))
with (e / 'CHANGES_FINAL.diff').open('x') as f: f.write(''.join(diff))
save('PRESERVATION_VERIFIED.json', dict(historical_before=len(historical), historical_after_excluding_this_run=len(historical),
    exact_membership_and_sha256_match=True, unchanged_protected=len(before['protected_sha256']),
    unchanged_build_metadata=len(build), frozen_sha256=before['frozen_sha256'],
    before_project_files=len(before['project_sha256']), after_project_files=len(project),
    modified=modified, added=added, removed=[], project_sha256=project,
    previous_seal_and_23_members_verified=True, selector_guard_and_prior_policy_unchanged=True))

for name, count in [('final_identity_hardening_tests.json', 26), ('existing_validation_policy_tests.json', 9)]:
    log = read(e / name)
    assert log['exit_code'] == 0 and 'Ran ' + str(count) + ' tests' in log['stderr'] and log['stderr'].rstrip().endswith('OK')
assert read(e / 'focused_compatibility_tests.json')['exit_code'] == 1
assert read(e / 'session_auth_attempt.json')['exit_code'] == 0
assert 'No active sessions found on server' in read(e / 'session_auth_attempt.json')['stdout']

lines = ['# Commands and exit statuses', '', 'Repository cwd: ' + str(r), '',
         'Recovery scope: source/policy repairs, focused inert Python regressions, read-only identity/log checks and Colab CLI metadata. No CTest discovery/execution, configure/build, GPU workload/resource probe, benchmark, warmup, pilot or measured trial.', '',
         '## Initial unwrapped read-only inspection (each shell exit0)', '',
         'Exact inspection command groups, before the recorder was established:', '```sh',
         'pwd',
         "rg --files -g 'AGENTS.md' -g '*record.py' -g '*cpu_gpu*' -g '*validation_policy*' scripts tests docs results/raw/cpu_gpu_final_preflight_20261011T074147349659Z",
         'cat AGENTS.md',
         'cat results/raw/cpu_gpu_final_preflight_20261011T074147349659Z/FINAL_AUDIT.md',
         'cat results/raw/cpu_gpu_final_preflight_20261011T074147349659Z/COMMANDS.md',
         'cat results/raw/cpu_gpu_final_preflight_20261011T074147349659Z/FINAL_INTEGRITY.json',
         'cat results/raw/cpu_gpu_final_preflight_20261011T074147349659Z/record.py',
         'cat scripts/cpu_gpu_protocol.py', 'cat scripts/cpu_gpu_provenance.py',
         'cat docs/CPU_GPU_VALIDATION_POLICY_v2.json', 'cat scripts/cpu_gpu_validation_policy.py',
         "sed -n '1,210p' scripts/run_cpu_gpu_pilot.py", "sed -n '1,150p' scripts/analyze_cpu_gpu.py",
         'cat scripts/run_cpu_gpu_study.py',
         'cat results/raw/cpu_gpu_final_preflight_20261011T074147349659Z/finalize_review.py',
         'cat docs/CPU_GPU_COMPARISON_PROTOCOL_v1.md', 'cat docs/CPU_GPU_VALIDATION_POLICY_v2.md',
         'cat tests/test_validation_policy.py',
         "rg -n 'BUILD_COMPLETE|input_tool_sha256|binary_sha256|comparison_input' scripts/validate_cpu_gpu_pilot.py results/raw/bounded_resume_20261011T024034091796Z/*.py",
         'cat README.md', 'cat docs/ROADMAP.md', 'cat docs/EXPERIMENT_PROTOCOL.md', '```', '',
         'Some large combined outputs were truncated at the tool display. Targeted source reads and the complete retained inspection leaf provide the policy/runner evidence. No truncated display is treated as proof of reading omitted source.', '',
         'Bootstrap: `python3 -B -` used hashlib/json/pathlib to verify23 prior seal members, all original188 project files,80 protected files,65 build metadata and prior historical hashes; captured all12,261 current historical result hashes, created this unique directory and copied record.py. BEFORE.json retains exact maps. Exit0. No workload. Initial current root/AGENTS inspection also used only cat/pwd.', '']
for p in sorted(e.glob('*.json')):
    d = read(p)
    if not isinstance(d, dict) or 'argv' not in d or 'exit_code' not in d: continue
    lines += ['## ' + p.name, '', '- Exit: ' + str(d['exit_code']), '- Scope: ' + d.get('scope', ''),
              '- UTC: ' + d.get('started_utc', ''), '- cwd: ' + d.get('cwd', ''),
              '- Full output: [' + p.name + '](' + p.name + ')', '', '```sh', shlex.join(d['argv']), '```', '']
lines += ['## Other read-only inspection and evidence assembly (exit0)', '',
          'Python here-doc inspections read BUILD_COMPLETE.json, CORRECTNESS_BUNDLE.json, VALIDATION_CONTEXT.json, and baseline manifest field counts; inspected the retained pilot cuda_ctest.json lines containing Ran14/OK/framework names. No modules/test functions were executed in those inspections.', '', '```sh',
          "sed -n '1,180p' tests/test_cpu_gpu_safety.py", "sed -n '1,120p' tests/fixtures/cpu_gpu_provenance_reproducer.py",
          "sed -n '350,470p' tests/test_cpu_gpu_comparison.py", "sed -n '1,130p' scripts/non_timing_tests.py",
          'cat docs/CPU_GPU_DRIVER_REVIEW_v1.json', "sed -n '205,270p' scripts/run_cpu_gpu_pilot.py",
          "rg -n 'validate_retained_source|source_review|verify_source_extension' scripts/analyze_cpu_gpu.py scripts/run_cpu_gpu_pilot.py",
          "sed -n '1,100p' scripts/validate_cuda_sort.py", 'cat ' + str(previous.relative_to(r)) + '/COMMANDS.md',
          'cat ' + str(e.relative_to(r)) + '/CHANGES.diff', 'cat scripts/cpu_gpu_build_identity.py',
          'cat scripts/cpu_gpu_framework_compatibility.py', '```', '',
          'Evidence assembly used Python file I/O to save six original sources, construct the pinned new policy JSON, and later read (without extracting) the original run_cpu_gpu_study.py member from the sealed reviewed_source_v2.tar.gz. Its bytes matched BEFORE.json before being saved as a seventh original. difflib generated CHANGES.diff/CHANGE_INVENTORY.json. All these here-doc commands exited0. Source edits used apply_patch; final complete changes are CHANGES_FINAL.diff. No existing artifact was replaced.', '',
          '## Final consolidation', '', '```sh', 'python3 -B ' + str(e.relative_to(r)) + '/finalize_recovery.py', '```', '',
          'Exit0 is supported by RECOVERY_SEALED and FINAL_INTEGRITY.json. Hash/file operations only. The final seal excludes itself, and the after-seal read-only verification is a separate python3 -B - hash/manifest check with exit0; it does not alter the sealed evidence.', '',
          'Failure history retained: initial focused fixture run23 methods,12 errors due duplicated missing keyword; corrected fixture23/23, then24/24, then26/26 as coverage was added. Final strict-schema/import safety26/26. Existing policy9/9. The prior review parser failure/correction remains unchanged under its original paths. No GPU access or timing failure was retried/hidden.', '']
with (e / 'COMMANDS.md').open('x') as f: f.write('\n'.join(lines))

gates = [dict(gate=1, name='Framework compatibility and eligibility', status='BLOCKED',
              implementation='PASS: pinned explicit compatibility and public launch/analyzer regressions',
              blocker='Full evidence remains absent; new source snapshot needs independent review/reclassification. No prerequisite was upgraded.'),
         dict(gate=2, name='Colab authentication and environment', status='BLOCKED',
              implementation='Authentication metadata command succeeds; CLI0.7.4',
              blocker='Server reports no active sessions. No replacement created in this recovery; current T4/toolchain/resources cannot be inspected.'),
         dict(gate=3, name='Identity-matched GPU/framework validation', status='BLOCKED',
              implementation='No new GPU execution; retained bounded results preserved',
              blocker='No accessible intended build. Current production475/1900 and full GPU framework14 coverage still not established; timing runs forbidden here.'),
         dict(gate=4, name='comparison_input identity', status='BLOCKED',
              implementation='PASS: read-only snapshot/verification and missing/stale/mismatched regressions',
              blocker='Actual intended remote input-tool hash unavailable; old BUILD_COMPLETE lacks it. No historical manifest rewritten or substitute binary accepted.')]
save('GATES.json', dict(gates=gates, study_launched=False, benchmark_trials=0, verdict='NO-GO'))
table = '\n'.join('| ' + str(g['gate']) + ' | ' + g['name'] + ' | ' + g['status'] + ' | ' + g['implementation'] + '; ' + g['blocker'] + ' |' for g in gates)
audit = f'''# CPU/GPU recovery audit

**NO-GO — recovery repairs implemented; required validation gates remain open.**

No benchmark/timing sample, pilot, warmup, measured trial, full study,100M workload,
CTest discovery/test, native executable, build/configuration or GPU command ran.
Only the focused inert tests below executed. No commit/push/Git initialization.

## Gate decision

| Gate | Requirement | Status | Evidence / remaining condition |
| --- | --- | --- | --- |
{table}

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
'''
with (e / 'FINAL_AUDIT.md').open('x') as f: f.write(audit)
members = {str(p.relative_to(e)): sha(p) for p in sorted(e.rglob('*')) if p.is_file()}
save('FINAL_INTEGRITY.json', dict(schema_version=1, created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    seal_excludes_itself=True, seal_command=['python3', '-B', str(e.relative_to(r)) + '/finalize_recovery.py'],
    evidence_sha256=members, evidence_files_excluding_seal=len(members),
    historical_files_verified=len(historical), protected_files_unchanged=80, build_metadata_unchanged=65,
    frozen_sha256=before['frozen_sha256'], project_after_sha256=project,
    modified=modified, added=added, native_tests=0, ctest_discovery=0, new_builds=0,
    fresh_inert_test_methods=35, gpu_workloads=0, benchmark_trials=0, warmups=0,
    study_launched=False, gates=gates, verdict='NO-GO'))
print('RECOVERY_SEALED', len(members), 'members;', len(historical), 'historical files preserved')
