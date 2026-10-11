import json
from pathlib import Path
from colab_cli.state import StateStore
p=json.loads(Path('build/colab_validation_paths.json').read_text());e=Path(p['evidence']);s=StateStore(str((Path(p['backup'])/'private_cli/reconnect.json').resolve())).get(p['session'])
secrets=[x.encode() for x in [s.token,s.url] if x and len(x)>16]
matches=[str(f.relative_to(e)) for f in e.rglob('*') if f.is_file() and any(value in f.read_bytes() for value in secrets)]
assert not matches,'Private session credential found in evidence'
result={'runtime_proxy_credentials_in_evidence':False,'private_state_exported':False}
with (e/'privacy_check.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result))
