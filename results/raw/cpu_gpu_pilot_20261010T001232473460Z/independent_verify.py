from pathlib import Path
import csv,hashlib,json,math,sys
sys.path.insert(0,'scripts')
from cpu_gpu_protocol import load_protocol,verify_source_extension
E=Path('results/raw/cpu_gpu_pilot_20261010T001232473460Z');root=E/'remote_v3/modern-algorithm-benchmark';raw=root/'results/raw/pilot_v3'
p=Path('results/processed/cpu_gpu_pilot_20261010T001232473460Z');a=p/'summary.json';b=p/'summary_regenerated.json';cloud=root/'results/processed/pilot_v3'
assert a.read_bytes()==b.read_bytes()==(cloud/'summary.json').read_bytes()==(cloud/'summary_regenerated.json').read_bytes()
summary=json.loads(a.read_text());assert summary['complete'] and summary['measured']==dict(successful=150,failed=0,interrupted=0,missing=0)
assert summary['warmups']==dict(successful=30,failed=0,interrupted=0,missing=0)
manifest=json.loads((raw/'RAW_SHA256.json').read_text());assert all(hashlib.sha256((raw/k).read_bytes()).hexdigest()==v for k,v in manifest.items())
model=load_protocol();local=verify_source_extension(model);remote=json.loads((raw/'source_review.json').read_text());assert local==remote
metrics_checked=0;primary_rows=prepared_rows=0
for cell in model['pilot']['cells']:
 d=raw/('data_'+cell['dataset_id'])/'measurements'
 with (d/'primary.csv').open(newline='') as f:primary=list(csv.DictReader(f))
 with (d/'prepared/trials.csv').open(newline='') as f:prepared=list(csv.DictReader(f))
 primary_rows+=len(primary);prepared_rows+=len(prepared)
 for group in [g for g in summary['groups'] if g['dataset_id']==cell['dataset_id']]:
  rows=[r for r in (prepared if group['backend_id']=='gpu_cub_prepared' else primary) if r['phase']=='measure' and (group['backend_id']=='gpu_cub_prepared' or r['backend_id']==group['backend_id'])]
  assert len(rows)==5 and all(r['status']=='ok' and r['correctness']=='passed' for r in rows)
  for metric,s in group['metrics'].items():
   values=[float(r['elapsed_ns' if metric=='host_call_e2e_ns' else metric]) for r in rows]
   assert all(math.isfinite(v) and v>=0 for v in values)
   mean=sum(values)/5
   expected=dict(median_ns=sorted(values)[2],mean_ns=mean,stdev_ns=math.sqrt(sum((v-mean)**2 for v in values)/4),min_ns=min(values),max_ns=max(values))
   assert s['successful_trials']==5 and all(math.isclose(s[k],v,rel_tol=1e-12,abs_tol=1e-9) for k,v in expected.items())
   metrics_checked+=1
assert primary_rows==144 and prepared_rows==36 and metrics_checked==48
for ratio in summary['paired_host_call_ratios']:
 assert ratio['denominator']=='gpu_cub_adapter' and ratio['scope']=='host_vector_api_call_v1'
 groups={g['backend_id']:g for g in summary['groups'] if g['dataset_id']==ratio['dataset_id']}
 n=groups[ratio['baseline']]['metrics']['host_call_e2e_ns']['median_ns'];d=groups['gpu_cub_adapter']['metrics']['host_call_e2e_ns']['median_ns']
 if ratio['ratio'] is not None:assert math.isclose(ratio['ratio'],n/d,rel_tol=1e-12)
result=dict(complete=True,primary_rows=primary_rows,prepared_rows=prepared_rows,independently_recomputed_metric_groups=metrics_checked,paired_ratios_checked=len(summary['paired_host_call_ratios']),raw_manifest_files=len(manifest),all_raw_hashes_matched=True,local_source_matches_gpu_tested_source=True,cloud_local_regeneration_identical=True,summary_sha256=hashlib.sha256(a.read_bytes()).hexdigest())
with (E/'INDEPENDENT_VERIFICATION.json').open('x') as f:json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
