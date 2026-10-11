import json
from pathlib import Path
p=Path('/content/mab_bounded_20261011T020343203635Z')
print(json.dumps({'content_entries':sorted(x.name for x in Path('/content').iterdir()),'destination':str(p),'exists':p.exists()}))
assert not p.exists(),'exclusive remote destination already exists'
p.mkdir()
print('EXCLUSIVE_REMOTE_ROOT_CREATED')