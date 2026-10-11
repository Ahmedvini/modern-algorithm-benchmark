#!/usr/bin/env python3
import datetime,json,os,subprocess,sys,time
from pathlib import Path
raw=Path(__file__).resolve().parent
name=sys.argv[1]; command=sys.argv[2:]
record=raw/'commands'/(name+'.json')
assert not record.exists()
start={'argv':command,'cwd':os.getcwd(),'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
with (raw/'commands'/(name+'_started.json')).open('x') as f:json.dump(start,f,indent=2)
t=time.monotonic()
result=subprocess.run(command,capture_output=True,text=True)
start.update(exit_code=result.returncode,stdout=result.stdout,stderr=result.stderr,wall_seconds=time.monotonic()-t,ended_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
with record.open('x') as f:json.dump(start,f,indent=2);f.write('\n')
print('COMMAND',command,'EXIT',result.returncode)
print(result.stdout,end='');print(result.stderr,end='',file=sys.stderr)
sys.exit(result.returncode)
