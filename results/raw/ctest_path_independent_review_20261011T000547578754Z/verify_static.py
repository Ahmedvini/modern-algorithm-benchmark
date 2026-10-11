"""Independent file/JSON/AST inspection only. No repository imports or execution."""
import ast
import hashlib
import json
import re
from pathlib import Path

ROOT = Path.cwd()
E = Path(__file__).resolve().parent
REPAIR = ROOT/'results/raw/ctest_path_repair_20261010T234224414430Z'
checks = {}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_text())

def verify_map(mapping):
    failures = []
    for key, expected in mapping.items():
        p = ROOT/key
        if not p.is_file() or digest(p) != expected:
            failures.append(key)
    return {'entries': len(mapping), 'differences': failures}

def tree_files(base):
    return {str(p.relative_to(ROOT)): digest(p) for p in sorted(base.rglob('*')) if p.is_file()}

before = read(REPAIR/'BEFORE.json')
seal = read(REPAIR/'FINAL_INTEGRITY.json')
checks['repair_prior_results'] = verify_map(before['prior_results_sha256'])
original = read(ROOT/'results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/BEFORE.json')
checks['original_historical_results'] = verify_map(original['prior_results_sha256'])
production = {k:v for k,v in original['current_source_sha256'].items()
              if k.startswith(('src/', 'include/', 'third_party/')) or k == 'CMakeLists.txt'}
checks['production_headers_dependencies'] = verify_map(production)
checks['build_metadata'] = verify_map(before['build_metadata_sha256'])

current_prior = {k:v for k,v in tree_files(ROOT/'results').items() if not (ROOT/k).is_relative_to(E)}
with (E/'BEFORE_ALL_RESULTS.json').open('x') as f:
    json.dump({'prior_results_sha256':current_prior,
               'note':'Full inventory including the one historical __pycache__ file excluded by initial snapshot filter. No prior file was written.'},f,indent=2,sort_keys=True)
    f.write('\n')
bootstrap = read(E/'BEFORE.json')
excluded = sorted(set(current_prior)-set(bootstrap['prior_results_sha256']))
checks['initial_snapshot_filter_qualification'] = {
    'filtered_count':len(bootstrap['prior_results_sha256']), 'all_files_count':len(current_prior),
    'excluded':excluded, 'filtered_files':verify_map(bootstrap['prior_results_sha256']),
    'excluded_matches_repair_before':{k:current_prior[k] == before['prior_results_sha256'].get(k) for k in excluded}}

directories = ['cpu_gpu_safety_repair_20261010T140524185993Z',
               'cpu_gpu_repair_review_20261010T185659333607Z',
               'ctest_hook_repair_20261010T223851377458Z',
               'ctest_guard_review_20261010T232702450912Z',
               'ctest_path_repair_20261010T234224414430Z']
checks['evidence_seals'] = {}
for name in directories:
    base=ROOT/'results/raw'/name
    data=read(base/'FINAL_INTEGRITY.json')
    recorded={str((ROOT/k).relative_to(ROOT)):v for k,v in data['evidence_sha256'].items()}
    actual=tree_files(base)
    expected=set(recorded)|{str((base/'FINAL_INTEGRITY.json').relative_to(ROOT))}
    checks['evidence_seals'][name]={**verify_map(recorded),'actual_files':len(actual),
        'unexpected':sorted(set(actual)-expected),'missing':sorted(expected-set(actual))}

freeze_path=ROOT/'docs/studies/cpu_gpu_comparison_v1.freeze.json'
review_path=ROOT/'docs/CPU_GPU_DRIVER_REVIEW_v1.json'
checks['independent_literal_pins']={
    'freeze':digest(freeze_path)=='518ac535473e50fb61dab3a70858bdfe42dfdb43570f649174f44bffe40e1ac6',
    'cmake_review':digest(review_path)=='b6a63a7e65827970d6b27e872e738052cd5faf94d88ee711dbccd5f77f90ef2a'}
freeze=read(freeze_path)
checks['frozen_members']=verify_map(freeze['files_sha256'])
matrix=read(ROOT/'docs/studies/cpu_gpu_comparison_v1.matrix.json')
anchors=dict(matrix['source_at_freeze_sha256'])
anchors['CMakeLists.txt']=read(review_path)['current_cmake_sha256']
checks['protected_anchors_existing_reviewed_cmake_exception']=verify_map(anchors)
cub=ROOT/'third_party/cub/UPSTREAM.json'
checks['cub_pin']={'sha256':digest(cub),'unchanged':digest(cub)=='477b1ee70b0a9113c9f98b263c19a31d05ccee54f45ce8476aec4cc98965ced1','content':read(cub)}
adapter=ROOT/'src/cuda/cub_sort.cu'
checks['production_adapter']={'sha256':digest(adapter),'unchanged':digest(adapter)=='b6d7f37c7494587fc6e4a676c00c166dc322d31cce96710811e3a4cb9cd8b9cb'}

modified={k:{'before':v,'current':digest(ROOT/k)} for k,v in before['project_sha256'].items() if digest(ROOT/k)!=v}
checks['repair_project_changes']={'modified':modified,
    'matches_declared_inventory':set(modified)==set(seal['modified_project_files']),
    'copies_match':all(digest(REPAIR/'before'/k)==v['before'] and digest(REPAIR/'reviewed'/k)==v['current'] for k,v in modified.items())}
old_policy=read(REPAIR/'before/docs/NON_TIMING_TEST_SELECTION_v1.json')
policy=read(ROOT/'docs/NON_TIMING_TEST_SELECTION_v1.json')
old_hashes=old_policy.pop('reviewed_source_sha256')
new_hashes=dict(policy['reviewed_source_sha256'])
other_policy={k:v for k,v in policy.items() if k!='reviewed_source_sha256'}
expected=['baselines','cli','comparisons','cpu_gpu_comparison_framework','cuda_benchmark_analysis',
          'cuda_preflight','cuda_sort_handoff','datasets','environment_manifest','memory',
          'memory_unsupported','mergesort','metrics_cli','pdqsort','quicksort','radixsort','searching','structures','timsort']
selection=sorted(n for n in policy['cpu_build_tests'] if policy['tests'][n]['classification']=='cpu_correctness')
checks['policy']={'non_source_fields_identical':old_policy==other_policy,
    'changed_source_digests':sorted(k for k in new_hashes if old_hashes.get(k)!=new_hashes[k]),
    'source_key_sets_identical':set(old_hashes)==set(new_hashes), 'snapshot':verify_map(new_hashes),
    'exact_selection':selection,'matches_exact_19':selection==expected==seal['approved_cpu_selection'],
    'excluded_cpu':sorted(set(policy['cpu_build_tests'])-set(selection))}

def methods(path, cls):
    module=ast.parse(path.read_text(),filename=str(path))
    node=next(n for n in module.body if isinstance(n,ast.ClassDef) and n.name==cls)
    return {n.name:n for n in node.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name.startswith('test_')}

old_tests=methods(REPAIR/'before/tests/test_ctest_build_guard.py','BuildGuardTests')
tests=methods(ROOT/'tests/test_ctest_build_guard.py','BuildGuardTests')
existing=methods(ROOT/'tests/test_cpu_gpu_safety.py','SelectorTests')
added=sorted(set(tests)-set(old_tests))
checks['regression_ast']={'old_methods':len(old_tests),'current_methods':len(tests),'selector_methods':len(existing),
    'added':{k:tests[k].lineno for k in added},
    'all_old_bodies_identical':all(ast.dump(v,include_attributes=False)==ast.dump(tests[k],include_attributes=False) for k,v in old_tests.items())}
checks['preserved_reproducer']={
    'selector_matches_before':digest(REPAIR/'reproducer_before_fix/scripts/non_timing_tests.py')==digest(REPAIR/'before/scripts/non_timing_tests.py'),
    'tests_match_current':digest(REPAIR/'reproducer_before_fix/tests/test_ctest_build_guard.py')==digest(ROOT/'tests/test_ctest_build_guard.py'),
    'candidate_policy_maps_to_retained_selector':read(REPAIR/'reproducer_before_fix/docs/NON_TIMING_TEST_SELECTION_v1.json')['reviewed_source_sha256']['scripts/non_timing_tests.py']==digest(REPAIR/'reproducer_before_fix/scripts/non_timing_tests.py')}
checks['recorded_test_logs']={}
for name,names in [('inert_reproducer_before_fix',set(added)),('inert_regressions_after_repair',set(added)),
                   ('all_inert_selector_regressions',set(tests)|set(existing))]:
    data=read(REPAIR/'commands'/(name+'.json'))
    log=data['stderr']
    listed=set(re.findall(r'^(test_\w+) \(',log,re.M))
    checks['recorded_test_logs'][name]={'exit_code':data['exit_code'],'method_names_match_source':listed==names,
        'method_count':len(listed),'summary':re.findall(r'Ran \d+ tests.*|FAILED .*|^OK$',log,re.M),
        'passes':len(re.findall(r'^test_.* \.\.\. ok$',log,re.M))}

checks['alternate_entry_points']={}
for path in sorted((ROOT/'scripts').glob('*.py')):
    hits=[{'line':i,'text':line.strip()} for i,line in enumerate(path.read_text().splitlines(),1)
          if any(s in line for s in ['selected_ctest(', 'select_tests(', 'pre_discovery_gate(', '--show-only=json-v1'])]
    if hits:checks['alternate_entry_points'][str(path.relative_to(ROOT))]=hits
checks['current_review_project_preserved']=verify_map(bootstrap['project_sha256'])
checks['current_review_build_metadata_preserved']=verify_map(bootstrap['build_metadata_sha256'])

with (E/'INDEPENDENT_VERIFICATION.json').open('x') as f:
    json.dump(checks,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps(checks,indent=2,sort_keys=True))
