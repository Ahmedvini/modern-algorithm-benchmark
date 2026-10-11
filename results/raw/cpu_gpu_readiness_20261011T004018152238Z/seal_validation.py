"""Seal this diagnostic assessment; only reads/hash comparisons/evidence writes."""
import datetime
import hashlib
import json
from pathlib import Path
import shlex

r=Path.cwd();e=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def scan(paths,cache=False):
    return {str(p.relative_to(r)):sha(p) for b in paths
            for p in ([b] if b.is_file() else sorted(b.rglob('*')))
            if p.is_file() and not p.is_relative_to(e) and not(cache and '__pycache__' in p.parts)}
b=read(e/'BEFORE.json');static=read(e/'STATIC_READINESS.json');observed=read(e/'LOCAL_OBSERVATIONS.json')
prior=scan([r/'results'])
project=scan([r/p for p in ['AGENTS.md','README.md','CMakeLists.txt','docs','scripts','tests','include','src','cmake','third_party']],True)
names={'CTestTestfile.cmake','CTestCustom.cmake','CTestCustom.ctest','CTestConfig.cmake','DartConfiguration.tcl','CMakeCache.txt','build.ninja','Makefile','compile_commands.json'}
build={str(p.relative_to(r)):sha(p) for p in sorted((r/'build').rglob('*')) if p.is_file() and p.name in names}
assert prior==b['prior_results_sha256'], 'historical results membership/content changed'
assert project==b['project_sha256'], 'project membership/content changed'
assert build==b['build_metadata_sha256'], 'build metadata membership/content changed'
artifacts=0
for item in static['build_caches']:
    p=r/item['cache'];assert sha(p)==item['sha256']
    for name,entry in item['artifacts'].items():
        f=p.parent/name
        assert f.is_file()==entry['present']
        if entry['present']:
            assert sha(f)==entry['sha256'];artifacts+=1
production_baseline=read(r/'results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/BEFORE.json')['current_source_sha256']
production={k:v for k,v in production_baseline.items() if k.startswith(('src/','include/','third_party/')) or k=='CMakeLists.txt'}
assert all(sha(r/k)==v for k,v in production.items())
for key in ['frozen','protected_anchors','review_seal','reviewed_source']:
    assert not static[key]['differences']

logs=[]
for p in sorted(e.glob('*.json')):
    d=read(p)
    if isinstance(d,dict) and 'argv' in d and 'exit_code' in d:logs.append((p,d))
assert len(logs)==24,len(logs)
assert all(d['exit_code']==0 for _,d in logs)
lines=['# Exact diagnostic commands and observed exit statuses','',
       'Scope: static inspection and authorized non-benchmark tool/resource diagnostics only. '
       'No tests, CTest discovery, configure/build, CUDA execution, sorting calls, warmups or measured trials. '
       'A diagnostic command exit0 does not imply GPU availability or study eligibility.','',
       '## Initial unwrapped commands','']
for item in read(e/'EARLY_COMMANDS.json'):
    lines+=['```sh',shlex.join(item['argv']),'```','',f'Observed exit: {item["exit_code"]}. {item["scope"]}','']
lines+=['## Recorded child commands','',
        'Recorder: `python3 -B '+str(e.relative_to(r))+'/record.py NAME CATEGORY CHILD_ARGV...`. '
        'Each listed JSON contains exact argv, cwd, timestamp, stdout/stderr and observed child status. '
        'The recorder itself writes only this new evidence directory.','']
for p,d in logs:
    lines+=['### '+p.name,'','```sh',shlex.join(d['argv']),'```','',
            f'Observed child exit: {d["exit_code"]}. Category: {d["category"]}.','']
lines+=['## Not executed','',
        'No nvcc/nvidia-smi command ran locally because they are absent. No colab status/exec followed the empty session inventory. '
        'No session creation/reconnect, upload, install, kernel/runtime probe, CUB query/allocation, test, '
        'project binary, prerequisite runner, CTest, configure/build or benchmark was invoked. '
        'The Colab inventory reported pruning one stale external local session-cache entry.','',
        '## Evidence authoring','',
        'apply_patch created only record.py, PERMITTED_CHECKS.md, inspect_static.py, observe_local.py, '
        'EARLY_COMMANDS.json, FINAL_AUDIT.md and seal_validation.py inside this exclusive new evidence directory; '
        'all tool calls succeeded. BEFORE.json was created by the retained exclusive bootstrap. '
        'The static inspector and observation collector wrote their own JSON outputs here. '
        'No project or historical file was changed.','',
        '## Final preservation/seal command','',
        '```sh','python3 -B '+str((e/'seal_validation.py').relative_to(r)),'```','',
        'Executed directly to avoid writing an unsealed recorder log afterward. '
        'Successful terminal exit0 confirms all preservation assertions passed before the final seal was written. '
        'It creates this command inventory and the final manifest only.']
with (e/'COMMANDS.md').open('x') as f:f.write('\n'.join(lines)+'\n')
data={'schema_version':1,'status':'BLOCKED','observed_utc':observed['observed_utc'],
      'sealed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'command':['python3','-B',str((e/'seal_validation.py').relative_to(r))],'exit_code':0,
      'prior_result_files_verified':len(prior),'project_files_verified':len(project),
      'build_metadata_files_verified':len(build),'existing_artifact_hashes_rechecked':artifacts,
      'production_headers_dependencies_verified':len(production),
      'frozen_members_verified':static['frozen']['count'],
      'protected_anchors_verified':static['protected_anchors']['count'],
      'reviewed_source_verified':static['reviewed_source']['count'],
      'latest_review_sealed_files_verified':static['review_seal']['count'],
      'freeze_sha256':static['freeze_sha256'],'production_adapter_sha256':static['production_adapter_sha256'],
      'cub_version':static['cub_pin']['cub_version'],
      'cub_pin_sha256':sha(r/'third_party/cub/UPSTREAM.json'),
      'preservation_differences':[],
      'local_affinity':observed['affinity'],'local_memory_bytes':observed['memory_bytes'],
      'local_disk_free_bytes':observed['disk']['free_bytes'],
      'colab_session_inventory':read(e/'colab_sessions.json'),
      'blockers':['No active Colab server session','No local NVIDIA driver/device nodes or discoverable CUDA compiler/runtime',
                  'No local comparison executable; GPU build/dependencies/workspace/current VRAM not validated'],
      'unexecuted_out_of_scope':['configure/build','CTest discovery/tests','CUDA runtime/kernel/correctness probes',
          'actual OpenMP-team validation','CUB workspace/allocation/free-memory API diagnostic','timing/pilot/full study'],
      'tests_run':0,'ctest_discovery':0,'configures_builds':0,'cuda_workloads':0,
      'warmups':0,'measured_trials':0,'study_authorized':False,
      'recorded_commands':len(logs),'recorded_child_exit_codes':[d['exit_code'] for _,d in logs],
      'evidence_sha256':{str(p.relative_to(r)):sha(p) for p in sorted(e.rglob('*')) if p.is_file()},
      'manifest_excludes_itself':True}
data['new_evidence_files']=len(data['evidence_sha256'])+1
data['total_result_files']=len(prior)+data['new_evidence_files']
with (e/'FINAL_INTEGRITY.json').open('x') as f:json.dump(data,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps({k:v for k,v in data.items() if k not in ['evidence_sha256','colab_session_inventory']},indent=2))
