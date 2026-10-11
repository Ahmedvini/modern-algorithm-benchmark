"""File-only preservation check. No project imports, subprocesses or workloads."""
import hashlib,json
from pathlib import Path
root=Path.cwd(); evidence=Path(__file__).resolve().parent
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()
def write(name,value):
    with (evidence/name).open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
before=json.loads((evidence/'BEFORE.json').read_text())
history={str(p.relative_to(root)):sha(p) for p in sorted((root/'results').rglob('*'))
         if p.is_file() and not p.is_relative_to(evidence)}
assert history==before['results_sha256'],'historical membership/content changed'
directories=['include','src','scripts','tests','cmake','third_party','docs']
paths=[root/n for n in ['AGENTS.md','CMakeLists.txt','README.md']]
for n in directories:paths.extend(p for p in (root/n).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
project={str(p.relative_to(root)):sha(p) for p in sorted(set(paths))}
protected_paths=[root/'CMakeLists.txt']
for n in ['include','src','third_party']:
    protected_paths.extend(p for p in (root/n).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
protected={str(p.relative_to(root)):sha(p) for p in sorted(set(protected_paths))}
assert protected==before['protected_sha256'],'protected membership/content changed'
names={'CMakeCache.txt','CTestTestfile.cmake','DartConfiguration.tcl','Makefile','compile_commands.json'}
metadata={str(p.relative_to(root)):sha(p) for p in sorted((root/'build').rglob('*')) if p.is_file() and p.name in names}
assert metadata==before['build_metadata_sha256'],'build metadata changed'
assert all(sha(root/n)==h for n,h in before['frozen_sha256'].items()),'frozen inputs changed'
changes=dict(added=sorted(set(project)-set(before['project_sha256'])),
             removed=sorted(set(before['project_sha256'])-set(project)),
             modified=sorted(n for n in set(project)&set(before['project_sha256']) if project[n]!=before['project_sha256'][n]))
assert changes==json.loads((evidence/'CHANGE_INVENTORY.json').read_text()),'unexpected source changes'
source={n:h for n,h in project.items() if n=='CMakeLists.txt' or Path(n).parts[0] in directories[:-1]}
candidate=json.loads((root/'docs/NON_TIMING_TEST_SELECTION_v4.candidate.json').read_text())
assert candidate['reviewed_source_sha256']==source,'stale candidate'
base=json.loads((root/'docs/NON_TIMING_TEST_SELECTION_v3.json').read_text())
for field in ['tests','cpu_build_tests','cuda_additional_tests','build_metadata']:
    assert candidate[field]==base[field]
default=sorted(n for n,v in base['tests'].items() if v['classification']=='cpu_correctness' and not v.get('diagnostic_only'))
assert len(default)==19
unchanged=['docs/NON_TIMING_TEST_SELECTION_v3.json','scripts/non_timing_tests.py','scripts/ctest_build_guard.py',
           'docs/CPU_GPU_VALIDATION_POLICY_v2.json','scripts/cpu_gpu_validation_policy.py',
           'docs/CPU_GPU_FRAMEWORK_COMPATIBILITY_v1.json','scripts/run_cpu_gpu_pilot.py','scripts/run_cpu_gpu_study.py',
           'scripts/analyze_cpu_gpu.py','scripts/cpu_gpu_provenance.py','third_party/cub/UPSTREAM.json']
assert all(sha(root/n)==before['project_sha256'][n] for n in unchanged)
matrix=json.loads((root/'docs/studies/cpu_gpu_comparison_v1.matrix.json').read_text())
anchors={n:sha(root/n) for n in matrix['source_at_freeze_sha256']}
assert len(anchors)==26 and all(h==before['project_sha256'][n] for n,h in anchors.items())
review=root/'results/raw/cpu_gpu_recovery_independent_review_20261011T082542018841Z'
assert sha(review/'FINAL_INTEGRITY.json')==before['review_seal_sha256']
seal=json.loads((review/'FINAL_INTEGRITY.json').read_text())
assert all(sha(review/n)==h for n,h in seal['evidence_sha256'].items())
write('FINAL_PRESERVATION.json',dict(
    historical=dict(before_count=len(before['results_sha256']),after_count=len(history),exact_membership_and_sha256_match=True,changed=[],added=[],removed=[]),
    protected=dict(before_count=len(before['protected_sha256']),after_count=len(protected),exact_membership_and_sha256_match=True),
    build_metadata=dict(before_count=len(before['build_metadata_sha256']),after_count=len(metadata),exact_membership_and_sha256_match=True),
    frozen=dict(count=len(before['frozen_sha256']),sha256=before['frozen_sha256'],unchanged=True),
    anchors=dict(count=len(anchors),sha256=anchors,unchanged_since_task_start=True,
                 original_freeze_differences=sorted(n for n,h in anchors.items() if h!=matrix['source_at_freeze_sha256'][n])),
    project=dict(before_count=len(before['project_sha256']),after_count=len(project),changes=changes,sha256=project),
    exact_default_19=default,unchanged_guard_and_policy_sha256={n:sha(root/n) for n in unchanged},
    candidate=dict(approved=False,activated=False,source_count=len(source),sha256=sha(root/'docs/NON_TIMING_TEST_SELECTION_v4.candidate.json')),
    previous_review_seal_verified=True,policy_authority_installed=False,actual_build_provenance_established=False,
    benchmark_trials=0,warmups=0,gpu_commands=0,ctest_discovery=0,native_tests=0,builds=0))
print(json.dumps(dict(historical_unchanged=len(history),protected_unchanged=len(protected),
      build_metadata_unchanged=len(metadata),anchors_unchanged=len(anchors),frozen_unchanged=len(before['frozen_sha256']),
      project_before=len(before['project_sha256']),project_after=len(project),candidate_source_count=len(source))))
