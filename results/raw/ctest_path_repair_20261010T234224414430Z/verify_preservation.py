"""File hashes/strict JSON only; no project imports, tests or probes."""
import hashlib
import json
from pathlib import Path
import sys

root = Path.cwd(); base = Path(__file__).resolve().parent
def pairs(items):
    out = {}
    for k,v in items:
        if k in out: raise ValueError('duplicate JSON key: '+k)
        out[k]=v
    return out
def read(path):return json.loads(path.read_text(),object_pairs_hook=pairs)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def verify(mapping):
    differences=[p for p,h in mapping.items() if not (root/p).is_file() or sha(root/p)!=h]
    assert not differences,differences
    return len(mapping)
before=read(base/'BEFORE.json');stage=sys.argv[1]
report=dict(stage=stage,prior_result_files_verified=verify(before['prior_results_sha256']),
            build_metadata_verified=verify(before['build_metadata_sha256']),differences=[])
assert sha(root/'docs/studies/cpu_gpu_comparison_v1.freeze.json')=='518ac535473e50fb61dab3a70858bdfe42dfdb43570f649174f44bffe40e1ac6'
assert sha(root/'docs/CPU_GPU_DRIVER_REVIEW_v1.json')=='b6a63a7e65827970d6b27e872e738052cd5faf94d88ee711dbccd5f77f90ef2a'
report['frozen_members_verified']=verify(read(root/'docs/studies/cpu_gpu_comparison_v1.freeze.json')['files_sha256'])
anchors=read(root/'docs/studies/cpu_gpu_comparison_v1.matrix.json')['source_at_freeze_sha256'].copy()
anchors['CMakeLists.txt']=read(root/'docs/CPU_GPU_DRIVER_REVIEW_v1.json')['current_cmake_sha256']
report['protected_anchors_verified']=verify(anchors)
older=read(root/'results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/BEFORE.json')
report['original_historical_files_verified']=verify(older['prior_results_sha256'])
production={p:h for p,h in older['current_source_sha256'].items() if p.startswith(('src/','include/','third_party/')) or p=='CMakeLists.txt'}
report['production_headers_dependencies_verified']=verify(production)
report['production_adapter_sha256']=sha(root/'src/cuda/cub_sort.cu')
report['cub_pin_sha256']=sha(root/'third_party/cub/UPSTREAM.json')
report['cub_version']=read(root/'third_party/cub/UPSTREAM.json')['cub_version']
assert report['cub_version']==300001
report['prior_evidence_seals']={}
for name in ['cpu_gpu_safety_repair_20261010T140524185993Z','cpu_gpu_repair_review_20261010T185659333607Z','ctest_hook_repair_20261010T223851377458Z','ctest_guard_review_20261010T232702450912Z']:
    directory=root/'results/raw'/name;seal=read(directory/'FINAL_INTEGRITY.json')
    actual={p.resolve() for p in directory.rglob('*') if p.is_file()}
    assert actual=={(root/p).resolve() for p in seal['evidence_sha256']}|{(directory/'FINAL_INTEGRITY.json').resolve()}
    report['prior_evidence_seals'][name]=dict(sealed_hashes=verify(seal['evidence_sha256']),actual_files=len(actual))
current={str(p.relative_to(root)):sha(p) for p in [root/'AGENTS.md',root/'README.md',root/'CMakeLists.txt']+
         [p for n in ['scripts','tests','docs','include','src','cmake','third_party'] for p in (root/n).rglob('*') if p.is_file() and '__pycache__' not in p.parts]}
changes={p:dict(before=before['project_sha256'].get(p),after=current.get(p)) for p in sorted(current.keys()|before['project_sha256'].keys()) if current.get(p)!=before['project_sha256'].get(p)}
allowed={'scripts/non_timing_tests.py','tests/test_ctest_build_guard.py','docs/NON_TIMING_TEST_SELECTION_v1.json','docs/CTEST_BUILD_GUARD_v1.md','README.md','docs/ROADMAP.md','docs/AUDIT.md'}
assert not changes if stage=='BEFORE_VERIFIED' else set(changes)<=allowed
report['project_changes']=changes
old_policy=read(base/'before/docs/NON_TIMING_TEST_SELECTION_v1.json');new_policy=read(root/'docs/NON_TIMING_TEST_SELECTION_v1.json')
assert {k:v for k,v in old_policy.items() if k!='reviewed_source_sha256'}=={k:v for k,v in new_policy.items() if k!='reviewed_source_sha256'}
snapshot=new_policy['reviewed_source_sha256']
actual_source={p:h for p,h in current.items() if p=='CMakeLists.txt' or p.startswith(('scripts/','tests/','include/','src/','cmake/','third_party/'))}
assert snapshot==actual_source
report['reviewed_source_files_verified']=len(snapshot)
report['source_pin_changes']=[p for p in sorted(snapshot) if snapshot[p]!=old_policy['reviewed_source_sha256'][p]]
assert set(report['source_pin_changes'])<={'scripts/non_timing_tests.py','tests/test_ctest_build_guard.py'}
report['approved_cpu_selection']=sorted(n for n in new_policy['cpu_build_tests'] if new_policy['tests'][n]['classification']=='cpu_correctness')
previous=read(root/'results/raw/ctest_hook_repair_20261010T223851377458Z/SELECTED_TESTS.json')['selected']
assert report['approved_cpu_selection']==previous and len(previous)==19
results={str(p.relative_to(root)) for p in (root/'results').rglob('*') if p.is_file()}
added=results-set(before['prior_results_sha256']);assert all(p.startswith(str(base.relative_to(root))+'/') for p in added)
report['new_evidence_files_at_check']=len(added)
with (base/(stage+'.json')).open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps(report,indent=2,sort_keys=True))
