import hashlib,json,tarfile
from pathlib import Path
p=json.loads(Path('build/phase8_gate1_paths.json').read_text()); e=Path(p['evidence']); archive=Path(p['archive']); dest=Path(p['extracted'])
h=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
assert h(archive)==p['archive_sha256']
dest.mkdir()
with tarfile.open(archive,'r:gz') as t:
    for m in t.getmembers():
        assert not Path(m.name).is_absolute() and '..' not in Path(m.name).parts and m.isfile(), m.name
    members=len(t.getmembers());t.extractall(dest,filter='data')
source=dest/'modern-algorithm-benchmark'; manifest=json.loads((source/'SOURCE_SHA256.json').read_text())
assert all(h(source/f)==v for f,v in manifest.items())
assert manifest==json.loads((e/'source_before.json').read_text())
result=dict(archive_sha256=h(archive),archive_members=members,source_files_verified=len(manifest),all_source_matches_current_baseline=True,extraction=str(source),cloud_execution=False)
with (e/'archive_verification.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result,indent=2))
