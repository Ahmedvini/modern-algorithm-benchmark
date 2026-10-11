"""Finalize only this review's evidence. Read/hash/JSON operations, no workloads."""
import datetime
import hashlib
import json
import shlex
from pathlib import Path

ROOT=Path.cwd()
E=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def files(paths, omit_cache=False):
    result={}
    for base in paths:
        for p in ([base] if base.is_file() else sorted(base.rglob('*'))):
            if p.is_file() and not p.is_relative_to(E) and not (omit_cache and '__pycache__' in p.parts):
                result[str(p.relative_to(ROOT))]=sha(p)
    return result

baseline=read(E/'BEFORE.json')
all_results=read(E/'BEFORE_ALL_RESULTS.json')['prior_results_sha256']
results=files([ROOT/'results'])
project=files([ROOT/p for p in ['AGENTS.md','README.md','CMakeLists.txt','scripts','tests','docs','include','src','cmake','third_party']],True)
names={'CTestTestfile.cmake','CTestCustom.cmake','CTestCustom.ctest','CTestConfig.cmake','DartConfiguration.tcl'}
build={str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'build').rglob('*')) if p.is_file() and p.name in names}
assert results==all_results, 'result membership or hashes changed during review'
assert project==baseline['project_sha256'], 'project membership or hashes changed during review'
assert build==baseline['build_metadata_sha256'], 'build metadata membership or hashes changed during review'
verified=read(E/'INDEPENDENT_VERIFICATION.json')
for key in ['repair_prior_results','original_historical_results','production_headers_dependencies',
            'build_metadata','frozen_members','protected_anchors_existing_reviewed_cmake_exception',
            'current_review_project_preserved','current_review_build_metadata_preserved']:
    assert not verified[key]['differences'],key
assert verified['independent_literal_pins']=={'freeze':True,'cmake_review':True}
assert verified['production_adapter']['unchanged'] and verified['cub_pin']['unchanged']
assert verified['policy']['matches_exact_19'] and verified['policy']['non_source_fields_identical']
assert not verified['policy']['snapshot']['differences']
assert verified['regression_ast']['all_old_bodies_identical']
assert all(verified['preserved_reproducer'].values())
assert all(v['method_names_match_source'] for v in verified['recorded_test_logs'].values())
for name,data in verified['evidence_seals'].items():
    assert not(data['differences'] or data['missing'] or data['unexpected']),name

logs=[]
for p in sorted(E.glob('*.json')):
    data=read(p)
    if isinstance(data,dict) and 'argv' in data and 'exit_code' in data:
        logs.append((p.name,data))
assert all(data['exit_code']==0 for _,data in logs)
text=['# Review commands and statuses','',
      'Only file reads, directory listings, JSON/AST parsing, SHA-256 checks and new review-evidence writes occurred. '
      'No repository import/helper call, CTest discovery/tests, build, prerequisite/resource check, timer workload, benchmark, pilot, GPU command, or study ran.',
      '', '## Initial unwrapped commands','',
      'Full shell text/argv is retained in EARLY_COMMANDS.json and BEFORE.json. Overall shell statuses were observed; individual commands in multi-read shells were not independently instrumented.','']
for i,item in enumerate(read(E/'EARLY_COMMANDS.json'),1):
    text.extend([f'### Early command {i}', '', '```sh', shlex.join(item['argv']), '```', '',
                 f'Observed exit: {item["exit_code"]}. {item["note"]}', ''])
text.extend(['## Recorded inspection commands','',
             'Recorder invocation: `python3 -B '+str(E.relative_to(ROOT))+'/record.py NAME CHILD_ARGV...`. '
             'Each JSON below retains exact child argv, cwd, full stdout/stderr and observed exit. These are this review\'s commands; historical test commands read as text were not rerun.',''])
for filename,data in logs:
    text.extend(['### '+filename,'','```sh',shlex.join(data['argv']),'```','',
                 'Observed exit: '+str(data['exit_code'])+'. '+data['classification'], ''])
text.extend(['## Evidence-authoring operations and qualification','',
             'apply_patch authored only verify_static.py, EARLY_COMMANDS.json, FINAL_AUDIT.md and seal_review.py inside this new directory; all tool calls succeeded. '
             'The audit received one evidence-only wording correction to avoid claiming an uncaptured individual rg exit status. '
             'record.py and BEFORE.json were created by the explicitly retained early commands. '
             'No source/test/doc/build/historical artifact was authored or patched.','',
             'static_call_boundaries.json: rg named a nonexistent CUB header and emitted an error; the outer read-only shell continued and returned0. '
             'The individual rg status was not instrumented. cub_files.json then records the actual directory inventory, exit0. '
             'The initial result inventory excluded one historical cache file; the complete retained supplemental inventory and baseline hash comparison account for it.','',
             '## Final seal','', '```sh',
             'python3 -B '+str((E/'seal_review.py').relative_to(ROOT)), '```','',
             'Direct final command, outside the recorder to avoid adding an unsealed log afterward. '
             'Exit0 is confirmed by the terminal on completion; FINAL_INTEGRITY.json is written only after all preservation assertions pass. '
             'This program generates this command inventory, repeats read-only preservation checks, and hashes only the new review evidence.'])
with (E/'COMMANDS.md').open('x') as f:f.write('\n'.join(text)+'\n')

manifest={'schema_version':1,'review':'ctest_path_identity_independent_review',
    'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'verdict':'PASS',
    'command':['python3','-B',str((E/'seal_review.py').relative_to(ROOT))],'exit_code':0,
    'all_pre_review_result_files_verified':len(results),'repair_preexisting_results_verified':verified['repair_prior_results']['entries'],
    'original_historical_subset_verified':verified['original_historical_results']['entries'],
    'project_files_verified':len(project),'build_metadata_verified':len(build),
    'protected_anchors_verified':verified['protected_anchors_existing_reviewed_cmake_exception']['entries'],
    'production_headers_dependencies_verified':verified['production_headers_dependencies']['entries'],
    'frozen_members_verified':verified['frozen_members']['entries'],
    'freeze_and_review_literal_pins_verified':verified['independent_literal_pins'],
    'production_adapter_sha256':verified['production_adapter']['sha256'],
    'cub_pin_sha256':verified['cub_pin']['sha256'],'cub_version':verified['cub_pin']['content']['cub_version'],
    'approved_cpu_selection':verified['policy']['exact_selection'],
    'earlier_evidence_seals':verified['evidence_seals'],
    'preservation_differences':[], 'current_review_project_modified':[],
    'tests_rerun':0,'ctest_discovery':0,'ctest_execution':0,'builds':0,'prerequisite_resource_checks':0,
    'timing_trials':0,'benchmarks':0,'gpu_commands':0,'study_authorized':False,
    'recorded_inspection_commands':len(logs),'recorded_inspection_exit_codes':[v['exit_code'] for _,v in logs],
    'limitations':['quiescent exclusively owned tree and trusted tools required',
        'no atomic filesystem/executable attestation','legacy full-protocol paths outside selector policy',
        'historical test results inspected, not rerun; no independent past OS process trace',
        'local retained hash chains, not external signatures'],
    'evidence_sha256':{str(p.relative_to(ROOT)):sha(p) for p in sorted(E.rglob('*')) if p.is_file()},
    'manifest_excludes_itself':True}
manifest['new_review_files']=len(manifest['evidence_sha256'])+1
manifest['total_result_files_after_review']=len(results)+manifest['new_review_files']
with (E/'FINAL_INTEGRITY.json').open('x') as f:json.dump(manifest,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps({k:v for k,v in manifest.items() if k not in ['evidence_sha256','earlier_evidence_seals']},indent=2))
