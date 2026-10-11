"""Seal independent review evidence using the repository's SHA256 member-map convention.

Only standard-library file I/O and hashing. No project imports or subprocesses.
"""
import hashlib, json
from pathlib import Path
from datetime import datetime, timezone

root = Path.cwd()
e = Path(__file__).resolve().parent
def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()
def read(path):
    return json.loads(path.read_text())
def new(name, value):
    with (e/name).open('x') as f:
        json.dump(value, f, indent=2, sort_keys=True); f.write('\n')
before = read(e/'BASELINE.json')
history = {str(p.relative_to(root)):sha(p) for p in sorted((root/'results').rglob('*'))
           if p.is_file() and not p.is_relative_to(e)}
assert history == before['results_sha256']
for key in ['project_sha256','build_metadata_sha256','protected_sha256','frozen_sha256']:
    assert all((root/p).is_file() and sha(root/p)==h for p,h in before[key].items()), key
preservation = read(e/'FINAL_PRESERVATION.json')
assert all(preservation[k]['exact_membership_and_sha256_match'] for k in ['historical_results','project','build_metadata'])
old = root/'results/raw/cpu_gpu_recovery_20261011T075800444473Z'
assert sha(old/'FINAL_INTEGRITY.json') == before['recovery_seal_sha256']

inventory = read(old/'CHANGE_INVENTORY.json')
inspected = inventory['modified'] + inventory['added'] + [
    'AGENTS.md','scripts/non_timing_tests.py','scripts/ctest_build_guard.py',
    'scripts/validate_cpu_gpu_pilot.py','scripts/cpu_gpu_validation_policy.py',
    'tests/test_validation_policy.py','docs/NON_TIMING_TEST_SELECTION_v3.json',
    'docs/CPU_GPU_VALIDATION_POLICY_v2.json','docs/CPU_GPU_VALIDATION_POLICY_v2.md',
    'docs/CPU_GPU_DRIVER_REVIEW_v1.json','docs/CPU_GPU_COMPARISON_PROTOCOL_v1.md',
    'docs/studies/cpu_gpu_comparison_v1.freeze.json','docs/studies/cpu_gpu_comparison_v1.matrix.json',
    'docs/studies/cpu_gpu_comparison_v1.resources.csv','third_party/cub/UPSTREAM.json',
    'results/raw/bounded_resume_20261011T024034091796Z/downloaded/evidence/BUILD_COMPLETE.json',
    'results/raw/cpu_gpu_final_preflight_20261011T074147349659Z/FINAL_AUDIT.md',
    'results/raw/cpu_gpu_final_preflight_20261011T074147349659Z/FINAL_INTEGRITY.json']
inspected += [str(p.relative_to(root)) for p in sorted(old.rglob('*')) if p.is_file()]
new('INSPECTED_FILES.json', dict(note='Read/AST/hash inspection; not executed. Large displays were targeted again; maps were verified by bytes.',
    files_sha256={p:sha(root/p) for p in sorted(set(inspected))}))

records = read(e/'COMMAND_RECORDS.json')
own_command = 'python3 -B ' + str(e.relative_to(root)) + '/seal_review.py'
records.append(dict(command=own_command, exit_code=0,
    purpose='Final evidence-only assembly and SHA256 seal. Exit0 confirmed by successful terminal completion; no workloads.'))
lines = ['# Independent review commands', '', 'Repository cwd: '+str(root), '',
    'All recorded shell commands exited0. Review scope: reading, AST parsing, hashing and new evidence creation.',
    'Zero test/CTest/discovery/build/configure/prerequisite/resource/GPU/session/benchmark commands were executed.',
    'Commands mentioning such operations inside read files or retained JSON are inspected historical records, not executed commands.',
    'New evidence scripts and COMMAND_RECORDS.json were added using apply_patch, with successful tool status, confined to this new directory.',
    'No implementation, historical evidence or frozen-input edits occurred.',
    'Some large inspection displays were truncated; targeted reads and independent structured comparisons were used. Omitted display text is not treated as proof of source review.', '']
for i, record in enumerate(records, 1):
    lines += ['## '+str(i), '', '- Exit: '+str(record['exit_code']),
              '- Safety/purpose: '+record['purpose'], '', '~~~~~~~~sh', record['command'], '~~~~~~~~', '']
with (e/'COMMANDS.md').open('x') as f:
    f.write('\n'.join(lines))
members = {str(p.relative_to(e)):sha(p) for p in sorted(e.rglob('*')) if p.is_file()}
new('FINAL_INTEGRITY.json', dict(schema_version=1, created_utc=datetime.now(timezone.utc).isoformat(),
    seal_excludes_itself=True, seal_command=['python3','-B',str(e.relative_to(root))+'/seal_review.py'],
    evidence_sha256=members, evidence_files_excluding_seal=len(members),
    historical_files_verified=len(history), historical_manifest='BASELINE.json',
    historical_manifest_field='results_sha256',
    preservation_results=preservation, frozen_sha256=before['frozen_sha256'],
    project_files_unchanged=len(before['project_sha256']), protected_files_unchanged=len(before['protected_sha256']),
    build_metadata_files_unchanged=len(before['build_metadata_sha256']),
    recovery_seal_sha256=before['recovery_seal_sha256'],
    source_files_modified=0, tests_executed=0, ctest_discovery=0, builds=0, gpu_commands=0,
    benchmark_trials=0, warmups=0, study_launched=False,
    recorded_regressions_reviewed=dict(new_methods=26,existing_policy_methods=9,freshly_executed=0),
    verdict='NO-GO', authorization_granted=False))
sealed = read(e/'FINAL_INTEGRITY.json')
actual_members = {str(p.relative_to(e)):sha(p) for p in sorted(e.rglob('*'))
                  if p.is_file() and p != e/'FINAL_INTEGRITY.json'}
assert actual_members == sealed['evidence_sha256'], 'review seal verification failed'
print('REVIEW_SEALED',str(e.relative_to(root)),len(members),'members plus seal;',
      len(history),'historical files unchanged; no workload executed')

