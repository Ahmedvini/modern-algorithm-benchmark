import json
from pathlib import Path
p=Path('/content/mab_bounded_resume_20261011T024034091796Z')
print(json.dumps({'content_entries':sorted(x.name for x in Path('/content').iterdir()),'destination':str(p),'exists':p.exists()}))
assert not p.exists(),'exclusive remote destination already exists'
p.mkdir()
print('EXCLUSIVE_REMOTE_ROOT_CREATED')