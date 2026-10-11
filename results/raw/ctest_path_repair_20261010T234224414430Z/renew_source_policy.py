"""Explicit repair-time renewal of two reviewed source hashes only. Never runs tests."""
import ast
import hashlib
import json
from pathlib import Path
import sys

root=Path.cwd();base=Path(__file__).resolve().parent
path=root/'docs/NON_TIMING_TEST_SELECTION_v1.json';policy=json.loads(path.read_text())
changed={}
for name in ['scripts/non_timing_tests.py','tests/test_ctest_build_guard.py']:
    source=(root/name).read_bytes();ast.parse(source,filename=name)
    digest=hashlib.sha256(source).hexdigest()
    changed[name]=dict(before=policy['reviewed_source_sha256'][name],after=digest)
    policy['reviewed_source_sha256'][name]=digest
before=json.loads((base/'before/docs/NON_TIMING_TEST_SELECTION_v1.json').read_text())
assert {k:v for k,v in policy.items() if k!='reviewed_source_sha256'}=={k:v for k,v in before.items() if k!='reviewed_source_sha256'}
path.write_text(json.dumps(policy,indent=2,sort_keys=True)+'\n')
with (base/(sys.argv[1]+'.json')).open('x') as f:json.dump(changed,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps(changed,indent=2,sort_keys=True))
