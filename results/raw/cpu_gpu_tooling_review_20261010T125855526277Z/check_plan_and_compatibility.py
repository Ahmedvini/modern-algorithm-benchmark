"""Dry-run and retained-summary checks only; do not execute any worker."""
import collections
import hashlib
import json
from pathlib import Path
import subprocess
import sys

root = Path.cwd()
base = Path(__file__).resolve().parent
sys.path.insert(0, str(root / 'scripts'))
from cpu_gpu_protocol import BACKENDS, load_protocol, schedule, sha

model = load_protocol()
argv = [sys.executable, '-B', 'scripts/run_cpu_gpu_study.py', '--dry-run',
        '--executable', 'UNEXECUTED_REVIEW_WORKER', '--input-tool', 'UNEXECUTED_REVIEW_INPUT',
        '--output', str(base / 'UNEXECUTED_STUDY')]
children = [subprocess.run(argv, capture_output=True, text=True) for _ in range(2)]
assert all(c.returncode == 0 for c in children)
assert children[0].stdout == children[1].stdout
assert not (base / 'UNEXECUTED_STUDY').exists()
plan = json.loads(children[0].stdout)
cells = model['study']['cells']
assert cells == sorted(cells, key=lambda c: (hashlib.sha256(('314159|' + c['dataset_id']).encode('ascii')).hexdigest(), c['dataset_id']))
rows = [r for i,c in enumerate(cells) for r in schedule(c, i*30)]
assert len(rows) == 1440 and len(plan['commands']) == 48
assert [r['global_trial_index'] for r in rows] == list(range(1440))
assert collections.Counter(r['phase'] for r in rows) == {'measure':1200,'warmup':240}
for i, cell in enumerate(cells):
    worker = plan['commands'][i]['worker']
    assert worker[worker.index('--global-offset')+1] == str(i*30)
    assert worker[worker.index('--base-order')+1] == ','.join(cell['warmup_order'][0])
for backend in BACKENDS:
    assert sum(r['backend_id']==backend and r['phase']=='measure' for r in rows) == 240
    assert sum(r['backend_id']==backend and r['phase']=='warmup' for r in rows) == 48
digest = sha(base / 'PILOT_REANALYSIS.json')
assert digest == '07e69e2e0c8853f93d3f3da895337b5e4b72e5e2dd0ff0577db3cbd1f7053a22'
report = dict(pass_checks=True, commands=[dict(argv=argv,exit_code=c.returncode,stderr=c.stderr) for c in children],
    deterministic_dry_run=True, generated_study_directory=False, planned_only=dict(datasets=48,measured=1200,warmups=240),
    pilot_reanalysis_sha256=digest, pilot_summary_byte_identical=True, resume_supported=plan['resume_supported'],
    actual_timing_calls=0, timeout_policy=plan['timeout_policy'], frozen_resources=plan['resources'])
with (base / 'PLAN_AND_COMPATIBILITY.json').open('x') as stream:
    json.dump(report,stream,indent=2,sort_keys=True);stream.write('\n')
with (base / 'DRY_RUN.json').open('x') as stream:
    stream.write(children[0].stdout)
print(json.dumps(report,indent=2))
