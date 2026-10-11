import datetime
import json
import os
from pathlib import Path
import subprocess
import sys

base=Path(__file__).resolve().parent
name,safety,*argv=sys.argv[1:]
result=subprocess.run(argv,capture_output=True,text=True)
record=dict(argv=argv,cwd=os.getcwd(),exit_code=result.returncode,stdout=result.stdout,stderr=result.stderr,
            safety_classification=safety,timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
with (base/'commands'/(name+'.json')).open('x') as stream:json.dump(record,stream,indent=2,sort_keys=True);stream.write('\n')
print(json.dumps(dict(command=name,exit_code=result.returncode,safety=safety)))
print(result.stdout);print(result.stderr,file=sys.stderr)
raise SystemExit(result.returncode)
