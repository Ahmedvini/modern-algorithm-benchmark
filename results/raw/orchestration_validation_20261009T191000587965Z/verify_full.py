"""Independent full matrix coverage, statistics, regeneration and immutable evidence."""
from pathlib import Path
import sys,json,subprocess,tempfile
root=Path.cwd();sys.path.insert(0,str(root/'scripts'))
from experiment_model import load_json,save_json,tree_hashes,sha256,validate_study,aggregate,preset
p=load_json(root/'build/phase5_paths.json');e=root/p['evidence'];stamp=p['stamp']
prior=load_json(e/'prior_results_sha256.json');pilots=load_json(e/'smoke_and_calibration_before_full.json')
assert all(sha256(root/f)==h for f,h in prior.items());assert all(sha256(root/f)==h for f,h in pilots.items())
raw=root/'results/raw'/('phase5_full_'+stamp);processed=root/'results/processed'/('phase5_full_'+stamp);figures=root/'results/figures'/('phase5_full_'+stamp)
checkpoint=tree_hashes(raw);save_json(e/'full_before_regeneration.json',checkpoint)
v=validate_study(raw);s=aggregate(v)
assert v['plan']['configuration']==preset('full') and s['complete'] and not s['missing_configurations']
assert sum(len(f['children']) for f in v['plan']['families'])==180
assert len(v['observations'])==26424 and len(s['per_dataset'])==4404 and len(s['cross_dataset'])==1468
for family,measured,warmup in [('sorting',1800,360),('search',7020,1404),('structures',13200,2640)]:
 c=s['counts'][family];assert c['successful_measured']==measured and c['warmup_rows']==warmup
 assert c['failed_measured']==c['missing_measured_known']==c['failed_warmups']==c['missing_warmups_known']==c['missing_configurations']==0
assert sum(o['family']=='structures' and o['operation']=='build' and o['phase']=='measure' for o in v['observations'])==1500
assert all(o['run_kind']=='performance' and o['build_type']=='Release' and o['sanitizers'] is False for o in v['observations'])
assert all(o['status']=='ok' and o['correctness']=='passed' for o in v['observations'])
assert sum(not a['available'] for a in s['availability'])==144
manifest=load_json(figures/'plot_manifest.json');assert len(manifest['figures'])==177
with tempfile.TemporaryDirectory() as tmp:
 q=Path(tmp)/'processed';f=Path(tmp)/'figures'
 cmd=[sys.executable,'scripts/analyze_experiment.py',str(raw),'--output',str(q),'--figures',str(f)]
 result=subprocess.run(cmd,capture_output=True,text=True);assert result.returncode==0,result.stderr
 assert tree_hashes(q)==tree_hashes(processed),'processed bytes differ'
 assert tree_hashes(f)==tree_hashes(figures),'figure bytes/manifest differ'
assert tree_hashes(raw)==checkpoint
assert all(sha256(root/f)==h for f,h in prior.items());assert all(sha256(root/f)==h for f,h in pilots.items())
protocol=load_json(e/'protocol.json');assert sha256(root/protocol['path'])==protocol['sha256']==sha256(raw/'PROTOCOL_v1.md')
record=dict(complete=True,configurations=180,measured_successes=22020,warmup_successes=4404,total_rows=26424,
 counts=s['counts'],measured_builds=1500,measured_structure_lookups=11700,failed_trials=0,missing_trials=0,
 per_dataset_groups=4404,cross_dataset_groups=1468,figure_pairs=177,plot_files=len(tree_hashes(figures)),
 unavailable_category_configuration_pairs=144,prior_artifacts_unchanged=len(prior),pilot_artifacts_unchanged=len(pilots),raw_files_unchanged=len(checkpoint),
 raw_protocol_unchanged=True,all_processed_and_plot_bytes_regenerated=True,regeneration_exit_code=result.returncode,regeneration_command=cmd,
 measured_input_sizes=v['plan']['configuration']['sizes'],family_wall_seconds={f:load_json(raw/(f+'_command.json'))['wall_seconds'] for f in ['sorting','search','structures']},
 analysis_wall_seconds=load_json(raw/'analysis_command.json')['wall_seconds'])
save_json(e/'full_verification.json',record);print(json.dumps(record,indent=2))
