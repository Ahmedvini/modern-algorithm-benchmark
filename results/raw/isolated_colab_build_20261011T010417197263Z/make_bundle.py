import hashlib,io,json,tarfile
from pathlib import Path
r=Path.cwd();e=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
policy=json.loads((r/'docs/NON_TIMING_TEST_SELECTION_v1.json').read_text())
expected=dict(policy['reviewed_source_sha256'])
matrix=json.loads((r/'docs/studies/cpu_gpu_comparison_v1.matrix.json').read_text())
baseline=json.loads((e/'BEFORE.json').read_text())['project_sha256']
extra=set(matrix['source_at_freeze_sha256'])|{'AGENTS.md','README.md','docs/NON_TIMING_TEST_SELECTION_v1.json','docs/CPU_GPU_DRIVER_REVIEW_v1.json','docs/studies/cpu_gpu_comparison_v1.freeze.json'}
extra |= set(json.loads((r/'docs/studies/cpu_gpu_comparison_v1.freeze.json').read_text())['files_sha256'])
for path in extra:expected[path]=baseline[path]
for path,digest in expected.items():
    p=r/path
    assert not p.is_symlink() and p.is_file() and sha(p)==digest,path
    assert path.startswith(('src/','include/','scripts/','tests/','cmake/','third_party/','docs/')) or path in ['AGENTS.md','README.md','CMakeLists.txt']
    assert '__pycache__' not in p.parts and not any(part.startswith('.') for part in p.parts),path
identity={'schema_version':1,'identity_method':'reviewed SHA-256 file manifest; no Git metadata','files_sha256':dict(sorted(expected.items())),'files':len(expected),'protocol':'cpu_gpu_comparison_v1','reviewed_source_count':len(policy['reviewed_source_sha256'])}
with (e/'SOURCE_IDENTITY.json').open('x') as f:json.dump(identity,f,sort_keys=True,indent=2);f.write('\n')
with (e/'reviewed_source.tar.gz').open('xb') as f:
    with tarfile.open(fileobj=f,mode='w:gz') as tar:
        for path in sorted(expected):tar.add(r/path,arcname=path,recursive=False)
        tar.add(e/'SOURCE_IDENTITY.json',arcname='SOURCE_IDENTITY.json',recursive=False)
bundle={'archive':'reviewed_source.tar.gz','archive_sha256':sha(e/'reviewed_source.tar.gz'),'source_identity_sha256':sha(e/'SOURCE_IDENTITY.json'),'files':len(expected),'revision':'No Git metadata; SOURCE_IDENTITY.json is the precise content identity'}
with (e/'BUNDLE.json').open('x') as f:json.dump(bundle,f,indent=2);f.write('\n')
print(json.dumps(bundle,indent=2))
