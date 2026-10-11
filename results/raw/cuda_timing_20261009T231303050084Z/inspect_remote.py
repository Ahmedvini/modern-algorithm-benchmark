def _mab_inspect():
 import json,subprocess,platform
 from pathlib import Path
 result={'platform':platform.platform(),'commands':[],'content_entries':[p.name for p in Path('/content').iterdir()]}
 for argv in [['nvidia-smi','--query-gpu=name,driver_version,compute_cap,memory.total','--format=csv,noheader'],['nvcc','--version'],['cmake','--version'],['c++','--version']]:
  r=subprocess.run(argv,capture_output=True,text=True,timeout=30);result['commands'].append(dict(argv=argv,exit_code=r.returncode,stdout=r.stdout,stderr=r.stderr))
 print('MAB_ENVIRONMENT='+json.dumps(result))
 assert all(c['exit_code']==0 for c in result['commands'])
 assert 'T4' in result['commands'][0]['stdout']
_mab_inspect()
del _mab_inspect
