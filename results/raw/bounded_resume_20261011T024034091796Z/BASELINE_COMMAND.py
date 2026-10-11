from pathlib import Path
import datetime,hashlib,json
r=Path.cwd();old=r/'results/raw/bounded_validation_20261011T020343203635Z'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
seal=json.loads((old/'FINAL_INTEGRITY.json').read_text());assert all(sha(old/p)==h for p,h in seal['evidence_sha256'].items())
pres=json.loads((old/'PRESERVATION_VERIFIED.json').read_text())
assert all(sha(r/p)==h for k in ['project_current_sha256','build_metadata_current_sha256'] for p,h in pres[k].items())
assert all(sha(r/p)==h for p,h in seal['preservation']['frozen_sha256'].items())
e=r/'results/raw'/('bounded_resume_'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'));e.mkdir()
before={'project_sha256':pres['project_current_sha256'],'build_metadata_sha256':pres['build_metadata_current_sha256'],'historical_results_sha256':{str(p.relative_to(r)):sha(p) for p in sorted((r/'results').rglob('*')) if p.is_file() and not p.is_relative_to(e)},'previous_seal_sha256':sha(old/'FINAL_INTEGRITY.json')}
(e/'BEFORE.json').write_text(json.dumps(before,indent=2,sort_keys=True)+'\n');(e/'record.py').write_bytes((old/'record.py').read_bytes())
for name in ['scripts/ctest_build_guard.py','scripts/non_timing_tests.py']:
 p=e/'before'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((r/name).read_bytes())
print(json.dumps({'evidence':str(e.relative_to(r)),'counts':{k:len(before[k]) for k in ['project_sha256','build_metadata_sha256','historical_results_sha256']}}))
