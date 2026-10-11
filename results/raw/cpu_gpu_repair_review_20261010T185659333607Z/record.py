import datetime,json,os,subprocess,sys
from pathlib import Path
base=Path(__file__).resolve().parent
name,safety,*argv=sys.argv[1:]
r=subprocess.run(argv,capture_output=True,text=True)
d=dict(argv=argv,cwd=os.getcwd(),exit_code=r.returncode,stdout=r.stdout,stderr=r.stderr,safety_classification=safety,timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
with (base/'commands'/(name+'.json')).open('x') as stream:json.dump(d,stream,indent=2,sort_keys=True);stream.write('\n')
print(json.dumps(dict(command=name,exit_code=r.returncode,safety=safety)));print(r.stdout);print(r.stderr,file=sys.stderr)
raise SystemExit(r.returncode)
