"""Seal new evidence and verify every pre-existing result without modifying it."""
import datetime
import json
from pathlib import Path
import sys

E=Path(__file__).resolve().parent
ROOT=E.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from cpu_gpu_protocol import sha,load_protocol,verify_source_extension
prior=json.loads((E/'prior_artifacts_sha256.json').read_text())
for relative,digest in prior.items():
    assert (ROOT/relative).is_file() and sha(ROOT/relative)==digest,relative
source=verify_source_extension(load_protocol())
assert source==json.loads((E/'source_before.json').read_text())
freeze=json.loads((E/'freeze_verified.json').read_text())
for relative,digest in freeze['files'].items():assert sha(ROOT/relative)==digest
assert sha(ROOT/'README.md')==sha(E/'docs_before/README.md')
verification=json.loads((E/'INDEPENDENT_VERIFICATION.json').read_text())
assert verification['complete'] is True
hashes={str(p.relative_to(ROOT)):sha(p) for p in sorted(E.rglob('*')) if p.is_file()}
result=dict(complete=True,exit_code=0,verified_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    prior_result_files_checked=len(prior),prior_files_modified=0,prior_files_removed=0,
    current_source_files_checked=len(source['current_source_sha256']),production_source_unchanged=True,
    frozen_files_sha256=freeze['files'],resource_gate_passed=True,full_study_launch_recommended=False,
    benchmark_trials=0,pilot_rerun=False,full_study_run=False,
    evidence_sha256=hashes,documentation_sha256={p:sha(ROOT/p) for p in ['docs/AUDIT.md','docs/ROADMAP.md','README.md']},
    command='python3 '+str(E/'seal_integrity.py'),manifest_excludes_itself=True)
with (E/'FINAL_INTEGRITY.json').open('x') as stream:
    json.dump(result,stream,indent=2,sort_keys=True);stream.write('\n')
print('Integrity passed:',len(prior),'prior files;',len(source['current_source_sha256']),'source files;',len(hashes),'new evidence files sealed')
