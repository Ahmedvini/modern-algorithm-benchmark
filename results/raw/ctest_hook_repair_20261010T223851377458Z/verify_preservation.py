import hashlib
import json
from pathlib import Path
import sys

root = Path.cwd()
base = Path(__file__).resolve().parent
before = json.loads((base/'BEFORE.json').read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def verify(mapping):
    differences = [str(p) for p,h in mapping.items() if not (root/p).is_file() or sha(root/p) != h]
    assert not differences, differences
    return len(mapping)
report = dict(prior_result_files_verified=verify(before['results_sha256']),
              existing_build_metadata_verified=verify(before['build_metadata_sha256']))
for directory in ['cpu_gpu_safety_repair_20261010T140524185993Z',
                  'cpu_gpu_repair_review_20261010T185659333607Z']:
    path=root/'results/raw'/directory
    seal=json.loads((path/'FINAL_INTEGRITY.json').read_text())
    report[directory]=dict(sealed_files_verified=verify(seal['evidence_sha256']),
                          actual_files=len([p for p in path.rglob('*') if p.is_file()]))
historical=json.loads((root/'results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/BEFORE.json').read_text())
report['original_historical_files_verified']=verify(historical['prior_results_sha256'])
freeze=json.loads((root/'docs/studies/cpu_gpu_comparison_v1.freeze.json').read_text())
report['freeze_assets_verified']=verify(freeze['files_sha256'])
matrix=json.loads((root/'docs/studies/cpu_gpu_comparison_v1.matrix.json').read_text())
anchors=matrix['source_at_freeze_sha256'].copy()
review=json.loads((root/'docs/CPU_GPU_DRIVER_REVIEW_v1.json').read_text())
anchors['CMakeLists.txt']=review['current_cmake_sha256']
report['protected_anchors_verified']=verify(anchors)
production={p:h for p,h in before['project_sha256'].items()
            if p.startswith(('src/cuda/','include/algorithms/cuda','include/benchmark/cuda','third_party/'))
            or p in ['cmake/cuda.cmake','docs/CPU_GPU_DRIVER_REVIEW_v1.json','docs/studies/cpu_gpu_comparison_v1.freeze.json']}
report['production_dependency_and_protected_files_verified']=verify(production)
report['cub_pin']=json.loads((root/'third_party/cub/UPSTREAM.json').read_text())
with (base/(sys.argv[1]+'.json')).open('x') as f:
    json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps(report,indent=2,sort_keys=True))
