import json, subprocess, sys, datetime
from pathlib import Path
name=sys.argv[1]; command=sys.argv[2:]; directory=Path(__file__).resolve().parent
started=datetime.datetime.now(datetime.timezone.utc).isoformat()
result=subprocess.run(command,capture_output=True,text=True)
with (directory/(name+'.json')).open('x') as stream:
 json.dump({'command':command,'exit_code':result.returncode,'started_utc':started,'stdout':result.stdout,'stderr':result.stderr},stream,indent=2)
 stream.write('\n')
print(name+': exit '+str(result.returncode))
print((result.stdout+result.stderr)[-2200:])
sys.exit(result.returncode)
