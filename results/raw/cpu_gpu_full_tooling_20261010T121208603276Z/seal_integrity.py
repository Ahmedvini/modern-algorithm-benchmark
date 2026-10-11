"""Seal tooling evidence, preserving historical results and frozen inputs."""
import datetime
import json
from pathlib import Path
import sys
E=Path(__file__).resolve().parent;ROOT=E.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from cpu_gpu_protocol import sha,load_protocol,verify_source_extension
prior=json.loads((E/'prior_artifacts_sha256.json').read_text())
for name,digest in prior.items():assert (ROOT/name).is_file() and sha(ROOT/name)==digest,name
freeze=json.loads((E/'freeze_verified.json').read_text())
for name,digest in freeze['files'].items():assert sha(ROOT/name)==digest,name
model=load_protocol();source=verify_source_extension(model)
bundle=json.loads((E/'source_bundle.json').read_text())
assert source['current_source_sha256']==bundle['source_sha256']
summary=json.loads((E/'VALIDATION_SUMMARY.json').read_text());assert summary['complete'] and summary['full_study_launch']=='NO-GO'
assert not (ROOT/'results/raw/UNEXECUTED_FULL_COMPARISON').exists()
documentation=['README.md','docs/AUDIT.md','docs/ROADMAP.md','docs/CPU_GPU_FULL_MATRIX_TOOLING_v1.md']
result=dict(complete=True,exit_code=0,verified_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    command='python3 '+str(E/'seal_integrity.py'),prior_artifacts_checked=len(prior),prior_artifacts_modified=0,prior_artifacts_removed=0,
    frozen_files_sha256=freeze['files'],protected_anchors_checked=len(model['source_at_freeze_sha256']),
    protected_source_review=source,current_source_sha256=source['current_source_sha256'],
    documentation_sha256={name:sha(ROOT/name) for name in documentation},
    evidence_sha256={str(p.relative_to(ROOT)):sha(p) for p in sorted(E.rglob('*')) if p.is_file()},
    manifest_excludes_itself=True,pilot_run=False,full_study_run=False,gpu_benchmark_run=False,
    unintended_cpu_unit_timing_rows=6,full_study_launch_recommendation='NO-GO')
with (E/'FINAL_INTEGRITY.json').open('x') as f:json.dump(result,f,indent=2,sort_keys=True);f.write('\n')
print('Integrity passed:',len(prior),'earlier result files unchanged;',len(source['current_source_sha256']),'current source hashes;',len(result['evidence_sha256']),'new evidence files sealed')
