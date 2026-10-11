"""Static source/evidence verification only; no project imports or workload."""
import hashlib,json,tarfile
from pathlib import Path
r=Path.cwd();e=Path(__file__).resolve().parent
old=r/'results/raw/isolated_colab_build_20261011T010417197263Z'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def verified(mapping,base):
    assert all((base/p).is_file() and not (base/p).is_symlink() and sha(base/p)==h for p,h in mapping.items())
base=load(e/'BEFORE.json');verified(base['project_sha256'],r);verified(base['build_metadata_sha256'],r)
areas=['AGENTS.md','README.md','CMakeLists.txt','docs','scripts','tests','include','src','cmake','third_party']
current={str(p.relative_to(r)) for n in areas for b in [r/n] for p in ([b] if b.is_file() else b.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}
assert current==set(base['project_sha256']), 'unreviewed added/missing source or documentation'
counts={}
for name in ['ctest_path_independent_review_20261011T000547578754Z','cpu_gpu_readiness_20261011T004018152238Z','colab_t4_diagnostics_20261011T005409276199Z','isolated_colab_build_20261011T010417197263Z']:
    d=r/'results/raw'/name;seal=load(d/'FINAL_INTEGRITY.json');entries=seal['evidence_sha256']
    prefix=str(d.relative_to(r))+'/'
    if all(path.startswith(prefix) for path in entries):
        entries={path[len(prefix):]:h for path,h in entries.items()}
    else:
        assert all(not path.startswith('results/') and not Path(path).is_absolute() and '..' not in Path(path).parts for path in entries), 'ambiguous seal path convention'
    verified(entries,d)
    assert set(entries)=={str(p.relative_to(d)) for p in d.rglob('*') if p.is_file() and p.name!='FINAL_INTEGRITY.json'}
    counts[name]=len(entries)
assert '**Verdict: PASS.**' in (r/'results/raw/ctest_path_independent_review_20261011T000547578754Z/FINAL_AUDIT.md').read_text()
freeze=r/'docs/studies/cpu_gpu_comparison_v1.freeze.json'
assert sha(freeze)=='518ac535473e50fb61dab3a70858bdfe42dfdb43570f649174f44bffe40e1ac6'
verified(load(freeze)['files_sha256'],r)
review=r/'docs/CPU_GPU_DRIVER_REVIEW_v1.json'
assert sha(review)=='b6a63a7e65827970d6b27e872e738052cd5faf94d88ee711dbccd5f77f90ef2a'
anchors=dict(load(r/'docs/studies/cpu_gpu_comparison_v1.matrix.json')['source_at_freeze_sha256'])
anchors['CMakeLists.txt']=load(review)['current_cmake_sha256'];verified(anchors,r)
policy=load(r/'docs/NON_TIMING_TEST_SELECTION_v1.json');verified(policy['reviewed_source_sha256'],r)
identity=load(old/'SOURCE_IDENTITY.json');verified(identity['files_sha256'],r)
assert sha(old/'SOURCE_IDENTITY.json')=='7ce8297b76037af65d6d2dbbf3e2ccf5ec4684849090ee554a6d9552fcd50bda'
assert set(policy['reviewed_source_sha256'])<=set(identity['files_sha256'])
archive=old/'reviewed_source.tar.gz'
assert sha(archive)=='953319b89a78d1e21498c4324570ec301bfb574eae4530a353db9c648b61b400'
with tarfile.open(archive,'r:gz') as tar:
    names=tar.getnames();assert len(names)==len(set(names))
    assert set(names)==set(identity['files_sha256'])|{'SOURCE_IDENTITY.json'}
    assert all(m.isfile() for m in tar.getmembers())
    for p,h in identity['files_sha256'].items():assert hashlib.sha256(tar.extractfile(p).read()).hexdigest()==h
pin=load(r/'third_party/cub/UPSTREAM.json');assert pin['reference_release']=='v3.0.1' and pin['cub_version']==300001
for name in ['SOURCE_IDENTITY.json','BUNDLE.json','reviewed_source.tar.gz']:
    with (e/name).open('xb') as f:f.write((old/name).read_bytes())
result=dict(verified=True,git_metadata='absent; no clean-Git or commit claim',reviewed_revision_sha256=sha(e/'SOURCE_IDENTITY.json'),
    archive_sha256=sha(e/'reviewed_source.tar.gz'),source_files=len(identity['files_sha256']),project_membership_verified=len(current),
    reviewed_implementation_files=len(policy['reviewed_source_sha256']),protected_anchors_verified=len(anchors),
    evidence_seals_rehashed=counts,unreviewed_source_changes=[],frozen_verified=True)
with (e/'SOURCE_REVIEW.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result,indent=2))
