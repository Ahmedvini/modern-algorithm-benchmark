import sys,json,subprocess,datetime
from pathlib import Path
e=Path(__file__).resolve().parent
purpose,cmd=sys.argv[1:]
t=datetime.datetime.now(datetime.timezone.utc).isoformat()
p=subprocess.run(cmd,shell=True,cwd=e.parents[2],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
n=len(list(e.glob('command_*.json')))+1
record=dict(command=cmd,purpose=purpose,working_directory=str(e.parents[2]),started_utc=t,exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr)
with (e/f'command_{n:03d}.json').open('x') as f:json.dump(record,f,indent=2)
print(p.stdout,end='');print(p.stderr,end='',file=sys.stderr);print('RECORDED EXIT:',p.returncode)
sys.exit(p.returncode)
