import hashlib,json
from pathlib import Path
p=json.loads(Path('build/colab_validation_paths.json').read_text());e=Path(p['evidence']);old=json.loads((e/'prior_artifacts_sha256.json').read_text())
changed=[name for name,sha in old.items() if not Path(name).is_file() or hashlib.sha256(Path(name).read_bytes()).hexdigest()!=sha]
source=json.loads((e/'source_before.json').read_text());protected=[name for name in source if (name.startswith('docs/studies/') or (name.startswith('docs/') and ('PROTOCOL' in name or 'GUIDE' in name)) or name in ['third_party/pdqsort/pdqsort.h','third_party/timsort/include/gfx/timsort.hpp','third_party/cub/LICENSE'])]
protected_changed=[name for name in protected if hashlib.sha256(Path(name).read_bytes()).hexdigest()!=source[name]]
result={'previous_artifacts':len(old),'changed_or_missing':changed,'protected_source_files':len(protected),'protected_source_changed':protected_changed,'original_bundle_sha256':hashlib.sha256(Path(p['archive']).read_bytes()).hexdigest()}
assert result['original_bundle_sha256']==p['archive_sha256'];assert not changed and not protected_changed
with (e/'integrity_after_validation.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result,indent=2))
