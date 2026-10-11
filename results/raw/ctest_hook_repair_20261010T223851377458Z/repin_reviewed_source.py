"""Explicit repair-policy renewal after source inspection; not auto-enrollment."""
import ast
import json
from pathlib import Path
import sys
root=Path.cwd();base=Path(__file__).resolve().parent
sys.path.insert(0,str(root/'scripts'))
from cpu_gpu_protocol import source_manifest
paths=['scripts/ctest_build_guard.py','scripts/non_timing_tests.py','tests/ctest_fixture.py',
       'tests/test_ctest_build_guard.py','tests/test_cpu_gpu_safety.py','tests/test_cpu_gpu_comparison.py']
for name in paths:ast.parse((root/name).read_text(),filename=name)
path=root/'docs/NON_TIMING_TEST_SELECTION_v1.json'
manifest=json.loads(path.read_text()); old=manifest['reviewed_source_sha256'];new=source_manifest()
changes={p:dict(before=old.get(p),after=new.get(p)) for p in old.keys()|new.keys() if old.get(p)!=new.get(p)}
assert set(changes)<=set(paths),changes
manifest['reviewed_source_sha256']=new
path.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
with (base/sys.argv[1]).open('x') as stream:json.dump(dict(changes=changes,syntax_checked=paths),stream,indent=2,sort_keys=True);stream.write('\n')
print(json.dumps(dict(changed_paths=sorted(changes),reviewed_source_count=len(new)),indent=2))
