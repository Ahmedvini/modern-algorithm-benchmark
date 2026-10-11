"""Verify all frozen evidence, regenerate derived data, and retain fresh proofs."""
from pathlib import Path
import hashlib,json,subprocess,tempfile,sys
root=Path.cwd();paths=json.loads((root/'build/phase5_paths.json').read_text());e=root/paths['evidence']
sys.path.insert(0,str(root/'scripts'))
from experiment_model import load_json,sha256,tree_hashes,validate_study,aggregate,save_json
prior=load_json(e/'prior_results_sha256.json');before=load_json(e/'repository_before.json')
allowed={'CMakeLists.txt','README.md',*[f'docs/{n}.md' for n in ['ALGORITHMS','AUDIT','BENCHMARKING','EXPERIMENT_PROTOCOL','METRICS','ROADMAP']]}
assert all(sha256(root/p)==h for p,h in prior.items())
assert all(sha256(root/p)==h for p,h in before.items() if p not in allowed)
protocol=load_json(e/'protocol.json');assert sha256(root/protocol['path'])==protocol['sha256']==sha256(e/'PROTOCOL_v1.md')
for kind in ['release','sanitize']:
 for stage in ['configure','build','ctest']:
  c=load_json(e/'commands'/f'final_{kind}_{stage}.json');assert c['exit_code']==0
  if stage=='ctest':assert '100% tests passed, 0 tests failed out of 22' in c['stdout']
  else:assert 'warning:' not in c['stdout']+c['stderr']
for family in ['sort','search','structure']:
 assert 'mab_metrics' not in (root/f'build/release/CMakeFiles/{family}_benchmark.dir/link.txt').read_text()
assert sha256(root/'build/release/sort_benchmark')=='98ae6eea14525a27241936abf4b493650a428bf6f0afcc1a94042dcfad087c7f'
source=root/paths['study'];processed=root/paths['processed'];figures=root/paths['figures']
checkpoint=load_json(e/'smoke_before_analysis.json');assert tree_hashes(source)==checkpoint
v=validate_study(source);s=aggregate(v);assert s['complete'] and not s['missing_configurations']
assert sum(len(f['children']) for f in v['plan']['families'])==36
assert all(c['failed_measured']==c['missing_measured_known']==c['failed_warmups']==c['missing_warmups_known']==c['missing_configurations']==0 for c in s['counts'].values())
assert sum(c['successful_measured']+c['warmup_rows'] for c in s['counts'].values())==len(v['observations'])
manifest=load_json(figures/'plot_manifest.json')
assert manifest['output_sha256']=={p:h for p,h in tree_hashes(figures).items() if p!='plot_manifest.json'}
for f in manifest['figures']:
 assert all((figures/path).is_file() for path in f['outputs'].values())
with tempfile.TemporaryDirectory() as temp:
 p=Path(temp)/'processed';f=Path(temp)/'figures'
 command=[sys.executable,'scripts/analyze_experiment.py',str(source),'--output',str(p),'--figures',str(f)]
 r=subprocess.run(command,capture_output=True,text=True);assert r.returncode==0,r.stderr
 assert tree_hashes(p)==tree_hashes(processed),'derived summary/report/observations differs'
 assert tree_hashes(f)==tree_hashes(figures),'plot bytes/manifest differ'
assert tree_hashes(source)==checkpoint
assert all(sha256(root/p)==h for p,h in prior.items())
save_json(e/'verification.json',dict(complete=True,prior_artifacts_unchanged=len(prior),protected_existing_files_unchanged=len(before)-len(allowed),
 protocol_unchanged=True,protocol_sha256=protocol['sha256'],sort_executable_unchanged=True,
 configurations=36,observations=len(v['observations']),counts=s['counts'],summary_groups=len(s['per_dataset']),cross_dataset_groups=len(s['cross_dataset']),
 figure_pairs=len(manifest['figures']),plot_files=len(tree_hashes(figures)),raw_files_unchanged=len(checkpoint),
 regeneration_exit_code=r.returncode,regeneration_command=command,all_derived_regenerated_byte_identical=True,
 unavailable_policies=sum(not a['available'] for a in s['availability'])))
print(json.dumps(load_json(e/'verification.json'),indent=2))
