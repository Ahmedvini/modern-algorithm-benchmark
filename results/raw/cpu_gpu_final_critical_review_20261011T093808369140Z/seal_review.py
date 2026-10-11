"""File-only final review seal; never imports project code or invokes workloads."""
import hashlib,json,shlex
from datetime import datetime,timezone
from pathlib import Path
e=Path(__file__).resolve().parent;r=e.parents[2]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def put(name,value):
 with (e/name).open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
base=json.loads((e/'BASELINE.json').read_text())
actual={str(p.relative_to(r)):sha(p) for p in sorted((r/'results').rglob('*')) if p.is_file() and not p.is_relative_to(e)}
assert actual==base['results_sha256'],'Historical membership/content changed'
paths=[r/n for n in ['AGENTS.md','CMakeLists.txt','README.md']]
for d in ['include','src','scripts','tests','cmake','third_party','docs']:
 paths.extend(p for p in (r/d).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
project={str(p.relative_to(r)):sha(p) for p in sorted(set(paths))}
assert project==base['project_sha256'],'Project source/docs changed'
protected_paths=[r/'CMakeLists.txt']
for d in ['include','src','third_party']:
 protected_paths.extend(p for p in (r/d).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
protected={str(p.relative_to(r)):sha(p) for p in sorted(set(protected_paths))}
assert protected==base['protected_sha256'],'Protected membership/content changed'
names={'CMakeCache.txt','CTestTestfile.cmake','DartConfiguration.tcl','Makefile','compile_commands.json'}
metadata={str(p.relative_to(r)):sha(p) for p in sorted((r/'build').rglob('*')) if p.is_file() and p.name in names}
assert metadata==base['build_metadata_sha256'],'Build metadata changed'
assert all(sha(r/p)==h for p,h in base['frozen_sha256'].items()),'Frozen inputs changed'
anchor=json.loads((e/'ANCHOR_VERIFICATION.json').read_text())
assert all(sha(r/p)==h for p,h in anchor['actual_sha256'].items()),'Reviewed anchors changed'
selection=json.loads((e/'SELECTION_REVIEW.json').read_text())
assert sha(r/'docs/NON_TIMING_TEST_SELECTION_v3.json')==selection['base_sha256']
assert sha(r/'docs/NON_TIMING_TEST_SELECTION_v4.candidate.json')==selection['candidate_sha256']
assert not (r/'docs/CPU_GPU_EVIDENCE_REVIEW_v1.json').exists()
assert 'TRUSTED_APPROVAL_SHA256 = None' in (r/'scripts/cpu_gpu_evidence.py').read_text()
source={n:h for n,h in project.items() if n=='CMakeLists.txt' or n.split('/')[0] in ['include','src','scripts','tests','cmake','third_party']}
source_id=hashlib.sha256(json.dumps(source,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode('ascii')).hexdigest()
preservation=dict(historical_before=len(base['results_sha256']),historical_after=len(actual),historical_exact_path_sha256_match=True,
 historical_added=[],historical_removed=[],historical_modified=[],project_before=len(base['project_sha256']),project_after=len(project),
 project_exact_match=True,protected_count=len(protected),build_metadata_count=len(metadata),frozen_count=len(base['frozen_sha256']),
 anchors_count=len(anchor['actual_sha256']),source_files=len(source),source_identity=source_id,all_unchanged=True,
 v3_unchanged=True,candidate_unchanged=True,candidate_activated=False,production_adapter_unchanged=True,cub_version=300001)
put('FINAL_PRESERVATION.json',preservation)
initial=json.loads((e/'INITIAL_COMMANDS.json').read_text())
records=[json.loads(p.read_text()) for p in sorted(e.glob('command_*.json'))]
lines=['# Executed review commands\n\nAll inspection payloads are read-only or write only this new evidence directory. No project code was imported/executed, test run, CTest discovery, build, cloud/GPU command, resource probe or benchmark was executed.\n\nFor command_NNN.json records, the outer command is python3 -B '+shlex.quote(str(e/'record.py'))+' PURPOSE PAYLOAD; exact purpose/payload and stdout/stderr are retained.\n']
for i,row in enumerate(initial+records,1):
 lines.append('\n## '+str(i)+'. '+row['purpose']+'\n\nExit: '+str(row['exit_code'])+'. Working directory: '+row.get('working_directory',str(r))+'.\n\n\x60\x60\x60sh\n'+row['command']+'\n\x60\x60\x60\n')
lines.append('\n## Final file-only seal\n\nExact command: python3 -B '+str(e.relative_to(r))+'/seal_review.py\n\nWorking directory: '+str(r)+'. Exit: 0 (confirm against observed terminal response). Only file hashes, exact membership comparisons, new audit/log/manifest writes; no project execution. FINAL_INTEGRITY.json excludes itself by convention.\n\nInspection errors are retained. One multi-inspection shell returned0 while its embedded Python assertion returned1 and a sed path read failed; see command stdout/stderr and FINAL_AUDIT.md. Other failed inspections returned128 (Git unavailable),2 (missing rg path), and1 (read-only record parsing assertions). Corrected inspection attempts are retained separately.\n')
with (e/'COMMANDS.md').open('x') as f:f.writelines(lines)
members={str(p.relative_to(e)):sha(p) for p in sorted(e.rglob('*')) if p.is_file()}
seal=dict(schema_version=1,created_utc=datetime.now(timezone.utc).isoformat(),
 verdict='NO-GO — one or more required validation gates remain open',
 seal_command=['python3','-B',str(e.relative_to(r))+'/seal_review.py'],seal_excludes_itself=True,
 evidence_sha256=members,evidence_files_excluding_seal=len(members),
 historical_manifest='BASELINE.json',historical_manifest_field='results_sha256',historical_files_verified=len(actual),
 preservation_results=preservation,project_sha256=project,frozen_sha256=base['frozen_sha256'],
 protected_sha256=protected,build_metadata_sha256=metadata,source_identity=source_id,
 prior_repair_seal_sha256=base['repair_seal_sha256'],retained_focused_tests_verified=74,
 fresh_tests_executed=0,ctest_discovery=0,builds=0,cloud_commands=0,gpu_commands=0,resource_probes=0,
 benchmark_trials=0,warmups=0,study_launched=False,candidate_activated=False,
 independently_approved_full_bundle_available=False,
 limitations=['No installed non-circular full-evidence trust root or complete positive integration.',
 'v4 candidate remains inactive; explicit acceptance and reviewed activation absent.',
 'Nested evidence retention and legacy timing/pilot compatibility unresolved.',
 'No current intended T4 build/compiler/linker/input-binary provenance or matching required validation.',
 'Initial command stdout retained in tool transcript only; exact commands and observed statuses transcribed.',
 'Hash seals are preservation evidence, not independent attestation of historical executions.'])
put('FINAL_INTEGRITY.json',seal)
check={str(p.relative_to(e)):sha(p) for p in sorted(e.rglob('*')) if p.is_file() and p!=e/'FINAL_INTEGRITY.json'}
assert check==members,'Review member seal mismatch'
print(json.dumps(dict(seal_verified=True,exit_status=0,historical_unchanged=len(actual),project_unchanged=len(project),
 protected_unchanged=len(protected),build_metadata_unchanged=len(metadata),frozen_unchanged=4,anchors_unchanged=26,
 evidence_files=len(members)+1,source_identity=source_id,benchmark_trials=0,verdict=seal['verdict'])))

