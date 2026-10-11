import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

root=Path('/content/mab_bounded_resume_20261011T024034091796Z')
source=root/'source'; evidence=root/'evidence'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected=json.loads((root/'source_manifest.json').read_text())
assert all(sha(source/p)==h for p,h in expected.items())
sys.path.insert(0,str(source/'scripts'))
from cpu_gpu_validation_policy import verify_current_sources
verify_current_sources()
commands=evidence/'build_commands';commands.mkdir()

def call(name,argv,timeout=900):
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    p=subprocess.run(argv,cwd=source,capture_output=True,text=True,timeout=timeout)
    record=dict(argv=argv,cwd=str(source),started_utc=started,exit_code=p.returncode,
                stdout=p.stdout,stderr=p.stderr,classification='configuration/build only; no tests/workloads')
    with (commands/(name+'.json')).open('x') as f:json.dump(record,f,indent=2);f.write('\n')
    print(name,'exit',p.returncode,flush=True)
    if p.returncode:print(p.stdout,p.stderr);raise RuntimeError(name+' failed')

common=['cmake','-S',str(source),'-DCMAKE_CXX_FLAGS=','-DCMAKE_CXX_FLAGS_RELEASE=-O3 -DNDEBUG',
        '-DMAB_ENABLE_OPENMP=ON','-DBUILD_TESTING=ON','-DMAB_ENABLE_VALIDATION_DIAGNOSTICS=ON',
        '-DPython3_EXECUTABLE='+str(Path(sys.executable).resolve())]
builds={}
for name,configuration,extra in [
    ('cpu-release','Release',['-DMAB_ENABLE_CUDA=OFF','-DMAB_ENABLE_CPU_GPU_COMPARISON=OFF']),
    ('cpu-sanitize','Debug',['-DMAB_ENABLE_CUDA=OFF','-DMAB_ENABLE_CPU_GPU_COMPARISON=OFF','-DMAB_ENABLE_SANITIZERS=ON']),
    ('gpu-release','Release',['-DMAB_ENABLE_CUDA=ON','-DMAB_ENABLE_CUDA_SORT=ON','-DMAB_ENABLE_CPU_GPU_COMPARISON=ON',
                              '-DMAB_ENABLE_SANITIZERS=OFF','-DCMAKE_CUDA_ARCHITECTURES=75',
                              '-DCMAKE_CUDA_FLAGS=','-DCMAKE_CUDA_FLAGS_RELEASE=-O3 -DNDEBUG'])]:
    build=root/name
    assert not build.exists(),'isolated build directory exists'
    call(name+'_configure',common+['-B',str(build),'-DCMAKE_BUILD_TYPE='+configuration]+extra)
    call(name+'_build',['cmake','--build',str(build),'--parallel','2'],1200)
    builds[name]=str(build)
assert all(sha(source/p)==h for p,h in expected.items())
identities={}
for name,build in builds.items():
    b=Path(build)
    files=[b/'CMakeCache.txt',b/'compile_commands.json',b/'CTestTestfile.cmake',b/'test_parallel_workers',b/'libmab_parallel.a']
    if name=='gpu-release':files += [b/'cpu_gpu_comparison',b/'test_cuda_prepared_correctness',b/'libmab_cuda_timing.a']
    identities[name]={str(p.relative_to(b)):sha(p) for p in files}
with (evidence/'BUILD_COMPLETE.json').open('x') as f:
    json.dump(dict(builds=builds,source_verified=True,identities=identities),f,indent=2);f.write('\n')
print('ISOLATED_BUILDS_COMPLETE',flush=True)
