"""Read-only fields from established environment/resource capture procedures."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import shutil

e=Path(__file__).resolve().parent
def optional(path):
    try:return dict(path=str(path),text=Path(path).read_text().strip(),available=True)
    except OSError as error:return dict(path=str(path),available=False,error=str(error))
mem=optional('/proc/meminfo')
memory={line.split(':',1)[0]:int(line.split(':',1)[1].split()[0])*1024
        for line in mem.get('text','').splitlines() if line.startswith(('MemTotal:','MemAvailable:'))}
paths=['/sys/fs/cgroup/cpu.max','/sys/fs/cgroup/memory.max','/sys/fs/cgroup/memory.current',
       '/sys/fs/cgroup/cpu/cpu.cfs_quota_us','/sys/fs/cgroup/cpu/cpu.cfs_period_us',
       '/sys/fs/cgroup/cpu,cpuacct/cpu.cfs_quota_us','/sys/fs/cgroup/cpu,cpuacct/cpu.cfs_period_us',
       '/sys/fs/cgroup/memory/memory.limit_in_bytes','/sys/fs/cgroup/memory/memory.usage_in_bytes']
cgroup=optional('/proc/self/cgroup');ancestors={}
for line in cgroup.get('text','').splitlines():
    if line.startswith('0::'):
        suffix=line.split('::',1)[1]
        leaf=Path('/sys/fs/cgroup')/suffix.lstrip('/')
        if '..' not in leaf.parts:
            for p in [leaf,*leaf.parents]:
                if p==Path('/sys'):break
                if str(p).startswith('/sys/fs/cgroup'):
                    ancestors[str(p)]={name:optional(p/name) for name in ['cpu.max','memory.max','memory.current']}
disk=shutil.disk_usage(e)
pci=[]
for p in sorted(Path('/sys/bus/pci/devices').glob('*')):
    vendor=optional(p/'vendor');cls=optional(p/'class')
    if vendor.get('text')=='0x10de' and cls.get('text','').startswith('0x03'):
        pci.append({'path':str(p),'vendor':vendor,'device':optional(p/'device'),'class':cls,
                    'driver':str((p/'driver').resolve()) if (p/'driver').exists() else None})
library=json.loads((e/'openmp_library.json').read_text())['stdout'].strip()
libraries=json.loads((e/'library_cache.json').read_text())
cuda_rows=[line.strip() for line in libraries['stdout'].splitlines()
           if any(s in line.lower() for s in ['libcuda','libcudart','libnvrtc','libnvidia-ml'])]
cuda_locations=[str(p) for p in Path('/usr/local').glob('cuda*')]
envnames=['OMP_DYNAMIC','OMP_THREAD_LIMIT','OMP_MAX_ACTIVE_LEVELS','OMP_WAIT_POLICY','OMP_PROC_BIND',
          'OMP_NUM_THREADS','CUDA_VISIBLE_DEVICES','CUDA_HOME','CUDA_PATH','CUDACXX','CC','CXX','ASAN_OPTIONS','LSAN_OPTIONS','UBSAN_OPTIONS']
data={'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'platform':platform.platform(),'uname':list(platform.uname()),'os_release':optional('/etc/os-release'),
      'logical_cpus':os.cpu_count(),'affinity':sorted(os.sched_getaffinity(0)),
      'memory_bytes':memory,'proc_meminfo':mem,'load_average':list(os.getloadavg()),
      'disk':dict(path=str(e),total_bytes=disk.total,used_bytes=disk.used,free_bytes=disk.free),
      'resource_files':{p:optional(p) for p in paths},'self_cgroup':cgroup,'cgroup_ancestors':ancestors,
      'limits':{n:list(resource.getrlimit(getattr(resource,n))) for n in ['RLIMIT_AS','RLIMIT_DATA','RLIMIT_MEMLOCK','RLIMIT_NOFILE','RLIMIT_NPROC']},
      'governors':{str(p):optional(p) for p in Path('/sys/devices/system/cpu').glob('cpu*/cpufreq/scaling_governor')},
      'environment':{k:os.environ.get(k) for k in envnames},
      'ctest_environment_keys_present':[k for k in os.environ if k.startswith('CTEST_')],
      'openmp_runtime':{'path':library,'present':Path(library).is_file(),
          'sha256':hashlib.sha256(Path(library).read_bytes()).hexdigest() if Path(library).is_file() else None},
      'nvidia_pci':pci,'nvidia_driver':optional('/proc/driver/nvidia/version'),
      'nvidia_module_present':Path('/sys/module/nvidia').is_dir(),
      'nvidia_device_nodes':{str(p):p.exists() for p in [Path('/dev/nvidiactl'),Path('/dev/nvidia0')]},
      'cuda_library_cache_rows':cuda_rows,'cuda_toolkit_locations':cuda_locations,
      'cuda_runtime_executed':False,'study_authorized':False}
with (e/'LOCAL_OBSERVATIONS.json').open('x') as f:json.dump(data,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps({k:v for k,v in data.items() if k not in ['proc_meminfo','governors','cgroup_ancestors']},indent=2))
