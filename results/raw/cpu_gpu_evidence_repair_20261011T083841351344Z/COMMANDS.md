# Commands and observed exit statuses

Working directory: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`.

No native CTest discovery/tests, configuration/build, GPU/session/resource commands or benchmark workloads were executed. Focused Python files use inert fixtures. Command strings containing `ctest` in source/JSON fixtures were parsed only, never invoked.

Some earliest read-only inspection text predates the accumulator; this gap is explicit in FINAL_AUDIT.md. All focused executions and failures are retained. Source patch operations succeeded through apply_patch, with CHANGES_VERIFIED.diff and CHANGE_INVENTORY.json as the exact resulting change record.

## 1. Initial read-only inspection orchestration failed before any shell execution: JavaScript SyntaxError: Missing initializer in const declaration (accidental object suffix on cmd string). Corrected next call; no workload ran.

Observed exit: not applicable (no shell launched).

## 2. File-only baseline capture; verified latest review seal and all protected/project/historical hashes before edits.

Observed exit: 0.

```sh
python3 -B - <<'PY'
import hashlib,json,datetime
from pathlib import Path
r=Path.cwd();p=r/'results/raw/cpu_gpu_recovery_independent_review_20261011T082542018841Z'
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=json.loads((p/'FINAL_INTEGRITY.json').read_text())
assert all(h(p/n)==v for n,v in s['evidence_sha256'].items())
prior=json.loads((p/'BASELINE.json').read_text())
assert all(h(r/n)==v for k in ['project_sha256','frozen_sha256','protected_sha256','build_metadata_sha256','results_sha256'] for n,v in prior[k].items())
e=r/'results/raw'/('cpu_gpu_evidence_repair_'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'));e.mkdir()
d=dict(prior,results_sha256={str(f.relative_to(r)):h(f) for f in sorted((r/'results').rglob('*')) if f.is_file() and not f.is_relative_to(e)},review_seal_sha256=h(p/'FINAL_INTEGRITY.json'))
(e/'BEFORE.json').write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
for n in prior['project_sha256']:
 f=e/'before_sources'/n;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes((r/n).read_bytes())
print('EVIDENCE='+str(e.relative_to(r)));print('historical',len(d['results_sha256']),'project',len(d['project_sha256']))
PY
```

## 3. Read-only actual command/result/selection schemas and diagnostic implementations.

Observed exit: 0.

```sh
python3 -B - <<'PY'
import json
from pathlib import Path
base=Path('results/raw/bounded_resume_20261011T024034091796Z/downloaded/evidence')
for p in sorted(base.rglob('*.json')):
 if any(w in p.name for w in ['selection','workspace','worker','prepared','ctest','BUILD_COMPLETE']):
  d=json.loads(p.read_text()); print(str(p),list(d) if isinstance(d,dict) else type(d).__name__)
  if isinstance(d,dict) and 'stdout' in d:print('output',d['stdout'][:300],d.get('argv'))
PY
cat tests/test_cuda_prepared_correctness.cpp
cat tests/test_parallel_workers.cpp
sed -n '1,100p' scripts/non_timing_tests.py
cat docs/CTEST_COLAB_METADATA_v2.md
```

## 4. Read-only current targets, unchanged parent classifier, actual worker/selection and workspace command schemas.

Observed exit: 0.

```sh
rg -n 'cpu_gpu_comparison|comparison_input|mab_cuda_timing|test_parallel_workers|target_link_libraries' CMakeLists.txt
cat scripts/cpu_gpu_validation_policy.py
python3 -B - <<'PY'
import json
from pathlib import Path
b=Path('results/raw/bounded_resume_20261011T024034091796Z/downloaded/evidence')
for n in ['validation_commands/actual_workers_untimed.json','cpu_release_ctest_selection.json','validation_commands/workspace_1025.json']:
 p=b/n
 if p.exists():
  d=json.loads(p.read_text()); print(n); print(d.get('stdout','') if 'stdout' in d else json.dumps({k:v for k,v in d.items() if k!='excluded'},indent=2)[:1800])
print('commandnames',[p.name for p in (b/'validation_commands').glob('*.json')])
PY
```

## 5. Read-only analysis APIs and candidate snapshot semantics; no analysis runner or timing executed.

Observed exit: 0.

```sh
sed -n '1,210p' scripts/analyze_cuda_results.py
sed -n '1,120p' scripts/run_cuda_matrix.py
sed -n '165,250p' tests/test_framework_compatibility.py
sed -n '1,90p' docs/NON_TIMING_TEST_SELECTION_v3.json
cat results/raw/cpu_gpu_recovery_independent_review_20261011T082542018841Z/INITIAL_VERIFICATION.json
```

## 6. Static inspection of existing synthetic fixture writers; no helper executed.

Observed exit: 0.

```sh
rg -n '^class|def fixture|def make|def full|def synthetic' tests/test_cpu_gpu_comparison.py
sed -n '1,145p' tests/test_cpu_gpu_comparison.py
sed -n '1,110p' tests/fixtures/cpu_gpu_provenance_reproducer.py
```

## 7. Static inspection of new validators and existing public validation/tests; no execution.

Observed exit: 0.

```sh
sed -n '240,430p' scripts/cpu_gpu_evidence.py
cat scripts/cpu_gpu_build_provenance.py
cat scripts/cpu_gpu_framework_compatibility.py
cat scripts/cpu_gpu_build_identity.py
cat tests/test_framework_compatibility.py
```

## 8. Read-only public launch and compatibility-policy inspection.

Observed exit: 0.

```sh
rg --files src | rg 'comparison_input|cpu_gpu'
sed -n '120,230p' scripts/run_cpu_gpu_pilot.py
sed -n '1,100p' docs/CPU_GPU_FRAMEWORK_COMPATIBILITY_v1.md
cat results/raw/cpu_gpu_recovery_independent_review_20261011T082542018841Z/FINAL_AUDIT.md
```

## 9. Pure manifest inspection; corrected inspection after missing default_selection key (exit 1).

Observed exit: 0.

```sh
python3 -B - <<'PY'
import json
from pathlib import Path
m=json.loads(Path('docs/NON_TIMING_TEST_SELECTION_v3.json').read_text())
print(m.keys());print(m['tests']['baselines']);print(m['build_metadata']['test_properties']['baselines']);print([n for n,v in m['tests'].items() if v['classification']=='cpu_correctness'])
PY
```

## 10. Pure AST/diff review before focused tests; no Python target execution or native compilation.

Observed exit: 0.

```sh
python3 -B - <<'PY'
import ast,difflib,hashlib,json
from pathlib import Path
root=Path.cwd();e=root/"results/raw/cpu_gpu_evidence_repair_20261011T083841351344Z"
b=json.loads((e/'BEFORE.json').read_text());inventory=[];diff=[]
paths=set(b['project_sha256'])
for directory in ['include','src','scripts','tests','cmake','third_party']:
 paths.update(str(p.relative_to(root)) for p in (root/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
paths.add('CMakeLists.txt')
for name in sorted(paths):
 p=root/name;old=e/'before_sources'/name
 if old.exists() and p.exists() and old.read_bytes()==p.read_bytes():continue
 inventory.append(name)
 if p.suffix=='.py':ast.parse(p.read_text(),filename=name)
 before=old.read_text().splitlines(True) if old.exists() else []
 diff.extend(difflib.unified_diff(before,p.read_text().splitlines(True),fromfile='before/'+name,tofile='after/'+name))
(e/'SOURCE_REVIEW.diff').write_text(''.join(diff))
(e/'SOURCE_REVIEW.json').write_text(json.dumps(dict(changed_or_added=inventory,review='Static AST and diff; tests block subprocess/shell and create inert temporary data; no CTest registration or guard changes.'),indent=2)+'\n')
print('\n'.join(inventory));print('diff lines',len(diff))
PY
```

## 11. Focused inert unit regressions only; subprocess/Popen/shell patched to raise; no CTest/build/GPU/timing.

Observed exit: 1.

```sh
python3 -B tests/test_evidence_enforcement.py -v > 'results/raw/cpu_gpu_evidence_repair_20261011T083841351344Z/evidence_tests_attempt1.log' 2>&1
repair_test_status=$?
cat 'results/raw/cpu_gpu_evidence_repair_20261011T083841351344Z/evidence_tests_attempt1.log'
exit "$repair_test_status"
```

## 12. Focused inert test file; subprocess/shell/runner invocation forbidden by mocks. No native build/discovery/timing/GPU.

Observed exit: 0.

```sh
python3 -B tests/test_evidence_enforcement.py -v > 'results/raw/cpu_gpu_evidence_repair_20261011T083841351344Z/evidence_tests_attempt2.log' 2>&1
repair_test_status=$?
cat 'results/raw/cpu_gpu_evidence_repair_20261011T083841351344Z/evidence_tests_attempt2.log'
exit "$repair_test_status"
```

## 13. Focused inert test file; subprocess/shell/runner invocation forbidden by mocks. No native build/discovery/timing/GPU.

Observed exit: 0.

```sh
python3 -B tests/test_framework_compatibility.py -v > 'results/raw/cpu_gpu_evidence_repair_20261011T083841351344Z/compatibility_attempt1.log' 2>&1
repair_test_status=$?
cat 'results/raw/cpu_gpu_evidence_repair_20261011T083841351344Z/compatibility_attempt1.log'
exit "$repair_test_status"
```

## 14. Static schema and existing focused-policy-test safety inspection.

Observed exit: 0.

```sh
rg -n 'classification|operational|report|ready' scripts/cuda_preflight.py | tail -35
rg -n 'preflight|records|build_provenance' scripts/analyze_cpu_gpu.py | head -28
cat tests/test_validation_policy.py
sed -n '1,80p' docs/ROADMAP.md
sed -n '1,65p' README.md
```

## 15. Read-only preflight classifier, resource validator, original selector safeguards and source-map contract.

Observed exit: 0.

```sh
sed -n '85,130p' scripts/cuda_preflight.py
sed -n '155,175p' scripts/cuda_preflight.py
sed -n '130,170p' scripts/analyze_cpu_gpu.py
sed -n '1,105p' scripts/non_timing_tests.py
sed -n '1,90p' scripts/cpu_gpu_protocol.py
```

## 16. Read-only protected-document membership and Git availability; Git status absent expected, no Git mutation.

Observed exit: 128.

```sh
python3 -B - <<'PY'
import json
from pathlib import Path
b=json.loads(Path('results/raw/cpu_gpu_evidence_repair_20261011T083841351344Z/BEFORE.json').read_text())
print('protected framework doc',any('CPU_GPU_FRAMEWORK_COMPATIBILITY' in n for n in b['protected_sha256']))
print('build metadata',len(b['build_metadata_sha256']))
PY
git status --short --branch
```

## 17. Focused inert Python tests only; no CTest discovery, native compiler, resource/GPU query, timings or benchmark workloads.

Observed exit: 0.

```sh
python3 -B tests/test_evidence_enforcement.py -v > 'results/raw/cpu_gpu_evidence_repair_20261011T083841351344Z/evidence_tests_attempt3.log' 2>&1
repair_test_status=$?
cat 'results/raw/cpu_gpu_evidence_repair_20261011T083841351344Z/evidence_tests_attempt3.log'
exit "$repair_test_status"
```

## 18. Focused inert Python tests only; no CTest discovery, native compiler, resource/GPU query, timings or benchmark workloads.

Observed exit: 0.

```sh
python3 -B tests/test_framework_compatibility.py -v > 'results/raw/cpu_gpu_evidence_repair_20261011T083841351344Z/compatibility_final.log' 2>&1
repair_test_status=$?
cat 'results/raw/cpu_gpu_evidence_repair_20261011T083841351344Z/compatibility_final.log'
exit "$repair_test_status"
```

## 19. Focused inert Python tests only; no CTest discovery, native compiler, resource/GPU query, timings or benchmark workloads.

Observed exit: 0.

```sh
python3 -B tests/test_validation_policy.py -v > 'results/raw/cpu_gpu_evidence_repair_20261011T083841351344Z/validation_policy_final.log' 2>&1
repair_test_status=$?
cat 'results/raw/cpu_gpu_evidence_repair_20261011T083841351344Z/validation_policy_final.log'
exit "$repair_test_status"
```

## 20. Exclusive inactive candidate creation, pure source hashes/AST and final diff; no guard activation or discovery.

Observed exit: 0.

```sh
python3 -B - <<'PY'
import ast,copy,difflib,hashlib,json,sys
from pathlib import Path
root=Path.cwd();e=root/'results/raw/cpu_gpu_evidence_repair_20261011T083841351344Z';sys.path.insert(0,str(root/'scripts'))
from cpu_gpu_protocol import source_manifest
from cpu_gpu_evidence import candidate,BASE_SELECTION_SHA256
base_path=root/'docs/NON_TIMING_TEST_SELECTION_v3.json';base=json.loads(base_path.read_text());source=source_manifest();old=base['reviewed_source_sha256']
delta=dict(added=sorted(set(source)-set(old)),removed=sorted(set(old)-set(source)),modified=sorted(n for n in set(source)&set(old) if source[n]!=old[n]))
reasons={
 'scripts/analyze_cpu_gpu.py':'Prior recovery: explicit opt-in compatibility validation in independent analyzer; unchanged in this repair.',
 'scripts/cpu_gpu_protocol.py':'Prior recovery: explicit policy dispatch; unchanged in this repair.',
 'scripts/cpu_gpu_provenance.py':'Prior recovery: protected compatibility source review dispatch; unchanged in this repair.',
 'scripts/run_cpu_gpu_pilot.py':'Prior recovery: shared prerequisite validator and binary verification; unchanged in this repair.',
 'scripts/run_cpu_gpu_study.py':'Prior recovery: explicit study-only compatibility option; unchanged in this repair.',
 'scripts/cpu_gpu_build_identity.py':'Prior recovery addition; repair now requires compiler/linker proof in addition to snapshots.',
 'scripts/cpu_gpu_framework_compatibility.py':'Prior recovery addition; repair adds strict independently pinned evidence-content validation.',
 'tests/test_framework_compatibility.py':'Prior recovery addition; unsafe positive fixture is now rejected; prior protections retained.',
 'scripts/cpu_gpu_build_provenance.py':'New offline compiler/linker graph validation; not a build or execution collector.',
 'scripts/cpu_gpu_evidence_io.py':'New verified-byte snapshot reader with strict references and JSON parsing.',
 'scripts/cpu_gpu_evidence.py':'New strict record, CPU plan, build and independent review checks; trust pin remains unset.',
 'tests/test_evidence_enforcement.py':'New inert adversarial parser regressions; not implicitly approved for CTest selection.'}
assert set(reasons)==set(delta['added']+delta['modified']+delta['removed'])
c=copy.deepcopy(base);c.update(schema_version=4,policy='non_timing_correctness_v4_candidate',review_status='pending_independent_review',base_manifest_sha256=BASE_SELECTION_SHA256,reviewed_source_sha256=source,source_delta=delta,source_change_reasons=reasons)
p=root/'docs/NON_TIMING_TEST_SELECTION_v4.candidate.json'
with p.open('x') as f:json.dump(c,f,indent=2,sort_keys=True);f.write('\n')
assert candidate(c,source)==delta
b=json.loads((e/'BEFORE.json').read_text());all_paths=set(b['project_sha256'])|set(source)|{str(p.relative_to(root)),'docs/CPU_GPU_EVIDENCE_ENFORCEMENT_v1.md'}
inventory=dict(modified=[],added=[],removed=[]);diff=[]
for name in sorted(all_paths):
 after=root/name;before=e/'before_sources'/name
 if before.exists() and after.exists() and before.read_bytes()==after.read_bytes():continue
 kind='added' if not before.exists() else 'removed' if not after.exists() else 'modified'
 inventory[kind].append(name)
 if after.suffix=='.py':ast.parse(after.read_text(),filename=name)
 diff.extend(difflib.unified_diff(before.read_text().splitlines(True) if before.exists() else [],after.read_text().splitlines(True) if after.exists() else [],fromfile='before/'+name,tofile='after/'+name))
(e/'CHANGES_FINAL.diff').write_text(''.join(diff))
(e/'SELECTION_CANDIDATE_REVIEW.json').write_text(json.dumps(dict(base_sha256=hashlib.sha256(base_path.read_bytes()).hexdigest(),candidate_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),old_source_count=len(old),current_source_count=len(source),delta=delta,reasons=reasons,approved=False,activated=False,inventory=inventory),indent=2,sort_keys=True)+'\n')
print(json.dumps(dict(old_count=len(old),current_count=len(source),delta=delta,inventory=inventory),indent=2))
PY
```

## 21. Final focused inert regressions; native subprocess/shell execution forbidden in evidence/compatibility tests; policy methods read/static/classify only.

Observed exit: 0.

```sh
python3 -B tests/test_evidence_enforcement.py -v > 'results/raw/cpu_gpu_evidence_repair_20261011T083841351344Z/evidence_tests_final.log' 2>&1
repair_test_status=$?
cat 'results/raw/cpu_gpu_evidence_repair_20261011T083841351344Z/evidence_tests_final.log'
exit "$repair_test_status"
```

## 22. Final focused inert regressions; native subprocess/shell execution forbidden in evidence/compatibility tests; policy methods read/static/classify only.

Observed exit: 0.

```sh
python3 -B tests/test_framework_compatibility.py -v > 'results/raw/cpu_gpu_evidence_repair_20261011T083841351344Z/compatibility_final2.log' 2>&1
repair_test_status=$?
cat 'results/raw/cpu_gpu_evidence_repair_20261011T083841351344Z/compatibility_final2.log'
exit "$repair_test_status"
```

## 23. Final focused inert regressions; native subprocess/shell execution forbidden in evidence/compatibility tests; policy methods read/static/classify only.

Observed exit: 0.

```sh
python3 -B tests/test_validation_policy.py -v > 'results/raw/cpu_gpu_evidence_repair_20261011T083841351344Z/validation_policy_final2.log' 2>&1
repair_test_status=$?
cat 'results/raw/cpu_gpu_evidence_repair_20261011T083841351344Z/validation_policy_final2.log'
exit "$repair_test_status"
```

## 24. Read-only established integrity manifest structure and existing file-only hashing mechanism inspection.

Observed exit: 0.

```sh
python3 -B - <<'PY'
import json
from pathlib import Path
p=Path('results/raw/cpu_gpu_recovery_independent_review_20261011T082542018841Z/FINAL_INTEGRITY.json');v=json.loads(p.read_text());print(v.keys());print(json.dumps({k:x for k,x in v.items() if k not in ['evidence_sha256','current_project_sha256','project_sha256','historical_sha256','results_sha256']},indent=2)[:5000])
PY
rg -n 'def .*integrity|FINAL_INTEGRITY|evidence_sha256|historical_unchanged' scripts | head -45
```

## 25. Read-only baseline membership and established sealing script inspection.

Observed exit: 0.

```sh
python3 -B - <<'PY'
import json
from pathlib import Path
b=json.loads(Path('results/raw/cpu_gpu_evidence_repair_20261011T083841351344Z/BEFORE.json').read_text())
print('project roots',sorted(set(Path(p).parts[0] for p in b['project_sha256'])))
print('protected roots',sorted(set(Path(p).parts[0] for p in b['protected_sha256'])))
print('metadata names',list(b['build_metadata_sha256'])[:8])
print('project count',len(b['project_sha256']))
PY
rg -n 'project_sha256|rglob|metadata' results/raw/cpu_gpu_recovery_independent_review_20261011T082542018841Z/seal_review.py
```

## 26. Static sealing conventions only; no previous seal script executed or overwritten.

Observed exit: 0.

```sh
python3 -B - <<'PY'
import json
from pathlib import Path
b=json.loads(Path('results/raw/cpu_gpu_evidence_repair_20261011T083841351344Z/BEFORE.json').read_text());print(sorted({Path(n).name for n in b['build_metadata_sha256']}))
PY
sed -n '1,38p' results/raw/cpu_gpu_recovery_independent_review_20261011T082542018841Z/seal_review.py
```

## 27. Final pure AST/diff/candidate hash refresh after stricter schema edits; initial candidate retained, v3/default selector untouched.

Observed exit: 0.

```sh
python3 -B - <<'PY'
import ast,difflib,hashlib,json,sys
from pathlib import Path
r=Path.cwd();e=r/'results/raw/cpu_gpu_evidence_repair_20261011T083841351344Z';sys.path.insert(0,str(r/'scripts'))
from cpu_gpu_protocol import source_manifest
from cpu_gpu_evidence import candidate
p=r/'docs/NON_TIMING_TEST_SELECTION_v4.candidate.json';original=p.read_bytes()
with (e/'SELECTION_CANDIDATE_INITIAL.json').open('xb') as f:f.write(original)
c=json.loads(original);c['reviewed_source_sha256']=source_manifest()
base=json.loads((r/'docs/NON_TIMING_TEST_SELECTION_v3.json').read_text())['reviewed_source_sha256'];current=c['reviewed_source_sha256']
c['source_delta']=dict(added=sorted(set(current)-set(base)),removed=sorted(set(base)-set(current)),modified=sorted(n for n in set(current)&set(base) if current[n]!=base[n]))
# This is an unapproved working-source addition from this task, not historical or frozen evidence.
p.write_text(json.dumps(c,indent=2,sort_keys=True)+'\n');candidate(c,current)
b=json.loads((e/'BEFORE.json').read_text());paths=set(b['project_sha256'])|set(current)|{str(p.relative_to(r)),'docs/CPU_GPU_EVIDENCE_ENFORCEMENT_v1.md'}
inventory=dict(added=[],modified=[],removed=[]);diff=[]
for name in sorted(paths):
 old=e/'before_sources'/name;new=r/name
 if old.exists() and new.exists() and old.read_bytes()==new.read_bytes():continue
 k='added' if not old.exists() else 'removed' if not new.exists() else 'modified';inventory[k].append(name)
 if new.suffix=='.py':ast.parse(new.read_text(),filename=name)
 diff.extend(difflib.unified_diff(old.read_text().splitlines(True) if old.exists() else [],new.read_text().splitlines(True) if new.exists() else [],fromfile='before/'+name,tofile='after/'+name))
with (e/'CHANGES_REVIEWED.diff').open('x') as f:f.writelines(diff)
with (e/'CHANGE_INVENTORY.json').open('x') as f:json.dump(inventory,f,indent=2,sort_keys=True);f.write('\n')
with (e/'SELECTION_CANDIDATE_FINAL.json').open('x') as f:json.dump(dict(path=str(p.relative_to(r)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),old_count=len(base),current_count=len(current),delta=c['source_delta'],reasons=c['source_change_reasons'],approved=False,activated=False,retained_initial_sha256=hashlib.sha256(original).hexdigest()),f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps(inventory,indent=2));print('candidate',len(current),'source files; pending; selector unchanged')
PY
```

## 28. Final static source review of all strict parser/provenance paths, no code invoked.

Observed exit: 0.

```sh
sed -n '1,240p' scripts/cpu_gpu_evidence.py
sed -n '240,420p' scripts/cpu_gpu_evidence.py
sed -n '1,165p' scripts/cpu_gpu_build_provenance.py
```

## 29. Final read-only analyzer API check; no raw analysis or workload execution.

Observed exit: 0.

```sh
sed -n '1,175p' scripts/analyze_cuda_results.py
sed -n '305,332p' scripts/analyze_cpu_gpu.py
```

## 30. Final reviewed focused synthetic regressions only; no CTest/build/GPU/resource commands or timing trials.

Observed exit: 0.

```sh
python3 -B tests/test_evidence_enforcement.py -v > 'results/raw/cpu_gpu_evidence_repair_20261011T083841351344Z/evidence_tests_reviewed.log' 2>&1
repair_test_status=$?
cat 'results/raw/cpu_gpu_evidence_repair_20261011T083841351344Z/evidence_tests_reviewed.log'
exit "$repair_test_status"
```

## 31. Final reviewed focused synthetic regressions only; no CTest/build/GPU/resource commands or timing trials.

Observed exit: 0.

```sh
python3 -B tests/test_framework_compatibility.py -v > 'results/raw/cpu_gpu_evidence_repair_20261011T083841351344Z/compatibility_reviewed.log' 2>&1
repair_test_status=$?
cat 'results/raw/cpu_gpu_evidence_repair_20261011T083841351344Z/compatibility_reviewed.log'
exit "$repair_test_status"
```

## 32. Final reviewed focused synthetic regressions only; no CTest/build/GPU/resource commands or timing trials.

Observed exit: 0.

```sh
python3 -B tests/test_validation_policy.py -v > 'results/raw/cpu_gpu_evidence_repair_20261011T083841351344Z/validation_policy_reviewed.log' 2>&1
repair_test_status=$?
cat 'results/raw/cpu_gpu_evidence_repair_20261011T083841351344Z/validation_policy_reviewed.log'
exit "$repair_test_status"
```

## 33. Pure protected anchor field discovery for sealing.

Observed exit: 0.

```sh
python3 -B - <<'PY'
import json
from pathlib import Path
for n in ['docs/CPU_GPU_VALIDATION_POLICY_v2.json','docs/CPU_GPU_DRIVER_REVIEW_v1.json']:
 v=json.loads(Path(n).read_text());print(n,list(v))
 print([(k,len(x)) for k,x in v.items() if isinstance(x,dict)])
PY
```

## 34. Read-only exact trusted-anchor derivation for final preservation audit.

Observed exit: 0.

```sh
sed -n '1,105p' scripts/cpu_gpu_provenance.py
```

## 35. Final pure candidate/diff refresh; earlier candidates/diffs retained. No runtime selection activation or workloads.

Observed exit: 0.

```sh
python3 -B - <<'PY'
import ast,difflib,hashlib,json,sys
from pathlib import Path
r=Path.cwd();e=r/'results/raw/cpu_gpu_evidence_repair_20261011T083841351344Z';sys.path.insert(0,str(r/'scripts'))
from cpu_gpu_protocol import source_manifest
from cpu_gpu_evidence import candidate
p=r/'docs/NON_TIMING_TEST_SELECTION_v4.candidate.json';old=p.read_bytes()
with (e/'SELECTION_CANDIDATE_INTERMEDIATE.json').open('xb') as f:f.write(old)
c=json.loads(old);c['reviewed_source_sha256']=source_manifest();candidate(c,c['reviewed_source_sha256'])
p.write_text(json.dumps(c,indent=2,sort_keys=True)+'\n')
with (e/'FINAL_SELECTION.json').open('x') as f:json.dump(dict(path=str(p.relative_to(r)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),source_count=len(c['reviewed_source_sha256']),source_delta=c['source_delta'],activated=False,approved=False),f,indent=2,sort_keys=True);f.write('\n')
b=json.loads((e/'BEFORE.json').read_text());inv=json.loads((e/'CHANGE_INVENTORY.json').read_text());diff=[]
for name in sorted(inv['modified']+inv['added']):
 old=e/'before_sources'/name;after=r/name
 if after.suffix=='.py':ast.parse(after.read_text(),filename=name)
 diff.extend(difflib.unified_diff(old.read_text().splitlines(True) if old.exists() else [],after.read_text().splitlines(True),fromfile='before/'+name,tofile='after/'+name))
with (e/'CHANGES_SEALED.diff').open('x') as f:f.writelines(diff)
print('Final source diff',len(diff),'lines; inactive candidate',len(c['reviewed_source_sha256']),'source hashes')
PY
```

## 36. File-only full membership/SHA256 comparison of historical, frozen, protected, metadata and candidate; no project imports/execution.

Observed exit: 0.

```sh
python3 -B results/raw/cpu_gpu_evidence_repair_20261011T083841351344Z/verify_preservation.py
```

## 37. Read-only final current diff/AST/log verification; writes new review artifacts only, no test invocation.

Observed exit: 0.

```sh
python3 -B - <<'PY'
import ast,difflib,json,re
from pathlib import Path
r=Path.cwd();e=r/'results/raw/cpu_gpu_evidence_repair_20261011T083841351344Z';inv=json.loads((e/'CHANGE_INVENTORY.json').read_text());changes=[];methods={}
for n in sorted(inv['modified']+inv['added']):
 old=e/'before_sources'/n;after=r/n
 changes.extend(difflib.unified_diff(old.read_text().splitlines(True) if old.exists() else [],after.read_text().splitlines(True),fromfile='before/'+n,tofile='after/'+n))
 if after.suffix=='.py':ast.parse(after.read_text(),filename=n)
with (e/'CHANGES_VERIFIED.diff').open('x') as f:f.writelines(changes)
logs=['evidence_tests_reviewed.log','compatibility_reviewed.log','validation_policy_reviewed.log']
expected=[39,26,9]
for name,count in zip(logs,expected):
 text=(e/name).read_text();names=re.findall(r'^test_[^ ]+ .* \.\.\. ok$',text,re.M)
 assert len(names)==count and re.search(r'Ran '+str(count)+r' tests? in [0-9.]+s\n\nOK\s*$',text)
 methods[name]=dict(executed=count,passed=count,failed=0,errors=0,skipped=0,exit_code=0,scope='inert Python fixtures only')
initial=(e/'evidence_tests_attempt1.log').read_text()
assert 'Ran 28 tests' in initial and 'FAILED (errors=1)' in initial
with (e/'TEST_RESULTS.json').open('x') as f:json.dump(dict(final=methods,final_distinct_total=sum(expected),initial_error=dict(executed=28,passed=27,errors=1,exit_code=1,reason='duplicate missing keyword in synthetic fixture constructor'),native_or_gpu_tests_run=0),f,indent=2,sort_keys=True);f.write('\n')
print('Reviewed final diff',len(changes),'lines; 74 final focused tests passed, no skips; initial error retained')
PY
```

## 38. Read-only inspection; KeyError default_selection; corrected later; no selection or test execution.

Observed exit: 1.

```sh
python3 -B - <<'PY'
import json
from pathlib import Path
m=json.loads(Path('docs/NON_TIMING_TEST_SELECTION_v3.json').read_text())
print(m['policy']);print(len(m['cpu_build_tests']));print(m['default_selection']);print(m['tests']['baselines']);print(m['build_metadata']['test_properties']['baselines'])
PY
```

## Final sealing

File-only command: `python3 -B results/raw/cpu_gpu_evidence_repair_20261011T083841351344Z/seal_repair.py`.
The script writes SEAL_STATUS.md only after verifying all existing evidence/source/preservation checks, then creates and verifies the SHA256 member-map seal. Its observed process return is reported separately after execution; no success is inferred from a hash or planned command. FINAL_INTEGRITY.json excludes itself by convention. No project execution is imported by the sealer.
