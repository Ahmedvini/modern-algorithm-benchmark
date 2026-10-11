import difflib,hashlib,json
from pathlib import Path
p=json.loads(Path('build/colab_validation_paths.json').read_text());e=Path(p['evidence']);before=json.loads((e/'source_before.json').read_text());retry=json.loads((e/'retry_source_sha256.json').read_text())
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
after={}
for base in ['include','src','tests','scripts','cmake','docs','third_party']:
 for f in sorted(Path(base).rglob('*')):
  if f.is_file() and '__pycache__' not in f.parts:after[str(f)]=digest(f)
for name in ['CMakeLists.txt','AGENTS.md','README.md','.gitignore']:after[name]=digest(name)
changed=[name for name,sha in after.items() if sha!=before.get(name)]
expected={'README.md','docs/ROADMAP.md','docs/AUDIT.md','docs/ALGORITHMS.md','docs/BENCHMARKING.md','docs/EXPERIMENT_PROTOCOL.md','docs/CUDA_SORT_PROTOCOL_v2.md','docs/CUDA_SORT_VALIDATION_GUIDE_v3.md','cmake/cuda.cmake','src/cuda/cub_sort.cu','scripts/validate_cuda_sort.py','tests/test_cuda_sorting.cpp','tests/test_cuda_sort_handoff.py','third_party/cub/README.md','third_party/cub/UPSTREAM.json'}
assert set(changed)==expected,(changed,expected)
assert set(before).issubset(after)
post_gpu=[name for name,sha in after.items() if sha!=retry.get(name)]
assert set(post_gpu)=={'README.md','docs/ROADMAP.md','docs/AUDIT.md','docs/ALGORITHMS.md','docs/BENCHMARKING.md','docs/EXPERIMENT_PROTOCOL.md'}
original=(Path(p['backup'])/'tests/test_cuda_sorting.cpp').read_text()
assert Path('tests/test_cuda_sorting.cpp').read_text().replace('cuda_sort_correctness_v2','cuda_sort_correctness_v1')==original
original=(Path(p['backup'])/'src/cuda/cub_sort.cu').read_text()
assert Path('src/cuda/cub_sort.cu').read_text().replace('CUB_VERSION == 300001','CUB_VERSION == 300000')==original
artifacts=json.loads((e/'prior_artifacts_sha256.json').read_text());bad=[name for name,sha in artifacts.items() if not Path(name).is_file() or digest(name)!=sha];assert not bad
with (e/'source_after.json').open('x') as f:json.dump(after,f,indent=2,sort_keys=True);f.write('\n')
patch=''
for name in sorted(changed):
 backup=Path(p['backup'])/name;prior=backup.read_text() if backup.is_file() else ''
 patch+=''.join(difflib.unified_diff(prior.splitlines(True),Path(name).read_text().splitlines(True),fromfile='a/'+name,tofile='b/'+name))
with (e/'final_changes.patch').open('x') as f:f.write(patch)
verification=json.loads((e/'download_verification.json').read_text());assert verification['result']['cases']==475 and verification['result']['output_checks']==1900 and verification['verified_files']==611
assert not json.loads((e/'privacy_check.json').read_text())['runtime_proxy_credentials_in_evidence']
result={'source_files':len(after),'modified':sorted(n for n in changed if n in before),'added':sorted(n for n in changed if n not in before),'removed':[],'changes_after_gpu_execution':post_gpu,'post_gpu_code_changes':False,'test_fixtures_unchanged':True,'adapter_behavior_unchanged':True,'previous_artifacts_verified':len(artifacts),'previous_artifacts_changed':bad,'gpu_sort_correctness_milestone_complete':True,'gpu_timing_or_study_complete':False,'warnings_retained':100,'downloaded_evidence_files_verified':611}
with (e/'final_review.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result,indent=2))
