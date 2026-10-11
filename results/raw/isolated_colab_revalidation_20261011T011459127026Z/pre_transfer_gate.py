import hashlib,json
from pathlib import Path
r=Path.cwd();e=Path(__file__).resolve().parent
def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
review=load(e/'SOURCE_REVIEW.json');assert review['verified'] and not review['unreviewed_source_changes']
identity=load(e/'SOURCE_IDENTITY.json')
assert all(sha(r/p)==h for p,h in identity['files_sha256'].items())
assert sha(e/'reviewed_source.tar.gz')==review['archive_sha256']
session=load(e/'session_identity.json');assert session['exit_code']==0
assert '[cpu-gpu-validation] gpu-t4-s-kkb-usw4b0-21qggbdn9iask | Hardware: T4' in session['stdout']
record=load(e/'remote_destination_check.json');assert record['exit_code']==0
text=record['stdout'];assert text.count('REMOTE_CHECK_BEGIN')==text.count('REMOTE_CHECK_END')==1
remote=json.loads(text.split('REMOTE_CHECK_BEGIN')[1].split('REMOTE_CHECK_END')[0]);assert remote['paths_absent']
assert remote['destination']=='/content/mab_isolated_20261011T011459127026Z'
assert remote['archive']=='/content/mab_source_20261011T011459127026Z.tar.gz'
assert len(remote['commands'])==4 and all(c['exit_code']==0 for c in remote['commands'])
assert remote['commands'][0]['stdout'].startswith('Tesla T4, GPU-c51b969a-fbb1-a810-8346-93e2f6fc1849,')
result=dict(transfer_permitted=True,source_files=153,reviewed_revision_sha256=review['reviewed_revision_sha256'],
    archive_sha256=review['archive_sha256'],remote=remote,scope='new exclusive source/build, two existing direct correctness tests, metadata-only describe; no CTest or timing trials')
with (e/'PRE_TRANSFER.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print('Reviewed source, exact existing T4 session identity, and absent destination independently confirmed before upload')
