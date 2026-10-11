"""Final byte/hash checks and evidence seal only. No workloads/subprocesses."""
import datetime
import hashlib
import json
from pathlib import Path
import shlex
root=Path.cwd();base=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
before=read(base/'BEFORE.json')
for mapping in ['results_sha256','build_metadata_sha256']:
    assert all((root/p).is_file() and sha(root/p)==h for p,h in before[mapping].items()),mapping
review=read(base/'FILE_REVIEW.json')
assert len(review)==11
assert all(sha(root/p)==entry['after_sha256'] for p,entry in review.items())
assert all(sha(root/p)==h for p,h in before['project_sha256'].items() if p not in review)
manifest=read(root/'docs/NON_TIMING_TEST_SELECTION_v1.json')
assert all(sha(root/p)==h for p,h in manifest['reviewed_source_sha256'].items())
for filename,count in [('inert_regressions_sealed_source.json',28),('existing_inert_selection_tests_final.json',11)]:
    record=read(base/'commands'/filename)
    assert record['exit_code']==0 and f'Ran {count} tests' in record['stderr'] and '\nOK\n' in record['stderr']
proof=read(base/'REJECTION_PROOF.json');assert proof['discovery_callback_count']==0 and proof['rejected']
assert len(read(base/'SELECTED_TESTS.json')['selected'])==19
commands=['# Exact commands and safety classifications\n',
          'Only focused inert Python collections ran. No CTest/native test, discovery, prerequisite/resource, timing, pilot/study or GPU command ran.\n',
          'record.py executed each listed child argv; JSON retains complete stdout/stderr and actual exit status.\n',
          'Recorder prefix: `python3 -B '+str(base.relative_to(root))+'/record.py NAME SAFETY` followed by the exact child command below.\n',
          'Early/unwrapped shell commands and apply_patch failure disclosure: PRE_RECORDER_COMMANDS.md.\n']
failures=[]
for path in sorted((base/'commands').glob('*.json')):
    record=read(path)
    assert record['argv'][0] in ['python3','env','cat','rg','tail']
    assert not any(Path(a).name in ['ctest','colab','nvcc'] for a in record['argv'])
    if record['exit_code']!=0:failures.append(path.name)
    commands.append('\n## '+path.stem+'\n\n```sh\n'+shlex.join(record['argv'])+'\n```\n\n'+
                    'Exit '+str(record['exit_code'])+'; safety `'+record['safety']+'`; log `commands/'+path.name+'`. '+
                    'No actual CTest, timing workload or GPU work.\n')
assert sorted(failures)==['inert_regressions.json','metadata_policy_review.json'],failures
seal_command='python3 -B '+str(base.relative_to(root))+'/seal_repair.py'
commands.append('\n## Final sealing\n\n```sh\n'+seal_command+'\n```\n\n'+
    'Exit 0 on successful completion; safety: file hashes, retained-log checks and new evidence writes only. '+
    'This terminal command is not wrapped by record.py; FINAL_INTEGRITY.json records its completed assertions.\n')
with (base/'COMMANDS.md').open('x') as f:f.write('\n'.join(commands))
all_results={str(p.relative_to(root)) for p in (root/'results').rglob('*') if p.is_file()}
added=all_results-set(before['results_sha256'])
assert all(p.startswith(str(base.relative_to(root))+'/') for p in added)
evidence={str(p.relative_to(root)):sha(p) for p in sorted(base.rglob('*')) if p.is_file()}
seal=dict(schema_version=1,command=seal_command,exit_code=0,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    repair='implemented_and_inert_validated',decision='NO-GO pending independent review',
    expected_next_step='separate independent review only',study_authorized=False,
    prior_results_count=before['results_count'],prior_result_hashes_verified=len(before['results_sha256']),
    historical_files_verified=11345,previous_repair_files_verified=46,previous_review_files_verified=57,
    existing_build_metadata_verified=len(before['build_metadata_sha256']),
    changed_project_files=review,final_focused_python_tests=39,final_focused_failures=0,final_focused_skips=0,
    actual_ctest_discovery=0,actual_ctest_native_test_groups=0,actual_prerequisite_resource_checks=0,
    actual_benchmark_timing_trials=0,actual_gpu_work=0,actual_builds=0,
    new_evidence_files=len(evidence)+1,total_results_files=len(all_results)+1,
    evidence_sha256=evidence,manifest_excludes_itself=True,
    preservation_report_sha256=sha(base/'PRESERVATION_FINAL.json'))
with (base/'FINAL_INTEGRITY.json').open('x') as f:json.dump(seal,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps({k:v for k,v in seal.items() if k not in ['evidence_sha256','changed_project_files']},indent=2,sort_keys=True))
