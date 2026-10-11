"""Seal repair using SHA256 member maps. File I/O only; no project execution."""
import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
root=Path.cwd();e=Path(__file__).resolve().parent
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def read(p):return json.loads(p.read_text())
before=read(e/'BEFORE.json');preserved=read(e/'FINAL_PRESERVATION.json')
history={str(p.relative_to(root)):sha(p) for p in sorted((root/'results').rglob('*')) if p.is_file() and not p.is_relative_to(e)}
assert history==before['results_sha256']
for key in ['frozen_sha256','protected_sha256','build_metadata_sha256']:
    assert all((root/n).is_file() and sha(root/n)==h for n,h in before[key].items()),key
assert all(sha(root/n)==h for n,h in preserved['project']['sha256'].items())
assert all(sha(e/'before_sources'/n)==h for n,h in before['project_sha256'].items())
assert read(e/'TEST_RESULTS.json')['final_distinct_total']==74
assert read(e/'FINAL_SELECTION.json')['sha256']==sha(root/'docs/NON_TIMING_TEST_SELECTION_v4.candidate.json')
assert not (root/'docs/CPU_GPU_EVIDENCE_REVIEW_v1.json').exists()
assert 'TRUSTED_APPROVAL_SHA256 = None' in (root/'scripts/cpu_gpu_evidence.py').read_text()
with (e/'SEAL_STATUS.md').open('x') as f:
    f.write('# Seal checks\n\nFile-only SHA256 comparisons completed successfully before seal creation. Historical12,307, protected80, metadata65, frozen4 and anchor26 preservation verified. Source/diff/log/candidate evidence retained. No native or GPU execution occurred.\n\nCommand: python3 -B '+str(e.relative_to(root))+'/seal_repair.py. Process exit must be confirmed from the actual terminal/tool response, not inferred from this file.\n')
members={str(p.relative_to(e)):sha(p) for p in sorted(e.rglob('*')) if p.is_file()}
seal=dict(schema_version=1,created_utc=datetime.now(timezone.utc).isoformat(),verdict='NO-GO',
    seal_command=['python3','-B',str(e.relative_to(root))+'/seal_repair.py'],seal_excludes_itself=True,
    evidence_sha256=members,evidence_files_excluding_seal=len(members),
    historical_manifest='BEFORE.json',historical_manifest_field='results_sha256',historical_files_verified=len(history),
    preservation_results=preserved,project_sha256=preserved['project']['sha256'],frozen_sha256=before['frozen_sha256'],
    focused_tests_executed=74,focused_tests_passed=74,focused_tests_failed_final=0,focused_tests_skipped_final=0,
    initial_regression_errors_retained=1,native_tests_executed=0,ctest_discovery=0,builds=0,
    gpu_commands=0,benchmark_trials=0,warmups=0,study_launched=False,authorization_granted=False,
    independent_approval_installed=False,candidate_activated=False,actual_build_provenance_established=False,
    limitations=['Independent non-circular trust activation not implemented/approved.',
                 'Candidate pending; v3 active and rejects current source before discovery.',
                 'Actual T4 build/compiler/linker/binary provenance unavailable; no collector executed.',
                 'Nested full-run retention and positive full-evidence integration remain unvalidated.',
                 'Initial read-only command transcript incomplete; all focused attempts/statuses retained.'])
with (e/'FINAL_INTEGRITY.json').open('x') as f:json.dump(seal,f,indent=2,sort_keys=True);f.write('\n')
actual={str(p.relative_to(e)):sha(p) for p in sorted(e.rglob('*')) if p.is_file() and p.name!='FINAL_INTEGRITY.json'}
assert actual==members
print(json.dumps(dict(seal_verified=True,historical_unchanged=len(history),evidence_members=len(members),
    total_new_evidence_files=len(members)+1,focused_tests_passed=74,verdict='NO-GO')))
