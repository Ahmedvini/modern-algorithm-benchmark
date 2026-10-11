"""Evidence-only stopped-validation audit. No project imports or subprocesses."""
import datetime
import hashlib
import json
import shlex
from pathlib import Path

R = Path.cwd()
E = Path(__file__).resolve().parent

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def new(name, value):
    with (E / name).open('x') as f:
        json.dump(value, f, indent=2, sort_keys=True)
        f.write('\n')

b = json.loads((E / 'BEFORE.json').read_text())
preservation = {}
for key, mapping in b.items():
    differences = [p for p, h in mapping.items() if not (R / p).is_file() or sha(R / p) != h]
    preservation[key] = {'count': len(mapping), 'changed_or_missing': differences}
    assert not differences, (key, differences)
actual = {str(p.relative_to(R)) for p in (R / 'results').rglob('*') if p.is_file() and not p.is_relative_to(E)}
assert actual == set(b['historical_results_sha256']), 'historical membership changed'
preservation['historical_membership'] = {'before': len(actual), 'after': len(actual), 'added': [], 'missing': []}

review = R / 'results/raw/cpu_gpu_prelaunch_review_20261011T012430643251Z'
isolated = R / 'results/raw/isolated_colab_revalidation_20261011T011459127026Z'
for directory in [review, isolated]:
    seal = json.loads((directory / 'FINAL_INTEGRITY.json').read_text())['evidence_sha256']
    assert all(sha(directory / p) == h for p, h in seal.items())
    assert set(seal) == {str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file() and p.name != 'FINAL_INTEGRITY.json'}
    preservation[directory.name] = {'sealed_members_verified': len(seal), 'exact_membership': True}

freeze_path = R / 'docs/studies/cpu_gpu_comparison_v1.freeze.json'
assert sha(freeze_path) == '518ac535473e50fb61dab3a70858bdfe42dfdb43570f649174f44bffe40e1ac6'
freeze = json.loads(freeze_path.read_text())
assert all(sha(R / p) == h for p, h in freeze['files_sha256'].items())
matrix = json.loads((R / 'docs/studies/cpu_gpu_comparison_v1.matrix.json').read_text())
anchors = matrix['source_at_freeze_sha256'].copy()
approved = R / 'docs/CPU_GPU_DRIVER_REVIEW_v1.json'
assert sha(approved) == 'b6a63a7e65827970d6b27e872e738052cd5faf94d88ee711dbccd5f77f90ef2a'
exception = json.loads(approved.read_text())
assert anchors['CMakeLists.txt'] == exception['frozen_cmake_sha256']
anchors['CMakeLists.txt'] = exception['current_cmake_sha256']
assert all(sha(R / p) == h for p, h in anchors.items())
original = json.loads((R / 'results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/BEFORE.json').read_text())['current_source_sha256']
production = {p: h for p, h in original.items() if p.startswith(('src/', 'include/', 'third_party/')) or p == 'CMakeLists.txt'}
assert all(sha(R / p) == h for p, h in production.items())
pin = R / 'third_party/cub/UPSTREAM.json'
assert sha(pin) == '477b1ee70b0a9113c9f98b263c19a31d05ccee54f45ce8476aec4cc98965ced1'
assert sha(R / 'src/cuda/cub_sort.cu') == 'b6d7f37c7494587fc6e4a676c00c166dc322d31cce96710811e3a4cb9cd8b9cb'
source = json.loads((isolated / 'SOURCE_IDENTITY.json').read_text())['files_sha256']
assert all(sha(R / p) == h for p, h in source.items())
policy = json.loads((R / 'docs/NON_TIMING_TEST_SELECTION_v1.json').read_text())
reviewed = policy['reviewed_source_sha256']
assert all(sha(R / p) == h for p, h in reviewed.items())
preservation.update(frozen_members_verified=freeze['files_sha256'], effective_anchors_verified=len(anchors),
                    production_files_verified=len(production), reviewed_source_files_verified=len(reviewed),
                    transferred_source_entries_locally_verified=len(source), cub_pin_sha256=sha(pin))
new('PRESERVATION.json', preservation)

warning_log = isolated / 'remote_evidence/validation/build.stderr.txt'
warnings = [line for line in warning_log.read_text().splitlines() if 'warning:' in line]
assert len(warnings) == 341
assert all('warning: style of line directive is a GCC extension' in line for line in warnings)

session = json.loads((E / 'colab_sessions.json').read_text())
status = json.loads((E / 'colab_status.json').read_text())
assert session['exit_code'] == status['exit_code'] == 0
assert 'No active sessions found' in session['stdout'] and "Session 'cpu-gpu-validation' not found" in status['stdout']

audit = '''# Approved pre-launch validation — stopped at session gate

**NO-GO — one or more required validation gates remain open**

## Stop condition and scope

The existing approved Colab session could not be established. `colab sessions` exited0 but reported `[colab] Pruned 1 stale local session(s).` and `[colab] No active sessions found on server.` `colab status --session cpu-gpu-validation` also exited0 but reported `Session 'cpu-gpu-validation' not found.` These semantic responses are blockers, not successful GPU-readiness checks. CLI session bookkeeping pruned a stale local record; no replacement cloud session was created or connected, no authentication/credentials were requested or logged, and no remote workload was launched.

Stopped before all executable validation gates. The first command batch after baseline creation read the required audits/command logs/seals, frozen protocol/matrix/resources and local test/selector/workspace/worker source. The subsequent inspection batch included session-list/status confirmation and read-only numbered source inspection. Once its results established the unavailable session, no further validation, build, discovery or resource command was issued; only local preservation/evidence assembly followed.

## Identity and integrity

Repository cwd is `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`. All177 source-area baseline entries match the independent review; all153 entries in the last transferred source manifest match local contents. The reviewed source identity remains SOURCE_IDENTITY.json SHA256 `7ce8297b76037af65d6d2dbbf3e2ccf5ec4684849090ee554a6d9552fcd50bda`. Remote source/build/executable presence and hashes cannot be freshly confirmed because the approved session is unavailable. No historical binary or session claim was promoted to current evidence. Git metadata was not assumed or created, and no Git mutation occurred.

Independently verified latest review seal25 members and isolated validation seal75 members with exact membership. All three frozen study members match their approved SHA256 values, and freeze-manifest SHA256 remains `518ac535473e50fb61dab3a70858bdfe42dfdb43570f649174f44bffe40e1ac6`. Exact frozen member digests are retained in PRESERVATION.json. All26 effective protected anchors match (including only the existing independently approved CMake exception),80 production/header/dependency files match, and144 reviewed implementation entries match. Production CUB adapter and CUB3.0.1 pin are unchanged.

Historical results baseline is **11,859 files**: calculated from every regular file under results/ before work, excluding only this new evidence directory. It includes the previous review's26 files in addition to its11,833-file prior baseline. All11,859 remain present, byte-identical by SHA256, with zero additions/removals outside this new directory. All65 pre-existing local build-metadata entries and177 project entries also match. No historical evidence, source, frozen input, protocol, build metadata or pin was modified. Hashes prove retained local contents, not current remote availability or externally signed attestation.

## Five authorized gates

| Gate | Current outcome | Evidence/limitation |
|---|---|---|
|1 Broader CPU Release correctness/regression|OPEN — not run|Approved remote source/build identity unavailable. No configure/build, CTest discovery or selected tests ran.|
|2 ASan/UBSan correctness|OPEN — not run|No current-session sanitizer compiler/configuration/build/tests executed. No settings changed or failures suppressed.|
|3 Prepared GPU framework correctness|OPEN — session unavailable; documented full test also conflicts with scope|Existing integration path explicitly invokes warm-ups/repetitions and timing instrumentation; it was not run.|
|4 All-size workspace/resources|OPEN — not run|No current CUDA queries, allocations, host/GPU/resource snapshots or memory validation at1,025/65,537/1,000,000.|
|5 Actual two-worker verification|OPEN — not run|No current topology/runtime or executable identity; existing combined parallel test contains six embedded timing rows and was not run.|

**Closed executable validation gates: none.** Local source/frozen/evidence integrity checks passed, but they do not close any of the five current-environment gates. Fresh tests discovered0, executed0, passed0, failed0, skipped by a test runner0. All five gates were not attempted after the stop condition; this is not a zero-test pass. No GPU framework samples, warm-ups or measured trials were executed. No study-eligible PREREQUISITES.json was generated.

## Inspected safety paths and further scope conflicts

- `scripts/non_timing_tests.py:133–150,155–175`: shared pre-discovery guard retains its exact absolute path for discovery and execution, validates command/source/build metadata, rechecks before execution, and emits an anchored approved selection. No selector entry point, discovery or selected test was invoked. The previously approved19-test CPU list remains a recorded policy, not a fresh discovery/test result.
- `scripts/validate_cpu_gpu_pilot.py` was read, including Release/sanitizer configuration and prerequisite-only behavior. It is a build/test orchestration entry point, not a read-only command. The broad alternative includes GPU timing-framework execution and then a pilot; neither is within this task's authorization. It was not called.
- `tests/test_cuda_benchmark.py:159–167` loops ten sizes and distributions, calling the GPU benchmark with `--warmups 1 --repetitions 2 --validation-only`. `src/cuda/cub_timing.cu:82–115` measures steady_clock and CUDA-event intervals around transfers and CUB SortKeys. Thus the documented whole GPU framework test cannot be treated as timing-free merely because its output is labelled validation. Host-only/schema/invalid-CLI checks alone would not establish actual prepared GPU sorting correctness. This is a separate scope conflict to resolve before invoking that test, even after the session returns.
- `tests/test_parallel_mergesort.cpp:103–108` unconditionally executes N32,768, one warm-up/two repetitions for two algorithms (six timing rows). Its useful earlier correctness/team observer assertions do not make the whole executable timing-free. No attempt was made to truncate, patch or run it. `--describe` establishes metadata, not an actual two-worker team. A safe, existing correctness-only actual-worker diagnostic has not been established in this stopped run.
- `src/cuda/comparison_resources.cu` was read: the isolated diagnostic queries signed-int32 SortKeys with prepared/private-stream and production/default-stream parameters, checks caps and requests temporary buffers outside timing; it includes allocations rather than being a zero-allocation query. It was not executed. No estimate was substituted for a current workspace requirement or physical allocation measurement.

## Command classification and unexecuted plan

Executed commands were local `pwd`, file listings/reads/numbered text inspection, evidence-only Python hashing/writing and the two Colab session-management inspections. Exact argv/cwd/status/stdout/stderr is retained in per-command JSON and COMMANDS.md. All executed commands exited0, including the two semantic session failures. No compiler/tool-version/GPU/resource command ran after that stop condition.

Proposed validation operations were classified but not finalized into remote commands because the mandatory session/source/build identities failed: guarded discovery/approved CPU CTest execution = correctness; fresh isolated Release configure/build = build/configuration; separate Debug MAB_ENABLE_SANITIZERS build plus approved correctness selection = sanitizer; whole GPU framework integration = **timing/benchmark, forbidden**; isolated workspace diagnostic = resource/query with allocations requiring safety inspection; combined parallel_mergesort executable = **timing-bearing, forbidden**; actual-worker correctness-only alternative = not yet established. No command with unresolved scope was executed.

## Warnings and inherited observations

Recounted the unchanged last build.stderr.txt:341 warnings, all `style of line directive is a GCC extension`. The previous review traced them to nvcc-generated host line markers under GCC -Wpedantic, with80/100/161 warnings in comparison_resources/cub_sort/cub_timing translation-unit blocks. These are **inherited retained build diagnostics**, not a fresh build result; no flags were suppressed or modified. No fresh compiler/sanitizer outcome or current GPU model/runtime/memory observation is claimed here.

Historical T4 correctness475inputs/1,900checks, sequential Merge Sort4,015inputs, two logical CPUs/one physical core, driver580.82.07/nvcc13.0.88 and prior resource snapshots remain historical only. They do not prove session availability, fresh workspace caps, current cgroup headroom or actual workers now. No performance ranking or resource guarantee is made.

## Next permitted action

Restore the existing approved `cpu-gpu-validation` session and establish its identity before any resumed validation. This authorization expressly forbids creating a replacement session, so none was provisioned. Separately reconcile the prepared-framework and actual-worker correctness-only validation paths with the no-timing/no-source-change constraints. Do not run the timing-bearing wrappers, reinterpret validation labels as permission, or relax the frozen gates. No study execution is authorized. Stop after this audit.
'''
with (E / 'FINAL_AUDIT.md').open('x') as f:
    f.write(audit)

controls = json.loads((E / 'CONTROL_COMMANDS.json').read_text())
lines = ['# Commands and exit statuses', '',
         'No CTest discovery/tests, configure/build, sanitizer, CUDA workload, workspace allocation, warm-up, measured trial, pilot or study command ran. Exact child argv and cwd are below; recorder JSON retains full outputs.', '']
for item in controls:
    lines += ['## Control command', '', 'Exit:0; classification: ' + item['classification'], '', '```bash', item['command'], '```', '']
for p in sorted(E.glob('*.json')):
    d = json.loads(p.read_text())
    if not isinstance(d, dict) or not {'argv', 'exit_code', 'scope'} <= d.keys():
        continue
    assert d['exit_code'] == 0
    lines += ['## ' + p.name, '', 'Exit:' + str(d['exit_code']) + '; classification: ' + d['scope'], '',
              '```bash', shlex.join(d['argv']), '```', '', 'cwd: `' + d['cwd'] + '`.', '']
lines += ['## Evidence-only tool action and finalization', '',
          'apply_patch added only this directory\'s finalize.py and returned success. No project source was patched.', '',
          '```bash', 'python3 -B ' + str(E.relative_to(R) / 'finalize.py'), '```', '',
          'Exit:0 upon successful completion; assertions abort on any integrity mismatch. Standard-library reads/hashes and exclusive evidence writes only; no subprocesses or repository imports.', '',
          'Recorder wrapper: `python3 -B ' + str(E.relative_to(R) / 'record.py') + ' NAME SCOPE TIMEOUT CHILD_ARGV...`.',
          'Terminal polling retrieves already-running evidence-hash command output and starts no additional workload. URL-shaped text is redacted by the copied recorder; original files remain authoritative.']
with (E / 'COMMANDS.md').open('x') as f:
    f.write('\n'.join(lines) + '\n')
manifest = dict(schema_version=1, verdict='NO-GO — one or more required validation gates remain open',
                observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                approved_session_available=False, validation_gates_closed=[], validation_gates_open=[1, 2, 3, 4, 5],
                source_modified=False, study_authorized=False, tests_discovered=0, tests_executed=0,
                tests_passed=0, tests_failed=0, tests_skipped_by_runner=0, builds=0, ctest_invocations=0,
                gpu_workloads=0, resource_queries=0, warmups=0, measured_trials=0,
                preservation=preservation,
                evidence_sha256={str(p.relative_to(E)): sha(p) for p in sorted(E.rglob('*')) if p.is_file()},
                seal_note='Self excluded. Local retained-file integrity, not external signed attestation.')
new('FINAL_INTEGRITY.json', manifest)
assert all(sha(E / p) == h for p, h in manifest['evidence_sha256'].items())
print(json.dumps({'verdict': manifest['verdict'], 'historical_results_preserved': len(actual),
                  'sealed_members': len(manifest['evidence_sha256']),
                  'final_audit': str((E / 'FINAL_AUDIT.md').relative_to(R)), 'exit_code': 0}, indent=2))
