from pathlib import Path
import hashlib,json,sys
root=Path('/content/mab_bounded_resume_20261011T024034091796Z_revision2');source=root/'source';e=root/'evidence'
sys.dont_write_bytecode=True
sys.path.insert(0,str(source/'scripts'))
from non_timing_tests import pre_discovery_gate
from cpu_gpu_validation_policy import verify_current_sources
verify_current_sources()
assert (e/'BUILD_COMPLETE.json').is_file()
approved=['baselines','cli','comparisons','cpu_gpu_comparison_framework','cuda_benchmark_analysis',
          'cuda_preflight','cuda_sort_handoff','datasets','environment_manifest','memory','memory_unsupported',
          'mergesort','metrics_cli','pdqsort','quicksort','radixsort','searching','structures','timsort']
result={}
for name in ['cpu-release','cpu-sanitize','gpu-release']:
    manifest,guard=pre_discovery_gate(root/name)
    names=[n for n in guard['test_names'] if manifest['tests'][n]['classification']=='cpu_correctness']
    base=[n for n in names if not manifest['tests'][n].get('diagnostic_only')]
    assert sorted(base)==approved
    assert sorted(names)==sorted(approved+['parallel_workers_correctness','validation_policy'])
    assert not {'parallel_mergesort','comparison_engine','cuda_benchmark_gpu_framework'}&set(names)
    result[name]=dict(guard=guard,base_approved=sorted(base),selected_cpu_with_diagnostics=sorted(names),
                      source_policy=manifest['policy'],tests_executed=False,ctest_discovery_executed=False)
with (e/'STATIC_SELECTION_REVIEW.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({k:dict(guarded_build=v['guard']['build_dir'],registered=len(v['guard']['test_names']),
                       selected=v['selected_cpu_with_diagnostics'],discovery_ran=False) for k,v in result.items()},indent=2))
print('STATIC_SELECTION_REVIEW_PASSED')
