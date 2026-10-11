"""Exclusive final evidence seal; read/hash/write only, no workload execution."""
from pathlib import Path
import datetime, hashlib, json, re, shlex, sys

E = Path(__file__).resolve().parent
ROOT = E.parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
b = read(E/'BEFORE.json')
p = read(E/'PRESERVATION_VERIFIED.json')
assert all(sha(ROOT/k)==h for k,h in p['project_current_sha256'].items())
assert all(sha(ROOT/k)==h for k,h in p['build_metadata_current_sha256'].items())
results = {str(f.relative_to(ROOT)):sha(f) for f in sorted((ROOT/'results').rglob('*'))
           if f.is_file() and not f.is_relative_to(E)}
assert results == b['historical_results_sha256']
remote = E/'downloaded/evidence'
assert all(sha(remote/k)==h for k,h in read(remote/'REMOTE_INTEGRITY.json').items())
assert sha(E/'validation_evidence.tar.gz') == '46dc7fc6bd00b95125995f1e8427a07dc714750976e5ae373462f6cfc059989e'
for name in ['policy_retry.json','test_validation_selection.json','guard_regression.json','final_assembly.json','partial_classification.json']:
    assert read(E/name)['exit_code']==0
assert 'unknown/missing Dart setting' in read(E/'remote_static_selection.json')['stderr']
assert read(remote/'DIRECT_DIAGNOSTICS_COMPLETE.json')['full_validation_complete'] is False
assert read(E/'PARTIAL_CLASSIFICATION.json')['actual_partial_bundle_accepted'] is False

# Inspect text evidence for common actual-secret encodings, without echoing values.
# This is a bounded pattern check, not a general proof that arbitrary text is secret-free.
patterns = [re.compile(r'\bgh[pousr]_[A-Za-z0-9]{30,}\b'),
            re.compile(r'\bya29\.[A-Za-z0-9_-]{25,}'),
            re.compile(r'\bBearer\s+[A-Za-z0-9._-]{30,}',re.I)]
hits=[]
for f in E.rglob('*'):
    if f.is_file() and f.suffix in {'.json','.md','.txt','.py','.diff','.tcl','.cmake','.hpp'}:
        text=f.read_text(errors='replace')
        if any(pattern.search(text) for pattern in patterns):hits.append(str(f.relative_to(E)))
assert not hits, 'potential credential-shaped value; inspect filenames without exposing contents: '+repr(hits)

assembly=read(E/'final_assembly.json')
own_command=['python3','-B',str(Path(sys.argv[0]))]
with (E/'COMMANDS.md').open('a') as out:
    out.write('\n## Final evidence-only commands\n\n')
    out.write('- `'+shlex.join(assembly['argv'])+'`: child0; hash/report assembly; [final_assembly.json](final_assembly.json).\n')
    out.write('- `'+shlex.join(own_command)+'`: exit0 on completing the assertions and exclusive seal write; read/hash/write only, no subprocesses. Recorded by FINAL_INTEGRITY.json.\n')
    out.write('\nPolling of the running local assembly command merely retrieved its completion (child0); it did not launch another workload. Final readback verification, if performed, hashes/reads existing evidence only.\n')
files={str(f.relative_to(E)):sha(f) for f in sorted(E.rglob('*')) if f.is_file()}
assert 'FINAL_INTEGRITY.json' not in files
seal={
 'schema_version':2,'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'verdict':'NO-GO — one or more required validation gates remain open',
 'seal_note':'FINAL_INTEGRITY.json excludes itself; all other evidence members and content hashes are sealed.',
 'evidence_sha256':files,'evidence_files_excluding_seal':len(files),
 'preservation':{k:p[k] for k in ['historical_files_before','historical_files_after_excluding_new_evidence',
 'historical_content_and_membership_identical','existing_build_metadata_files_unchanged','trusted_anchors_count',
 'protected_80_changed_only_authorized','trusted_anchor_exceptions','frozen_sha256','production_adapter_sha256',
 'cub_pin_sha256','legacy_analyzer_runner_and_guard_unchanged','current_vs_transferred_difference']},
 'inventory_reference':'PRESERVATION_VERIFIED.json',
 'stage_status':{'0':'PASS','1':'PASS','2':'PASS','3':'PASS','4':'BLOCKED','5':'PASS'},
 'gates':read(remote/'DIRECT_DIAGNOSTICS_COMPLETE.json')['states'],
 'source_revision':'Git unavailable; manifest/hash identity;185 transferred files,149 current reviewed executable sources.',
 'replacement_session':'gpu-t4-s-kkb-usw4b1-2i9q6dkvjw07d',
 'source_archive_sha256':sha(E/'reviewed_source.tar.gz'),
 'remote_evidence_archive_sha256':sha(E/'validation_evidence.tar.gz'),
 'local_inert_tests':{'policy_passed':9,'selection_passed':3,'guard_passed':36,'initial_policy_errors_retained':1},
 'configures_passed':3,'builds_passed':3,'ctest_discovery':0,'ctest_executions':0,
 'sanitizer_suite_executed':False,'leak_detection_disabled':False,
 'gpu_prepared_inputs':163,'gpu_prepared_output_checks':489,'invalid_operations_rejected':489,
 'worker_output_checks':12,'workspace_sizes':[1025,65537,1000000],
 'build_warning_counts':{'cpu-release':0,'cpu-sanitize':0,'gpu-release':367},
 'gpu_warning_category':'style of line directive is a GCC extension',
 'benchmark_trials':0,'warmups':0,'pilot_runs':0,'study_execution_authorized':False,
 'study_eligible':False,'full_study_executed':False,'hundred_million_executed':False,
 'bounded_secret_pattern_scan_hits':hits,
 'secret_scan_limit':'Only common PAT/OAuth/Bearer value patterns checked; allowlisted diagnostics and redacted recorder were primary controls.',
 'seal_command':{'argv':own_command,'cwd':str(ROOT),'exit_code':0,'scope':'Evidence-only final hashing/sealing; no subprocess/tests/CTest/GPU/benchmarks'},
}
with (E/'FINAL_INTEGRITY.json').open('x') as out:json.dump(seal,out,indent=2,sort_keys=True);out.write('\n')
print(json.dumps({'seal':str((E/'FINAL_INTEGRITY.json').relative_to(ROOT)),
                  'sealed_members':len(files),'historical_files_preserved':len(results),
                  'status':seal['verdict']},indent=2))
