#!/usr/bin/env python3
"""Read-only evidence checks plus exclusively created derived regeneration/proof."""
import hashlib,json,subprocess,sys,tempfile
from pathlib import Path
root=Path.cwd();raw=Path(__file__).resolve().parent
sys.path.insert(0,str(root/'scripts'))
import analyze_structure_results as analysis

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def hashes(directory):return {str(p.relative_to(directory)):digest(p) for p in sorted(directory.rglob('*')) if p.is_file()}
def save(path,data):
    with path.open('x') as stream:json.dump(data,stream,indent=2);stream.write('\n')

prior=json.loads((raw/'prior_results_sha256.json').read_text())
assert all(digest(root/p)==h for p,h in prior.items()),'prior artifact changed'
before=json.loads((raw/'repository_before.json').read_text())
allowed={'CMakeLists.txt','README.md',*[f'docs/{n}.md' for n in ['ALGORITHMS','AUDIT','BENCHMARKING','EXPERIMENT_PROTOCOL','METRICS','ROADMAP']]}
assert all(digest(root/p)==h for p,h in before.items() if p not in allowed),'protected source/doc/test changed'
protocol=json.loads((raw/'protocol.json').read_text())
assert digest(root/protocol['path'])==protocol['sha256']==digest(raw/'PROTOCOL_v1.md'),'protocol changed'
for kind in ['release','sanitize']:
    result=json.loads((raw/'commands'/f'final_{kind}_ctest.json').read_text())
    assert result['exit_code']==0 and '100% tests passed, 0 tests failed out of 21' in result['stdout']
    for stage in ['configure','build']:
        result=json.loads((raw/'commands'/f'final_{kind}_{stage}.json').read_text());assert result['exit_code']==0
        assert 'warning:' not in result['stdout']+result['stderr']
# Production timing must not link counting libraries.
link=(root/'build/release/CMakeFiles/structure_benchmark.dir/link.txt').read_text()
assert 'mab_metrics' not in link and 'mab_search_metrics' not in link
assert digest(root/'build/release/sort_benchmark')=='98ae6eea14525a27241936abf4b493650a428bf6f0afcc1a94042dcfad087c7f'
manifest=json.loads((root/'build/release/generated/Release/source_hashes.json').read_text())
assert all(digest(root/f['path'])==f['sha256'] for f in manifest['files'])
smoke=raw/'smoke_matrix';checkpoint=json.loads((raw/'smoke_before_analysis.json').read_text())
assert hashes(smoke)==checkpoint,'raw changed since smoke'
summary=root/'results/processed/structures_smoke_20261009T181402878134Z.json'
result=analysis.analyze(smoke)
assert result['complete'] and len(result['groups'])==275 and not result['missing_runs']
assert sum(g['successful_trials'] for g in result['groups'])==1375
assert sum(g['warmup_rows'] for g in result['groups'])==275
assert sum(g['failed_trials']+g['failed_warmups']+g['missing_measured_trials']+g['missing_warmups'] for g in result['groups'])==0
assert sum(g['successful_trials'] for g in result['groups'] if g['operation']=='build')==200
assert sum(g['successful_trials'] for g in result['groups'] if g['operation']=='lookup')==1175
matrix=json.loads((smoke/'matrix.json').read_text());assert len(matrix['runs'])==8
configs=set();query_count=0;eligible=0
for name in matrix['runs']:
    directory=smoke/name;meta=json.loads((directory/'run.json').read_text())
    configs.add((meta['size'],meta['distribution']))
    assert meta['algorithms']==list(analysis.ALGORITHMS) and meta['seed']==1729 and meta['query_seed']==2718 and meta['structure_seed']==1729
    assert (meta['warmups'],meta['repetitions'],meta['batch_size'])==(1,5,64)
    assert meta['run_kind']=='performance' and meta['build_type']=='Release' and meta['sanitizers'] is False
    query_count+=meta['query_rows'];eligible+=sum(e['available'] for e in meta['categories'])
    # Same logical input and byte-identical query identity as retained Phase 3 smoke.
    previous=root/'results/raw/search_validation_20261009T173830593675Z/smoke_matrix'/name
    old=json.loads((previous/'run.json').read_text())
    assert (meta['size'],meta['distribution'],meta['input_hash_fnv1a64'])==(old['size'],old['distribution'],old['input_hash_fnv1a64'])
    assert (directory/'queries.csv').read_bytes()==(previous/'queries.csv').read_bytes()
    assert json.loads((directory/'source_hashes.json').read_text())==manifest
assert configs=={(n,d) for n in [0,1,64,1000] for d in ['uniform','duplicate_heavy']}
assert eligible==47 and query_count==3008
with tempfile.TemporaryDirectory() as tmp:
    regenerated=Path(tmp)/'summary.json'
    command=[sys.executable,str(root/'scripts/analyze_structure_results.py'),str(smoke),'--output',str(regenerated)]
    run=subprocess.run(command,capture_output=True,text=True);assert run.returncode==0,run.stderr
    assert regenerated.read_bytes()==summary.read_bytes(),'summary differs'
assert hashes(smoke)==checkpoint and digest(root/protocol['path'])==protocol['sha256']
assert all(digest(root/p)==h for p,h in prior.items())
report={'complete':True,'prior_artifacts_unchanged':len(prior),'protected_existing_project_files_unchanged':len(before)-len(allowed),
        'protocol_sha256':protocol['sha256'],'protocol_unchanged':True,'frozen_sorting_study_unchanged':True,
        'source_manifest_matches':True,'sort_executable_unchanged':True,'uncounted_timing_link':True,
        'configurations':8,'build_measured_successes':200,'lookup_measured_successes':1175,'warmup_successes':275,
        'total_rows':1650,'failed_trials':0,'missing_trials':0,'summary_groups':275,'query_rows':query_count,
        'eligible_category_config_pairs':eligible,'unavailable_category_config_pairs':72-eligible,
        'timed_query_answers_including_warmups':47*5*6*64,'summary_regenerated_byte_identical':True,
        'raw_files_unchanged':len(checkpoint),'regeneration_command':command,'regeneration_exit_code':run.returncode}
save(raw/'verification.json',report);print(json.dumps(report,indent=2))
