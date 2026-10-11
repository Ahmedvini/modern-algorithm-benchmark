from pathlib import Path
import json,shlex,shutil
p=json.loads(Path('build/phase6_paths.json').read_text());e=Path(p['evidence'])
records=[]
for file in (e/'commands').glob('*.json'):
 if file.name.endswith('_started.json'):continue
 d=json.loads(file.read_text());records.append(dict(name=file.stem,path=str(file),**d))
records.sort(key=lambda d:d['started_utc'])
with (e/'commands_index.json').open('x') as stream:json.dump(records,stream,indent=2);stream.write('\n')
lines=['# Phase 6 exact recorded commands','', 'Each record retains cwd, UTC start/end, argv, exit status, stdout/stderr and wall duration. The original recorder setup failure is separate in initial_recorder_failure.json; no child was launched. Git absence is recorded in each environment manifest. Exploratory source reads are not benchmark/test commands.','', '| Record | Exit | Wall seconds | Exact command |','|---|---:|---:|---|']
for r in records:lines.append(f"| [{r['name']}](commands/{r['name']}.json) | {r['exit_code']} | {r['wall_seconds']:.6f} | `{shlex.join(r['argv'])}` |")
lines+=['','## Per-configuration benchmark commands','',f"Full retry: ../{p['full_retry']}/matrix.json and run_XXXXXX_command.json (180 children, all exit0).",f"Smoke retry: ../{p['smoke_retry']}/matrix.json (32 children, all exit0).",f"Original full attempt: ../{p['full']}/matrix.json (180 children exit0; runner exit1, metadata-analysis defect, retained FAILED).",'', 'Diagnostics and all failed attempts are retained; timing observations from different attempts are never pooled. No CUDA or100M command was run.','',f"Ledger generated with `python3 {e}/generate_ledger.py` after final_review exited0."]
with (e/'COMMANDS.md').open('x') as stream:stream.write('\n'.join(lines)+'\n')
source=json.loads((e/'source_after.json').read_text());destination=e/'reviewed_source';destination.mkdir()
for name in source:
 out=destination/name;out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(name,out)
shutil.copyfile(e/'source_after.json',destination/'sha256.json')
print('Saved',len(records),'command records and',len(source),'reviewed project files.')
