import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,'scripts')
from cpu_gpu_protocol import load_protocol, source_manifest, verify_source_extension, sha
from cpu_gpu_provenance import trusted_source_anchors
base=Path(__file__).resolve().parent
before=json.loads((base/'BEFORE.json').read_text())
def verify(mapping):
    missing=[];changed=[]
    for name,digest in mapping.items():
        path=Path(name)
        if not path.is_file():missing.append(name)
        elif sha(path)!=digest:changed.append(name)
    assert not missing and not changed,dict(missing=missing,changed=changed)
    return dict(checked=len(mapping),missing=missing,changed=changed)
prior=verify(before['prior_results_sha256'])
frozen=verify(before['frozen_files_sha256'])
model=load_protocol();expected=trusted_source_anchors(model)
protected=verify(expected)
source=source_manifest();verify_source_extension(model)
production={p:h for p,h in before['current_source_sha256'].items() if p.startswith(('src/','include/','third_party/')) or p=='CMakeLists.txt'}
production_result=verify(production)
assert sha('docs/CPU_GPU_DRIVER_REVIEW_v1.json')==before['cmake_review_sha256']
prior_review=json.loads(Path('results/raw/cpu_gpu_tooling_review_20261010T125855526277Z/FINAL_INTEGRITY.json').read_text())
review_seal=verify(prior_review['evidence_sha256'])
all_results={str(p) for p in Path('results').rglob('*') if p.is_file()}
new=sorted(all_results-set(before['prior_results_sha256']))
assert all(p.startswith(str(base.relative_to(Path.cwd()))+'/') if base.is_absolute() else p.startswith(str(base)+'/') for p in new)
result=dict(prior_results=prior,frozen_files=frozen,protected_anchors_with_existing_cmake_exception=protected,
    production_headers_sources_and_dependency_files=production_result,prior_review_seal=review_seal,
    trusted_cmake_review_unchanged=True,before_results_count=before['before_results_count'],
    current_results_count_before_final_audit=len(all_results),new_evidence_files_before_final_audit=len(new),
    all_new_results_confined_to_new_evidence_directory=True,current_source_sha256=source,
    frozen_files_sha256={p:sha(p) for p in before['frozen_files_sha256']},production_adapter_sha256=sha('src/cuda/cub_sort.cu'),
    cub_pin_sha256=sha('third_party/cub/UPSTREAM.json'),current_results_added=new)
with (base/'INTEGRITY_CHECK.json').open('x') as stream:json.dump(result,stream,indent=2,sort_keys=True);stream.write('\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['current_source_sha256','current_results_added']},indent=2,sort_keys=True))
