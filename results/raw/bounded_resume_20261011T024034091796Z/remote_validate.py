"""Explicit bounded validation only. No benchmark runner, pilot or timing API."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

root=Path('/content/mab_bounded_resume_20261011T024034091796Z');source=root/'source';e=root/'evidence'
sys.dont_write_bytecode=True
sys.path.insert(0,str(source/'scripts'))
from cpu_gpu_protocol import load_protocol, canonical
from cpu_gpu_provenance import TRUSTED_FREEZE_SHA256, strict_json
from cpu_gpu_validation_policy import verify_current_sources, trusted_policy, classify
from non_timing_tests import pre_discovery_gate, selected_ctest
from analyze_cpu_gpu import validate_resources

sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected=json.loads((root/'source_manifest.json').read_text())
assert all(sha(source/p)==h for p,h in expected.items())
verify_current_sources();model=load_protocol()
builds=json.loads((e/'BUILD_COMPLETE.json').read_text())
review=json.loads((e/'STATIC_SELECTION_REVIEW.json').read_text())
os.environ.update(model['openmp_policy']['environment'])
os.environ['PYTHONDONTWRITEBYTECODE']='1'
commands=e/'validation_commands';commands.mkdir()

def save(path,value):
    with path.open('x') as f:json.dump(value,f,indent=2);f.write('\n')

def call(name,argv,timeout=900):
    start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        p=subprocess.run(argv,cwd=source,capture_output=True,text=True,timeout=timeout)
        record=dict(argv=argv,cwd=str(source),started_utc=start,exit_code=p.returncode,status='completed',
                    stdout=p.stdout,stderr=p.stderr,omp_environment={k:os.environ.get(k) for k in model['openmp_policy']['environment']})
    except subprocess.TimeoutExpired as x:
        record=dict(argv=argv,cwd=str(source),started_utc=start,exit_code=None,status='timeout',
                    stdout=str(x.stdout),stderr=str(x.stderr))
    save(commands/(name+'.json'),record)
    print(name,'exit',record['exit_code'],flush=True)
    if record['exit_code']!=0:raise RuntimeError(name+' failed; inspect retained command record')
    return record

# Never trust a stale build or a guard review from a different directory.
for name in ['cpu-release','cpu-sanitize','gpu-release']:
    b=Path(builds['builds'][name])
    assert all(sha(b/p)==h for p,h in builds['identities'][name].items())
    _,guard=pre_discovery_gate(b)
    assert guard==review[name]['guard']

records={}
for label,name,prefix in [('cpu_release','cpu-release',None),
                         ('cpu_sanitize','cpu-sanitize',['env','-u','ASAN_OPTIONS','-u','LSAN_OPTIONS','UBSAN_OPTIONS=halt_on_error=1'])]:
    command_name=label+'_ctest'
    try:
        result=selected_ctest(call,e,command_name,Path(builds['builds'][name]),prefix=prefix,allow_diagnostics=True)
    except RuntimeError:
        if label!='cpu_sanitize':raise
        failed=json.loads((commands/(command_name+'.json')).read_text())
        assert 'LeakSanitizer does not work under ptrace' in failed['stdout']+failed['stderr'], 'unrelated sanitizer failure'
        save(e/'LEAK_LIMITATION.json',dict(reason='LeakSanitizer does not work under ptrace',original_record=command_name+'.json'))
        command_name+='__ptrace_no_leaks'
        result=selected_ctest(call,e,command_name,Path(builds['builds'][name]),
                              prefix=['env','ASAN_OPTIONS=detect_leaks=0','UBSAN_OPTIONS=halt_on_error=1'],allow_diagnostics=True)
    plan=json.loads((e/(command_name+'_selection.json')).read_text())
    assert plan['selected_count']==21 and plan['selected']==review[name]['selected_cpu_with_diagnostics']
    assert re.search(r'0 tests failed out of 21(?:\s|$)',result['stdout']) and '***Skipped' not in result['stdout']
    records[label]=dict(status='passed',exit_code=0,skipped=0,missing=0,passed=21,sha256=sha(commands/(command_name+'.json')))

gpu=Path(builds['builds']['gpu-release'])
binary_hashes={n:sha(gpu/n) for n in ['cpu_gpu_comparison','test_cuda_prepared_correctness','test_parallel_workers']}
description=call('comparison_description',[str(gpu/'cpu_gpu_comparison'),'--describe'],60)
description_data=strict_json(description['stdout'])
assert description_data['cub_version']==300001 and description_data['cuda_architectures']=='75'
assert description_data['build_type']=='Release' and not description_data['sanitizers']
save(e/'COMPARISON_DESCRIPTION.json',description_data)
gpu_result=call('gpu_prepared_untimed',[str(gpu/'test_cuda_prepared_correctness')],240)
gpu_data=strict_json(gpu_result['stdout'])
assert gpu_data['status']=='passed' and gpu_data['inputs']==163 and gpu_data['output_checks']==489
assert gpu_data['invalid_operations_rejected']==489 and gpu_data['failures']==0 and gpu_data['study_eligible'] is False
records['gpu_prepared']=dict(status='passed',exit_code=0,skipped=0,missing=0,inputs=gpu_data['inputs'],
                             output_checks=gpu_data['output_checks'],failures=gpu_data['failures'],
                             sha256=sha(commands/'gpu_prepared_untimed.json'))

# Existing bounded sizing/allocation path returns before input generation/timing.
# It allocates only diagnostic keys/workspaces, never the complete benchmark workload.
sizes=sorted({cell['recipe']['size'] for cell in model['study']['cells']})
assert sizes==[1025,65537,1000000]
memory={line.split(':')[0]:line.split(':')[1].strip() for line in Path('/proc/meminfo').read_text().splitlines() if ':' in line}
host_available=int(memory['MemAvailable'].split()[0])*1024
disk=shutil.disk_usage(root).free
assert host_available>=1024**3 and disk>=1024**3
resource_rows=[]
for n in sizes:
    result=call('resources_'+str(n),[str(gpu/'cpu_gpu_comparison'),'--resources',str(n)],90)
    data=strict_json(result['stdout']);validate_resources(data,n)
    assert data['known_host_peak_payload_bytes']<=256*1024**2 and 24*n<=host_available//2
    resource_rows.append(dict(size=n,query=data,explicit_key_cudaMalloc_requested_bytes=8*n,
                              explicit_workspace_cudaMalloc_requested_bytes=data['prepared_diagnostic_cudaMalloc_requested_bytes']+data['adapter_diagnostic_cudaMalloc_requested_bytes'],
                              calculated_full_study_host_payload_bytes=24*n,host_available_bytes=host_available,
                              disk_free_bytes=disk,physical_gpu_allocation='not measured',sorting_executed=False))
save(e/'WORKSPACE_RESOURCES.json',dict(rows=resource_rows,all_limits_passed=True,sizes=sizes))
records['workspace']=dict(status='passed',exit_code=0,skipped=0,missing=0,sizes=sizes,all_limits_passed=True,
                         sha256=sha(e/'WORKSPACE_RESOURCES.json'))
worker_result=call('actual_workers_untimed',[str(gpu/'test_parallel_workers')],120)
worker=strict_json(worker_result['stdout'])
assert worker['status']=='passed' and worker['output_checks']==12 and len(worker['calls'])==12
assert worker['executable']==str((gpu/'test_parallel_workers').resolve())
for row in worker['calls']:
    parallel=row['size']>=32768
    assert row['actual_team_size']==(2 if parallel else 1) and row['parallel_region']==parallel and row['correctness'] is True
assert worker['build_type']=='Release' and not worker['sanitizers']
records['workers']=dict(status='passed',exit_code=0,skipped=0,missing=0,output_checks=12,threshold_team_verified=True,
                       sha256=sha(commands/'actual_workers_untimed.json'))
assert all(sha(gpu/n)==h for n,h in binary_hashes.items())
assert all(sha(source/p)==h for p,h in expected.items())
verify_current_sources()
context=dict(session_id='gpu-t4-s-kkb-usw1b1-zafww0nxdtgf',source_identity=hashlib.sha256(canonical(expected)).hexdigest(),
             build_identity=sha(e/'BUILD_COMPLETE.json'),binary_identity=binary_hashes['cpu_gpu_comparison'],
             freeze_sha256=TRUSTED_FREEZE_SHA256,record_sha256={n:r['sha256'] for n,r in records.items()})
_,anchors=trusted_policy()
artifact=dict(schema_version=2,policy='cpu_gpu_validation_v2',artifact_kind='correctness_validation',status='passed',
              study_eligible=False,execution_authorized=False,protected_source_sha256=anchors,records=records,
              **{k:v for k,v in context.items() if k!='record_sha256'})
assessment=classify(artifact,context)
save(e/'CORRECTNESS_BUNDLE.json',artifact);save(e/'VALIDATION_CONTEXT.json',context)
save(e/'CLASSIFICATION.json',assessment)
save(e/'BOUNDED_COMPLETE.json',dict(complete=True,study_eligible=False,study_execution_authorized=False,
                                  tests=records,executable_sha256=binary_hashes,benchmark_trials=0,warmups=0))
print('BOUNDED_VALIDATION_PASSED; FULL STUDY NOT AUTHORIZED',flush=True)
