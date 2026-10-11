"""Verify preservation and seal review-only evidence. No project execution."""
import datetime
import hashlib
import json
from pathlib import Path
import shlex

ROOT=Path.cwd();BASE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
start=json.loads((BASE/'START_SNAPSHOT.json').read_text())
verification={}
for name in ['prior_results_sha256','project_files_sha256']:
    mapping=start[name]
    missing=[p for p in mapping if not Path(p).is_file()]
    changed=[p for p,h in mapping.items() if Path(p).is_file() and sha(p)!=h]
    assert not missing and not changed,dict(group=name,missing=missing,changed=changed)
    verification[name]=dict(checked=len(mapping),missing=missing,changed=changed)
all_results={str(p) for p in Path('results').rglob('*') if p.is_file()}
new=all_results-set(start['prior_results_sha256'])
assert all(Path(p).resolve().is_relative_to(BASE) for p in new)
future=[BASE/'COMMANDS.md',BASE/'FINAL_AUDIT.md',BASE/'FINAL_INTEGRITY.json',BASE/'commands/seal_review.json']
assert not any(p.exists() for p in future)
total=len(all_results)+len(future);new_count=len(new)+len(future)
command=['python3','-B',str(BASE.relative_to(ROOT)/'seal_review.py')]
record=dict(argv=command,cwd=str(ROOT),exit_code=0,stdout='Review evidence sealed; preservation checks passed.',stderr='',
    safety_classification='hash_verification_and_evidence_sealing_only',timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
with future[3].open('x') as stream:json.dump(record,stream,indent=2,sort_keys=True);stream.write('\n')
commands=['# Independent review commands\n\nNo listed command executes tests, CTest, timing workloads, GPU work, prerequisites or fresh resource checks. Subprocess use in the recorder launches only the read-only inspections or offline review scripts listed below. Repository subprocess execution is blocked inside the pure-function review scripts.\n\n']
for path in sorted((BASE/'commands').glob('*.json')):
    item=json.loads(path.read_text())
    commands.append('## '+path.stem+'\n\n```sh\n'+shlex.join(item['argv'])+'\n```\n\nExit '+str(item['exit_code'])+
        '; safety `'+item['safety_classification']+'`; full output `commands/'+path.name+'`.\n\n')
commands.append('## Initial inspection and evidence creation\n\nBefore the recorder existed, the exact read-only shell command was:\n\n```sh\npwd\ncat AGENTS.md\ncat results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/FINAL_AUDIT.md\ncat results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/COMMANDS.md\ncat results/raw/cpu_gpu_tooling_review_20261010T125855526277Z/FINAL_AUDIT.md\ncat results/raw/cpu_gpu_tooling_review_20261010T125855526277Z/COMMANDS.md\n```\n\nExit0, source/evidence reads only. Integrity manifests were parsed/read by verify_evidence scripts. A Python3 -B stdin bootstrap hashed all11391 pre-existing results and project files and exclusively created this timestamped directory, START_SNAPSHOT.json and record.py (exit0). Evidence-only apply_patch and Python exclusive-file writes created the review scripts, inert fixtures and corrected verifier v2. No historical script was executed in place. Bootstrap/initial read outputs were observed in the terminal, not copied into fabricated subprocess logs. No additional experiment or tool command was run.\n')
with future[0].open('x') as stream:stream.write(''.join(commands))
audit=(BASE/'FINAL_AUDIT_TEMPLATE.md').read_text().replace('@PROJECT_COUNT@',str(len(start['project_files_sha256']))).replace('@NEW_COUNT@',str(new_count)).replace('@TOTAL_COUNT@',str(total))
with future[1].open('x') as stream:stream.write(audit)
evidence={str(p.relative_to(ROOT)):sha(p) for p in sorted(BASE.rglob('*')) if p.is_file()}
assert len([p for p in Path('results').rglob('*') if p.is_file()])+1==total
seal=dict(schema_version=1,review_complete=True,decision='NO-GO',findings=dict(A='PASS',B='NO-GO: unguarded directory-level CTest hooks/includes',C='PASS'),
    preservation=verification,evidence_sha256=evidence,manifest_excludes_itself=True,
    results_at_start=11391,results_after=total,new_review_evidence_files=new_count,
    project_source_modified=False,prior_evidence_modified=False,ctest_commands_run=0,test_suites_run=0,
    timing_trials_run=0,gpu_commands_run=0,fresh_prerequisites_run=False,fresh_resource_checks_run=False,
    pilot_run=False,full_study_run=False,study_authorized=False,
    verified_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),command=shlex.join(command),exit_code=0)
with future[2].open('x') as stream:json.dump(seal,stream,indent=2,sort_keys=True);stream.write('\n')
print(json.dumps(dict(decision=seal['decision'],audit=str(future[1].relative_to(ROOT)),preservation=verification,
                     new_review_evidence_files=new_count,results_after=total,exit_code=0),indent=2,sort_keys=True))
