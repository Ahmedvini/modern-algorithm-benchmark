import ctypes
import ctypes.util
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess

commands = [ ['nvidia-smi','--query-gpu=name,uuid,driver_version,memory.total,memory.free','--format=csv'],
             ['nvcc','--version'],['c++','--version'],['cmake','--version'],['python3','--version'],
             ['lscpu'],['free','-b'],['df','-B1','/content'] ]
records=[]
for argv in commands:
    try:
        p=subprocess.run(argv,capture_output=True,text=True,timeout=45)
        records.append(dict(argv=argv,exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr))
    except Exception as e: records.append(dict(argv=argv,exit_code=None,error=str(e)))
print(json.dumps(dict(scope='diagnostics_only',commands=records,platform=platform.platform(),
                     python_packages={n:importlib.metadata.version(n) for n in ['pip','numpy','matplotlib']},
                     environment={n:os.environ.get(n) for n in ['OMP_DYNAMIC','OMP_THREAD_LIMIT','OMP_MAX_ACTIVE_LEVELS','OMP_PROC_BIND','OMP_WAIT_POLICY','CUDA_VISIBLE_DEVICES']},
                     approved_replacement_alias='cpu-gpu-bounded-validation-v3'),indent=2))
assert records[0]['exit_code']==0 and 'Tesla T4' in records[0]['stdout'], 'replacement T4 identity failed'
assert all(r['exit_code']==0 for r in records), 'missing environment prerequisites'
print('ENVIRONMENT_DIAGNOSTICS_PASSED')
