import hashlib,json,re
from pathlib import Path
p=json.loads(Path('build/cuda_timing_paths.json').read_text());e=Path(p['evidence']);processed=Path('results/processed')/p['runid']
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
source=json.loads((e/'source_after.json').read_text());assert all(digest(k)==v for k,v in source.items())
previous=json.loads((e/'prior_artifacts_sha256.json').read_text());assert all(Path(k).is_file() and digest(k)==v for k,v in previous.items())
remote=json.loads((e/'downloaded/SHA256_MANIFEST.json').read_text())
for name,sha in remote.items():
 path=processed/name[len('processed/'):] if name.startswith('processed/') else e/'downloaded'/name
 assert digest(path)==sha,name
raw=e/'downloaded/raw'
for name in ['smallest','matrix']:
 assert (processed/(name+'.json')).read_bytes()==(processed/(name+'_regenerated.json')).read_bytes()
 assert (processed/(name+'_local.json')).read_bytes()==(processed/(name+'_local_regenerated.json')).read_bytes()
 assert json.loads((processed/(name+'.json')).read_text())['groups']==json.loads((processed/(name+'_local.json')).read_text())['groups']
for file in ['README.md','docs/ROADMAP.md','docs/ALGORITHMS.md','docs/BENCHMARKING.md','docs/EXPERIMENT_PROTOCOL.md']:
 text=Path(file).read_text().split('## Prepared CUB timing milestone validated')[-1]
 for target in re.findall(r'\]\(([^)]+)\)',text):
  if not target.startswith('https:'):assert (Path(file).parent/target).exists(),(file,target)
for name in ['CHANGES.md','COMMANDS_FINAL.md','FINAL_AUDIT.md','verification.json','changes.json']:
 assert (e/name).is_file()
report=dict(complete=True,previous_artifacts_verified=len(previous),previous_artifacts_changed=0,final_source_files_verified=len(source),
            downloaded_files_reverified=len(remote),summaries_unchanged=True,final_document_links_verified=True,
            source_archive_sha256=digest(e/'cuda_timing_source_v1.tar.gz'),download_archive_sha256=digest(e/'colab_gpu_timing_evidence.tar.gz'))
with (e/'FINAL_INTEGRITY.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
files=[q for base in [e,processed] for q in sorted(base.rglob('*')) if q.is_file()]
manifest={str(q):digest(q) for q in files}
with (e/'FINAL_SHA256_MANIFEST.json').open('x') as f:json.dump(manifest,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps(report,indent=2));print('Sealed files:',len(manifest));print('Final manifest SHA256:',digest(e/'FINAL_SHA256_MANIFEST.json'))
