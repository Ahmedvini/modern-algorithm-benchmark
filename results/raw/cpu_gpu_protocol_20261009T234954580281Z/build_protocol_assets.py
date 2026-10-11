#!/usr/bin/env python3
"""Generate protocol assets only. No benchmark, GPU, subprocess or timing execution."""
import argparse,csv,hashlib,io,json,math
from pathlib import Path
ROOT=Path.cwd()
PROTOCOL='cpu_gpu_comparison_v1'
SIZES=[1025,65537,1000000]
SEEDS=[1729,42,2718]
DISTRIBUTIONS=['uniform','sorted','reverse_sorted','duplicate_heavy','nearly_sorted','signed_edges']
BACKENDS=[dict(id='cpu_std_sort',algorithm='std_sort',path='mab::find_sorter',scope='host_vector_api_call_v1',threads=1),
 dict(id='cpu_merge_sort',algorithm='merge_sort',path='mab::find_sorter',scope='host_vector_api_call_v1',threads=1),
 dict(id='cpu_parallel_merge_sort_t2',algorithm='parallel_merge_sort',path='mab::find_parallel_sorter',scope='host_vector_api_call_v1',threads=2),
 dict(id='gpu_cub_adapter',algorithm='cub_radix_sort',path='mab::find_cuda_sorter',scope='host_vector_api_call_v1',threads=None),
 dict(id='gpu_cub_prepared',algorithm='cub_radix_sort',path='mab::CudaTimingSession::sample',scope='cuda_sort_timing_v1_four_metrics',threads=None)]
ORDER_SEED=314159
PRIMARY_FIELDS=['schema_version','protocol','run_id','matrix_sha256','build_id','environment_id',
 'dataset_id','input_sha256','input_hash_fnv1a64','size','distribution','seed','dataset_generator',
 'nearly_sorted_swaps','duplicate_cardinality','backend_id','algorithm','implementation_identity_ref','scope',
 'phase','trial_index','execution_order','global_trial_index','requested_cpu_threads','actual_cpu_threads',
 'parallel_region','elapsed_ns','elapsed_unit','status','correctness','error']
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode('ascii')
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def recipe(n,d,s):
 if type(n) is not int or n not in SIZES or d not in DISTRIBUTIONS or type(s) is not int or s not in SEEDS:raise ValueError('outside frozen matrix domain')
 if d=='signed_edges' and s!=1729:raise ValueError('signed_edges has one nonrandom dataset')
 return dict(key_type='signed_int32',size=n,distribution=d,seed=s,dataset_generator='signed_edges_v1' if d=='signed_edges' else 'mt19937_64_v1',
             nearly_sorted_swaps=n//100 if d=='nearly_sorted' else 0,duplicate_cardinality=16)
def cell(n,d,s):
 data=recipe(n,d,s);identity=hashlib.sha256(canonical(data)).hexdigest()
 backend_ids=[b['id'] for b in BACKENDS]
 base=sorted(backend_ids,key=lambda b:(hashlib.sha256(f'{ORDER_SEED}|{identity}|{b}'.encode('ascii')).hexdigest(),b))
 return dict(dataset_id=identity,recipe=data,warmup_order=[base],measure_order=[base[i:]+base[:i] for i in range(5)])
def cases(pilot=False):
 ns=[1025,1000000] if pilot else SIZES
 ds=['uniform','duplicate_heavy','signed_edges'] if pilot else DISTRIBUTIONS
 result=[cell(n,d,s) for n in ns for d in ds for s in ([1729] if pilot or d=='signed_edges' else SEEDS)]
 return sorted(result,key=lambda c:(hashlib.sha256(f'{ORDER_SEED}|{c["dataset_id"]}'.encode('ascii')).hexdigest(),c['dataset_id']))
def counts(cells):
 n=len(cells)
 return dict(datasets=n,backend_configurations=n*5,measured_invocations=n*25,warmup_invocations=n*5,
             primary_measured_rows=n*20,primary_warmup_rows=n*4,prepared_measured_rows=n*5,prepared_warmup_rows=n,
             measured_prepared_metric_values=n*20,total_invocations=n*30,paired_primary_ratios=n*3)
def resources():
 # A reserve cap is a planning allowance, not a measured or proven CUB bound.
 rows=[]
 for n in SIZES:
  rows.append(dict(size=n,one_array_bytes=4*n,host_vectors_persistent_bytes=12*n,pinned_host_bytes=8*n,
    cpu_workspace_or_adapter_output_peak_bytes=4*n,known_host_peak_payload_bytes=24*n,
    prepared_device_keys_bytes=8*n,adapter_device_keys_bytes=8*n,combined_device_keys_bytes=16*n,
    prepared_workspace_historical_bytes=1 if n==1025 else 279295 if n==65537 else '',
    adapter_workspace_bytes='unknown_requires_query',prepared_workspace_current_bytes='unknown_requires_query',
    workspace_cap_each_bytes=64*1024**2,combined_device_planning_cap_bytes=16*n+128*1024**2,
    allocation_payload_cap_bytes=256*1024**2,unmeasured_overhead='runtime/context/allocator/pageable-staging/stack/tasks/metadata'))
 return rows
def runtime_model(cells,B):
 per=[]
 for c in cells:
  n=c['recipe']['size'];cpu=max(.001,4*B*(n*math.log2(n))/(1000000*math.log2(1000000)))
  seconds=.5+6*(3*cpu+.05+.01)+30*.01*n/1000000
  per.append(dict(dataset_id=c['dataset_id'],size=n,estimated_seconds=seconds))
 return dict(kind='planning_model_not_measurement',cpu_1m_proxy_max_seconds=B,cross_host_cpu_multiplier_assumption=4,
   cpu_call_floor_seconds_assumption=.001,gpu_adapter_call_seconds_assumption=.05,gpu_prepared_call_seconds_assumption=.01,
   setup_per_dataset_seconds_assumption=.5,validation_per_call_1m_seconds_assumption=.01,
   model_seconds=sum(c['estimated_seconds'] for c in per),contingency_budget_seconds=4*sum(c['estimated_seconds'] for c in per),
   compile_regression_preflight_budget_seconds=[300,1200],model_omits='fresh build/full regressions, session provisioning, transfers of evidence; actual pilot will replace proxy',per_dataset=per)
def build():
 previous=Path('results/raw/cuda_timing_20261009T231303050084Z')
 historical_cpu=json.loads(Path('results/processed/sorting_1m_20261009T172003802655Z/per_seed.json').read_text())
 B=max(g['max_ns'] for g in historical_cpu['groups'] if g['algorithm'] in ['std_sort','merge_sort'])/1e9
 pilot=cases(True);study=cases()
 pin=json.loads(Path('third_party/cub/UPSTREAM.json').read_text())
 files=['CMakeLists.txt','cmake/cuda.cmake','include/common/types.hpp','include/algorithms/sorting.hpp',
  'src/algorithms/baselines.cpp','src/algorithms/mergesort.cpp','include/algorithms/detail/mergesort_impl.hpp',
  'src/algorithms/parallel_mergesort.cpp','include/algorithms/detail/parallel_mergesort_impl.hpp','include/algorithms/parallel_mergesort.hpp',
  'include/algorithms/cuda_sorting.hpp','src/cuda/cub_sort.cu','src/cuda/cub_timing.cu','include/benchmark/cuda_timing.hpp',
  'include/benchmark/detail/timing_impl.hpp','src/benchmark/timing.cpp','src/datasets/generator.cpp',
  'src/benchmark/cuda_main.cpp','src/benchmark/parallel_timing.cpp','include/datasets/generator.hpp',
  'scripts/analyze_results.py','scripts/analyze_cuda_results.py','scripts/analyze_parallel_results.py',
  'docs/CUDA_TIMING_PROTOCOL_v1.md','third_party/cub/UPSTREAM.json','third_party/cub/LICENSE']
 return dict(schema_version=1,protocol=PROTOCOL,status='frozen_for_review',execution_authorized=False,comparison_implementation='not_implemented',
   key_type='signed_int32',max_size=1000000,warmups=1,repetitions=5,backend_order_seed=ORDER_SEED,
   order_policy='sha256_ascii_dataset_and_backend_permutation_then_left_rotate_v1',
   dataset_id_policy='sha256_canonical_recipe_json_v1',input_identity_policy='FNV1a64_existing_and_SHA256_uint32_low_to_high_bytes_v1',
   backend_modes=BACKENDS,build=dict(cxx_standard=17,type='Release',sanitizers=False,openmp=True,cuda=True,cuda_sort=True,
      cxx_release_flags='-O3 -DNDEBUG',cuda_release_flags='-O3 -DNDEBUG',cuda_architectures='75',cpu_timing_host='same Colab VM and process as GPU'),
   dependency={k:pin[k] for k in ['upstream','reference_release','commit','cub_version','license','files']},
   source_at_freeze_sha256={f:sha(f) for f in files},
   runtime_metadata=None,runtime_metadata_note='fresh collection required; historical T4 readiness is not current session readiness',
   openmp_policy=dict(requested_threads=2,minimum_effective_logical_cpus=2,parallel_threshold=32768,task_grain=16384,
      environment=dict(OMP_DYNAMIC='FALSE',OMP_THREAD_LIMIT='2',OMP_MAX_ACTIVE_LEVELS='1',OMP_WAIT_POLICY='PASSIVE',OMP_PROC_BIND='FALSE'),
      expected_actual_below_threshold=1,expected_actual_at_or_above_threshold=2),
   pilot=dict(cells=pilot,expected=counts(pilot),reuse_in_study=False),study=dict(cells=study,expected=counts(study)),
   resources=dict(table=resources(),memory_unit='bytes',workspace_each_cap_bytes=64*1024**2,
      payload_cap_bytes=256*1024**2,combined_device_peak_formula='16*N+max(W_prepared,1)+max(W_adapter,1)',
      host_peak_payload_formula='24*N',minimum_host_headroom_bytes=1024**3,minimum_free_disk_bytes=1024**3,
      raw_csv_budget_assumption_bytes_per_row=1024,study_csv_budget_bytes=counts(study)['total_invocations']*1024,
      study_raw_and_build_planning_budget_bytes=512*1024**2,
      required_before_launch='query both CUB workspaces; combined device peak <=256MiB and <=half cudaMemGetInfo free before persistent allocations'),
   timing_scopes=dict(primary='host_vector_api_call_v1',primary_metric='host_call_e2e_ns',primary_csv_elapsed_column='elapsed_ns',
      prepared_protocol='cuda_sort_timing_v1',prepared_metrics=['h2d_ns','device_sort_ns','d2h_ns','end_to_end_ns'],
      allowed_ratio_denominator='gpu_cub_adapter',forbidden_ratio_backends=['gpu_cub_prepared'],
      context_policy='warm context; process/context initialization outside all metrics; algorithm-internal allocations inside primary calls'),
   primary_schema=dict(status='specified_not_implemented',protocol='cpu_gpu_host_call_v1',schema_version=1,csv_fields=PRIMARY_FIELDS,
      gpu_cpu_thread_fields='empty/not_applicable; never GPU worker counts',elapsed_unit='ns'),
   statistics=dict(within_dataset=['successful','failed','interrupted','missing','median','mean','sample_sd_ddof1','min','max'],
      cross_dataset_unit='distinct input content within size/distribution',cross_dataset_weight='equal per distinct input_sha256',
      cross_dataset_inputs='dataset medians and separately paired ratios of primary medians',warmups_in_statistics=False,
      outlier_policy='retain_all',confidence_intervals=None,significance_tests=None,
      single_distinct_dataset_sd=None,timer_calibration_pairs=1000,resolution_ratio_gate_multiplier=10,
      timer_overhead_subtraction=False),
   record_identity=dict(phase_values=['warmup','measure'],trial_index='zero-based within phase',
      execution_order='zero-based within dataset, including warmups',global_trial_index='zero-based across datasets, including warmups',
      prepared_order_sidecar_required=True),
   launch_gates=dict(required_device='Tesla T4',compute_capability='7.5',review_before_pilot=True,
      pilot_success_before_study=True,review_before_study=True,current_session_verified=False,
      no_concurrent_workloads=True,actual_cpu_team_check=True,complete_oracle_equality=True),
   estimation=dict(pilot=runtime_model(pilot,B),study=runtime_model(study,B),
      sources=[str(previous/'downloaded/raw/smoke_matrix.json'),'results/processed/sorting_1m_20261009T172003802655Z/per_seed.json'],
      disclaimer='Different-host CPU proxy and unmeasured GPU adapter budget; neither prediction nor measured comparison.'),
   timeout_policy=dict(per_dataset_seconds=60,pilot_total_seconds=300,study_total_seconds=1800,action='stop and retain failed/interrupted/missing; no automatic retry'),
   implementation_required=['isolated comparison driver with five-mode interleaving','shared signed_edges helper used across both paths',
      'allocation-inclusive host-call CSV and paired-scope validator/analyzer','pre-execution dual-workspace planning query','strict scheduler/CLI safety tests'],
   interpretation='descriptive per-dataset medians before equal-weight distinct-input summaries; no confidence intervals/significance; retain all outliers')
def write(output):
 output=Path(output);output.mkdir()
 model=build()
 with (output/'cpu_gpu_comparison_v1.matrix.json').open('x') as f:json.dump(model,f,indent=2,sort_keys=True,allow_nan=False);f.write('\n')
 rows=model['resources']['table']
 with (output/'cpu_gpu_comparison_v1.resources.csv').open('x',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
 return model
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
 model=write(args.output)
 print(json.dumps(dict(study=model['study']['expected'],pilot=model['pilot']['expected'],
   runtime_model_study_seconds=model['estimation']['study']['model_seconds'],runtime_model_pilot_seconds=model['estimation']['pilot']['model_seconds']),indent=2))
