from pathlib import Path
import hashlib,json,tarfile,sys
root=Path('/content/mab_bounded_resume_20261011T024034091796Z')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(root/'source.tar.gz')=='320bc0a2574993efba0609c22d572551184ccafac9b8b3b41cb70d41297a72cc'
assert sha(root/'source_manifest.json')=='2a647c5f37ad1803d4f06e4e322d404236a7434ca99971f03a13aac171f8e49f'
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
(evidence/'transfer.json').write_text(json.dumps(dict(verified=True,files=len(files),archive_sha256='320bc0a2574993efba0609c22d572551184ccafac9b8b3b41cb70d41297a72cc',manifest_sha256='2a647c5f37ad1803d4f06e4e322d404236a7434ca99971f03a13aac171f8e49f',source=str(dest),source_sha256=files),indent=2)+'\n')
print('TRANSFER_VERIFIED',len(files),'320bc0a2574993efba0609c22d572551184ccafac9b8b3b41cb70d41297a72cc')
