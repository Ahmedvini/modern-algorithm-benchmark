from pathlib import Path
import hashlib,json,tarfile,sys
root=Path('/content/mab_bounded_20261011T020343203635Z')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(root/'source.tar.gz')=='03de3a45743206244c480195de4629b8d440139f0fc5e236981f1f9cecac7fa5'
assert sha(root/'source_manifest.json')=='52dfe8d47d83ccba8e520dc79dc24465fdeaf88cdbd8c9bce4036c848e6b936b'
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
(evidence/'transfer.json').write_text(json.dumps(dict(verified=True,files=len(files),archive_sha256='03de3a45743206244c480195de4629b8d440139f0fc5e236981f1f9cecac7fa5',manifest_sha256='52dfe8d47d83ccba8e520dc79dc24465fdeaf88cdbd8c9bce4036c848e6b936b',source=str(dest),source_sha256=files),indent=2)+'\n')
print('TRANSFER_VERIFIED',len(files),'03de3a45743206244c480195de4629b8d440139f0fc5e236981f1f9cecac7fa5')
