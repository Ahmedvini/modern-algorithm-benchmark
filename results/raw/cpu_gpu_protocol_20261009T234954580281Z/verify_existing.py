import hashlib,json,statistics
from pathlib import Path
paths=json.loads(Path('build/cpu_gpu_protocol_paths.json').read_text());e=Path(paths['evidence']);old=Path('results/raw/cuda_timing_20261009T231303050084Z')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(old/'FINAL_SHA256_MANIFEST.json')=='8cc3b50f5aea82932faa36662844cb61799f04a5f7fd0d3e6803a152abc5dfef'
sealed=json.loads((old/'FINAL_SHA256_MANIFEST.json').read_text());assert all(Path(k).is_file() and sha(k)==v for k,v in sealed.items())
prior=json.loads((e/'prior_artifacts_sha256.json').read_text());assert all(Path(k).is_file() and sha(k)==v for k,v in prior.items())
sources=json.loads((old/'source_after.json').read_text());assert all(sha(k)==v for k,v in sources.items())
archive=json.loads((old/'download_verification.json').read_text());assert sha(old/'colab_gpu_timing_evidence.tar.gz')==archive['archive_sha256']
summary=json.loads(Path('results/processed/cuda_timing_20261009T231303050084Z/matrix.json').read_text());assert summary['complete'] and len(summary['groups'])==48
assert sum(g['successful_trials'] for g in summary['groups'])==240 and not any(g['failed_trials'] or g['missing_trials'] for g in summary['groups'])
for name in ['release_ctest_final','sanitize_ctest']:
 record=json.loads((old/'commands'/(name+'.json')).read_text());assert record['exit_code']==0 and '0 tests failed out of 27' in record['stdout']
raw=old/'downloaded/raw'
for name in ['correctness/COMPLETE.json','gpu_framework.json','COMPLETE.json']:
 record=json.loads((raw/name).read_text())
 if name=='gpu_framework.json':assert record['exit_code']==0 and 'Ran 14 tests' in record['stdout'] and 'OK (' not in record['stdout']
 elif name=='correctness/COMPLETE.json':assert record['result']['cases']==475 and record['result']['output_checks']==1900 and record['sorting_validated']
 else:assert record['complete'] and record['configurations']==48
workspaces={}
for f in (raw/'matrix').glob('run_*/run.json'):
 m=json.loads(f.read_text());workspaces.setdefault(str(m['size']),set()).add(m['workspace_bytes'])
workspaces={k:sorted(v) for k,v in workspaces.items()}
cpu=json.loads(Path('results/processed/sorting_1m_20261009T172003802655Z/per_seed.json').read_text())
max_cpu_ns=max(g['max_ns'] for g in cpu['groups'] if g['algorithm'] in ['std_sort','merge_sort'])
report=dict(complete=True,required_evidence_present=True,prior_files_verified=len(prior),sealed_smoke_files_verified=len(sealed),source_files_verified=len(sources),
            historical_release_groups=27,historical_sanitizer_groups=27,fresh_build_or_gpu_test=False,
            historical_gpu_cases=475,historical_gpu_output_checks=1900,historical_gpu_framework_methods=14,
            historical_gpu_prepared_workspace_bytes=workspaces,workspace_for_1m=None,workspace_for_default_stream_adapter=None,
            historical_local_cpu_1m_largest_observed_sample_ns=max_cpu_ns,historical_cpu_source='results/processed/sorting_1m_20261009T172003802655Z/per_seed.json',
            warning='CPU timing is from a different host; use only a labelled planning proxy, never a CPU/GPU ratio.')
with (e/'existing_evidence_verification.json').open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps(report,indent=2))
