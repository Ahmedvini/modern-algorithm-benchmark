"""Capture authorized session setup and diagnostics, redacting credential output."""
import datetime,json,re,subprocess,sys
from pathlib import Path
e=Path(__file__).resolve().parent
name,scope=sys.argv[1:3];argv=sys.argv[3:]
def redact(s):
    # Never persist OAuth credentials/codes or authentication URLs if CLI asks.
    s=re.sub(r'https?://[^\s\x1b]*', '[URL REDACTED]',s)
    s=re.sub(r'(?i)((?:access_token|refresh_token|id_token|authorization|oauth.?code)\s*[:=]\s*)[^\s,]+',r'\1[REDACTED]',s)
    return s
try:
    p=subprocess.run(argv,input='',capture_output=True,text=True,timeout=150)
    d=dict(argv=argv,cwd=str(Path.cwd()),started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
           exit_code=p.returncode,stdout=redact(p.stdout),stderr=redact(p.stderr),scope=scope)
except (OSError,subprocess.TimeoutExpired) as error:
    d=dict(argv=argv,cwd=str(Path.cwd()),exit_code=None,error=redact(str(error)),scope=scope)
with (e/(name+'.json')).open('x') as f:json.dump(d,f,indent=2);f.write('\n')
print(json.dumps(d,indent=2))
