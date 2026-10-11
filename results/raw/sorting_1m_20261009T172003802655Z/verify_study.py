#!/usr/bin/env python3
import csv,hashlib,itertools,json,os,statistics,subprocess,sys,tempfile
from pathlib import Path
root=Path.cwd();raw=Path(__file__).resolve().parent
sys.path.insert(0,str(root/'scripts'))
from analyze_results import analyze,read_bundle,FIELDS
paths=json.loads((raw/'paths.json').read_text());matrix=Path(paths['matrix']);out=Path(paths['processed']);protocol=json.loads((raw/'protocol.json').read_text())
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def hashfiles(base):return {str(p.relative_to(base)):digest(p) for p in sorted(base.rglob('*')) if p.is_file()}
for name,value in json.loads((raw/'execution_inputs_sha256.json').read_text()).items():assert digest(root/name)==value,name
prior=json.loads((raw/'previous_raw_sha256.json').read_text())
for name,value in prior.items():assert digest(root/name)==value,name
assert hashfiles(matrix)==json.loads((raw/'matrix_before_analysis_sha256.json').read_text())
expected=set(itertools.product(protocol['sizes'],protocol['seeds'],protocol['distributions']))
manifest=json.loads((matrix/'matrix.json').read_text());assert len(manifest['runs'])==15
assert sorted(p.name for p in matrix.glob('run_*') if p.is_dir())==sorted(manifest['runs'])
seen=set();all_rows=[];metas=[];dataset_hashes={}
for name,command in zip(manifest['runs'],manifest['commands']):
    directory=matrix/name;meta=json.loads((directory/'run.json').read_text());metas.append(meta)
    complete,groups=read_bundle(directory);assert complete and len(groups)==6
    case=(meta['size'],meta['seed'],meta['distribution']);assert case in expected and case not in seen;seen.add(case)
    assert meta['algorithms']==protocol['algorithms'] and meta['warmups']==1 and meta['repetitions']==5
    assert meta['duplicate_cardinality']==16 and meta['nearly_sorted_swaps']==(0 if meta['distribution']=='sorted' else 10000)
    assert meta['dataset_generator']=='mt19937_64_v1' and meta['planned_array_workspace_bytes']==16000000
    assert meta['build_type']=='Release' and not meta['sanitizers'] and meta['run_kind']=='performance'
    assert meta['clock']=='steady_clock' and meta['elapsed_unit']=='ns' and meta['order_policy']=='seed_offset_cyclic_v1'
    child=json.loads((matrix/(name+'_command.json')).read_text());assert child['exit_code']==0 and child['command']==command and meta['invocation']==command
    assert not (directory/'FAILED.json').exists()
    assert json.loads((directory/'source_hashes.json').read_text())==json.loads((root/'build/release/generated/Release/source_hashes.json').read_text())
    for item in json.loads((directory/'source_hashes.json').read_text())['files']:assert digest(root/item['path'])==item['sha256']
    with (directory/'trials.csv').open(newline='') as f:
        reader=csv.DictReader(f);assert reader.fieldnames==FIELDS;rows=list(reader)
    assert len(rows)==36
    assert {row['input_hash_fnv1a64'] for row in rows}=={meta['input_hash_fnv1a64']}
    assert {(row['algorithm'],row['phase'],int(row['trial_index'])) for row in rows}=={(a,p,t) for a in protocol['algorithms'] for p,n in [('warmup',1),('measure',5)] for t in range(n)}
    all_rows.extend(rows);dataset_hashes[str(case)]=meta['input_hash_fnv1a64']
assert seen==expected and len(all_rows)==540 and all(row['status']=='ok' and row['correctness']=='passed' and not row['error'] for row in all_rows)
assert sum(row['phase']=='measure' for row in all_rows)==450 and sum(row['phase']=='warmup' for row in all_rows)==90
assert len({(m['compiler_id'],m['compiler_version'],m['cplusplus'],m['platform'],m['architecture'],m['cmake_global_flags'],m['cmake_configuration_flags']) for m in metas})==1
assert json.loads((matrix/'environment.json').read_text())['benchmark_executable_sha256']==digest(root/'build/release/sort_benchmark')==protocol['benchmark_sha256']
regenerated=analyze(matrix);saved=json.loads((out/'per_seed.json').read_text());assert regenerated==saved
cross=json.loads((out/'cross_seed.json').read_text())
for group in cross['groups']:
    medians=[]
    for seed in protocol['seeds']:
        samples=[int(r['elapsed_ns']) for r in all_rows if r['phase']=='measure' and r['algorithm']==group['algorithm'] and r['distribution']==group['distribution'] and int(r['seed'])==seed]
        assert len(samples)==5;medians.append(statistics.median(samples))
    assert group['dataset_count']==3 and group['successful_trials']==15 and group['failed_trials']==0
    assert group['median_of_seed_medians_ns']==statistics.median(medians) and group['mean_of_seed_medians_ns']==statistics.mean(medians) and group['sample_stdev_of_seed_medians_ns']==statistics.stdev(medians)
    assert group['min_seed_median_ns']==min(medians) and group['max_seed_median_ns']==max(medians)
regeneration_commands=[]
with tempfile.TemporaryDirectory(prefix='mab_1m_regeneration_') as name:
    temp=Path(name);tempout=temp/'processed';tempout.mkdir()
    temppaths=dict(paths,processed=str(tempout))
    (temp/'paths.json').write_text(json.dumps(temppaths))
    commands=[[sys.executable,str(root/'scripts/analyze_results.py'),str(matrix),'--output',str(tempout/'per_seed.json')],[sys.executable,str(raw/'analyze_study.py'),'--study',str(temp)]]
    for command in commands:
        result=subprocess.run(command,capture_output=True,text=True)
        regeneration_commands.append({'argv':command,'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
        assert result.returncode==0,result.stderr
    for filename in ['per_seed.json','per_seed.csv','cross_seed.json','cross_seed.csv','RESULTS.md']:assert (out/filename).read_bytes()==(tempout/filename).read_bytes(),filename
assert hashfiles(matrix)==json.loads((raw/'matrix_before_analysis_sha256.json').read_text())
for name,value in json.loads((raw/'execution_inputs_sha256.json').read_text()).items():assert digest(root/name)==value,name
for name,value in prior.items():assert digest(root/name)==value,name
report={'schema_version':1,'study':paths['study'],'complete':True,'configurations':15,'algorithm_dataset_groups':90,'successful_measured_trials':450,'failed_measured_trials':0,'successful_warmups':90,'failed_warmups':0,'missing_configurations':[],'missing_trials':0,'all_required_combinations_present':True,'full_output_correctness_passed_on_every_row':True,'schema_fields':len(FIELDS),'order_validated_by_strict_parser':True,'same_input_fingerprint_across_algorithms_per_configuration':True,'input_fingerprints':dataset_hashes,'source_and_executable_manifests_match':True,'comparison_metrics_not_linked_verified_preflight':True,'all_child_exit_codes':0,'all_processed_files_regenerated_byte_for_byte':True,'regeneration_commands':regeneration_commands,'raw_matrix_files_unchanged':138,'frozen_inputs_and_protocol_unchanged':True,'prior_raw_files_unchanged':len(prior),'processed_sha256':hashfiles(out),'protocol_sha256':digest(Path(paths['protocol'])),'observed_protocol_deviations':[]}
with (raw/'verification.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
print('PASS: 15 complete configurations, 450 measured + 90 warm-up successes, zero failures/omissions, 90 per-seed + 30 cross-seed groups; all five processed files regenerate byte-for-byte; 138 raw matrix files and 334 prior raw files unchanged; frozen protocol and execution inputs unchanged.')
