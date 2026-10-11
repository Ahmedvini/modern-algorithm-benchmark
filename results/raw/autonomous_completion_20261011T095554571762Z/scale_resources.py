import hashlib,json,os,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
E=Path(__file__).resolve().parent
stage=sys.argv[1]
n=10000000 if stage=='10m' else 100000000
memory={line.split(':')[0]:int(line.split(':')[1].split()[0])*1024 for line in Path('/proc/meminfo').read_text().splitlines() if ':' in line and line.split(':')[1].strip().endswith('kB')}
payload=16*n;available=memory['MemAvailable'];disk=shutil.disk_usage(ROOT).free
cgroup={p:Path(p).read_text().strip() if Path(p).exists() else None for p in ['/sys/fs/cgroup/memory.max','/sys/fs/cgroup/memory.current','/sys/fs/cgroup/cpu.max']}
assert available>=payload+3*1024**3, 'insufficient RAM headroom'
assert disk>=2*1024**3, 'insufficient disk'
if cgroup['/sys/fs/cgroup/memory.max'] not in [None,'max']:
    assert int(cgroup['/sys/fs/cgroup/memory.max'])-int(cgroup['/sys/fs/cgroup/memory.current'])>=payload+3*1024**3, 'insufficient cgroup headroom'
assert not (E/('sorting_'+stage)).exists(), 'output collision'
if stage=='100m':
    complete=json.loads((E/'sorting_10m/COMPLETE.json').read_text());assert complete['complete'] and complete['runs']==15
    assert (E/'sorting_10m_summary.json').exists(), '10M correctness analysis required first'
observed=dict(stage=stage,size=n,payload_estimate_bytes=payload,available_host_bytes=available,disk_free_bytes=disk,cgroup=cgroup,
    margin_host_bytes=available-payload,guarantee=False,policy_sha256=hashlib.sha256((ROOT/'docs/CPU_SCALING_PROTOCOL_v1.md').read_bytes()).hexdigest(),
    cpu_affinity=sorted(os.sched_getaffinity(0)),load_average=os.getloadavg(),governors={str(p):p.read_text().strip() for p in Path('/sys/devices/system/cpu').glob('cpu*/cpufreq/scaling_governor')})
with (E/('RESOURCES_'+stage+'.json')).open('x') as f:json.dump(observed,f,indent=2,sort_keys=True)
print(json.dumps(observed,indent=2))
