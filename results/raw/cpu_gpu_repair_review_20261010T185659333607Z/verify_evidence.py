"""Read-only SHA verification; writes only this review's new report."""
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
REPAIR = Path('results/raw/cpu_gpu_safety_repair_20261010T140524185993Z')
OLD = Path('results/raw/cpu_gpu_tooling_review_20261010T125855526277Z')
TOOLING = Path('results/raw/cpu_gpu_full_tooling_20261010T121208603276Z')

def read(path):
    return json.loads(path.read_text())

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def verify(mapping):
    missing = [p for p in mapping if not Path(p).is_file()]
    changed = [p for p,h in mapping.items() if Path(p).is_file() and sha(p) != h]
    assert not missing and not changed, dict(missing=missing,changed=changed)
    return dict(checked=len(mapping),missing=missing,changed=changed)

seal = read(REPAIR/'FINAL_INTEGRITY.json')
before = read(REPAIR/'BEFORE.json')
report = dict(repair_seal=verify(seal['evidence_sha256']),
              repaired_source=verify(seal['source_after']),
              repaired_documentation=verify(seal['documentation_sha256']),
              frozen_assets=verify(seal['frozen_files_sha256']),
              historical_11345=verify(before['prior_results_sha256']),
              previous_review_seal=verify(read(OLD/'FINAL_INTEGRITY.json')['evidence_sha256']),
              original_tooling_seal=verify(read(TOOLING/'FINAL_INTEGRITY.json')['evidence_sha256']))
assert len(before['prior_results_sha256']) == 11345
assert before['current_source_sha256'] == seal['source_before'] == read(TOOLING/'FINAL_INTEGRITY.json')['current_source_sha256']
freeze = read(Path('docs/studies/cpu_gpu_comparison_v1.freeze.json'))
assert sha('docs/studies/cpu_gpu_comparison_v1.freeze.json') == '518ac535473e50fb61dab3a70858bdfe42dfdb43570f649174f44bffe40e1ac6'
report['frozen_members'] = verify(freeze['files_sha256'])
matrix = read(Path('docs/studies/cpu_gpu_comparison_v1.matrix.json'))
review = read(Path('docs/CPU_GPU_DRIVER_REVIEW_v1.json'))
assert sha('docs/CPU_GPU_DRIVER_REVIEW_v1.json') == 'b6a63a7e65827970d6b27e872e738052cd5faf94d88ee711dbccd5f77f90ef2a'
assert review['frozen_cmake_sha256'] == matrix['source_at_freeze_sha256']['CMakeLists.txt']
anchors = dict(matrix['source_at_freeze_sha256'])
anchors['CMakeLists.txt'] = review['current_cmake_sha256']
report['protected_anchors_existing_cmake_exception'] = verify(anchors)
production = {p:h for p,h in before['current_source_sha256'].items()
              if p.startswith(('src/','include/','third_party/')) or p == 'CMakeLists.txt'}
report['production_headers_dependencies'] = verify(production)
repair_actual = {str(p):sha(p) for p in REPAIR.rglob('*') if p.is_file()}
assert set(repair_actual) == set(seal['evidence_sha256']) | {str(REPAIR/'FINAL_INTEGRITY.json')}
assert not set(repair_actual) & set(before['prior_results_sha256'])
assert len(repair_actual) == 46
start = read(BASE/'START_SNAPSHOT.json')
assert set(start['prior_results_sha256']) == set(before['prior_results_sha256']) | set(repair_actual)
report['additive_repair_evidence_files'] = len(repair_actual)
report['results_at_review_start'] = start['prior_result_count']
report['source_before_matches_original_tooling'] = True
manifest = read(Path('docs/NON_TIMING_TEST_SELECTION_v1.json'))
report['reviewed_selection_source_snapshot'] = verify(manifest['reviewed_source_sha256'])
assert manifest['reviewed_source_sha256'] == seal['source_after']
pilots = [REPAIR/'PILOT_REANALYSIS.json', OLD/'PILOT_REANALYSIS.json']
assert pilots[0].read_bytes() == pilots[1].read_bytes()
report['pilot_summary_hashes'] = {str(p):sha(p) for p in pilots}
assert sha(pilots[0]) == '07e69e2e0c8853f93d3f3da895337b5e4b72e5e2dd0ff0577db3cbd1f7053a22'
copies = [REPAIR/'reproducer.py',Path('tests/fixtures/cpu_gpu_provenance_reproducer.py'),OLD/'probe_full_analysis.py']
report['exact_reproducer_hashes'] = {str(p):sha(p) for p in copies}
assert len(set(report['exact_reproducer_hashes'].values())) == 1
report['prior_reproducer_observation'] = read(OLD/'FULL_ANALYSIS_PROBE.json')
report['repaired_reproducer_observation'] = read(REPAIR/'FULL_ANALYSIS_PROBE.json')
for name in ['focused_regressions','focused_regressions_final','comparison_synthetic_regressions','exact_full_matrix_reproducer']:
    result = read(REPAIR/'commands'/ (name+'.json'))
    report[name] = dict(exit_code=result['exit_code'],stdout=result['stdout'],stderr=result['stderr'])
report['retained_attempt1_files'] = {str(p):sha(p) for p in (REPAIR/'attempt1').rglob('*') if p.is_file()}
report['cub_pin'] = read(Path('third_party/cub/UPSTREAM.json'))
report['no_workloads_executed'] = True
with (BASE/'EVIDENCE_VERIFICATION.json').open('x') as stream:
    json.dump(report,stream,indent=2,sort_keys=True);stream.write('\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['focused_regressions','focused_regressions_final',
    'comparison_synthetic_regressions','exact_full_matrix_reproducer','cub_pin']},indent=2,sort_keys=True))
