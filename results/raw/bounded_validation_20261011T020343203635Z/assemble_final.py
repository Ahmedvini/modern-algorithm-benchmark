"""Evidence assembly only: no subprocesses, discovery, tests, network or GPU calls."""
from pathlib import Path
import datetime, difflib, hashlib, json, shlex, sys

E = Path(__file__).resolve().parent
ROOT = E.parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
def save(name, value):
    with (E / name).open('x') as out:
        json.dump(value, out, indent=2, sort_keys=True)
        out.write('\n')

before = read(E / 'BEFORE.json')
allowed = {'CMakeLists.txt', 'README.md', 'docs/ROADMAP.md',
           'include/benchmark/cuda_timing.hpp', 'scripts/non_timing_tests.py',
           'src/cuda/cub_timing.cu', 'tests/test_cpu_gpu_comparison.py'}
new = {'tests/test_cuda_prepared_correctness.cpp', 'tests/test_parallel_workers.cpp',
       'scripts/cpu_gpu_validation_policy.py', 'tests/test_validation_policy.py',
       'tests/test_validation_selection.py', 'docs/CPU_GPU_VALIDATION_POLICY_v2.json',
       'docs/NON_TIMING_TEST_SELECTION_v2.json', 'docs/CPU_GPU_VALIDATION_POLICY_v2.md'}
current_results = {str(p.relative_to(ROOT)): sha(p) for p in sorted((ROOT / 'results').rglob('*'))
                   if p.is_file() and not p.is_relative_to(E)}
assert current_results == before['historical_results_sha256'], 'historical preservation mismatch'
assert all(sha(ROOT / p) == h for p, h in before['build_metadata_sha256'].items())
changed = {p for p, h in before['project_sha256'].items() if sha(ROOT / p) != h}
assert changed == allowed, changed
bundle = read(E / 'SOURCE_MANIFEST.json')
assert set(bundle) - set(before['project_sha256']) == new
assert {p for p, h in bundle.items() if sha(ROOT / p) != h} == {'README.md', 'docs/ROADMAP.md'}
for name in allowed:
    original = E / 'before' / name
    assert sha(original) == before['project_sha256'][name]
    diff = ''.join(difflib.unified_diff(original.read_text().splitlines(True),
               (ROOT/name).read_text().splitlines(True), fromfile='before/'+name, tofile=name))
    target = E / (name.replace('/', '_') + '.final.diff')
    with target.open('x') as out: out.write(diff)
sys.path.insert(0, str(ROOT/'scripts'))
from cpu_gpu_protocol import load_protocol
from cpu_gpu_provenance import trusted_source_anchors, TRUSTED_FREEZE_SHA256
from cpu_gpu_validation_policy import verify_current_sources
anchors = trusted_source_anchors(load_protocol())
policy = verify_current_sources()
exceptions = set(policy['authorized_framework_exceptions'])
anchor_changes = {p for p,h in anchors.items() if sha(ROOT/p) != h}
assert anchor_changes == exceptions
oldprod = read(ROOT/'results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/BEFORE.json')
production = {p:h for p,h in oldprod['current_source_sha256'].items()
              if p.startswith(('src/','include/','third_party/')) or p == 'CMakeLists.txt'}
assert len(production) == 80
assert {p for p,h in production.items() if sha(ROOT/p) != h} == exceptions
reviewed = read(ROOT/'docs/NON_TIMING_TEST_SELECTION_v2.json')
assert all(sha(ROOT/p) == h for p,h in reviewed['reviewed_source_sha256'].items())
oldselector = read(ROOT/'docs/NON_TIMING_TEST_SELECTION_v1.json')
selected = lambda m: sorted(n for n,v in m['tests'].items()
                     if v['classification'] == 'cpu_correctness' and not v.get('diagnostic_only',False))
assert selected(oldselector) == selected(reviewed) and len(selected(reviewed)) == 19
remote = E/'downloaded/evidence'
remote_seal = read(remote/'REMOTE_INTEGRITY.json')
assert all(sha(remote/p) == h for p,h in remote_seal.items())
assert {str(p.relative_to(remote)) for p in remote.rglob('*') if p.is_file()} == set(remote_seal)|{'REMOTE_INTEGRITY.json'}
assert sha(E/'reviewed_source.tar.gz') == '03de3a45743206244c480195de4629b8d440139f0fc5e236981f1f9cecac7fa5'
assert sha(E/'validation_evidence.tar.gz') == '46dc7fc6bd00b95125995f1e8427a07dc714750976e5ae373462f6cfc059989e'
old = ROOT/'results/raw/cpu_gpu_blocker_plan_20261011T015333577826Z'
oldseal = read(old/'FINAL_INTEGRITY.json')
assert all(sha(old/p) == h for p,h in oldseal['evidence_sha256'].items())
freeze = ROOT/'docs/studies/cpu_gpu_comparison_v1.freeze.json'
assert sha(freeze) == TRUSTED_FREEZE_SHA256
frozen = read(freeze)['files_sha256']
assert all(sha(ROOT/p) == h for p,h in frozen.items())
inventory = {
 'modified_existing':{p:{'before':before['project_sha256'][p], 'after':sha(ROOT/p)} for p in sorted(allowed)},
 'added_project_files':{p:sha(ROOT/p) for p in sorted(new)},
 'historical_files_before':len(before['historical_results_sha256']),
 'historical_files_after_excluding_new_evidence':len(current_results),
 'historical_content_and_membership_identical':True,
 'original_project_files':len(before['project_sha256']),
 'existing_build_metadata_files_unchanged':len(before['build_metadata_sha256']),
 'trusted_anchors_count':len(anchors),'protected_80_changed_only_authorized':sorted(exceptions),
 'trusted_anchor_exceptions':policy['authorized_framework_exceptions'],
 'approved_19':selected(reviewed), 'reviewed_source_files':len(reviewed['reviewed_source_sha256']),
 'transferred_source_files':len(bundle), 'remote_sealed_members':len(remote_seal),
 'current_vs_transferred_difference':['README.md','docs/ROADMAP.md'],
 'difference_reason':'Two informational status updates after transfer; executable source149 and frozen/dependency files identical.',
 'frozen_sha256':dict(frozen, **{str(freeze.relative_to(ROOT)):sha(freeze)}),
 'production_adapter_sha256':sha(ROOT/'src/cuda/cub_sort.cu'),
 'cub_pin_sha256':sha(ROOT/'third_party/cub/UPSTREAM.json'),
 'legacy_analyzer_runner_and_guard_unchanged':all(sha(ROOT/p)==before['project_sha256'][p] for p in
 ['scripts/analyze_cpu_gpu.py','scripts/run_cpu_gpu_study.py','scripts/run_cpu_gpu_pilot.py','scripts/ctest_build_guard.py','scripts/cpu_gpu_provenance.py']),
 'protected_current_sha256':{p:sha(ROOT/p) for p in sorted(set(anchors)|set(production))},
 'project_current_sha256':{p:sha(ROOT/p) for p in sorted(bundle)},
 'build_metadata_current_sha256':{p:sha(ROOT/p) for p in before['build_metadata_sha256']},
 'historical_sha256':current_results,
}
save('PRESERVATION_VERIFIED.json',inventory)

commands=[]
for p in sorted(E.rglob('*.json')):
    if p.name == 'BEFORE.json': continue
    try: d=read(p)
    except (ValueError,OSError): continue
    if isinstance(d,dict) and 'argv' in d and 'exit_code' in d:
        commands.append({'evidence':str(p.relative_to(E)),**{k:d[k] for k in
          ['argv','cwd','started_utc','finished_utc','exit_code','scope','classification'] if k in d}})
    if p.name=='remote_environment.json':
        env=json.loads(d['stdout'].split('\nENVIRONMENT_DIAGNOSTICS_PASSED')[0])
        for row in env['commands']:
            commands.append({'evidence':str(p.relative_to(E)),'scope':'Read-only remote environment diagnostic',
                             'argv':row['argv'],'exit_code':row['exit_code']})
save('COMMAND_LEDGER.json',commands)
lines=['# Commands and execution boundaries','',
 'All paths are relative to this evidence directory unless absolute. JSON logs retain exact argv, working directories, timestamps, stdout/stderr and child exit codes. Shell recorder exit1 denotes a nonzero child, not necessarily child1. Colab CLI exit0 is not an execution-success assertion.', '',
 'No actual CTest discovery or CTest execution occurred. The static guard stopped selection. No benchmark executable was invoked in timing mode; comparison executable calls were only --describe and --resources N. remote_validate.py was prepared but never executed.', '',
 'Source/evidence edits used apply_patch or exclusive evidence writers; successful tool completion is not a test result. Initial read-only inspections and parallel-agent code inspections are listed separately in INSPECTION_COMMANDS.json; missing-path reads are retained as limitations, not passed checks.', '']
for c in commands:
    lines.extend(['- `'+shlex.join(c['argv']).replace('`','\\`')+'`',
       '  - Child exit: '+str(c['exit_code'])+'; cwd: '+str(c.get('cwd','inherited remote diagnostic cwd'))+
       '; classification: '+c.get('scope',c.get('classification','read-only diagnostic/evidence assembly; inspect referenced JSON'))+
       '; evidence: ['+c['evidence']+']('+c['evidence']+').'])
lines+=['','## Failed/blocked attempts','',
 '- git_status.json: child128; no Git metadata. Hash manifests establish source identity.',
 '- test_validation_policy.json: child1; one error among nine synthetic methods (duplicate fixture keyword). fixture_correction.json and policy_retry.json retain correction and9/9 pass. No production behavior was changed to make a test pass.',
 '- remote_static_selection.json: Colab child0 but remote traceback ValueError("unknown/missing Dart setting"). Semantic failure; no plan/discovery/tests. All3 Dart snapshots retained in downloaded/evidence; diagnostics found TLSVerify/TLSVersion and MemoryCheckCommand differences.',
 '- Optional guessed local paths cmake/parallel_metadata.cmake, include/benchmark/comparison_resources.hpp, scripts/non_timing_tests.manifest.json, tests/test_non_timing_tests.py, scripts/validation_policy.py were absent in inspection. Actual files were then located/read. No workloads involved.', '',
 'Evidence-only finalization: python3 -B assemble_final.py computes hashes, parses retained records, and writes reports; no subprocesses. seal_final.py performs final content/membership verification and writes FINAL_INTEGRITY.json. Their exact invocation and result are recorded in the final seal.']
with (E/'COMMANDS.md').open('x') as out: out.write('\n'.join(lines)+'\n')
print(json.dumps({k:inventory[k] for k in ['historical_files_before','historical_files_after_excluding_new_evidence','trusted_anchors_count','reviewed_source_files','remote_sealed_members']},indent=2))
