import hashlib,json,tarfile
from pathlib import Path
paths=json.loads(Path('build/cub_sort_paths.json').read_text());e=Path(paths['evidence']);bundle=json.loads((e/'source_bundle.json').read_text())
assert hashlib.sha256(Path(bundle['archive']).read_bytes()).hexdigest()==bundle['sha256']
dest=Path('build')/('cub_source_relocation_'+paths['stamp']);dest.mkdir()
with tarfile.open(bundle['archive']) as t:
 for m in t.getmembers():assert m.isfile() and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts
 t.extractall(dest,filter='data')
root=dest/'modern-algorithm-benchmark';manifest=json.loads((root/'SOURCE_SHA256.json').read_text())
assert all(hashlib.sha256((root/p).read_bytes()).hexdigest()==v for p,v in manifest.items())
assert manifest==json.loads((e/'source_after.json').read_text())
with (e/'relocation.json').open('x') as f:json.dump(dict(extraction=str(root),verified_files=len(manifest),source_matches_reviewed=True),f,indent=2);f.write('\n')
print('Verified extracted source files:',len(manifest))
