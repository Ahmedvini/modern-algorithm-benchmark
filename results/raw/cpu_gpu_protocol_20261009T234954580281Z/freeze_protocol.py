"""Install new planning assets and freeze hashes; never launches a benchmark."""
import hashlib,json
from pathlib import Path

paths=json.loads(Path('build/cpu_gpu_protocol_paths.json').read_text())
source=Path(paths['backup'])/'assets_final'
prefix=Path('docs/studies/cpu_gpu_comparison_v1')
targets=[Path(str(prefix)+'.matrix.json'),Path(str(prefix)+'.resources.csv'),Path(str(prefix)+'.freeze.json')]
if any(p.exists() or p.is_symlink() for p in targets):
    raise SystemExit('Refusing to overwrite an existing protocol asset')
for target in targets[:2]:
    with target.open('xb') as f:f.write((source/target.name).read_bytes())
protocol=Path('docs/CPU_GPU_COMPARISON_PROTOCOL_v1.md')
files=[protocol,*targets[:2]]
hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
manifest=dict(protocol='cpu_gpu_comparison_v1',status='frozen_for_review',execution_authorized=False,
              files_sha256=hashes,evidence=paths['evidence'],
              note='Specification only; review, missing driver/analyzer, fresh gates and pilot required before study')
with targets[2].open('x') as f:json.dump(manifest,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps(manifest,indent=2))
