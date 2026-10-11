"""Final hashes, retained-log assertions and exclusive evidence writes only."""
import datetime
import hashlib
import json
from pathlib import Path
import shlex

root=Path.cwd();base=Path(__file__).resolve().parent
def read(path):return json.loads(path.read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def mapping(paths):return {str(p.relative_to(root)):sha(p) for p in sorted(set(paths)) if p.is_file()}
before=read(base/'BEFORE.json');review=read(base/'FILE_REVIEW.json');after=read(base/'AFTER_VERIFIED.json')
assert len(review)==7
for p,h in before['prior_results_sha256'].items():assert (root/p).is_file() and sha(root/p)==h,p
current=mapping([root/'AGENTS.md',root/'README.md',root/'CMakeLists.txt']+
                [p for n in ['scripts','tests','docs','include','src','cmake','third_party'] for p in (root/n).rglob('*') if '__pycache__' not in p.parts])
assert set(current)==set(before['project_sha256'])
for p,h in current.items():
    assert h==(review[p]['after_sha256'] if p in review else before['project_sha256'][p]),p
assert {p for p,h in current.items() if h!=before['project_sha256'][p]}==set(review)
builds=mapping(p for p in (root/'build').rglob('*') if p.name in
               ['CTestTestfile.cmake','CTestCustom.cmake','CTestCustom.ctest','CTestConfig.cmake','DartConfiguration.tcl'])
assert builds==before['build_metadata_sha256']
policy=read(root/'docs/NON_TIMING_TEST_SELECTION_v1.json')
assert all(sha(root/p)==h for p,h in policy['reviewed_source_sha256'].items())
assert after['prior_result_files_verified']==11556 and after['differences']==[]
assert len(after['approved_cpu_selection'])==19 and len(after['source_pin_changes'])==2
failed=read(base/'commands/inert_reproducer_before_fix.json')
assert failed['exit_code']==1 and 'Ran 8 tests' in failed['stderr'] and 'FAILED (failures=4, errors=1)' in failed['stderr']
for name,count in [('inert_regressions_after_repair',8),('all_inert_selector_regressions',47)]:
    d=read(base/'commands'/(name+'.json'));assert d['exit_code']==0 and f'Ran {count} tests' in d['stderr'] and '\nOK\n' in d['stderr']
commands=['# Commands, observed statuses and safety classification\n',
          'Only static inspections, explicit local source-hash renewal and focused inert Python methods ran. '
          'No actual CTest, native selection, configure/build, prerequisite/resource probe, timing trial, benchmark or GPU command ran.\n',
          'Recorder prefix: `python3 -B '+str(base.relative_to(root))+'/record.py NAME SAFETY CHILD_ARGV...`. '
          'Every commands/*.json contains exact child argv/cwd, complete stdout/stderr and actual exit code.\n',
          'Early shell inspections and tool edits: EARLY_COMMANDS.md.\n',
          '## Exclusive evidence bootstrap\n\n```sh\n'+shlex.join(before['command_argv'])+
          '\n```\n\nExit0, observed in terminal. Only file hashes, seven original-file copies and exclusive evidence creation. Exact program retained in BEFORE.json.\n']
failures=[]
for path in sorted((base/'commands').glob('*.json')):
    d=read(path)
    assert not any(Path(a).name in ['ctest','cmake','nvcc','colab'] for a in d['argv'])
    if d['exit_code']!=0:failures.append(path.stem)
    commands.append('\n## '+path.stem+'\n\n```sh\n'+shlex.join(d['argv'])+'\n```\n\nExit '+str(d['exit_code'])+
                    '; safety: '+d['safety']+'. Full output: `commands/'+path.name+'`.\n')
assert failures==['inert_reproducer_before_fix'],failures
command='python3 -B '+str(base.relative_to(root))+'/seal_repair.py'
commands.append('\n## Final integrity seal\n\n```sh\n'+command+'\n```\n\nExit0 on successful completion, unwrapped terminal command; file hashes/retained-log checks/new evidence writes only.\n')
with (base/'COMMANDS.md').open('x') as f:f.write('\n'.join(commands))
results=mapping((root/'results').rglob('*'));added=set(results)-set(before['prior_results_sha256'])
assert all(p.startswith(str(base.relative_to(root))+'/') for p in added)
assert not set(before['prior_results_sha256'])-set(results)
evidence=mapping(base.rglob('*'));assert set(evidence)==added
seal=dict(schema_version=1,command=command,exit_code=0,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
          repair='guarded_absolute_path_retained',decision='NO-GO pending separate independent review',study_authorized=False,
          prior_result_files_before=len(before['prior_results_sha256']),prior_result_files_after_verified=len(before['prior_results_sha256']),
          missing_or_modified_prior_results=[],project_file_count=len(current),modified_project_files=review,
          protected_anchors_verified=after['protected_anchors_verified'],production_headers_dependencies_verified=after['production_headers_dependencies_verified'],
          frozen_members_verified=after['frozen_members_verified'],freeze_and_cmake_review_pins_verified=True,
          original_historical_files_verified=after['original_historical_files_verified'],existing_build_metadata_verified=len(builds),
          production_adapter_sha256=after['production_adapter_sha256'],cub_pin_sha256=after['cub_pin_sha256'],cub_version=after['cub_version'],
          approved_cpu_selection=after['approved_cpu_selection'],source_hashes_renewed=after['source_pin_changes'],
          initial_inert_reproducer=dict(exit_code=1,methods=8,passed=3,failures=4,errors=1),
          final_focused_methods=47,final_focused_failures=0,final_focused_errors=0,final_focused_skips=0,
          actual_ctest_discovery=0,actual_native_tests=0,actual_builds=0,actual_prerequisite_resource_checks=0,
          actual_timing_trials=0,actual_benchmarks=0,actual_gpu_commands=0,
          new_evidence_files=len(evidence)+1,total_result_files=len(results)+1,
          evidence_sha256=evidence,manifest_excludes_itself=True)
with (base/'FINAL_INTEGRITY.json').open('x') as f:json.dump(seal,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps({k:v for k,v in seal.items() if k not in ['evidence_sha256','modified_project_files']},indent=2,sort_keys=True))
