from pathlib import Path
import json,sys,difflib,shutil,re
root=Path.cwd();sys.path.insert(0,str(root/'scripts'))
from experiment_model import load_json,save_json,sha256,tree_hashes
from analyze_parallel_results import analyze
p=load_json(root/'build/phase6_paths.json');e=root/p['evidence'];backup=root/p['backup'];before=load_json(e/'repository_before.json')
original_paths=set(before);paths=set(original_paths)
for folder in ['include','src','scripts','tests','docs','cmake','third_party']:
 for f in (root/folder).rglob('*'):
  if f.is_file() and '__pycache__' not in f.parts and f.suffix in ['.hpp','.cpp','.py','.md','.cmake','.h','.json','.txt']:
   paths.add(f.relative_to(root).as_posix())
after={f:sha256(root/f) for f in sorted(paths)}
modified=sorted(f for f,h in before.items() if after[f]!=h);added=sorted(set(after)-original_paths)
expected={'CMakeLists.txt','include/benchmark/timing.hpp','src/benchmark/timing.cpp','README.md','docs/ALGORITHMS.md','docs/BENCHMARKING.md','docs/EXPERIMENT_PROTOCOL.md','docs/METRICS.md','docs/ROADMAP.md','docs/AUDIT.md'}
assert set(modified)==expected,(modified,expected)
assert len(before)==106 and len(added)==14 and len(after)==120,(len(before),len(added),len(after))
for f,h in before.items():assert sha256(backup/f)==h
protected=original_paths-expected;assert len(protected)==96 and all(after[f]==before[f] for f in protected)
for manifest in ['prior_artifacts_sha256.json','failed_full_attempt_sha256.json','smoke_before_full.json','smoke_retry_before_full.json']:
 assert all(sha256(root/f)==h for f,h in load_json(e/manifest).items()),manifest
for path,marker in [('docs/OPENMP_PROTOCOL_v1.md','protocol.json')]:assert sha256(root/path)==load_json(e/marker)['sha256']
for marker in ['full_protocol.json','retry_full_protocol.json']:
 m=load_json(e/marker);assert sha256(root/m['path'])==m['sha256']
for kind in ['smoke','full']:
 name=p[kind+'_retry'];raw=root/'results/raw'/name;processed=root/'results/processed'/name;figures=root/'results/figures'/name
 summary,rows=analyze(raw);proof=load_json(e/(kind+'_retry_verification.json'))
 assert summary['complete'] and proof['summary_report_figures_regenerated_byte_identical']
 assert summary['successful_measured']==proof['successful_measured'] and summary['warmup_rows']==proof['warmups']
 assert not any(summary[k] for k in ['failed_measured','missing_measured','failed_warmups','missing_warmups'])
 assert tree_hashes(raw)==load_json(e/(kind+'_retry_before_regeneration.json'))
 marker=load_json(raw/'COMPLETE.json');assert marker['processed_sha256']==tree_hashes(processed) and marker['figures_sha256']==tree_hashes(figures)
 marker=load_json(processed/'COMPLETE.json');files=tree_hashes(processed);files.pop('COMPLETE.json');assert marker['files_sha256']==files and marker['figures_sha256']==tree_hashes(figures)
for kind in ['release','sanitize']:
 for action in ['configure','build','ctest']:
  c=load_json(e/'commands'/('corrected_'+kind+'_'+action+'.json'));assert c['exit_code']==0
  if action=='build':assert not re.search(r'warning:|error:',c['stdout']+c['stderr'],re.I)
 c=load_json(e/'commands'/('corrected_'+kind+'_ctest.json'));assert '100% tests passed, 0 tests failed out of 24' in c['stdout'] and 'Ran 13 tests' in c['stdout']
 assert '523 inputs, 4184 public/registry output checks' in c['stdout']
 shutil.copyfile(root/'build'/kind/'Testing/Temporary/LastTest.log',e/('final_'+kind+'_LastTest.log'))
assert load_json(e/'commands/corrected_parallel_python.json')['exit_code']==0
assert load_json(e/'commands/full_pipeline.json')['exit_code']==1
assert load_json(e/'commands/retry_full_pipeline.json')['exit_code']==0
for stem in ['tsan_run','tsan_standalone_run']:
 c=load_json(e/'commands'/(stem+'.json'));assert c['exit_code']==66 and 'unexpected memory mapping' in c['stderr']
manifest=load_json(root/'build/release/generated/Release/source_hashes.json');assert all(sha256(root/f['path'])==f['sha256'] for f in manifest['files'])
full=root/'results/raw'/p['full_retry'];env=load_json(full/'environment.json')
assert sha256(root/'build/release/parallel_sort_benchmark')==env['executable_sha256']
assert env['tools_sha256']==load_json(e/'retry_execution_tools/sha256.json')
assert all(sha256(root/'scripts'/f)==h for f,h in env['tools_sha256'].items())
commands=load_json(full/'run_000000/compile_commands.json')
seq=next(x for x in commands if x['file'].endswith('/src/algorithms/mergesort.cpp'))['command']
par=next(x for x in commands if x['file'].endswith('/src/algorithms/parallel_mergesort.cpp'))['command']
assert '-O3' in seq and '-DNDEBUG' in seq and '-O3' in par and '-DNDEBUG' in par and '-fopenmp' in par
block=(root/'docs/AUDIT.md').read_text().split('## Phase 6 — OpenMP implementation')[1]
assert (e/'FINAL_AUDIT.md').read_text()=='## Phase 6 — OpenMP implementation'+block
changes=dict(modified=modified,added=added,protected_original_files=len(protected))
save_json(e/'file_changes.json',changes);save_json(e/'source_after.json',after)
patch=[]
for f in modified+added:
 old=(backup/f).read_text().splitlines(keepends=True) if f in before else []
 new=(root/f).read_text().splitlines(keepends=True)
 patch.extend(difflib.unified_diff(old,new,fromfile='a/'+f if f in before else '/dev/null',tofile='b/'+f))
with (e/'changes.patch').open('x') as stream:stream.write(''.join(patch))
proof=dict(complete=True,phase=6,release_groups_passed=24,sanitizer_groups_passed=24,leak_detection_enabled=True,parallel_python_methods=13,parallel_input_cases=523,public_registry_checks=4184,concurrent_large_calls=10,observed_tasks=8,observed_merges=65549,tsan_status='startup failure exit66, also independent non-OpenMP probe; no race-freedom claim',smoke_measured=320,smoke_warmups=64,full_configurations=180,full_measured=1800,full_warmups=360,failed_measured=0,missing_measured=0,full_figure_pairs=20,all_derived_byte_identical=True,prior_artifacts_unchanged=3796,failed_attempt_preserved_files=1806,original_files_unchanged=96,modified_files=len(modified),added_files=len(added),source_files=len(after),frozen_protocols_unchanged=True,source_manifest_matches_current_build=True,binary_sha256=env['executable_sha256'],source_after_sha256=sha256(e/'source_after.json'),patch_sha256=sha256(e/'changes.patch'),audit_sha256=sha256(e/'FINAL_AUDIT.md'))
save_json(e/'final_review.json',proof);print(json.dumps(proof,indent=2));print(json.dumps(changes,indent=2))
