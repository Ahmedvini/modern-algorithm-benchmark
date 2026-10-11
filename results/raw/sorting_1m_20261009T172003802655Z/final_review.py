#!/usr/bin/env python3
import datetime,difflib,hashlib,json,re
from pathlib import Path
root=Path.cwd();raw=Path(__file__).resolve().parent;paths=json.loads((raw/'paths.json').read_text());matrix=Path(paths['matrix']);processed=Path(paths['processed'])
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((raw/'repository_before.json').read_text());current={str(p.relative_to(root)):digest(p) for p in sorted(root.rglob('*')) if p.is_file() and p.parts[len(root.parts)] not in ['build','results','.git'] and '__pycache__' not in p.parts}
changed=[name for name,value in old.items() if current.get(name)!=value]
assert set(changed)=={'README.md','docs/AUDIT.md','docs/ROADMAP.md','docs/BENCHMARKING.md','docs/EXPERIMENT_PROTOCOL.md','docs/METRICS.md'}
added=sorted(set(current)-set(old));assert added==[str(Path(paths['protocol']).relative_to(root))]
for name,value in json.loads((raw/'execution_inputs_sha256.json').read_text()).items():assert digest(root/name)==value,name
prior=json.loads((raw/'previous_raw_sha256.json').read_text())
for name,value in prior.items():assert digest(root/name)==value,name
matrix_hashes={str(p.relative_to(matrix)):digest(p) for p in sorted(matrix.rglob('*')) if p.is_file()}
assert matrix_hashes==json.loads((raw/'matrix_before_analysis_sha256.json').read_text())
verified=json.loads((raw/'verification.json').read_text());assert verified['complete'] and verified['successful_measured_trials']==450 and verified['successful_warmups']==90
assert {str(p.relative_to(processed)):digest(p) for p in sorted(processed.rglob('*')) if p.is_file()}==verified['processed_sha256']
assert Path(paths['protocol']).read_bytes()==(raw/'PROTOCOL_v1.md').read_bytes()
assert all(json.loads(p.read_text())['exit_code']==0 for p in (raw/'commands').glob('*.json') if not p.stem.endswith('_started'))
links=[]
for name in changed:
    for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',(root/name).read_text()):
        if 'sorting_1m_' not in target or target.startswith('http'):continue
        resolved=(root/name).parent/target
        assert resolved.exists(),(name,target)
        links.append({'file':name,'target':target})
patch=''
for name in changed:
    original=raw/'docs_before'/Path(name).name
    patch+=''.join(difflib.unified_diff(original.read_text().splitlines(keepends=True),(root/name).read_text().splitlines(keepends=True),fromfile='a/'+name,tofile='b/'+name))
for name in added:patch+=''.join(difflib.unified_diff([],(root/name).read_text().splitlines(keepends=True),fromfile='/dev/null',tofile='b/'+name))
with (raw/'documentation_changes.patch').open('x') as f:f.write(patch)
report={'schema_version':1,'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'modified_files':changed,'added_project_files':added,'project_sha256':current,'code_tests_tools_build_configuration_vendors_unchanged':True,'documentation_links_checked':links,'raw_matrix_and_prior_raw_evidence_unchanged':True,'frozen_protocol_and_execution_inputs_unchanged':True,'processed_outputs_unchanged_after_verified_regeneration':True,'milestone_complete':True,'study_results':{'configurations':15,'measured_successes':450,'warmup_successes':90,'failures':0,'omissions':0,'deviations':[]},'final_audit_sha256':digest(raw/'FINAL_AUDIT.md')}
with (raw/'final_review.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
print('Final review passed:',len(changed),'existing documentation files updated, one frozen protocol added; production code/tests/tools/vendors unchanged; documentation links valid; raw/prior artifacts and processed outputs unchanged.')
