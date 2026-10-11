import csv,difflib,hashlib,json,subprocess,sys,tempfile
from pathlib import Path
root=Path.cwd();raw=Path(__file__).resolve().parent
sys.path.insert(0,str(root/'scripts'));import analyze_search_results as analysis
paths=json.loads((raw/'paths.json').read_text());summary_path=Path(paths['processed']);matrix=raw/'smoke_matrix'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
summary=json.loads(summary_path.read_text());assert analysis.analyze(matrix)==summary and summary['complete']
assert len(summary['groups'])==141 and len(summary['availability'])==72
assert sum(g['successful_trials'] for g in summary['groups'])==705 and sum(g['warmup_rows'] for g in summary['groups'])==141
assert all(g['failed_trials']==0 and g['missing_measured_trials']==0 and g['failed_warmups']==0 for g in summary['groups'])
expected={(n,d,1729,2718) for n in [0,1,64,1000] for d in ['uniform','duplicate_heavy']}
assert {(e['size'],e['distribution'],e['seed'],e['query_seed']) for e in summary['availability']}==expected
assert {e['category'] for e in summary['availability'] if e['available']}==set(analysis.CATEGORIES)
assert sum(e['available'] for e in summary['availability'])==47
for name,value in json.loads((raw/'smoke_before_analysis_sha256.json').read_text()).items():assert digest(raw/name)==value,name
prior=json.loads((raw/'prior_results_sha256.json').read_text())
for name,value in prior.items():assert digest(root/name)==value,name
protocol=json.loads((raw/'protocol_before_implementation.json').read_text());assert digest(root/'docs/SEARCH_PROTOCOL_v1.md')==protocol['sha256']==digest(raw/'SEARCH_PROTOCOL_v1.md')
for label in ['reviewed_release_ctest','reviewed_sanitize_ctest']:
    record=json.loads((raw/'commands'/(label+'.json')).read_text());assert record['exit_code']==0 and '100% tests passed, 0 tests failed out of 18' in record['stdout']
for build,config in [('release','Release'),('sanitize','Debug')]:
    for item in json.loads((root/'build'/build/'generated'/config/'source_hashes.json').read_text())['files']:assert digest(root/item['path'])==item['sha256']
    import shutil
    shutil.copyfile(root/'build'/build/'Testing/Temporary/LastTest.log',raw/('final_'+build+'_ctest.log'))
counts=list(csv.DictReader((raw/'counts_smoke/counts.csv').open(newline='')))
assert len(counts)==384 and all(r['correctness']=='passed' and r['actual_position']==r['expected_position'] for r in counts)
link=(root/'build/release/CMakeFiles/search_benchmark.dir/link.txt').read_text();assert 'metrics' not in link
nm=subprocess.run(['nm','-C',str(root/'build/release/search_benchmark')],capture_output=True,text=True);assert nm.returncode==0 and 'counted_search' not in nm.stdout and 'CountPredicate' not in nm.stdout
assert json.loads((matrix/'environment.json').read_text())['benchmark_executable_sha256']==digest(root/'build/release/search_benchmark')
for name in json.loads((matrix/'matrix.json').read_text())['runs']:
    for item in json.loads((matrix/name/'source_hashes.json').read_text())['files']:assert digest(root/item['path'])==item['sha256']
with tempfile.TemporaryDirectory(prefix='mab_search_regen_') as temp:
    output=Path(temp)/'summary.json';command=[sys.executable,str(root/'scripts/analyze_search_results.py'),str(matrix),'--output',str(output)]
    result=subprocess.run(command,capture_output=True,text=True);assert result.returncode==0 and output.read_bytes()==summary_path.read_bytes()
    regen={'argv':command,'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr}
for name,value in json.loads((raw/'smoke_before_analysis_sha256.json').read_text()).items():assert digest(raw/name)==value
before=json.loads((raw/'repository_before.json').read_text())
changed=[name for name,value in before.items() if digest(root/name)!=value]
allowed={'CMakeLists.txt','README.md','docs/ALGORITHMS.md','docs/AUDIT.md','docs/BENCHMARKING.md','docs/EXPERIMENT_PROTOCOL.md','docs/METRICS.md','docs/ROADMAP.md'}
assert set(changed)<=allowed
report={'schema_version':1,'release_and_sanitizer_groups_passed':18,'successful_measured_batches':705,'successful_warmup_batches':141,'failed_batches':0,'configurations':8,'available_category_configurations':47,'unavailable_category_configurations':25,'summary_groups':141,'query_records':sum(e['batch_size'] for e in summary['availability']),'hit_query_records':sum(e['hit_queries'] for e in summary['availability']),'miss_query_records':sum(e['miss_queries'] for e in summary['availability']),'count_records':384,'summary_regenerated_byte_for_byte':True,'regeneration':regen,'raw_smoke_unchanged':True,'prior_result_files_preserved':len(prior),'frozen_search_protocol_preserved':True,'existing_sorting_algorithms_tests_tools_vendors_unchanged':True,'no_comparison_instrumentation_linked_in_timing':True,'normal_link_command':link,'nm_probe':{'exit_code':nm.returncode,'stdout':nm.stdout,'stderr':nm.stderr},'summary_sha256':digest(summary_path)}
with (raw/'verification.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
print({k:v for k,v in report.items() if k not in ['nm_probe','regeneration','normal_link_command']})
