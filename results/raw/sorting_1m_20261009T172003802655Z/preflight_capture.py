#!/usr/bin/env python3
import datetime,hashlib,json,os,platform,shutil,subprocess,sys,tempfile
from pathlib import Path
root=Path.cwd();raw=Path(__file__).resolve().parent
sys.path.insert(0,str(root/'scripts'))
from capture_environment import capture,probe,read_optional
paths=json.loads((raw/'paths.json').read_text())
def snapshot():
    mem=read_optional('/proc/meminfo');fields={k:int(v.split()[0])*1024 for k,v in (line.split(':',1) for line in mem.splitlines())}
    cgroup=read_optional('/proc/self/cgroup');limits={}
    relative=next((line.split('::',1)[1] for line in cgroup.splitlines() if line.startswith('0::')),None)
    if relative is not None:
        leaf=Path('/sys/fs/cgroup')/relative.lstrip('/')
        for parent in [leaf,*leaf.parents]:
            if parent==Path('/sys/fs'):break
            for name in ['memory.max','memory.current','memory.swap.max','memory.events','cpu.max','cpuset.cpus.effective']:
                value=read_optional(parent/name)
                if value is not None:limits[str(parent/name)]=value.strip()
    freq={}
    for p in sorted(Path('/sys/devices/system/cpu/cpufreq').glob('policy*')):
        freq[p.name]={name:read_optional(p/name) for name in ['scaling_driver','scaling_governor','scaling_min_freq','scaling_max_freq','scaling_cur_freq','energy_performance_preference']}
    return {'captured_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'uname':platform.uname()._asdict(),'os_release':read_optional('/etc/os-release'),'meminfo':mem,'mem_bytes':fields,'disk_bytes':shutil.disk_usage(root)._asdict(),'loadavg':os.getloadavg(),'logical_cpus':os.cpu_count(),'allowed_cpus':sorted(os.sched_getaffinity(0)),'process_limits':read_optional('/proc/self/limits'),'cgroup':cgroup,'cgroup_ancestors':limits,'frequency_policies':freq,'intel_pstate_no_turbo':read_optional('/sys/devices/system/cpu/intel_pstate/no_turbo'),'pressure_cpu':read_optional('/proc/pressure/cpu'),'pressure_memory':read_optional('/proc/pressure/memory'),'pressure_io':read_optional('/proc/pressure/io'),'background_process_snapshot':probe(['ps','-eo','pid,comm,pcpu,pmem','--sort=-pcpu'])}
if len(sys.argv)>1:
    filename=sys.argv[1];record=snapshot()
else:
    filename='preflight.json';record=snapshot()
    with tempfile.TemporaryFile(dir=root) as f:f.write(b'access');f.seek(0);assert f.read()==b'access'
    record['writable']=True
    record['output_absent']=not os.path.lexists(paths['matrix'])
    record['estimated_array_workspace_bytes']=4*1000000*4
    record['planning_limit_bytes']=256*1024**2
    record['minimum_resource_headroom_bytes']=256*1024**2
    assert record['output_absent']
    assert record['mem_bytes']['MemAvailable']>=256*1024**2
    assert record['disk_bytes']['free']>=128*1024**2
    for name,value in record['cgroup_ancestors'].items():
        if name.endswith('/memory.max') and value!='max':
            current=record['cgroup_ancestors'].get(name.replace('memory.max','memory.current'))
            assert current is not None and int(value)-int(current)>=256*1024**2
    record['environment']=capture(root/'build/release',' '.join(sys.argv))
    record['commands']=[probe(c) for c in [['build/release/sort_benchmark','--help'],['build/release/sort_benchmark','--list-sorts'],['python3','scripts/run_matrix.py','--help'],['python3','scripts/analyze_results.py','--help'],['python3','--version'],['ldd','build/release/sort_benchmark'],['nm','-C','build/release/sort_benchmark']]]
    assert all(x['returncode']==0 for x in record['commands'])
    assert record['commands'][1]['stdout'].splitlines()==['std_sort','quick_sort','pdq_sort','tim_sort','merge_sort','radix_sort']
    assert 'libasan' not in record['commands'][-2]['stdout'] and 'libubsan' not in record['commands'][-2]['stdout']
    assert 'CountingLess' not in record['commands'][-1]['stdout']
    record['benchmark_sha256']=hashlib.sha256((root/'build/release/sort_benchmark').read_bytes()).hexdigest()
    record['benchmark_link_command']=(root/'build/release/CMakeFiles/sort_benchmark.dir/link.txt').read_text()
    assert 'mab_metrics' not in record['benchmark_link_command']
    manifest=json.loads((root/'build/release/generated/Release/source_hashes.json').read_text())
    for item in manifest['files']:assert hashlib.sha256((root/item['path']).read_bytes()).hexdigest()==item['sha256']
    record['source_manifest_matches']=True
    record['tool_sha256']={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [root/'scripts/run_matrix.py',root/'scripts/analyze_results.py',root/'scripts/capture_environment.py']}
    record['resource_checks_passed']=True
with (raw/filename).open('x') as f:json.dump(record,f,indent=2);f.write('\n')
print(filename,'load',record['loadavg'],'available RAM bytes',record['mem_bytes']['MemAvailable'],'disk free',record['disk_bytes']['free'])
