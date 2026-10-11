# Independent review commands

Repository cwd: /home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark

All recorded shell commands exited0. Review scope: reading, AST parsing, hashing and new evidence creation.
Zero test/CTest/discovery/build/configure/prerequisite/resource/GPU/session/benchmark commands were executed.
Commands mentioning such operations inside read files or retained JSON are inspected historical records, not executed commands.
New evidence scripts and COMMAND_RECORDS.json were added using apply_patch, with successful tool status, confined to this new directory.
No implementation, historical evidence or frozen-input edits occurred.
Some large inspection displays were truncated; targeted reads and independent structured comparisons were used. Omitted display text is not treated as proof of source review.

## 1

- Exit: 0
- Safety/purpose: Initial read-only repository/evidence identity inspection, before command ledger.

~~~~~~~~sh
pwd
cat results/raw/cpu_gpu_recovery_20261011T075800444473Z/FINAL_AUDIT.md
cat results/raw/cpu_gpu_recovery_20261011T075800444473Z/COMMANDS.md
cat results/raw/cpu_gpu_recovery_20261011T075800444473Z/FINAL_INTEGRITY.json
~~~~~~~~

## 2

- Exit: 0
- Safety/purpose: Read-only evidence listing and complete numbered new compatibility/identity modules.

~~~~~~~~sh
ls results/raw/cpu_gpu_recovery_20261011T075800444473Z && nl -ba scripts/cpu_gpu_framework_compatibility.py && nl -ba scripts/cpu_gpu_build_identity.py
~~~~~~~~

## 3

- Exit: 0
- Safety/purpose: Read-only complete project instructions, recovery audit, inventory and commands.

~~~~~~~~sh
cat AGENTS.md; cat results/raw/cpu_gpu_recovery_20261011T075800444473Z/FINAL_AUDIT.md; cat results/raw/cpu_gpu_recovery_20261011T075800444473Z/CHANGE_INVENTORY.json; cat results/raw/cpu_gpu_recovery_20261011T075800444473Z/COMMANDS.md
~~~~~~~~

## 4

- Exit: 0
- Safety/purpose: Read-only schema/inventory summaries, versioned policy and recorded source diff; targeted rereads address tool display truncation.

~~~~~~~~sh
python3 -B - <<'PY'
import json
from pathlib import Path
p=Path('results/raw/cpu_gpu_recovery_20261011T075800444473Z')
for n in ['FINAL_INTEGRITY.json','BEFORE.json','PRESERVATION_VERIFIED.json','OFFLINE_VERIFICATION.json']:
 d=json.loads((p/n).read_text())
 print(n, {k:(len(v) if isinstance(v,(dict,list)) else v) for k,v in d.items()})
PY
cat docs/CPU_GPU_FRAMEWORK_COMPATIBILITY_v1.json
cat docs/CPU_GPU_FRAMEWORK_COMPATIBILITY_v1.md
cat results/raw/cpu_gpu_recovery_20261011T075800444473Z/CHANGES_FINAL.diff
~~~~~~~~

## 5

- Exit: 0
- Safety/purpose: Independent byte-hash verification and exclusive review evidence creation; no workloads.

~~~~~~~~sh
python3 -B - <<'PY'
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone
root=Path.cwd(); old=root/'results/raw/cpu_gpu_recovery_20261011T075800444473Z'
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def compare(m):
 return [n for n,h in m.items() if not (root/n).is_file() or digest(root/n)!=h]
seal=json.loads((old/'FINAL_INTEGRITY.json').read_text()); before=json.loads((old/'BEFORE.json').read_text())
print('seal keys',list(seal)); print('evidence first keys',list(seal['evidence_sha256'])[:4])
checks={}
for k in ['historical_results_sha256','frozen_sha256','protected_sha256','build_metadata_sha256']:
 checks[k]={'count':len(before[k]),'differences':compare(before[k])}
checks['project_after_sha256']={'count':len(seal['project_after_sha256']),'differences':compare(seal['project_after_sha256'])}
checks['recovery_evidence']={'count':len(seal['evidence_sha256']),'differences':[]}
for n,h in seal['evidence_sha256'].items():
 p=old/n
 if not p.is_file() or digest(p)!=h:checks['recovery_evidence']['differences'].append(n)
allresults={str(p.relative_to(root)):digest(p) for p in sorted((root/'results').rglob('*')) if p.is_file()}
checks['results_start_count']=len(allresults)
e=root/'results/raw'/('cpu_gpu_recovery_independent_review_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
e.mkdir(exist_ok=False)
(e/'BASELINE.json').write_text(json.dumps({'results_sha256':allresults,'project_sha256':seal['project_after_sha256'],'frozen_sha256':before['frozen_sha256'],'protected_sha256':before['protected_sha256'],'build_metadata_sha256':before['build_metadata_sha256'],'recovery_seal_sha256':digest(old/'FINAL_INTEGRITY.json')},indent=2,sort_keys=True)+'\n')
(e/'INITIAL_VERIFICATION.json').write_text(json.dumps(checks,indent=2,sort_keys=True)+'\n')
print(json.dumps(checks,indent=2)); print('REVIEW_DIR='+str(e.relative_to(root)))
PY
~~~~~~~~

## 6

- Exit: 0
- Safety/purpose: Read-only numbered production validation/launch/analyzer and parent-policy control-flow inspection.

~~~~~~~~sh
nl -ba scripts/cpu_gpu_protocol.py | sed -n '1,150p'; nl -ba scripts/cpu_gpu_provenance.py | sed -n '1,160p'; nl -ba scripts/run_cpu_gpu_study.py; nl -ba scripts/run_cpu_gpu_pilot.py | sed -n '1,280p'
~~~~~~~~

## 7

- Exit: 0
- Safety/purpose: Read-only numbered production validation/launch/analyzer and parent-policy control-flow inspection.

~~~~~~~~sh
nl -ba scripts/analyze_cpu_gpu.py | sed -n '1,210p'; nl -ba scripts/cpu_gpu_validation_policy.py | sed -n '1,230p'; cat docs/CPU_GPU_VALIDATION_POLICY_v2.json
~~~~~~~~

## 8

- Exit: 0
- Safety/purpose: Read-only complete prerequisite/launch and analyzer metadata integration inspection, after combined-output truncation.

~~~~~~~~sh
nl -ba scripts/run_cpu_gpu_pilot.py | sed -n '73,270p'; nl -ba scripts/analyze_cpu_gpu.py | sed -n '55,115p'
~~~~~~~~

## 9

- Exit: 0
- Safety/purpose: Static selector, path/pre-discovery guard and prerequisite caller inspection; no module import or CTest.

~~~~~~~~sh
nl -ba scripts/non_timing_tests.py | sed -n '1,245p'; nl -ba scripts/ctest_build_guard.py | sed -n '1,255p'; rg -n 'selected_ctest|pre_discovery_gate|non_timing_tests|framework.compatibility|validate_prerequisites' scripts/validate_cpu_gpu_pilot.py scripts/run_cpu_gpu_study.py scripts/run_cpu_gpu_pilot.py
~~~~~~~~

## 10

- Exit: 0
- Safety/purpose: Read-only inspection of all 26 inert methods, nine existing policy methods and their fixture/mocking behavior; no tests run.

~~~~~~~~sh
nl -ba tests/test_framework_compatibility.py | sed -n '1,155p'; nl -ba tests/test_framework_compatibility.py | sed -n '156,310p'; nl -ba tests/test_validation_policy.py
~~~~~~~~

## 11

- Exit: 0
- Safety/purpose: AST-only method inventory and retained raw-log comparison; no project import or test execution. Writes new review LOG_REVIEW.json.

~~~~~~~~sh
python3 -B - <<'PY'
import ast,json,re,hashlib
from pathlib import Path
root=Path.cwd();old=root/'results/raw/cpu_gpu_recovery_20261011T075800444473Z'
report={}
for source,log in [('tests/test_framework_compatibility.py','final_identity_hardening_tests.json'),('tests/test_validation_policy.py','existing_validation_policy_tests.json')]:
 tree=ast.parse((root/source).read_text())
 methods=sorted(n.name for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_'))
 record=json.loads((old/log).read_text());text=record.get('stdout','')+'\n'+record.get('stderr','')
 observed=re.findall(r'(?m)^(test_\w+) \([^\n]+\) \.\.\. ok$',text)
 report[source]={'source_sha256':hashlib.sha256((root/source).read_bytes()).hexdigest(),'log':log,'argv':record.get('argv'),'exit_code':record.get('exit_code'),'source_methods':methods,'logged_passes':observed,'method_count':len(methods),'logged_pass_count':len(observed),'missing':sorted(set(methods)-set(observed)),'unexpected':sorted(set(observed)-set(methods)),'summary':re.findall(r'Ran \d+ tests[^\n]*|(?m:^OK[^\n]*$)',text)}
for n in ['focused_compatibility_tests.json','focused_compatibility_tests_v2.json','focused_compatibility_tests_v3.json','focused_compatibility_tests_final.json']:
 d=json.loads((old/n).read_text()); text=d.get('stdout','')+'\n'+d.get('stderr','');report[n]={'exit_code':d.get('exit_code'),'summary':re.findall(r'Ran \d+ tests[^\n]*|FAILED[^\n]*|(?m:^OK[^\n]*$)',text),'ok_methods':len(re.findall(r'(?m)^test_.* \.\.\. ok$',text)),'fixture_error':sorted(set(re.findall(r'TypeError:[^\n]*',text)))}
print(json.dumps(report,indent=2))
Path('results/raw/cpu_gpu_recovery_independent_review_20261011T082542018841Z/LOG_REVIEW.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
PY
~~~~~~~~

## 12

- Exit: 0
- Safety/purpose: Read-only frozen scope, prior blockers, documented prerequisite selection, and preservation/seal implementation inspection.

~~~~~~~~sh
cat docs/CPU_GPU_COMPARISON_PROTOCOL_v1.md; cat results/raw/cpu_gpu_final_preflight_20261011T074147349659Z/FINAL_AUDIT.md; nl -ba scripts/validate_cpu_gpu_pilot.py | sed -n '1,160p'; cat results/raw/cpu_gpu_recovery_20261011T075800444473Z/verify_recovery.py; cat results/raw/cpu_gpu_recovery_20261011T075800444473Z/finalize_recovery.py
~~~~~~~~

## 13

- Exit: 0
- Safety/purpose: Targeted reread after truncated combined inspection; prerequisite paths, exact inventory/seal mechanism, protocol launch constraints, previous audit.

~~~~~~~~sh
nl -ba scripts/validate_cpu_gpu_pilot.py | sed -n '15,130p'; sed -n '1,85p' results/raw/cpu_gpu_recovery_20261011T075800444473Z/finalize_recovery.py; sed -n '260,380p' docs/CPU_GPU_COMPARISON_PROTOCOL_v1.md; cat results/raw/cpu_gpu_final_preflight_20261011T074147349659Z/FINAL_AUDIT.md
~~~~~~~~

## 14

- Exit: 0
- Safety/purpose: Independent source-map, exact diff, frozen/approved anchor, selection and prior seal reconstruction with standard-library file operations only.

~~~~~~~~sh
python3 -B - <<'PY'
import json,hashlib,ast,difflib
from pathlib import Path
root=Path.cwd(); e=root/'results/raw/cpu_gpu_recovery_independent_review_20261011T082542018841Z';old=root/'results/raw/cpu_gpu_recovery_20261011T075800444473Z'
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
before=read(old/'BEFORE.json');seal=read(old/'FINAL_INTEGRITY.json');inv=read(old/'CHANGE_INVENTORY.json')
paths=[root/n for n in ['AGENTS.md','README.md','CMakeLists.txt']]
for directory in ['cmake','docs','include','scripts','src','tests','third_party']:
 paths.extend(p for p in (root/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
project={str(p.relative_to(root)):h(p) for p in sorted(set(paths))}
modified=sorted(p for p,v in before['project_sha256'].items() if p in project and project[p]!=v)
added=sorted(set(project)-set(before['project_sha256']));removed=sorted(set(before['project_sha256'])-set(project))
diff=[];oldcopies={}
for p in modified+added:
 raw=(old/'before_sources'/p).read_text() if p in modified else ''
 if p in modified:oldcopies[p]=(h(old/'before_sources'/p)==before['project_sha256'][p])
 diff.extend(difflib.unified_diff(raw.splitlines(True),(root/p).read_text().splitlines(True),fromfile='before/'+p,tofile='after/'+p))
manifest=read(root/'docs/NON_TIMING_TEST_SELECTION_v3.json');snapshot=manifest['reviewed_source_sha256']
paths=[root/'CMakeLists.txt']
for directory in ['include','src','scripts','tests','cmake','third_party']:
 paths.extend(p for p in (root/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
source={str(p.relative_to(root)):h(p) for p in sorted(set(paths))}
selected=sorted(n for n,t in manifest['tests'].items() if t['classification']=='cpu_correctness' and not t.get('diagnostic_only',False))
freeze=read(root/'docs/studies/cpu_gpu_comparison_v1.freeze.json');model=read(root/'docs/studies/cpu_gpu_comparison_v1.matrix.json')
policy=read(root/'docs/CPU_GPU_FRAMEWORK_COMPATIBILITY_v1.json');parent=read(root/'docs/CPU_GPU_VALIDATION_POLICY_v2.json')
original_differences={p:{'frozen':v,'current':h(root/p)} for p,v in model['source_at_freeze_sha256'].items() if h(root/p)!=v}
pin=read(root/'third_party/cub/UPSTREAM.json')
sealmembers={str(p.relative_to(old)):h(p) for p in old.rglob('*') if p.is_file() and p.name!='FINAL_INTEGRITY.json'}
prior=root/'results/raw/cpu_gpu_final_preflight_20261011T074147349659Z'
priorseal=read(prior/'FINAL_INTEGRITY.json')
result={'inventory':{'before':len(before['project_sha256']),'after':len(project),'modified':modified,'added':added,'removed':removed,'matches_recorded':modified==inv['modified'] and added==inv['added'] and removed==inv['removed'],'old_source_copies_match':oldcopies,'reconstructed_diff_matches':''.join(diff)==(old/'CHANGES_FINAL.diff').read_text(),'project_map_matches_seal':project==seal['project_after_sha256']},'selection':{'manifest':'docs/NON_TIMING_TEST_SELECTION_v3.json','manifest_sha256':h(root/'docs/NON_TIMING_TEST_SELECTION_v3.json'),'manifest_choices':sorted(str(p.relative_to(root)) for p in (root/'docs').glob('NON_TIMING_TEST_SELECTION*')),'snapshot_count':len(snapshot),'current_source_count':len(source),'modified':sorted(p for p,v in snapshot.items() if p in source and source[p]!=v),'added':sorted(set(source)-set(snapshot)),'removed':sorted(set(snapshot)-set(source)),'snapshot_matches_before':all(before['project_sha256'].get(p)==v for p,v in snapshot.items()),'selected_cpu_count':len(selected),'selected_cpu_names':selected,'guard_will_reject_before_discovery':snapshot!=source},'frozen':{'files_sha256':{p:h(root/p) for p in before['frozen_sha256']},'matches_freeze':all(h(root/p)==v for p,v in freeze['files_sha256'].items()),'source_anchor_count':len(model['source_at_freeze_sha256']),'original_anchor_differences':original_differences,'exact_three_exceptions':set(original_differences)==set(policy['authorized_framework_exceptions']),'current_exception_digests_match':all(h(root/p)==v['after_sha256'] for p,v in policy['authorized_framework_exceptions'].items()),'parent_exceptions_identical':policy['authorized_framework_exceptions']==parent['authorized_framework_exceptions'],'policy_hash':h(root/'docs/CPU_GPU_FRAMEWORK_COMPATIBILITY_v1.json'),'cub_pin':pin},'evidence':{'recovery_seal_exact_member_map':sealmembers==seal['evidence_sha256'],'recovery_members_excluding_seal':len(sealmembers),'previous_seal_matches_baseline':h(prior/'FINAL_INTEGRITY.json')==before['verified_prior_seal_sha256'],'previous_seal_member_count':len(priorseal['evidence_sha256']),'previous_seal_member_differences':[p for p,v in priorseal['evidence_sha256'].items() if h(prior/p)!=v]}}
(e/'STATIC_REVIEW.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps(result,indent=2))
PY
~~~~~~~~

## 15

- Exit: 0
- Safety/purpose: Read-only documentation/metric separation, retained authentication outcome and historical validation references.

~~~~~~~~sh
nl -ba docs/CPU_GPU_FRAMEWORK_COMPATIBILITY_v1.md | sed -n '1,110p'; nl -ba docs/CPU_GPU_VALIDATION_POLICY_v2.md | sed -n '1,100p'; nl -ba README.md | tail -n 18; nl -ba docs/ROADMAP.md | tail -n 23; rg -n 'primary|prepared|ratio|median|host_call' scripts/analyze_cpu_gpu.py | tail -n 30; cat results/raw/cpu_gpu_recovery_20261011T075800444473Z/session_auth_attempt.json; cat results/raw/cpu_gpu_recovery_20261011T075800444473Z/OFFLINE_VERIFICATION.json
~~~~~~~~

## 16

- Exit: 0
- Safety/purpose: Targeted read-only metric aggregation, independent-context policy contract, seven-file documentation append and non-source-map audit observations.

~~~~~~~~sh
nl -ba scripts/analyze_cpu_gpu.py | sed -n '300,390p'; nl -ba docs/CPU_GPU_VALIDATION_POLICY_v2.md | sed -n '30,63p'; tail -n 13 README.md; tail -n 18 docs/ROADMAP.md; python3 -B - <<'PY'
import json
from pathlib import Path
p=Path('results/raw/cpu_gpu_recovery_20261011T075800444473Z')
for n in ['session_auth_attempt.json','OFFLINE_VERIFICATION.json']:
 d=json.loads((p/n).read_text())
 if n=='OFFLINE_VERIFICATION.json':d.pop('compatibility_review',None)
 print(n,json.dumps(d,indent=2))
PY
~~~~~~~~

## 17

- Exit: 0
- Safety/purpose: Read-only retained build-identity location, resource validation, prepared/primary separation and context/launch scope.

~~~~~~~~sh
rg --files results/raw/bounded_resume_20261011T024034091796Z | rg '(BUILD_COMPLETE|VALIDATION_CONTEXT|CORRECTNESS_BUNDLE)'; nl -ba scripts/analyze_cpu_gpu.py | sed -n '1,55p'; nl -ba scripts/analyze_cpu_gpu.py | sed -n '210,298p'; nl -ba scripts/cpu_gpu_validation_policy.py | sed -n '44,91p'; sed -n '245,307p' docs/CPU_GPU_COMPARISON_PROTOCOL_v1.md
~~~~~~~~

## 18

- Exit: 0
- Safety/purpose: Static AST extraction of literal trust pins and retained build-manifest inspection; no imports/executable use.

~~~~~~~~sh
python3 -B - <<'PY'
import ast,json,hashlib
from pathlib import Path
root=Path.cwd()
def constants(p):
 out={}
 for n in ast.parse(p.read_text()).body:
  if isinstance(n,ast.Assign) and isinstance(n.value,ast.Constant):
   for t in n.targets:
    if isinstance(t,ast.Name):out[t.id]=n.value.value
 return out
pairs=[('scripts/cpu_gpu_framework_compatibility.py','TRUSTED_COMPATIBILITY_SHA256','docs/CPU_GPU_FRAMEWORK_COMPATIBILITY_v1.json'),('scripts/cpu_gpu_validation_policy.py','TRUSTED_POLICY_SHA256','docs/CPU_GPU_VALIDATION_POLICY_v2.json'),('scripts/cpu_gpu_provenance.py','TRUSTED_FREEZE_SHA256','docs/studies/cpu_gpu_comparison_v1.freeze.json'),('scripts/cpu_gpu_provenance.py','TRUSTED_CMAKE_REVIEW_SHA256','docs/CPU_GPU_DRIVER_REVIEW_v1.json')]
result={}
for module,key,file in pairs:
 literal=constants(root/module)[key];actual=hashlib.sha256((root/file).read_bytes()).hexdigest()
 result[file]={'literal_pin':literal,'actual_sha256':actual,'matches':literal==actual}
p=root/'results/raw/bounded_resume_20261011T024034091796Z/downloaded/evidence/BUILD_COMPLETE.json'
d=json.loads(p.read_text())
result['retained_build']={'path':str(p.relative_to(root)),'top_level_keys':list(d),'comparison_input_text_present':'comparison_input' in p.read_text(),'comparison_input_identity_present':'input_tool_sha256' in p.read_text()}
print(json.dumps(result,indent=2))
(root/'results/raw/cpu_gpu_recovery_independent_review_20261011T082542018841Z/TRUST_AND_BUILD_REVIEW.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
PY
~~~~~~~~

## 19

- Exit: 0
- Safety/purpose: Exclusive new review audit creation only; no implementation/historical changes or workloads.

~~~~~~~~sh
python3 -B - <<'PY'
from pathlib import Path
p=Path("results/raw/cpu_gpu_recovery_independent_review_20261011T082542018841Z")/'FINAL_AUDIT.md'
with p.open('x') as f: f.write("# Independent review of CPU/GPU recovery\n\n**Verdict: NO-GO.** This is an independent source/evidence review, not a prerequisite validation or study authorization. No tests, CTest discovery, configure/build, resource probes, Colab/GPU commands, sorting workloads, timing samples, pilots, warmups or study trials ran during this review. Only read-only inspection, AST parsing, byte hashing, and additive review-evidence writes occurred.\n\nReviewed recovery: results/raw/cpu_gpu_recovery_20261011T075800444473Z/.\nThis review's directory is recorded in COMMANDS.md. Existing implementation and historical evidence were not edited.\n\n## Gate table\n\n| Gate | Status | Independent finding |\n| --- | --- | --- |\n| Exact three-file compatibility exception and frozen adapter/CUB anchors | PASS | Pinned policy, parent policy, old CMake review and freeze hashes match actual bytes. Exceptions are exactly CMakeLists.txt, include/benchmark/cuda_timing.hpp, src/cuda/cub_timing.cu. Other frozen anchors remain authoritative. |\n| Full prerequisite evidence enforcement / independent context | FAIL | Nine framework files are hashed without parsing their content; coverage assertions and session identity can be self-consistent without independently verified coverage. Existing passing public-validator fixtures demonstrate placeholder acceptance. |\n| Existing path-identity / pre-discovery selector implementation | PASS | Exact implementation hashes unchanged; static gate remains before discovery and retains guard-approved absolute path through discovery, selection and execution rechecks. No discovery was invoked here. |\n| Current source snapshot admitted by approved 19-test selector | BLOCKED | v3 still describes 150 files; current source has 153, with five modified and three added. Exact equality rejects before discovery. No updated v4 selection snapshot exists. |\n| Recorded 26 new / 9 existing regression methods | PASS | Raw logs show exit0, every current method name exactly once as ok, 26/26 and 9/9. This verifies retained reports and source correspondence, not fresh execution or complete safety. |\n| comparison_input missing/stale/mismatch enforcement relative to a captured snapshot | PASS | Actual files/paths are rehashed at launch and completion; missing entry/file, changed bytes and mismatched paths have retained inert regression coverage. |\n| Intended build provenance and actual comparison_input identity | BLOCKED | Hash capture is not source-to-binary build proof; current intended remote executable is unavailable. Retained BUILD_COMPLETE.json does not contain comparison_input or input_tool_sha256. |\n| Project/frozen/build/historical preservation | PASS | Recovery seal and inventories independently reconstructed; final review preservation is in FINAL_INTEGRITY.json. No count-only preservation claim. |\n| Current T4 and identity-matched GPU/framework validation | BLOCKED | No new session/GPU validation attempted. Recovery's recorded session inventory reports no active sessions. Current availability is not independently probed here. |\n| Full-study eligibility / launch | BLOCKED | Evidence enforcement, approved selection snapshot and current environment/build/coverage gates remain open. No launch authorized or attempted. |\n\n## Finding 1 — coverage content is not enforced by the new public validation path\n\nscripts/cpu_gpu_framework_compatibility.py:100-110 checks each framework reference's safe path and digest and constructs a hash map. It never reads/parses those nine record bodies. At :111-116 it builds classification context, including session_id copied from the same prerequisite document, and calls classify on the nested framework_validation assertions.\n\nscripts/cpu_gpu_validation_policy.py:46-85 expects independent context and checks the asserted status/counts against policy and record hashes. It does not parse raw records. This is consistent with its documented limited classifier role, but the new launch integration provides no independently trusted assembler/review decision enforcing the underlying results. The parent documentation explicitly requires the assembler to parse actual command logs (docs/CPU_GPU_VALIDATION_POLICY_v2.md:35-40).\n\nThe existing positive fixture is concrete evidence of the gap:\n- tests/test_framework_compatibility.py:58-74 uses placeholder CPU Release/sanitizer/preflight command output.\n- :75-86 creates all nine framework files containing only synthetic_fixture and gate, then supplies separate passing coverage assertions.\n- :94-97 calls the actual runner.validate_prerequisites.\n- :138-139 requires that production validator to accept this data.\n- :245-268 also reaches analyzer.validate_study_metadata; only the environment gate is mocked there.\n\nThe retained final_identity_hardening_tests.json records both positive methods passing. No new reproducer or tests ran during this review. Static tracing shows an otherwise self-consistent reference to a malformed or failed framework body is not inspected; existing negative tests mutate coverage assertions or leave stale hashes, not a failed body with recomputed consistent hashes.\n\nThe legacy CPU command records are checked only for successful command status/exit and hash in scripts/run_cpu_gpu_pilot.py:118-127 and scripts/analyze_cpu_gpu.py:92-100. Their command arguments, guarded selection plan, discovered/selected test identities and actual test counts are not bound to the claimed 21-test coverage. Thus the selector itself remains fail-closed, but the new prerequisite path does not prove that accepted CPU evidence went through that selector. The current source-snapshot rejection does not automatically prevent someone supplying purported full prerequisites directly to the launch validator.\n\nThe new code does additionally parse CUDA framework output and production correctness at compatibility.py:121-146. Those checks, exact adapter anchors, explicit policy agreement and the CLI execution latch remain intact. This finding is not a claim that a real study was launched or that frozen adapters can be changed. It is a remaining evidence-enforcement weakness, partly inherited from the legacy prerequisite validator, which passing metadata tests do not close.\n\nRequired repair/review: validate raw record schemas and outcomes for every required gate, or require an independently protected, reviewed assembly decision binding the raw outputs, exact guarded CPU selection, session, source and build identities. Add negative fixtures with failed/malformed/wrong-selection record bodies and all consistency hashes recomputed. Preserve historical evidence classification and reject unsupported evidence. Do not create timing evidence under this review.\n\n## Finding 2 — the 19-test rejection is intentional and precisely attributable\n\nscripts/non_timing_tests.py:31-33 requires reviewed_source_sha256 == source_manifest(). Its active manifest remains docs/NON_TIMING_TEST_SELECTION_v3.json, SHA256 fef39034b063c36dabc3eccf9dc6a162ebcf6a4e5cb44abeda83e93fbcf1a434.\n\nIndependent file hashing reproduces:\n- Snapshot150 / current153.\n- Modified: scripts/analyze_cpu_gpu.py, scripts/cpu_gpu_protocol.py, scripts/cpu_gpu_provenance.py, scripts/run_cpu_gpu_pilot.py, scripts/run_cpu_gpu_study.py.\n- Added: scripts/cpu_gpu_build_identity.py, scripts/cpu_gpu_framework_compatibility.py, tests/test_framework_compatibility.py.\n- Removed: none.\n\nREADME/ROADMAP and the two new documentation files are not in source_manifest's source directories. No NON_TIMING_TEST_SELECTION_v4.json or other updated selection manifest was found. The current source map in the compatibility review is not an approved selection snapshot.\n\nThe exact unchanged default selection is:\nbaselines, cli, comparisons, cpu_gpu_comparison_framework, cuda_benchmark_analysis, cuda_preflight, cuda_sort_handoff, datasets, environment_manifest, memory, memory_unsupported, mergesort, metrics_cli, pdqsort, quicksort, radixsort, searching, structures, timsort.\n\nBoth scripts/non_timing_tests.py and scripts/ctest_build_guard.py, their v3 manifest, old policy and test registrations have unchanged recovery-baseline hashes. pre_discovery_gate calls load_manifest before build validation; selected_ctest retains guard['build_dir'] at :141-144, compares metadata after discovery and rechecks immediately before execution (:146-152). CLI and direct selection also use the gate. No path-identity or pre-discovery protection was weakened by this recovery.\n\nResolution is a separately reviewed additive snapshot after source/evidence fixes, preserving these exact19 defaults and timing exclusions. Do not disable the equality guard or overwrite v3.\n\n## Finding 3 — executable content identity is useful but not build provenance\n\nscripts/cpu_gpu_build_identity.py:24-42 checks explicit schema, frozen identity, source map, exact11-file inventory, comparison/input hashes and optionally compile-command hash. capture(:45-72) rejects missing/non-executable/aliased paths and wrong cache settings. verify(:75-79) checks canonical intended executable/input paths and compares a fresh capture with the retained snapshot.\n\nThe launcher applies verification before launch and again before completion; the analyzer binds retained comparison/input/compile digests. Tests :209-243 cover changed input bytes even with updated top-level prerequisite hash, missing document/entry/file, stale snapshots, wrong paths/symlinks, wrong configuration and source/compile mismatches. Logged passes match those current methods.\n\nLimitation: capture assigns the current source map to whatever files currently exist and accepts compile_commands.json if it is any JSON list (:68-72). The positive fixture explicitly uses inert text files and an empty list (:41-51). A newly captured snapshot therefore cannot establish that binaries were built from the reviewed source. This limitation is candidly documented in the module and compatibility guide (:68-70); it must remain a separate blocking provenance gate, not be treated as repaired by hashing alone.\n\nThe retained bounded BUILD_COMPLETE.json under results/raw/bounded_resume_20261011T024034091796Z/downloaded/evidence/ has build/source_verified/identities fields but no comparison_input identity. No actual missing remote hash was inferred or replaced. Independent build/link evidence and the exact intended comparison_input bytes remain required.\n\n## Inventory and tests\n\nAll seven modified and five added files were inspected. STATIC_REVIEW.json independently reconstructs the exact CHANGES_FINAL.diff from seven retained original copies plus current files, confirms each original copy's baseline digest, and confirms no other project change/removal. New source/policy integration requires further review because it alters full-study acceptance, despite no native algorithm changes.\n\nSeven modified: README.md; docs/ROADMAP.md; scripts/analyze_cpu_gpu.py; scripts/cpu_gpu_protocol.py; scripts/cpu_gpu_provenance.py; scripts/run_cpu_gpu_pilot.py; scripts/run_cpu_gpu_study.py.\nFive added: docs/CPU_GPU_FRAMEWORK_COMPATIBILITY_v1.json; docs/CPU_GPU_FRAMEWORK_COMPATIBILITY_v1.md; scripts/cpu_gpu_build_identity.py; scripts/cpu_gpu_framework_compatibility.py; tests/test_framework_compatibility.py.\n\nLOG_REVIEW.json records actual retained argv/exit statuses, current AST method inventory, logged method names, and summary matches. Latest26/26 and existing9/9 logs end OK with no reported failures/skips; none rerun here. The initial23-method attempt is retained with exit1,11 ok and12 errors from duplicate missing keyword arguments. The corrected23/23, then24/24 and26/26 attempts remain intact. No failures were deleted.\n\nTests block subprocess.run/Popen, os.system and runner.invoke and use inert temporary binaries. They exercise real launch prerequisite validation and analyzer metadata functions, not full orchestration. They do not test every new branch through the CLI/run loop, independently validated build provenance, underlying framework-record parsing, independently obtained session context, or current GPU execution.\n\nNative C++ sources were unchanged, so prior native observations are not erased. However the changed Python validation/analyzer/runner sources mean prior end-to-end framework and guarded-suite evidence cannot be silently relabeled as passing for this new source map. These35 focused methods are not a fresh Release/ASan/GPU regression suite.\n\nPrimary/prepared metric separation is preserved: analyze_cpu_gpu.py:195 rejects prepared backend rows in primary scope; :313-319 forms ratios only with gpu_cub_adapter host_call_e2e_ns. No metric definitions, matrix cells or production algorithms changed.\n\n## Integrity and claim boundaries\n\nIndependently verified before review:\n- Recovery seal32 members, plus its seal file33: exact member map and SHA256 match.\n- Recovery baseline12,261 historical files: every current file digest matches; those files plus33 recovery files give this review's starting12,294-result-file baseline.\n- Project188 before recovery /193 after: exactly7 changes and5 additions; no removal; reconstructed final diff identical.\n- Frozen4 files, protected80 production/header/dependency files and existing65 build-metadata files match baseline bytes.\n- All26 original frozen-anchor paths match recovery-start bytes; exactly the three approved historical framework exceptions differ from the original freeze. CUB3.0.1/CCCL f19d875da0d8bfb2e38c109b2b40522b8abbbbc3 remains unchanged.\n- Prior final-preflight seal hash and all23 member hashes match independently.\n\nFINAL_INTEGRITY.json records the after-review exact membership/hash comparisons against this review's BASELINE.json, including all12,294 pre-existing result files. No implementation, frozen input, build metadata or historical evidence file was modified during review. Only this new evidence directory was added.\n\nThe recorded no-workload claim is consistent with the recovery command inventory, inert test source and preserved artifact maps. Filesystem seals are not external attestations of remote execution or proof of unlogged activity. This review independently ran zero workloads; it did not refresh session state or verify current GPU readiness. Retained Release21/21, ASan21/21 and GPU/worker/resource claims remain historical; their existence is not a new validation PASS. Warning counts were not freshly generated or independently recounted in this review.\n\n## Prioritized recovery plan\n\n1. Repair evidence-content and independent-context binding in the compatibility launcher/analyzer path, without weakening anchors or promoting correctness-only data. Add hash-consistent adversarial record tests and preserve all stricter checks. Review that change independently.\n2. After fixes stabilize, create/review an additive source-selection snapshot preserving19 defaults, diagnostic opt-in and timing exclusions. Retain v3 unchanged. Do not execute discovery until the new snapshot and path/build guard are approved.\n3. Establish separately authorized accessible T4 environment and independently validated intended build. Record actual comparison_input and all other binary/library/metadata hashes with configure/compile/link/source evidence. Do not reuse missing or stale worker identities.\n4. Obtain only separately authorized, identity-matched bounded correctness, sanitizer, resource and worker evidence. Resolve required full GPU-framework/timing evidence explicitly; current non-timing review cannot generate it or relabel historical smoke/pilot coverage.\n5. A later independent final preflight must assess complete prerequisites and integrity before any separate study-authorization decision.\n\nStop after this review. Full-study eligibility is not established and launch is not authorized.\n")
print('Created',p)
PY
~~~~~~~~

## 20

- Exit: 0
- Safety/purpose: Create new evidence-only preservation checker; never imports project code or executes a workload.

~~~~~~~~sh
python3 -B - <<'PY'
from pathlib import Path
p=Path("results/raw/cpu_gpu_recovery_independent_review_20261011T082542018841Z")/'verify_preservation.py'
with p.open('x') as f:f.write("\"\"\"Review preservation check: standard-library file operations only.\"\"\"\nimport hashlib, json\nfrom pathlib import Path\n\nROOT = Path.cwd()\nEVIDENCE = Path(__file__).resolve().parent\ndef sha(path):\n    h = hashlib.sha256()\n    with path.open('rb') as stream:\n        for chunk in iter(lambda: stream.read(1048576), b''):\n            h.update(chunk)\n    return h.hexdigest()\ndef read(path):\n    return json.loads(path.read_text())\nbaseline = read(EVIDENCE/'BASELINE.json')\nhistorical = {str(p.relative_to(ROOT)): sha(p) for p in sorted((ROOT/'results').rglob('*'))\n              if p.is_file() and not p.is_relative_to(EVIDENCE)}\npaths = [ROOT/p for p in ['AGENTS.md', 'README.md', 'CMakeLists.txt']]\nfor directory in ['cmake','docs','include','scripts','src','tests','third_party']:\n    paths.extend(p for p in (ROOT/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts)\nproject = {str(p.relative_to(ROOT)):sha(p) for p in sorted(set(paths))}\nnames = {'CMakeCache.txt','CTestTestfile.cmake','DartConfiguration.tcl','Makefile','compile_commands.json'}\nbuild = {str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'build').rglob('*')) if p.is_file() and p.name in names}\ncomparisons = {}\nfor label, current, expected in [\n    ('historical_results',historical,baseline['results_sha256']),\n    ('project',project,baseline['project_sha256']),\n    ('build_metadata',build,baseline['build_metadata_sha256'])]:\n    comparisons[label] = dict(before_count=len(expected), after_count=len(current),\n        removed=sorted(set(expected)-set(current)), added=sorted(set(current)-set(expected)),\n        changed=sorted(p for p in set(expected)&set(current) if expected[p]!=current[p]),\n        exact_membership_and_sha256_match=current==expected)\nfor field in ['frozen_sha256','protected_sha256']:\n    expected = baseline[field]\n    comparisons[field] = dict(count=len(expected), changed=[p for p,h in expected.items()\n        if not (ROOT/p).is_file() or sha(ROOT/p)!=h])\nrecovery = ROOT/'results/raw/cpu_gpu_recovery_20261011T075800444473Z'\ncomparisons['recovery_seal_unchanged'] = sha(recovery/'FINAL_INTEGRITY.json')==baseline['recovery_seal_sha256']\nassert all(c['exact_membership_and_sha256_match'] for c in\n           [comparisons['historical_results'],comparisons['project'],comparisons['build_metadata']]), comparisons\nassert not comparisons['frozen_sha256']['changed'] and not comparisons['protected_sha256']['changed'], comparisons\nassert comparisons['recovery_seal_unchanged'], comparisons\nwith (EVIDENCE/'FINAL_PRESERVATION.json').open('x') as stream:\n    json.dump(comparisons,stream,indent=2,sort_keys=True); stream.write('\\n')\nprint(json.dumps(comparisons,indent=2,sort_keys=True))\n")
print('Created',p)
PY
~~~~~~~~

## 21

- Exit: 0
- Safety/purpose: Final exact membership/content preservation comparison: all 12,294 pre-existing results, 193 project files, 65 build metadata, four frozen assets and 80 protected files. Hashing only.

~~~~~~~~sh
python3 -B results/raw/cpu_gpu_recovery_independent_review_20261011T082542018841Z/verify_preservation.py
~~~~~~~~

## 22

- Exit: 0
- Safety/purpose: Final evidence-only assembly and SHA256 seal. Exit0 confirmed by successful terminal completion; no workloads.

~~~~~~~~sh
python3 -B results/raw/cpu_gpu_recovery_independent_review_20261011T082542018841Z/seal_review.py
~~~~~~~~
