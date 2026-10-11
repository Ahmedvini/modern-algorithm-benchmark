from pathlib import Path
import sys,json,tempfile
root=Path.cwd();sys.path.insert(0,str(root/'scripts'))
from experiment_model import load_json,save_json,sha256,tree_hashes
from analyze_parallel_results import analyze,write_analysis
from run_parallel_matrix import forecast,preset
p=load_json(root/'build/phase6_paths.json');e=root/p['evidence'];name=p['smoke'];raw=root/'results/raw'/name;processed=root/'results/processed'/name;figures=root/'results/figures'/name
before=tree_hashes(raw);s,rows=analyze(raw)
assert s['complete'] and len(load_json(raw/'matrix.json')['cases'])==32
assert (s['successful_measured'],s['warmup_rows'],s['failed_measured'],s['missing_measured'])==(320,64,0,0)
assert len(rows)==384
assert {r['raw']['actual_threads'] for r in rows if r['raw']['parallel_region']=='true'}=={'2','4','8'}
with tempfile.TemporaryDirectory() as tmp:
 d=Path(tmp)/'processed';f=Path(tmp)/'figures';write_analysis(raw,d,f)
 assert tree_hashes(d)==tree_hashes(processed) and tree_hashes(f)==tree_hashes(figures)
assert tree_hashes(raw)==before
prior=load_json(e/'prior_artifacts_sha256.json');assert all(sha256(root/f)==h for f,h in prior.items())
assert sha256(root/'docs/OPENMP_PROTOCOL_v1.md')==load_json(e/'protocol.json')['sha256']
result=dict(complete=True,configurations=32,successful_measured=320,warmups=64,failed_measured=0,missing_measured=0,summary_report_figures_regenerated_byte_identical=True,raw_unchanged_files=len(before),prior_artifacts_unchanged=len(prior),figure_pairs=len(load_json(figures/'plot_manifest.json')['figures']))
save_json(e/'smoke_verification.json',result);save_json(e/'full_forecast.json',forecast(raw,preset('full')))
print(json.dumps(result,indent=2));print(json.dumps(load_json(e/'full_forecast.json'),indent=2))
