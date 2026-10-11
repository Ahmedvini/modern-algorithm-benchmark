import json,requests
from pathlib import Path
from colab_cli.state import StateStore
p=json.loads(Path('build/colab_validation_paths.json').read_text());s=StateStore(str((Path(p['backup'])/'private_cli/sessions.json').resolve())).get(p['session'])
try:
 r=requests.get(s.url.rstrip('/')+'/api/kernels/'+s.kernel_id,params={'authuser':'0','colab-runtime-proxy-token':s.token},headers={'X-Colab-Runtime-Proxy-Token':s.token,'X-Colab-Client-Agent':'colab-cli'},timeout=20)
 result={'http_status':r.status_code}
 if r.status_code==200:
  d=r.json();result.update({k:d.get(k) for k in ['execution_state','last_activity','connections','name']})
except Exception as error:result={'error_type':type(error).__name__}
print(json.dumps(result))
