"""Offline evidence review only: reads/hashes/validates records; no command launch."""
from pathlib import Path
import hashlib,json,re,sys

r=Path.cwd();e=Path(__file__).resolve().parent
prior=r/'results/raw/bounded_resume_20261011T024034091796Z';raw=prior/'downloaded/evidence'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def save(name,data):
    with (e/name).open('x') as f:json.dump(data,f,indent=2,sort_keys=True);f.write('\n')
sys.path.insert(0,str(r/'scripts'))
from cpu_gpu_protocol import load_protocol,source_manifest,schedule,verify_source_extension
from cpu_gpu_provenance import trusted_source_anchors,validate_retained_source,TRUSTED_FREEZE_SHA256
from cpu_gpu_validation_policy import trusted_policy,verify_current_sources,classify
model=load_protocol();original=trusted_source_anchors(model);policy,approved=trusted_policy();verify_current_sources()
assert sha(r/'docs/studies/cpu_gpu_comparison_v1.freeze.json')==TRUSTED_FREEZE_SHA256
changed_frozen={p:dict(expected=h,actual=sha(r/p)) for p,h in original.items() if sha(r/p)!=h}
assert set(changed_frozen)==set(policy['authorized_framework_exceptions'])
rejections={}
try:verify_source_extension(model)
except ValueError as error:rejections['launch_guard']=str(error)
else:raise AssertionError('Expected legacy source guard mismatch was not reproduced')
claim=dict(current_source_sha256=source_manifest(),changed_anchors=['CMakeLists.txt'],
           cmake_review_sha256=sha(r/'docs/CPU_GPU_DRIVER_REVIEW_v1.json'))
try:validate_retained_source(claim,model)
except ValueError as error:rejections['analyzer_guard']=str(error)
else:raise AssertionError('Expected analyzer protected-anchor mismatch was not reproduced')
bundle=read(raw/'CORRECTNESS_BUNDLE.json');context=read(raw/'VALIDATION_CONTEXT.json')
assessment=classify(bundle,context)
assert assessment==read(raw/'CLASSIFICATION.json') and not assessment['study_eligible']
record_paths=dict(cpu_release=raw/'validation_commands/cpu_release_ctest.json',
                  cpu_sanitize=raw/'validation_commands/cpu_sanitize_ctest.json',
                  gpu_prepared=raw/'validation_commands/gpu_prepared_untimed.json',
                  workspace=raw/'WORKSPACE_RESOURCES.json',workers=raw/'validation_commands/actual_workers_untimed.json')
assert all(sha(p)==context['record_sha256'][n]==bundle['records'][n]['sha256'] for n,p in record_paths.items())
v3=read(r/'docs/NON_TIMING_TEST_SELECTION_v3.json');v2=read(r/'docs/NON_TIMING_TEST_SELECTION_v2.json')
assert v3['reviewed_source_sha256']==source_manifest()
assert all(v3[k]==v2[k] for k in ['tests','cpu_build_tests','cuda_additional_tests'])
selected=sorted(n for n,a in v3['tests'].items() if a['classification']=='cpu_correctness')
base=sorted(n for n in selected if not v3['tests'][n].get('diagnostic_only'))
assert len(selected)==21 and len(base)==19
counts={}
for kind in ['cpu_release','cpu_sanitize']:
    cmd=read(record_paths[kind]);text=cmd['stdout']
    plan=read(raw/(kind+'_ctest_selection.json'))
    discovery=read(raw/'validation_commands'/(kind+'_ctest_discovery.json'))
    discovered=json.loads(discovery['stdout'])['tests']
    assert discovery['exit_code']==cmd['exit_code']==0 and len(discovered)==31
    assert plan['selected']==selected and plan['selected_count']==21
    assert cmd['argv'][-2:]==['-R','^('+'|'.join(selected)+')$']
    passed=re.findall(r'\d+/21 Test\s+#\d+: ([a-z_]+)\s+\.{3,}\s+Passed',text)
    assert len(passed)==21 and sorted(passed)==selected
    assert '100% tests passed, 0 tests failed out of 21' in text and '***Skipped' not in text
    assert 'Ran 52 tests' in text and 'Ran 9 tests' in text
    assert 'OK (skipped=2)' in text
    if kind=='cpu_sanitize':
        assert cmd['argv'][:6]==['env','-u','ASAN_OPTIONS','-u','LSAN_OPTIONS','UBSAN_OPTIONS=halt_on_error=1']
        assert not (raw/'LEAK_LIMITATION.json').exists()
    counts[kind]=dict(discovered=31,selected=21,passed=21,failed=0,ctest_skipped=0,
                      excluded=10,host_gpu_timing_python_methods_skipped=2,framework_python_methods=52,
                      record_sha256=sha(record_paths[kind]),tests_rerun_in_review=False)
gpu_cmd=read(record_paths['gpu_prepared']);gpu=json.loads(gpu_cmd['stdout'])
assert gpu_cmd['exit_code']==0 and gpu['status']=='passed' and gpu['inputs']==163 and gpu['output_checks']==489
assert gpu['invalid_operations_rejected']==489 and gpu['failures']==0
worker_cmd=read(record_paths['workers']);worker=json.loads(worker_cmd['stdout'])
assert worker_cmd['exit_code']==0 and worker['status']=='passed' and worker['output_checks']==12
assert all(x['correctness'] and x['actual_team_size']==(2 if x['size']>=32768 else 1) for x in worker['calls'])
resources=read(record_paths['workspace'])
from analyze_cpu_gpu import validate_resources
for row in resources['rows']:validate_resources(row['query'],row['size'])
assert [x['size'] for x in resources['rows']]==[1025,65537,1000000]
assert resources['all_limits_passed'] and all(x['sorting_executed'] is False for x in resources['rows'])
assert all(x['host_available_bytes']>=1024**3 and x['disk_free_bytes']>=1024**3 for x in resources['rows'])
# MemAvailable/disk are present, but this bundle lacks fresh cgroup/affinity/quota
# observations required by environment_gate. Do not infer them from old sessions.
build=read(raw/'BUILD_COMPLETE.json');gpu_build=build['identities']['gpu-release']
assert gpu_build['cpu_gpu_comparison']==context['binary_identity']
assert gpu_build['test_parallel_workers']==build['identities']['cpu-release']['test_parallel_workers']
assert gpu_build['libmab_parallel.a']==build['identities']['cpu-release']['libmab_parallel.a']
assert 'comparison_input' not in gpu_build
description=read(raw/'COMPARISON_DESCRIPTION.json')
assert description['build_type']=='Release' and not description['sanitizers'] and description['cub_version']==300001
assert description['configuration_flags']==description['cuda_release_flags']=='-O3 -DNDEBUG'
assert description['global_flags']==description['cuda_flags']=='' and description['cuda_architectures']=='75'
source_transfer=read(prior/'SOURCE_MANIFEST_V2.json')
assert all(sha(r/p)==h for p,h in source_transfer.items() if p not in ['README.md','docs/ROADMAP.md'])

seals={}
for root,key in [
 ('results/raw/cpu_gpu_pilot_20261010T001232473460Z','evidence_and_processed_sha256'),
 ('results/raw/cub_workspace_65537_20261010T110457531249Z','evidence_sha256'),
 ('results/raw/ctest_path_independent_review_20261011T000547578754Z','evidence_sha256'),
 ('results/raw/isolated_colab_revalidation_20261011T011459127026Z','evidence_sha256'),
 ('results/raw/cpu_gpu_prelaunch_review_20261011T012430643251Z','evidence_sha256'),
 ('results/raw/bounded_resume_20261011T024034091796Z','evidence_sha256')]:
    directory=r/root;seal=read(directory/'FINAL_INTEGRITY.json');mapping=seal[key]
    for p,h in mapping.items():
        target=r/p if p.startswith('results/') else directory/p
        assert sha(target)==h,(root,p)
    seals[root]=dict(sealed_files_verified=len(mapping),manifest_sha256=sha(directory/'FINAL_INTEGRITY.json'))
pilot=r/'results/raw/cpu_gpu_pilot_20261010T001232473460Z/remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3'
pilot_build=read(pilot/'build.json')
assert pilot_build['binary_sha256']!=gpu_build['cpu_gpu_comparison']
pilot_source=read(pilot/'source_review.json')['current_source_sha256']
pilot_changes={p:dict(pilot=h,current=sha(r/p)) for p,h in pilot_source.items() if sha(r/p)!=h}
pilot_summary=r/'results/processed/cpu_gpu_pilot_20261010T001232473460Z/summary.json'
pilot_summary_sha=sha(pilot_summary)
assert pilot_summary_sha=='07e69e2e0c8853f93d3f3da895337b5e4b72e5e2dd0ff0577db3cbd1f7053a22'
rows=[row for i,c in enumerate(model['study']['cells']) for row in schedule(c,30*i)]
assert len(rows)==1440 and [x['global_trial_index'] for x in rows]==list(range(1440))
assert sum(x['phase']=='measure' for x in rows)==1200
warnings={}
for path in (raw/'build_commands').glob('*.json'):
    command=read(path);assert command['exit_code']==0
    lines=[x for x in (command['stdout']+'\n'+command['stderr']).splitlines() if 'warning:' in x]
    assert all(x.endswith('style of line directive is a GCC extension') for x in lines)
    warnings[path.stem]=len(lines)
policy_log=read(prior/'policy_regressions.json');assert policy_log['exit_code']==0 and 'Ran 9 tests' in policy_log['stderr']
facts=dict(frozen_assets_verified=4,trusted_original_anchors=len(original),approved_framework_differences=changed_frozen,
           strict_guard_rejections=rejections,correctness_classification=assessment,
           correctness_record_hashes_verified=True,counts=counts,gpu_prepared=gpu,workers=worker,
           resource_snapshots=resources,source_files_verified=len(source_manifest()),transferred_files=len(source_transfer),
           cpu_builds_and_gpu_build=build,comparison_input_digest_recorded=False,
           old_pilot_binary_sha256=pilot_build['binary_sha256'],intended_binary_sha256=gpu_build['cpu_gpu_comparison'],
           old_pilot_current_source_differences=pilot_changes,pilot_summary_sha256=pilot_summary_sha,
           required_cgroup_affinity_quota_fresh_evidence=False,prior_seals_verified=seals,
           expected_study_datasets=48,expected_measured=1200,expected_warmups=240,
           expected_scope=model['timing_scopes'],warning_counts=warnings,
           policy_unit_tests_retained_passed=9,new_tests_executed=0,new_workloads_executed=0,
           actual_current_session_verified=False,full_study_launched=False)
save('REVIEW_VERIFICATION.json',facts)
print(json.dumps(dict(frozen_verified=4,retained_cpu_release=counts['cpu_release'],retained_cpu_sanitize=counts['cpu_sanitize'],
                     retained_gpu_inputs=gpu['inputs'],retained_gpu_output_checks=gpu['output_checks'],
                     prior_seals_verified={k:v['sealed_files_verified'] for k,v in seals.items()},
                     source_guard_rejections=rejections,launch_eligible=False,comparison_input_identity='missing current hash',
                     historical_pilot_binary_matches_current=False,no_new_tests_or_workloads=True),indent=2))
