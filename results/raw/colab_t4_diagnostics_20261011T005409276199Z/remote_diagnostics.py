"""Read-only cloud diagnostics. No project executable, CUDA API or kernel runs."""
import datetime
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys

def command(argv):
    try:
        p=subprocess.run(argv,input='',capture_output=True,text=True,timeout=25)
        return dict(argv=argv,exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr)
    except (OSError,subprocess.TimeoutExpired) as error:
        return dict(argv=argv,exit_code=None,error=str(error))
def text(path):
    try:return Path(path).read_text().strip()
    except OSError:return None
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

# These are metadata/version commands, never CUDA execution or project binaries.
commands=[['uname','-a'],['python3','--version'],['cmake','--version'],['g++','--version'],
          ['nvcc','--version'],['nvidia-smi'],
          ['nvidia-smi','--query-gpu=name,uuid,driver_version,memory.total,memory.free,temperature.gpu,clocks.sm,clocks.mem,power.limit','--format=csv,noheader,nounits'],
          ['nvidia-smi','--query-compute-apps=pid,process_name,used_memory','--format=csv,noheader,nounits'],
          ['ldconfig','-p']]
observations=[command(a) for a in commands]
packages={}
for name in ['numpy','matplotlib','pip']:
    try:packages[name]=dict(present=True,version=importlib.metadata.version(name))
    except importlib.metadata.PackageNotFoundError:packages[name]=dict(present=False,version=None)
roots=[];errors=[];comparisons=[]
# Inspect ordinary Colab workspace only; never scan mounted private Drive data.
# Source discovery has a bounded, pruned walk and reads no source as executable.
base=Path('/content')
for directory,dirs,files in os.walk(base,followlinks=False):
    p=Path(directory);depth=len(p.relative_to(base).parts)
    dirs[:]=[d for d in dirs if d not in ['drive','.git','node_modules','.venv','venv','__pycache__','results','sample_data']
             and not (p/d).is_symlink() and depth<7]
    if 'cpu_gpu_comparison' in files:
        f=p/'cpu_gpu_comparison'
        comparisons.append(dict(path=str(f),bytes=f.stat().st_size,sha256=sha(f),executable_bit=os.access(f,os.X_OK),executed=False))
    if 'CMakeLists.txt' in files and (p/'scripts/cpu_gpu_protocol.py').is_file():
        item={'path':str(p),'files':{}}
        relative=['docs/CPU_GPU_COMPARISON_PROTOCOL_v1.md','docs/studies/cpu_gpu_comparison_v1.matrix.json',
            'docs/studies/cpu_gpu_comparison_v1.resources.csv','docs/studies/cpu_gpu_comparison_v1.freeze.json',
            'third_party/cub/UPSTREAM.json','src/cuda/cub_sort.cu']
        for name in relative:
            f=p/name
            item['files'][name]=dict(present=f.is_file(),sha256=sha(f) if f.is_file() else None)
        roots.append(item)
cuda_files={}
for prefix in [Path('/usr/local/cuda'),*sorted(Path('/usr/local').glob('cuda-*'))]:
    for name in ['version.json','version.txt','include/cuda_runtime_api.h','include/cuda.h',
                 'include/cccl/cub/version.cuh','include/cccl/cub/device/device_radix_sort.cuh',
                 'include/cub/version.cuh','include/cub/device/device_radix_sort.cuh']:
        p=prefix/name
        if p.is_file():
            item=dict(path=str(p),sha256=sha(p))
            if name in ['version.json','version.txt']:item['text']=text(p)
            elif name.endswith('version.cuh'):item['version_macros']=[l for l in p.read_text().splitlines() if l.startswith('#define CUB_')]
            cuda_files[str(p)]=item
disk=shutil.disk_usage('/content')
report=dict(schema_version=1,kind='colab_session_diagnostics_only',observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    command_results=observations,platform=platform.platform(),python_version=sys.version,
    affinity=sorted(os.sched_getaffinity(0)),logical_cpu_count=os.cpu_count(),meminfo=text('/proc/meminfo'),
    disk=dict(path='/content',total_bytes=disk.total,free_bytes=disk.free),load_average=list(os.getloadavg()),
    cgroup={p:text(p) for p in ['/sys/fs/cgroup/cpu.max','/sys/fs/cgroup/memory.max','/sys/fs/cgroup/memory.current']},
    packages=packages,tool_paths={n:shutil.which(n) for n in ['python3','cmake','g++','nvcc','nvidia-smi']},
    cuda_metadata_files=cuda_files,project_roots=roots,comparison_executables=comparisons,
    searched_scope='/content, depth<=8, pruned Drive/results/private and dependency directories; no files outside scope assumed absent',
    environment={k:os.environ.get(k) for k in ['CUDA_VISIBLE_DEVICES','CUDA_HOME','CUDA_PATH','CUDACXX',
        'OMP_DYNAMIC','OMP_THREAD_LIMIT','OMP_MAX_ACTIVE_LEVELS','OMP_WAIT_POLICY','OMP_PROC_BIND']},
    tests_run=0,builds_run=0,cuda_api_calls=0,cuda_kernels=0,benchmarks=0,study_authorized=False)
print('MAB_DIAGNOSTICS_JSON_BEGIN')
print(json.dumps(report,indent=2,sort_keys=True))
print('MAB_DIAGNOSTICS_JSON_END')
