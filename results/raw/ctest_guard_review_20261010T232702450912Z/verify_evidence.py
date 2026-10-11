"""Independent static review: stdlib file hashes/JSON only. No project imports."""
import hashlib
import json
from pathlib import Path

ROOT = Path.cwd()
BASE = Path(__file__).resolve().parent
REPAIR = ROOT / 'results/raw/ctest_hook_repair_20261010T223851377458Z'

def pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError('duplicate JSON key: ' + key)
        result[key] = value
    return result

def read(path):
    return json.loads(path.read_text(), object_pairs_hook=pairs,
                      parse_constant=lambda s: (_ for _ in ()).throw(ValueError(s)))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def verify(mapping):
    differences = [name for name, expected in mapping.items()
                   if not (ROOT / name).is_file() or digest(ROOT / name) != expected]
    if differences:
        raise ValueError('digest differences: ' + repr(differences))
    return len(mapping)

before = read(REPAIR / 'BEFORE.json')
start = read(BASE / 'START_SNAPSHOT.json')
report = {
    'repair_baseline_result_files_verified': verify(before['results_sha256']),
    'review_start_result_files_verified': verify(start['prior_results_sha256']),
    'review_start_project_files_verified': verify(start['project_sha256']),
    'review_start_build_metadata_verified': verify(start['build_metadata_sha256']),
    'repair_baseline_build_metadata_verified': verify(before['build_metadata_sha256']),
    'differences': [],
}
assert before['results_count'] == 11448 == len(before['results_sha256'])
assert start['prior_result_count'] == 11516 == len(start['prior_results_sha256'])

report['evidence_seals'] = {}
for directory in [ROOT / 'results/raw/cpu_gpu_safety_repair_20261010T140524185993Z',
                  ROOT / 'results/raw/cpu_gpu_repair_review_20261010T185659333607Z', REPAIR]:
    seal = read(directory / 'FINAL_INTEGRITY.json')
    actual = {p.resolve() for p in directory.rglob('*') if p.is_file()}
    expected = {(ROOT / p).resolve() for p in seal['evidence_sha256']}
    assert actual == expected | {(directory / 'FINAL_INTEGRITY.json').resolve()}
    report['evidence_seals'][directory.name] = {
        'sealed_file_hashes_verified': verify(seal['evidence_sha256']),
        'actual_directory_file_count': len(actual),
        'seal_digest': digest(directory / 'FINAL_INTEGRITY.json'),
        'seal_not_self_authenticated': True,
    }

older = read(ROOT / 'results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/BEFORE.json')
report['original_historical_files_verified'] = verify(older['prior_results_sha256'])
production = {p: h for p, h in older['current_source_sha256'].items()
              if p.startswith(('src/', 'include/', 'third_party/')) or p == 'CMakeLists.txt'}
report['production_headers_dependencies_verified'] = verify(production)
report['production_file_hashes'] = production

pins = {
    'docs/studies/cpu_gpu_comparison_v1.freeze.json':
        '518ac535473e50fb61dab3a70858bdfe42dfdb43570f649174f44bffe40e1ac6',
    'docs/CPU_GPU_DRIVER_REVIEW_v1.json':
        'b6a63a7e65827970d6b27e872e738052cd5faf94d88ee711dbccd5f77f90ef2a',
}
report['protected_identity_documents_verified'] = verify(pins)
freeze = read(ROOT / 'docs/studies/cpu_gpu_comparison_v1.freeze.json')
report['frozen_input_files_verified'] = verify(freeze['files_sha256'])
matrix = read(ROOT / 'docs/studies/cpu_gpu_comparison_v1.matrix.json')
anchors = dict(matrix['source_at_freeze_sha256'])
anchors['CMakeLists.txt'] = read(ROOT / 'docs/CPU_GPU_DRIVER_REVIEW_v1.json')['current_cmake_sha256']
report['protected_anchors_verified'] = verify(anchors)
report['anchor_hashes'] = anchors
report['production_adapter_sha256'] = digest(ROOT / 'src/cuda/cub_sort.cu')
report['cub_pin_sha256'] = digest(ROOT / 'third_party/cub/UPSTREAM.json')
report['cub_pin'] = read(ROOT / 'third_party/cub/UPSTREAM.json')
assert report['cub_pin']['cub_version'] == 300001

inventory = read(REPAIR / 'FILE_REVIEW.json')
after = start['project_sha256']
old = before['project_sha256']
changes = {p: {'before': old.get(p), 'after': after.get(p)}
           for p in sorted(old.keys() | after.keys()) if old.get(p) != after.get(p)}
assert set(changes) == set(inventory)
for p, change in changes.items():
    assert change == {'before': inventory[p]['before_sha256'], 'after': inventory[p]['after_sha256']}
report['repair_inventory'] = changes
report['added_project_files'] = [p for p, d in changes.items() if d['before'] is None]
report['modified_project_files'] = [p for p, d in changes.items() if d['before'] and d['after']]
report['deleted_project_files'] = [p for p, d in changes.items() if d['after'] is None]
assert len(report['added_project_files']) == 4
assert len(report['modified_project_files']) == 7
assert not report['deleted_project_files']
repair_additions = set(start['prior_results_sha256']) - set(before['results_sha256'])
assert len(repair_additions) == 68
assert all(p.startswith(str(REPAIR.relative_to(ROOT)) + '/') for p in repair_additions)
report['repair_additive_evidence_files'] = len(repair_additions)

policy = read(ROOT / 'docs/NON_TIMING_TEST_SELECTION_v1.json')
reviewed = policy['reviewed_source_sha256']
actual_source = {p: h for p, h in after.items()
                 if p == 'CMakeLists.txt' or p.startswith(('scripts/', 'tests/', 'src/', 'include/', 'cmake/', 'third_party/'))}
assert reviewed == actual_source
report['reviewed_source_snapshot_files_verified'] = verify(reviewed)
report['selected_cpu_tests'] = sorted(name for name in policy['cpu_build_tests']
                                      if policy['tests'][name]['classification'] == 'cpu_correctness')
assert len(report['selected_cpu_tests']) == 19
retained_plan = read(REPAIR / 'SELECTED_TESTS.json')
assert retained_plan['selected'] == report['selected_cpu_tests']
report['retained_plan_matches_policy'] = True
report['inspection_only'] = True
with (BASE / 'EVIDENCE_VERIFICATION.json').open('x') as f:
    json.dump(report, f, indent=2, sort_keys=True)
    f.write('\n')
print(json.dumps({k: v for k, v in report.items()
                  if k not in ['production_file_hashes', 'anchor_hashes', 'repair_inventory']}, indent=2, sort_keys=True))
