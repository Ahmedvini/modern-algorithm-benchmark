"""Read-only final validation; exclusively saves final inventory/review evidence."""
from pathlib import Path
import sys,json,difflib,hashlib
root=Path.cwd();sys.path.insert(0,str(root/'scripts'))
from experiment_model import load_json,save_json,sha256,tree_hashes,validate_study,aggregate,canonical
from analyze_experiment import report
p=load_json(root/'build/phase5_paths.json');e=root/p['evidence'];before=load_json(e/'repository_before.json');backup=root/p['backup'];stamp=p['stamp']
expected_modified={'CMakeLists.txt','README.md','docs/ALGORITHMS.md','docs/AUDIT.md','docs/BENCHMARKING.md','docs/EXPERIMENT_PROTOCOL.md','docs/METRICS.md','docs/ROADMAP.md'}
expected_added={'docs/ORCHESTRATION_PROTOCOL_v1.md','scripts/experiment_model.py','scripts/run_experiments.py','scripts/analyze_experiment.py','scripts/plot_results.py','scripts/assess_experiment.py','tests/test_experiments.py'}
paths={root/n for n in ['AGENTS.md','CMakeLists.txt','README.md']}
for directory in ['cmake','docs','include','scripts','src','tests','third_party']:
 paths.update(f for f in (root/directory).rglob('*') if f.is_file() and '__pycache__' not in f.parts)
current={f.relative_to(root).as_posix():sha256(f) for f in sorted(paths)}
added=set(current)-set(before);removed=set(before)-set(current);modified={f for f in before if current.get(f)!=before[f]}
assert added==expected_added and modified==expected_modified and not removed,(added,removed,modified)
assert len(before)==99 and len(current)==106
for f,h in before.items():assert sha256(backup/f)==h
prior=load_json(e/'prior_results_sha256.json');pilots=load_json(e/'smoke_and_calibration_before_full.json')
assert len(prior)==867 and len(pilots)==671
for files in [prior,pilots]:assert all(sha256(root/f)==h for f,h in files.items())
protocol=load_json(e/'protocol.json');assert sha256(root/protocol['path'])==protocol['sha256']==sha256(e/'PROTOCOL_v1.md')
archive=load_json(e/'execution_tools/sha256.json')
assert all(sha256(e/'execution_tools'/n)==h for n,h in archive.items())
validated_runs={}
for suffix in ['smoke','calibration','full']:
 name='phase5_'+suffix+'_'+stamp;raw=root/'results/raw'/name;processed=root/'results/processed'/name;figures=root/'results/figures'/name
 env=load_json(raw/'environment.json');assert env['tool_sha256']==archive
 v=validate_study(raw);s=aggregate(v);assert s['complete'];assert s==load_json(processed/'summary.json')
 summary_bytes=(json.dumps(s,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n').encode()
 assert summary_bytes==(processed/'summary.json').read_bytes()
 observations=''.join(canonical(o)+'\n' for o in v['observations']).encode();assert observations==(processed/'observations.jsonl').read_bytes()
 m=load_json(figures/'plot_manifest.json');assert report(s,v,m).encode()==(processed/'REPORT.md').read_bytes()
 complete=load_json(raw/'COMPLETE.json');assert complete['complete']
 assert tree_hashes(figures)==complete['figures_sha256'];assert tree_hashes(processed)==complete['processed_sha256']
 assert {k:h for k,h in tree_hashes(raw).items() if k!='COMPLETE.json'}==complete['raw_sha256']
 assert all(o['correctness']=='passed' and o['status']=='ok' for o in v['observations'])
 validated_runs[suffix]={'counts':s['counts'],'rows':len(v['observations']),'figure_pairs':len(m['figures']),'processed_bytes_recomputed':True,'figure_hashes_verified':True}
full_raw=root/'results/raw'/('phase5_full_'+stamp)
assert tree_hashes(full_raw)==load_json(e/'full_before_regeneration.json')
assert len(tree_hashes(full_raw))==1764
for stem in ['completion_release_configure','completion_release_build','completion_release_ctest','completion_sanitize_configure','completion_sanitize_build','completion_sanitize_ctest','completion_python_tests']:
 r=load_json(e/'commands'/(stem+'.json'));assert r['exit_code']==0
 if stem.endswith('build'):assert 'warning:' not in (r['stdout']+r['stderr']).lower()
 if stem.endswith('ctest'):assert '100% tests passed, 0 tests failed out of 22' in r['stdout'] and 'Ran 23 tests' in r['stdout']
 if stem=='completion_python_tests':assert 'Ran 23 tests' in r['stderr']+r['stdout'] and 'OK' in r['stderr']+r['stdout']
assert sha256(root/'build/release/sort_benchmark')=='98ae6eea14525a27241936abf4b493650a428bf6f0afcc1a94042dcfad087c7f'
for f in ['docs/SEARCH_PROTOCOL_v1.md','docs/STRUCTURES_PROTOCOL_v1.md','docs/studies/sorting_1m_20261009T172003802655Z_v1.md']:assert current[f]==before[f]
assert load_json(e/'verification.json')['all_processed_and_plot_bytes_regenerated']
assert load_json(e/'full_verification.json')['all_processed_and_plot_bytes_regenerated']
assert (e/'FINAL_AUDIT.md').read_text() in (root/'docs/AUDIT.md').read_text()
changes={'added':sorted(added),'modified':sorted(modified),'removed':[],'protected_original_files':91,'before_sha256':before,'after_sha256':current}
save_json(e/'file_changes.json',changes);save_json(e/'final_source_manifest.json',current)
diff=[]
for f in sorted(added|modified):
 old=(backup/f).read_text().splitlines(keepends=True) if f in modified else []
 new=(root/f).read_text().splitlines(keepends=True)
 diff.extend(difflib.unified_diff(old,new,fromfile='a/'+f if f in modified else '/dev/null',tofile='b/'+f))
with (e/'changes.patch').open('x') as stream:stream.writelines(diff)
review={'complete':True,'phase5_pipeline_complete':True,'full_study_complete':True,'prior_artifacts_unchanged':867,'pilot_artifacts_unchanged':671,'full_raw_artifacts_unchanged':1764,'protected_original_files_unchanged':91,'files_added':7,'files_modified':8,'frozen_protocols_unchanged':True,'release_groups_passed':22,'sanitize_groups_passed':22,'standalone_python_tests_passed':23,'leak_detection_disabled':False,'final_compiler_warnings':0,'execution_tools_archive_verified':True,'current_final_code_summaries_observations_reports_byte_identical':True,'independent_figure_regeneration_verified':True,'source_manifest_sha256':sha256(e/'final_source_manifest.json'),'patch_sha256':sha256(e/'changes.patch'),'runs':validated_runs,'known_limitations':['no resume','Linux orchestration resource/signal policy','shared-machine controls unmodified','plot byte identity requires same stack','no timing-study comparison or memory metrics','no direct individual-query latency','no independent-session replication'],'next_milestone':'Phase 6 OpenMP parallel sorting'}
save_json(e/'final_review.json',review)
print(json.dumps({k:v for k,v in review.items() if k!='runs'},indent=2))
