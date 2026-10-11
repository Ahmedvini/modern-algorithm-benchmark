import json,os
from pathlib import Path
from colab_cli.state import StateStore
p=json.loads(Path('build/colab_validation_paths.json').read_text());private=Path(p['backup'])/'private_cli'
store=StateStore(str((private/'sessions.json').resolve())); session=store.get(p['session']); assert session is not None
result={'kernel_registered':session.kernel_id is not None,'websocket_session_registered':session.session_id is not None,'cli_running':session.running}
session.session_id=None;session.running=None
mask=os.umask(0o077)
try:StateStore(str((private/'reconnect.json').resolve())).add(session)
finally:os.umask(mask)
print(json.dumps(result))
