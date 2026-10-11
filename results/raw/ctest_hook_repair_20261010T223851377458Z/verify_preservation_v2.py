"""Hash comparisons only; no selection, discovery, subprocess or measurements."""
import hashlib
import json
from pathlib import Path
import sys
root=Path.cwd();base=Path(__file__).resolve().parent
before=json.loads((base/'BEFORE.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads((root/p).read_text())
def verify(mapping):
    differences=[p for p,h in mapping.items() if not (root/p).is_file() or sha(root/p)!=h]
    assert not differences,differences
    return len(mapping)
report=dict(prior_results_verified=verify(before['results_sha256']),
            build_metadata_verified=verify(before['build_metadata_sha256']))
for name in ['cpu_gpu_safety_repair_20261010T140524185993Z','cpu_gpu_repair_review_20261010T185659333607Z']:
    directory=root/'results/raw'/name;seal=read(directory/'FINAL_INTEGRITY.json')
    actual={p.resolve() for p in directory.rglob('*') if p.is_file()}
    sealed={(root/p).resolve() for p in seal['evidence_sha256']}
    assert actual==sealed|{(directory/'FINAL_INTEGRITY.json').resolve()}
    report[name]=dict(sealed_files_verified=verify(seal['evidence_sha256']),actual_files=len(actual))
historical=read('results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/BEFORE.json')
report['historical_files_verified']=verify(historical['prior_results_sha256'])
production={p:h for p,h in historical['current_source_sha256'].items()
            if p.startswith(('src/','include/','third_party/')) or p=='CMakeLists.txt'}
report['production_headers_dependencies_verified']=verify(production)
assert sha(root/'docs/studies/cpu_gpu_comparison_v1.freeze.json')=='518ac535473e50fb61dab3a70858bdfe42dfdb43570f649174f44bffe40e1ac6'
assert sha(root/'docs/CPU_GPU_DRIVER_REVIEW_v1.json')=='b6a63a7e65827970d6b27e872e738052cd5faf94d88ee711dbccd5f77f90ef2a'
freeze=read('docs/studies/cpu_gpu_comparison_v1.freeze.json')
report['frozen_assets_verified']=verify(freeze['files_sha256'])
report['freeze_manifest_verified_against_pinned_hash']=True
anchors=read('docs/studies/cpu_gpu_comparison_v1.matrix.json')['source_at_freeze_sha256'].copy()
anchors['CMakeLists.txt']=read('docs/CPU_GPU_DRIVER_REVIEW_v1.json')['current_cmake_sha256']
report['protected_anchors_verified']=verify(anchors)
report['production_adapter_sha256']=sha(root/'src/cuda/cub_sort.cu')
report['cub_pin_sha256']=sha(root/'third_party/cub/UPSTREAM.json')
report['cub_version']=read('third_party/cub/UPSTREAM.json')['cub_version']
current={str(p.relative_to(root)):sha(p) for p in [root/'AGENTS.md',root/'README.md',root/'CMakeLists.txt']+
         [p for n in ['scripts','tests','docs','include','src','cmake','third_party'] for p in (root/n).rglob('*')
          if p.is_file() and '__pycache__' not in p.parts]}
changes={p:dict(before=before['project_sha256'].get(p),after=current.get(p))
         for p in current.keys()|before['project_sha256'].keys() if current.get(p)!=before['project_sha256'].get(p)}
allowed={'scripts/ctest_build_guard.py','scripts/non_timing_tests.py','tests/ctest_fixture.py',
         'tests/test_ctest_build_guard.py','tests/test_cpu_gpu_safety.py','tests/test_cpu_gpu_comparison.py',
         'docs/NON_TIMING_TEST_SELECTION_v1.json','README.md','docs/ROADMAP.md','docs/AUDIT.md','docs/CTEST_BUILD_GUARD_v1.md'}
assert set(changes)<=allowed,changes
report['intended_project_changes']=changes
results={str(p.relative_to(root)) for p in (root/'results').rglob('*') if p.is_file()}
new=results-set(before['results_sha256'])
assert all(p.startswith(str(base.relative_to(root))+'/') for p in new)
report['new_evidence_files_at_check']=len(new)
report['results_at_check']=len(results)
report['historical_differences']=[]
with (base/(sys.argv[1]+'.json')).open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps({k:v for k,v in report.items() if k!='intended_project_changes'},indent=2,sort_keys=True))
