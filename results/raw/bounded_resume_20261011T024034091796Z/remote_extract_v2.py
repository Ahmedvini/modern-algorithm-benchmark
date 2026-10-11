from pathlib import Path
import hashlib,json,tarfile,sys
root=Path('/content/mab_bounded_resume_20261011T024034091796Z_revision2')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(root/'source.tar.gz')=='5303683f37e48ab03bcb287b2c560d2100293b68209f63cc354fe0923ab9102f'
assert sha(root/'source_manifest.json')=='e5f16f241a6dd27fd5d4d751aecd06fc9d68f7dc28ae231be2fe4d608132b0c3'
files=json.loads((root/'source_manifest.json').read_text())
dest=root/'source';assert not dest.exists()
with tarfile.open(root/'source.tar.gz','r:gz') as t:
 members=t.getmembers()
 assert len(members)==len(files) and len({m.name for m in members})==len(members)
 for m in members:
  p=Path(m.name)
  assert m.isfile() and not p.is_absolute() and '..' not in p.parts and m.name in files
 dest.mkdir()
 t.extractall(dest,filter='data')
assert all(sha(dest/p)==h for p,h in files.items())
sys.path.insert(0,str(dest/'scripts'))
from cpu_gpu_validation_policy import verify_current_sources
from non_timing_tests import load_manifest
verify_current_sources();manifest=load_manifest()
assert len([n for n,a in manifest['tests'].items() if a['classification']=='cpu_correctness' and not a.get('diagnostic_only')])==19
evidence=root/'evidence';evidence.mkdir()
(evidence/'transfer.json').write_text(json.dumps(dict(verified=True,files=len(files),archive_sha256='5303683f37e48ab03bcb287b2c560d2100293b68209f63cc354fe0923ab9102f',manifest_sha256='e5f16f241a6dd27fd5d4d751aecd06fc9d68f7dc28ae231be2fe4d608132b0c3',source=str(dest),source_sha256=files),indent=2)+'\n')
print('TRANSFER_VERIFIED',len(files),'5303683f37e48ab03bcb287b2c560d2100293b68209f63cc354fe0923ab9102f')
