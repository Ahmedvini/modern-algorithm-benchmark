from pathlib import Path
import sys,json,tempfile
root=Path.cwd();sys.path.insert(0,str(root/'scripts'))
from experiment_model import load_json,save_json,sha256,tree_hashes
from analyze_parallel_results import analyze,write_analysis
from run_parallel_matrix import forecast,preset
p=load_json(root/'build/phase6_paths.json');e=root/p['evidence'];kind=sys.argv[1];name=p[kind+'_retry'];raw=root/'results/raw'/name;processed=root/'results/processed'/name;figures=root/'results/figures'/name
before=tree_hashes(raw);s,rows=analyze(raw);plan=load_json(raw/'matrix.json')
cases,measured,warm=(32,320,64) if kind=='smoke' else (180,1800,360)
assert s['complete'] and len(plan['cases'])==cases and plan['configuration']==preset(kind)
assert (s['successful_measured'],s['warmup_rows'],s['failed_measured'],s['missing_measured'],s['failed_warmups'],s['missing_warmups'])==(measured,warm,0,0,0,0)
assert len(rows)==measured+warm
for wrapped in rows:
 r=wrapped['raw'];assert r['correctness']=='passed' and r['status']=='ok' and r['build_type']=='Release' and r['sanitizers']=='false'
 if r['parallel_region']=='true':assert r['requested_threads']==r['actual_threads']
 assert int(r['size'])<=1000000
assert {r['raw']['actual_threads'] for r in rows if r['raw']['parallel_region']=='true'}=={'2','4','8'}
assert all(c['status']=='successful' and c['exit_code']==0 for c in s['commands'])
save_json(e/(kind+'_retry_before_regeneration.json'),before)
with tempfile.TemporaryDirectory() as tmp:
 d=Path(tmp)/'processed';f=Path(tmp)/'figures';write_analysis(raw,d,f)
 assert tree_hashes(d)==tree_hashes(processed) and tree_hashes(f)==tree_hashes(figures)
assert tree_hashes(raw)==before
for manifest in ['prior_artifacts_sha256.json','failed_full_attempt_sha256.json','smoke_before_full.json']:
 expected=load_json(e/manifest);assert all(sha256(root/f)==h for f,h in expected.items()),manifest
prior=load_json(e/'prior_artifacts_sha256.json')
assert sha256(root/'docs/OPENMP_PROTOCOL_v1.md')==load_json(e/'protocol.json')['sha256']
original_protocol=load_json(e/'full_protocol.json');assert sha256(root/original_protocol['path'])==original_protocol['sha256']
if kind=='full':
 launch=load_json(e/'retry_full_protocol.json');assert sha256(root/launch['path'])==launch['sha256']
 archive=load_json(e/'retry_execution_tools/sha256.json');assert load_json(raw/'environment.json')['tools_sha256']==archive
 assert all(sha256(e/'retry_execution_tools'/f)==h for f,h in archive.items())
 smoke=load_json(e/'smoke_retry_before_full.json');assert all(sha256(root/f)==h for f,h in smoke.items())
result=dict(complete=True,configurations=cases,successful_measured=measured,warmups=warm,failed_measured=0,missing_measured=0,failed_warmups=0,missing_warmups=0,summary_report_figures_regenerated_byte_identical=True,raw_unchanged_files=len(before),prior_artifacts_unchanged=len(prior),failed_attempt_unchanged_files=len(load_json(e/'failed_full_attempt_sha256.json')),figure_pairs=len(load_json(figures/'plot_manifest.json')['figures']),distinct_dataset_configurations=len(s['dataset_ratios']),cross_dataset_groups=len(s['cross_dataset']),actual_parallel_teams=[2,4,8])
save_json(e/(kind+'_retry_verification.json'),result);print(json.dumps(result,indent=2))
if kind=='smoke':save_json(e/'retry_full_forecast.json',forecast(raw,preset('full')))
else:
 for r in s['cross_dataset']:
  if r['size']==1000000 and r['threads']==8:print(json.dumps(r,sort_keys=True))
