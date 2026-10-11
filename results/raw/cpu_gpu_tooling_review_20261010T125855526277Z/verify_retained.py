"""Recompute actual historical files; do not trust summary counts."""
import hashlib
import json
from pathlib import Path

root = Path.cwd()
base = Path(__file__).resolve().parent
old = root / 'results/raw/cpu_gpu_full_tooling_20261010T121208603276Z'

def sha(path):
    d = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            d.update(block)
    return d.hexdigest()

def check(mapping):
    missing, changed = [], []
    for relative, digest in mapping.items():
        path = root / relative
        if not path.is_file():
            missing.append(relative)
        elif sha(path) != digest:
            changed.append(relative)
    return dict(checked=len(mapping), missing=missing, changed=changed)

seal = json.loads((old / 'FINAL_INTEGRITY.json').read_text())
report = {key: check(seal[key]) for key in
          ['evidence_sha256', 'current_source_sha256', 'documentation_sha256', 'frozen_files_sha256']}
prior = json.loads((old / 'prior_artifacts_sha256.json').read_text())
report['pre_tooling_artifacts'] = check(prior)
report['review_start_artifacts'] = check(json.loads((base / 'START_SNAPSHOT.json').read_text())['existing_results_sha256'])
freeze_path = root / 'docs/studies/cpu_gpu_comparison_v1.freeze.json'
freeze = json.loads(freeze_path.read_text())
report['frozen_assets_independent'] = check(freeze['files_sha256'])
report['freeze_sha256'] = sha(freeze_path)
report['freeze_matches_accepted_identity'] = report['freeze_sha256'] == '518ac535473e50fb61dab3a70858bdfe42dfdb43570f649174f44bffe40e1ac6'
model = json.loads((root / 'docs/studies/cpu_gpu_comparison_v1.matrix.json').read_text())
anchors = dict(model['source_at_freeze_sha256'])
cmake_review = json.loads((root / 'docs/CPU_GPU_DRIVER_REVIEW_v1.json').read_text())
assert cmake_review['frozen_cmake_sha256'] == anchors['CMakeLists.txt']
anchors['CMakeLists.txt'] = cmake_review['current_cmake_sha256']
report['protected_anchors_with_explicit_reviewed_cmake'] = check(anchors)
report['protected_files_actual_sha256'] = {p: sha(root / p) for p in anchors}
report['dependency_pin'] = json.loads((root / 'third_party/cub/UPSTREAM.json').read_text())
pilot = root / 'results/raw/cpu_gpu_pilot_20261010T001232473460Z'
pilot_seal = json.loads((pilot / 'FINAL_INTEGRITY.json').read_text())
report['accepted_pilot_evidence'] = check(pilot_seal['evidence_and_processed_sha256'])
workspace = root / 'results/raw/cub_workspace_65537_20261010T110457531249Z'
ws_seal = json.loads((workspace / 'FINAL_INTEGRITY.json').read_text())
report['workspace_evidence'] = check(ws_seal['evidence_sha256'])
gpu_dependencies = json.loads((old / 'downloaded/evidence/dependency_sha256.json').read_text())
pilot_dependencies = json.loads((pilot / 'remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/dependency_sha256.json').read_text())['files']
report['retained_installed_dependency_manifests'] = dict(count=len(gpu_dependencies), exactly_equal=pilot_dependencies == gpu_dependencies,
    note='Retained manifests checked; no assertion that the current remote installation is available or unchanged.')
report['pass'] = all(not v['missing'] and not v['changed'] for v in report.values() if isinstance(v, dict) and 'checked' in v)
report['pass'] &= report['freeze_matches_accepted_identity'] and report['retained_installed_dependency_manifests']['exactly_equal']
with (base / 'INDEPENDENT_INTEGRITY.json').open('x') as stream:
    json.dump(report, stream, indent=2, sort_keys=True)
    stream.write('\n')
print(json.dumps({k: v for k, v in report.items() if k not in ['protected_files_actual_sha256','dependency_pin']}, indent=2))
raise SystemExit(0 if report['pass'] else 1)
