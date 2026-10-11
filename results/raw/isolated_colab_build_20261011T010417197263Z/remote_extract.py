import hashlib,json,tarfile
from pathlib import Path,PurePosixPath
archive=Path('/content/mab_source_20261011T010417197263Z.tar.gz')
dest=Path('/content/mab_isolated_20261011T010417197263Z')
def digest(raw):return hashlib.sha256(raw).hexdigest()
assert digest(archive.read_bytes())=='953319b89a78d1e21498c4324570ec301bfb574eae4530a353db9c648b61b400'
assert not dest.exists() and not dest.is_symlink()
with tarfile.open(archive,'r:gz') as tar:
    members=tar.getmembers();names=[m.name for m in members]
    assert len(set(names))==len(names)
    for m in members:
        path=PurePosixPath(m.name)
        assert m.isfile() and not path.is_absolute() and '..' not in path.parts and str(path)==m.name
        assert m.size < 10*1024*1024
    identity_bytes=tar.extractfile('SOURCE_IDENTITY.json').read()
    assert digest(identity_bytes)=='7ce8297b76037af65d6d2dbbf3e2ccf5ec4684849090ee554a6d9552fcd50bda'
    identity=json.loads(identity_bytes);expected=identity['files_sha256']
    assert set(names)==set(expected)|{'SOURCE_IDENTITY.json'} and len(expected)==153
    # Verify every archived byte before creating any project directory.
    for path,h in expected.items():assert digest(tar.extractfile(path).read())==h,path
    dest.mkdir();source=dest/'source';source.mkdir()
    for m in members:
        path=source/m.name;path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('xb') as f:f.write(tar.extractfile(m).read())
    assert all(digest((source/p).read_bytes())==h for p,h in expected.items())
    freeze=source/'docs/studies/cpu_gpu_comparison_v1.freeze.json'
    assert digest(freeze.read_bytes())=='518ac535473e50fb61dab3a70858bdfe42dfdb43570f649174f44bffe40e1ac6'
    assert all(digest((source/p).read_bytes())==h for p,h in json.loads(freeze.read_text())['files_sha256'].items())
result=dict(archive_sha256=digest(archive.read_bytes()),source_identity_sha256=digest(identity_bytes),files_verified=len(expected),source=str(source),member_paths=names,source_files_sha256=expected,frozen_verified=True)
with (dest/'TRANSFER_VERIFIED.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print('TRANSFER_VERIFIED_BEGIN');print(json.dumps(result));print('TRANSFER_VERIFIED_END')
