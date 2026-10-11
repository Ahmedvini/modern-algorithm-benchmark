import datetime,json,re,subprocess,sys
from pathlib import Path
e=Path(__file__).resolve().parent
name,scope,seconds=sys.argv[1:4];argv=sys.argv[4:]
started=datetime.datetime.now(datetime.timezone.utc).isoformat()
def redact(text):
    text=re.sub(r'https?://[^\s\x1b]*','[URL REDACTED]',text)
    return re.sub(r'(?i)((?:access_token|refresh_token|id_token|authorization|oauth.?code)\s*[:=]\s*)[^\s,]+',r'\1[REDACTED]',text)
try:
    p=subprocess.run(argv,input='',capture_output=True,text=True,timeout=int(seconds))
    d=dict(argv=argv,cwd=str(Path.cwd()),started_utc=started,exit_code=p.returncode,stdout=redact(p.stdout),stderr=redact(p.stderr),scope=scope)
except (OSError,subprocess.TimeoutExpired) as error:
    d=dict(argv=argv,cwd=str(Path.cwd()),started_utc=started,exit_code=None,error=redact(str(error)),scope=scope)
with (e/(name+'.json')).open('x') as f:json.dump(d,f,indent=2);f.write('\n')
print(json.dumps(d,indent=2));sys.exit(0 if d['exit_code']==0 else 1)
