"""Record only explicitly selected inspection/version/resource diagnostics."""
import datetime
import json
from pathlib import Path
import subprocess
import sys

e=Path(__file__).resolve().parent
name,category=sys.argv[1:3];argv=sys.argv[3:]
started=datetime.datetime.now(datetime.timezone.utc).isoformat()
try:
    r=subprocess.run(argv,capture_output=True,text=True,timeout=90)
    data=dict(argv=argv,cwd=str(Path.cwd()),category=category,started_utc=started,
              exit_code=r.returncode,stdout=r.stdout,stderr=r.stderr)
except (OSError,subprocess.TimeoutExpired) as error:
    data=dict(argv=argv,cwd=str(Path.cwd()),category=category,started_utc=started,
              exit_code=None,error=str(error),stdout='',stderr='')
with (e/(name+'.json')).open('x') as f:json.dump(data,f,indent=2);f.write('\n')
print(json.dumps(data,indent=2))
