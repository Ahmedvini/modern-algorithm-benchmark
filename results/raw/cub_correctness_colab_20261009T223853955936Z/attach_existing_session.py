import json,os
from pathlib import Path
from colab_cli.common import state
from colab_cli.state import SessionState,StateStore
p=json.loads(Path('build/colab_validation_paths.json').read_text())
assignment=next((a for a in state.client.list_assignments() if a.endpoint==p['session']),None)
if assignment is None:raise RuntimeError('Requested backend assignment no longer exists')
assert assignment.accelerator.value=='T4'
private=Path(p['backup'])/'private_cli';private.mkdir(mode=0o700)
config=private/'sessions.json'
oldmask=os.umask(0o077)
try:
 store=StateStore(str(config.resolve()))
 store.add(SessionState(name=p['session'],endpoint=assignment.endpoint,
           token=assignment.runtime_proxy_info.token,url=assignment.runtime_proxy_info.url,
           token_expires_at=assignment.runtime_proxy_info.expires_at(),
           accelerator=assignment.accelerator.value,variant=assignment.variant.name,
           machine_shape=assignment.machine_shape.name))
finally:os.umask(oldmask)
# No credentials/proxy URLs are printed or placed in experiment evidence.
result=dict(existing_assignment=assignment.endpoint,created_gpu_session=False,isolated_config=str(config),credentials_retained_only_in_private_build_state=True)
with (Path(p['evidence'])/'session_attach.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result,indent=2))
