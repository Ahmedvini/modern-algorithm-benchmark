"""Independent direct diagnostics after CTest guard refusal. No discovery/tests suites."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

root=Path('/content/mab_bounded_resume_20261011T024034091796Z');source=root/'source';e=root/'evidence'
sys.dont_write_bytecode=True
sys.path.insert(0,str(source/'scripts'))
from cpu_gpu_protocol import load_protocol
from cpu_gpu_provenance import strict_json
from cpu_gpu_validation_policy import verify_current_sources
from analyze_cpu_gpu import validate_resources

sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected=json.loads((root/'source_manifest.json').read_text())
assert all(sha(source/p)==h for p,h in expected.items())
verify_current_sources();model=load_protocol()
builds=json.loads((e/'BUILD_COMPLETE.json').read_text());gpu=Path(builds['builds']['gpu-release'])
assert all(sha(gpu/p)==h for p,h in builds['identities']['gpu-release'].items())
os.environ.update(model['openmp_policy']['environment'])
os.environ['PYTHONDONTWRITEBYTECODE']='1'
commands=e/'direct_commands';commands.mkdir()
binary_hashes={n:sha(gpu/n) for n in ['cpu_gpu_comparison','test_cuda_prepared_correctness','test_parallel_workers']}

def save(path,value):
    with path.open('x') as f:json.dump(value,f,indent=2);f.write('\n')

def call(name,argv,timeout=240):
    allowed=([str(gpu/'test_cuda_prepared_correctness')], [str(gpu/'test_parallel_workers')],
             [str(gpu/'cpu_gpu_comparison'),'--describe'],
             *[[str(gpu/'cpu_gpu_comparison'),'--resources',str(n)] for n in [1025,65537,1000000]])
    assert argv in allowed,'unreviewed direct command; no timing command permitted'
    p=subprocess.run(argv,cwd=source,capture_output=True,text=True,timeout=timeout)
    record=dict(argv=argv,cwd=str(source),finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr,
                binary_sha256_before=binary_hashes[Path(argv[0]).name],binary_sha256_after=sha(Path(argv[0])),
                classification='untimed correctness or bounded resource diagnostic; no benchmarks')
    save(commands/(name+'.json'),record)
    print(name,'exit',p.returncode,flush=True)
    assert p.returncode==0 and record['binary_sha256_before']==record['binary_sha256_after'], name+' failed'
    return strict_json(p.stdout)

states=dict(cpu_release='BLOCKED: pre-discovery Dart metadata mismatch; no discovery/test executed',
            cpu_sanitize='BLOCKED: same pre-discovery policy mismatch; no sanitizer test executed')
try:
    description=call('comparison_description',[str(gpu/'cpu_gpu_comparison'),'--describe'])
    assert description['cub_version']==300001 and description['cuda_architectures']=='75'
    assert description['build_type']=='Release' and not description['sanitizers']
    save(e/'COMPARISON_DESCRIPTION.json',description)
    prepared=call('gpu_prepared_untimed',[str(gpu/'test_cuda_prepared_correctness')])
    assert prepared['status']=='passed' and prepared['inputs']==163 and prepared['output_checks']==489
    assert prepared['invalid_operations_rejected']==489 and prepared['failures']==0 and not prepared['study_eligible']
    states['gpu_prepared']=dict(status='PASS',inputs=prepared['inputs'],output_checks=prepared['output_checks'],
                                 rejected_invalid_operations=prepared['invalid_operations_rejected'],failed=0,skipped=0)
    sizes=sorted({c['recipe']['size'] for c in model['study']['cells']});assert sizes==[1025,65537,1000000]
    meminfo=Path('/proc/meminfo').read_text()
    mem={line.split(':')[0]:line.split(':')[1].strip() for line in meminfo.splitlines() if ':' in line}
    available=int(mem['MemAvailable'].split()[0])*1024;disk=shutil.disk_usage(root).free
    assert available>=1024**3 and disk>=1024**3
    cgroup={}
    for path in ['/sys/fs/cgroup/cpu.max','/sys/fs/cgroup/memory.max','/sys/fs/cgroup/memory.current',
                 '/sys/fs/cgroup/cpu/cpu.cfs_quota_us','/sys/fs/cgroup/cpu/cpu.cfs_period_us',
                 '/sys/fs/cgroup/cpu,cpuacct/cpu.cfs_quota_us','/sys/fs/cgroup/cpu,cpuacct/cpu.cfs_period_us',
                 '/sys/fs/cgroup/memory/memory.limit_in_bytes','/sys/fs/cgroup/memory/memory.usage_in_bytes']:
        p=Path(path);cgroup[path]=p.read_text().strip() if p.is_file() else None
    for limit,current in [('/sys/fs/cgroup/memory.max','/sys/fs/cgroup/memory.current'),
                          ('/sys/fs/cgroup/memory/memory.limit_in_bytes','/sys/fs/cgroup/memory/memory.usage_in_bytes')]:
        if cgroup[limit] and cgroup[limit]!='max' and cgroup[current]:
            assert int(cgroup[limit])-int(cgroup[current])>=1024**3
    assert len(os.sched_getaffinity(0))>=2
    for quota,period in [('/sys/fs/cgroup/cpu/cpu.cfs_quota_us','/sys/fs/cgroup/cpu/cpu.cfs_period_us'),
                         ('/sys/fs/cgroup/cpu,cpuacct/cpu.cfs_quota_us','/sys/fs/cgroup/cpu,cpuacct/cpu.cfs_period_us')]:
        if cgroup[quota] and cgroup[period] and int(cgroup[quota])>0:assert int(cgroup[quota])/int(cgroup[period])>=2
    if cgroup['/sys/fs/cgroup/cpu.max'] and cgroup['/sys/fs/cgroup/cpu.max'].split()[0]!='max':
        q,p=cgroup['/sys/fs/cgroup/cpu.max'].split();assert int(q)/int(p)>=2
    rows=[]
    for n in sizes:
        result=call('resources_'+str(n),[str(gpu/'cpu_gpu_comparison'),'--resources',str(n)],90)
        validate_resources(result,n)
        assert 24*n<=256*1024**2 and 24*n<=available//2
        rows.append(dict(size=n,query=result,explicit_key_cudaMalloc_requested_bytes=8*n,
                         explicit_workspace_cudaMalloc_requested_bytes=result['prepared_diagnostic_cudaMalloc_requested_bytes']+result['adapter_diagnostic_cudaMalloc_requested_bytes'],
                         calculated_full_study_host_payload_bytes=24*n,host_available_bytes=available,disk_free_bytes=disk,
                         physical_gpu_allocation='not measured',sorting_executed=False))
    save(e/'WORKSPACE_RESOURCES.json',dict(rows=rows,sizes=sizes,all_limits_passed=True,resource_snapshot_only=True,
                                        linux_meminfo=meminfo,cgroup=cgroup,cpu_affinity=sorted(os.sched_getaffinity(0))))
    states['workspace']=dict(status='PASS',sizes=sizes,all_limits_passed=True)
    workers=call('actual_workers_untimed',[str(gpu/'test_parallel_workers')],120)
    assert workers['status']=='passed' and workers['output_checks']==12 and len(workers['calls'])==12
    assert workers['executable']==str((gpu/'test_parallel_workers').resolve())
    for row in workers['calls']:
        parallel=row['size']>=32768
        assert row['actual_team_size']==(2 if parallel else 1) and row['parallel_region']==parallel and row['correctness'] is True
    assert workers['build_type']=='Release' and not workers['sanitizers']
    states['workers']=dict(status='PASS',output_checks=12,threshold_team_verified=True,task_participation='not measured')
    assert all(sha(gpu/n)==h for n,h in binary_hashes.items())
    assert all(sha(source/p)==h for p,h in expected.items())
    verify_current_sources()
    save(e/'DIRECT_DIAGNOSTICS_COMPLETE.json',dict(states=states,study_eligible=False,execution_authorized=False,
                                                session_id='gpu-t4-s-kkb-usw1b1-zafww0nxdtgf',executable_sha256=binary_hashes,
                                                full_validation_complete=False,benchmark_trials=0,warmups=0,source_unchanged=True))
    print(json.dumps(states,indent=2));print('INDEPENDENT_DIRECT_DIAGNOSTICS_PASSED; CPU SUITES BLOCKED; NO STUDY AUTHORIZATION')
except Exception as error:
    save(e/'DIRECT_DIAGNOSTICS_FAILED.json',dict(states=states,error=str(error),study_eligible=False,execution_authorized=False))
    raise
