"""Record read-only review commands; never run any repository test/selector."""
import datetime
import json
from pathlib import Path
import subprocess
import sys
base=Path(__file__).resolve().parent
name,safety,*argv=sys.argv[1:]
assert argv and argv[0] in ['cat','rg','sed','nl','tail','python3']
assert not any(Path(a).name in ['ctest','colab','nvcc'] for a in argv)
result=subprocess.run(argv,capture_output=True,text=True,check=False)
(base/'commands').mkdir(exist_ok=True)
record=dict(argv=argv,cwd=str(Path.cwd()),utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            exit_code=result.returncode,safety=safety,stdout=result.stdout,stderr=result.stderr)
with (base/'commands'/(name+'.json')).open('x') as f:json.dump(record,f,indent=2,sort_keys=True);f.write('\n')
print(result.stdout,end='');print(result.stderr,end='',file=sys.stderr)
raise SystemExit(result.returncode)
