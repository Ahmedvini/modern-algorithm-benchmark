from pathlib import Path
import datetime,hashlib,json,sys,tarfile,difflib
sys.path.insert(0,'scripts')
from cpu_gpu_protocol import load_protocol,verify_source_extension,source_manifest
E=Path('results/raw/cpu_gpu_pilot_20261010T001232473460Z');P=Path('results/processed/cpu_gpu_pilot_20261010T001232473460Z')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
prior=json.loads((E/'prior_artifacts_sha256.json').read_text());bad=[p for p,h in prior.items() if not Path(p).is_file() or sha(Path(p))!=h];assert not bad,bad
before=json.loads((E/'source_before.json').read_text());changed=[]
for p,h in before.items():
 assert Path(p).is_file(),p
 if sha(Path(p))!=h:changed.append(p)
allowed=['CMakeLists.txt','README.md','docs/AUDIT.md','docs/BENCHMARKING.md','docs/ROADMAP.md'];assert sorted(changed)==sorted(allowed),changed
model=load_protocol();review=verify_source_extension(model)
raw=E/'remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3';remote=json.loads((raw/'source_review.json').read_text());assert review==remote
with tarfile.open(E/'cpu_gpu_pilot_source_v1.tar.gz') as t:
 old=t.extractfile('modern-algorithm-benchmark/CMakeLists.txt').read().decode()
expected=''.join(difflib.unified_diff(old.splitlines(keepends=True),Path('CMakeLists.txt').read_text().splitlines(keepends=True),fromfile='frozen/CMakeLists.txt',tofile='CMakeLists.txt'))
assert expected==(E/'CMAKE_ADDITIONS.diff').read_text()
manifest=json.loads((raw/'RAW_SHA256.json').read_text());assert all(sha(raw/p)==h for p,h in manifest.items())
download=json.loads((E/'remote_v3/download_manifest.json').read_text());assert all(sha(E/'remote_v3'/p)==h for p,h in download.items())
cloud=E/'remote_v3/modern-algorithm-benchmark/results/processed/pilot_v3'
assert (P/'summary.json').read_bytes()==(P/'summary_regenerated.json').read_bytes()==(cloud/'summary.json').read_bytes()==(cloud/'summary_regenerated.json').read_bytes()
summary=json.loads((P/'summary.json').read_text());assert summary['measured']==dict(successful=150,failed=0,interrupted=0,missing=0) and summary['warmups']==dict(successful=30,failed=0,interrupted=0,missing=0)
assert json.loads((E/'INDEPENDENT_VERIFICATION.json').read_text())['complete']
files={str(p):sha(p) for root in [E,P] for p in sorted(root.rglob('*')) if p.is_file()}
result=dict(schema_version=1,complete=True,verified_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),command='python3 '+str(E/'final_integrity.py'),exit_code=0,
 prior_artifacts_checked=len(prior),prior_artifacts_mismatches=bad,existing_files_changed=changed,existing_files_removed=[],protected_source_review=review,
 frozen_files_sha256={p:sha(Path(p)) for p in ['docs/CPU_GPU_COMPARISON_PROTOCOL_v1.md','docs/studies/cpu_gpu_comparison_v1.matrix.json','docs/studies/cpu_gpu_comparison_v1.resources.csv','docs/studies/cpu_gpu_comparison_v1.freeze.json']},
 raw_manifest_files=len(manifest),download_manifest_files=len(download),raw_and_download_hashes_matched=True,summary_regeneration_matches=True,summary_sha256=sha(P/'summary.json'),pilot_accepted=True,full_study_run=False,
 current_source_sha256=source_manifest(),evidence_and_processed_sha256=files,manifest_excludes_itself=True)
with (E/'FINAL_INTEGRITY.json').open('x') as f:json.dump(result,f,indent=2,sort_keys=True);f.write(chr(10))
print(json.dumps({k:result[k] for k in ['complete','exit_code','prior_artifacts_checked','prior_artifacts_mismatches','existing_files_changed','raw_and_download_hashes_matched','summary_regeneration_matches','pilot_accepted','full_study_run']},indent=2))
