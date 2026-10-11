import json
from pathlib import Path
e=Path(__file__).resolve().parent
def load(p):return json.loads(Path(p).read_text())
log=load(e/'extract.json');assert log['exit_code']==0
text=log['stdout'];assert text.count('TRANSFER_VERIFIED_BEGIN')==text.count('TRANSFER_VERIFIED_END')==1
remote=json.loads(text.split('TRANSFER_VERIFIED_BEGIN')[1].split('TRANSFER_VERIFIED_END')[0])
assert remote['files_verified']==153 and remote['frozen_verified']
assert remote['source_files_sha256']==load(e/'SOURCE_IDENTITY.json')['files_sha256']
assert remote['archive_sha256']==load(e/'BUNDLE.json')['archive_sha256']
assert remote['source']=='/content/mab_isolated_20261011T011459127026Z/source'
with (e/'TRANSFER_CHECKED.json').open('x') as f:json.dump(remote,f,indent=2);f.write('\n')
print('Exact guarded source identity retained through remote archive and extraction; build permitted, timing trials prohibited')
