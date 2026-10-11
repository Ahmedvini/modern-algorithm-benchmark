from pathlib import Path, PurePosixPath
import hashlib,json,tarfile
archive=Path('/content/cuda_timing_20261009T231303050084Z_source.tar.gz')
expected='fa7c1d2fc131ba832a5c357498a6c1523c3eeeea99d6c7c4478df30d04ab0f73'
actual=hashlib.sha256(archive.read_bytes()).hexdigest()
assert actual==expected,(actual,expected)
parent=Path('/content/cuda_timing_20261009T231303050084Z')
assert not parent.exists() and not parent.is_symlink(),str(parent)
with tarfile.open(archive,'r:gz') as tar:
 members=tar.getmembers();names=[]
 for member in members:
  path=PurePosixPath(member.name)
  assert not path.is_absolute() and '..' not in path.parts and path.parts[0]=='modern-algorithm-benchmark'
  assert member.isfile(),member.name
  names.append(member.name)
 assert len(names)==len(set(names))
 parent.mkdir()
 tar.extractall(parent,filter='data')
project=parent/'modern-algorithm-benchmark'
manifest=json.loads((project/'SOURCE_SHA256.json').read_text())
assert all(hashlib.sha256((project/name).read_bytes()).hexdigest()==sha for name,sha in manifest.items())
for name in ['results/raw','results/processed','results/figures']:(project/name).mkdir(parents=True,exist_ok=True)
report=dict(archive_sha256=actual,archive_members=names,source_files_verified=len(manifest),project=str(project))
(parent/'transfer_verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(archive_sha256=actual,source_files_verified=len(manifest),project=str(project))))
