import json,platform,subprocess
from pathlib import Path
dest=Path('/content/mab_isolated_20261011T010417197263Z')
archive=Path('/content/mab_source_20261011T010417197263Z.tar.gz')
assert not dest.exists() and not dest.is_symlink(), 'destination already exists; do not overwrite'
assert not archive.exists() and not archive.is_symlink(), 'archive already exists; do not overwrite'
results=[]
for argv in [['nvidia-smi','--query-gpu=name,uuid,driver_version,memory.total,memory.free','--format=csv,noheader,nounits'],['nvcc','--version'],['cmake','--version'],['g++','--version']]:
    p=subprocess.run(argv,capture_output=True,text=True,timeout=30)
    results.append(dict(argv=argv,exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr))
assert all(v['exit_code']==0 for v in results)
assert results[0]['stdout'].split(',')[0]=='Tesla T4'
print('REMOTE_CHECK_BEGIN')
print(json.dumps(dict(destination=str(dest),archive=str(archive),paths_absent=True,platform=platform.platform(),commands=results)))
print('REMOTE_CHECK_END')
