import csv,hashlib,itertools,json,statistics,subprocess,sys
from pathlib import Path
paths=json.loads(Path('build/cuda_timing_paths.json').read_text());e=Path(paths['evidence']);raw=e/'downloaded/raw';processed=Path('results/processed')/paths['runid']
metrics=['h2d_ns','device_sort_ns','d2h_ns','end_to_end_ns']
for name in ['smallest','matrix']:
 for suffix in ['local','local_regenerated']:
  argv=[sys.executable,'scripts/analyze_cuda_results.py',str(raw/name),'--output',str(processed/(name+'_'+suffix+'.json'))]
  result=subprocess.run(argv,capture_output=True,text=True)
  assert result.returncode==0,(argv,result.stdout,result.stderr)
 assert (processed/(name+'_local.json')).read_bytes()==(processed/(name+'_local_regenerated.json')).read_bytes()
 local=json.loads((processed/(name+'_local.json')).read_text());remote=json.loads((processed/(name+'.json')).read_text())
 assert local['groups']==remote['groups'] and local['complete']==remote['complete']
 assert (processed/(name+'.json')).read_bytes()==(processed/(name+'_regenerated.json')).read_bytes()
 groups=local['groups']
 if name=='matrix':
  expected=set(itertools.product([0,1,1025,65537],['uniform','sorted','reverse_sorted','duplicate_heavy','nearly_sorted','signed_edges'],[1729,42]))
  assert {(g['size'],g['distribution'],g['seed']) for g in groups}==expected
  bundles=[raw/name/g['run_id'] for g in groups]
 else:bundles=[raw/name]
 for bundle,g in zip(bundles,groups):
  with (bundle/'trials.csv').open(newline='') as f:rows=list(csv.DictReader(f))
  assert len(rows)==6 and all(r['status']=='ok' and r['correctness']=='passed' for r in rows)
  measured=[r for r in rows if r['phase']=='measure'];assert len(measured)==5
  for key in metrics:
   values=[float(r[key]) for r in measured]
   expected_stats=dict(successful_trials=5,median_ns=statistics.median(values),mean_ns=statistics.mean(values),stdev_ns=statistics.stdev(values),min_ns=min(values),max_ns=max(values))
   assert expected_stats==g['metrics'][key],(bundle,key)
# The smallest smoke and the equivalent matrix configuration used identical input.
small=json.loads((raw/'smallest/run.json').read_text());matrix_summary=json.loads((processed/'matrix_local.json').read_text())
match=next(g for g in matrix_summary['groups'] if (g['size'],g['distribution'],g['seed'])==(1025,'uniform',1729))
assert match['input_hash_fnv1a64']==small['input_hash_fnv1a64']
protected=json.loads((e/'prior_artifacts_sha256.json').read_text())
changed=[name for name,sha in protected.items() if not Path(name).is_file() or hashlib.sha256(Path(name).read_bytes()).hexdigest()!=sha]
assert not changed,changed
remote_manifest=json.loads((e/'downloaded/SHA256_MANIFEST.json').read_text())
for name,sha in remote_manifest.items():
 path=processed/name[len('processed/'):] if name.startswith('processed/') else e/'downloaded'/name
 assert hashlib.sha256(path.read_bytes()).hexdigest()==sha,name
report=dict(complete=True,matrix_configurations=48,matrix_measured_trials=240,matrix_warmups=48,smallest_measured_trials=5,smallest_warmups=1,
            failed_trials=0,missing_trials=0,raw_metrics_checked=245*4,independent_statistics_checked=49*4,
            remote_summary_byte_regeneration=True,local_summary_byte_regeneration=True,remote_local_groups_equal=True,
            provenance_note='Absolute source path differs between local and remote summaries; groups and all statistics identical.',
            earlier_artifacts_verified=len(protected),earlier_artifacts_changed=changed,downloaded_files_reverified=len(remote_manifest))
with (e/'verification.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
print(json.dumps(report,indent=2))
for g in matrix_summary['groups']:
 if g['size']==65537 and g['distribution']=='uniform' and g['seed']==1729:
  print('EXAMPLE_METRICS_NS='+json.dumps(g['metrics']))
