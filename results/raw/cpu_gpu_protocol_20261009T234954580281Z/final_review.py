"""Verify historical integrity and narrowly scoped documentation changes."""
import hashlib,json
from pathlib import Path

paths=json.loads(Path('build/cpu_gpu_protocol_paths.json').read_text())
e=Path(paths['evidence']);backup=Path(paths['backup'])/'before'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
prior=json.loads((e/'prior_artifacts_sha256.json').read_text())
source=json.loads((e/'source_before.json').read_text())
allowed={'README.md','docs/ROADMAP.md','docs/AUDIT.md','docs/BENCHMARKING.md'}
assert all(Path(p).is_file() and sha(p)==h for p,h in prior.items())
actual_changes={p for p,h in source.items() if sha(p)!=h}
assert actual_changes==allowed,actual_changes
for p in allowed-{'docs/ROADMAP.md'}:
    assert Path(p).read_bytes().startswith((backup/p).read_bytes()),p
old=(backup/'docs/ROADMAP.md').read_text()
before='| 7 — CUDA | Correctness and prepared four-metric timing smoke validated on T4; 48 configurations/240 measured trials plus smallest5; full comparative GPU study remains pending |'
after='| 7 — CUDA | Correctness and prepared four-metric timing smoke validated on T4; controlled <=1M CPU/GPU protocol frozen for review; comparison driver, pilot and full comparative study remain pending |'
assert old.count(before)==1
assert Path('docs/ROADMAP.md').read_text().startswith(old.replace(before,after))
oldroot=Path('results/raw/cuda_timing_20261009T231303050084Z')
assert sha(oldroot/'FINAL_SHA256_MANIFEST.json')=='8cc3b50f5aea82932faa36662844cb61799f04a5f7fd0d3e6803a152abc5dfef'
sealed=json.loads((oldroot/'FINAL_SHA256_MANIFEST.json').read_text())
assert all(sha(p)==h for p,h in sealed.items())
freeze=Path('docs/studies/cpu_gpu_comparison_v1.freeze.json')
frozen=json.loads(freeze.read_text())
assert frozen['execution_authorized'] is False
assert all(sha(p)==h for p,h in frozen['files_sha256'].items())
matrix=json.loads(Path('docs/studies/cpu_gpu_comparison_v1.matrix.json').read_text())
assert all(sha(p)==h for p,h in matrix['source_at_freeze_sha256'].items())
for command in ('verify_existing','targeted_cpu_ctest','generate_assets','generate_final_assets','freeze_assets','validate_assets','local_planning_environment'):
    assert json.loads((e/'commands'/(command+'.json')).read_text())['exit_code']==0,command
for p in ('FINAL_AUDIT.md','CHANGES.md','COMMANDS.md','editor_diagnostics.json'):
    assert (e/p).is_file(),p
report=dict(complete=True,scope='protocol planning and integrity only; no comparative experiment executed',
    prior_result_files_verified=len(prior),previous_sealed_smoke_files_verified=len(sealed),
    original_source_files=len(source),unchanged_protected_source_files=len(source)-len(allowed),
    changed_existing_files={p:dict(before=source[p],after=sha(p)) for p in sorted(allowed)},
    source_anchor_files_verified=len(matrix['source_at_freeze_sha256']),
    frozen_assets_verified=frozen['files_sha256'],freeze_manifest_sha256=sha(freeze),
    frozen_protocol_unchanged_after_validation=True,production_adapter_and_dependency_pin_unchanged=True,
    fresh_cpu_ctest_groups_passed=3,static_protocol_methods_passed=14,
    fresh_full_build=False,fresh_full_sanitizers=False,remote_session_queried=False,gpu_pilot_executed=False,
    main_comparison_executed=False)
with (e/'FINAL_INTEGRITY.json').open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps(report,indent=2))
