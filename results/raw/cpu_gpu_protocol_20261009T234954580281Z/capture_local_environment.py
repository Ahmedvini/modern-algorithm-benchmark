"""Non-destructive local planning metadata; not current Colab/GPU metadata."""
import json,os,platform,resource,shutil,sys
from pathlib import Path

here=Path(__file__).resolve().parent
def read(path):
    try:return Path(path).read_text().strip()
    except OSError:return None
memory={}
for line in (read('/proc/meminfo') or '').splitlines():
    key,value=line.split(':',1)
    if key in ('MemTotal','MemAvailable'):memory[key]=value.strip()
cpu_model=next((line.split(':',1)[1].strip() for line in (read('/proc/cpuinfo') or '').splitlines() if line.startswith('model name')),None)
disk=shutil.disk_usage('.')
report=dict(kind='local_planning_host_not_colab',os=platform.platform(),kernel=platform.release(),architecture=platform.machine(),
    cpu_model=cpu_model,logical_cpus=os.cpu_count(),affinity=sorted(os.sched_getaffinity(0)) if hasattr(os,'sched_getaffinity') else None,
    memory=memory,cgroup_memory_max=read('/sys/fs/cgroup/memory.max'),cgroup_cpu_max=read('/sys/fs/cgroup/cpu.max'),
    disk_free_bytes=disk.free,python=sys.version,load_average=os.getloadavg() if hasattr(os,'getloadavg') else None,
    address_space_limit=resource.getrlimit(resource.RLIMIT_AS),cuda_session_checked=False,
    note='No GPU/toolchain execution or remote session query; resource estimates target a future fresh T4 preflight')
with (here/'local_planning_environment.json').open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps(report,indent=2))
