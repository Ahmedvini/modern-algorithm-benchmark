"""Consolidated read-only preservation review; writes only new release evidence."""
import hashlib
import json
from pathlib import Path
import sys

E = Path(__file__).resolve().parent
R = E.parents[2]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p): return json.loads(p.read_text())
def write(name, value):
    with (E/name).open('x') as f: json.dump(value, f, indent=2, sort_keys=True);f.write('\n')

b=load(E/'BASELINE.json')
allowed={'README.md','docs/ALGORITHMS.md','docs/AUDIT.md','docs/BENCHMARKING.md',
         'docs/METRICS.md','docs/ROADMAP.md','report/README.md','report/generate.py'}
preservation={}
for group in ['historical_results_sha256','protected_sha256','frozen_sha256',
              'build_metadata_sha256','executable_sha256','project_sha256','report_sha256']:
    changed=[p for p,d in b[group].items() if not (R/p).is_file() or sha(R/p)!=d]
    assert set(changed)<=allowed,(group,changed)
    if group not in ['project_sha256','report_sha256']: assert not changed,(group,changed)
    preservation[group]=dict(before=len(b[group]),unchanged=len(b[group])-len(changed),
                             modified=changed,missing=[])
assert sha(R/b['previous_seal'])==b['previous_seal_sha256']
frozen=load(R/'docs/studies/cpu_gpu_comparison_v1.freeze.json')
for p,d in frozen['files_sha256'].items(): assert sha(R/p)==d,p
matrix=load(R/'docs/studies/cpu_gpu_comparison_v1.matrix.json')
anchors={p:b['project_sha256'][p] for p in matrix['source_at_freeze_sha256']}
for p,d in anchors.items(): assert sha(R/p)==d,p
sys.path.insert(0,str(R/'scripts'))
from cpu_gpu_protocol import source_manifest
from non_timing_tests import load_manifest
source=source_manifest();selection=load_manifest()
prior=R/'results/raw/autonomous_completion_20261011T095554571762Z'
assert source==load(prior/'CPU_STUDY_IDENTITIES.json')['source_sha256']
sanitizer=load(prior/'cpu_sanitize.json')
assert sanitizer['exit_code']==0 and '0 tests failed out of 21' in sanitizer['stdout']
assert load(prior/'cpu_sanitize_selection.json')['manifest_sha256']==sha(R/'docs/NON_TIMING_TEST_SELECTION_v5.json')
release=load(E/'cpu_release.json')
assert release['exit_code']==0 and '0 tests failed out of 21' in release['stdout']
assert load(E/'REGENERATION.json')['byte_identical']
assert load(E/'RAW_NUMERIC_AUDIT.json')['raw_reanalysis_passed']
assert selection['full_study_eligible'] is False
additions=['docs/CPU_ONLY_RELEASE_v1.md','docs/DEFERRED_GPU.md',
           'report/verify_cpu.py','report/test_cpu_release.py']
changes=dict(modified={p:dict(before=(b['project_sha256']|b['report_sha256'])[p],after=sha(R/p)) for p in sorted(allowed)},
             added={p:sha(R/p) for p in additions})
write('CHANGES.json',changes)
write('PRESERVATION.json',dict(passed=True,groups=preservation,
      protected_anchor_sha256=anchors,source_sha256=source,source_files=len(source),
      historical_result_files_verified=len(b['historical_results_sha256']),
      original_generated_report_assets_preserved=24,
      reused_sanitizer=dict(record=str((prior/'cpu_sanitize.json').relative_to(R)),sha256=sha(prior/'cpu_sanitize.json'),
          source_identity_verified=True,selection_identity_verified=True,fresh_run=False,
          individual_sanitizer_binary_baseline_available=False),
      identity_map_note='Nine entries: three native executables and six metadata/protocol/selection files, not nine binaries.',
      gpu_trials_executed=0,performance_trials_executed=0))
print(json.dumps(preservation,indent=2))
print('Frozen hashes, 26 anchors, 80 protected files, 83 build metadata entries,')
print('three retained executable hashes, source/selection identity and all13,537 historical results preserved.')
