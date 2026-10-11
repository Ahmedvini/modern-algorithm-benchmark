def _mab_inspect():
 import hashlib,json,platform,subprocess
 from pathlib import Path
 commands=[['nvidia-smi','--query-gpu=index,name,driver_version,compute_cap,memory.total','--format=csv,noheader,nounits'],['nvcc','--version'],['cmake','--version'],['c++','--version']]
 records=[]
 for argv in commands:
  r=subprocess.run(argv,capture_output=True,text=True,timeout=30)
  records.append(dict(argv=argv,exit_code=r.returncode,stdout=r.stdout,stderr=r.stderr))
 archive=Path('/content/cub_sort_source_v2.tar.gz')
 result=dict(platform=platform.platform(),python=platform.python_version(),commands=records,
             content_entries=[p.name for p in sorted(Path('/content').iterdir()) if not p.name.startswith('.')],
             archive_exists=archive.exists() or archive.is_symlink(),
             archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest() if archive.is_file() else None,
             destination_exists=Path('/content/mab_cub_20261009T223853955936Z').exists())
 print('MAB_INSPECTION_JSON='+json.dumps(result,sort_keys=True))
 assert all(r['exit_code']==0 for r in records), 'Remote GPU/toolchain unavailable'
 assert 'T4' in records[0]['stdout'], 'Expected T4 not visible'
_mab_inspect()
del _mab_inspect
