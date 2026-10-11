"""Static AST and exact before/after source diffs only; no project code executed."""
import ast
import difflib
import hashlib
import json
from pathlib import Path

root=Path.cwd();base=Path(__file__).resolve().parent
before=json.loads((base/'BEFORE.json').read_text())
paths=['scripts/non_timing_tests.py','tests/test_ctest_build_guard.py','docs/NON_TIMING_TEST_SELECTION_v1.json',
       'docs/CTEST_BUILD_GUARD_v1.md','README.md','docs/ROADMAP.md','docs/AUDIT.md']
review={};diff=[]
for p in paths:
    old=(base/'before'/p).read_text();new=(root/p).read_text()
    entry=dict(before_sha256=hashlib.sha256(old.encode()).hexdigest(),after_sha256=hashlib.sha256(new.encode()).hexdigest())
    assert entry['before_sha256']==before['project_sha256'][p]
    if p.endswith('.py'):
        tree=ast.parse(new,filename=p)
        entry['functions']=[dict(name=n.name,line=n.lineno) for n in ast.walk(tree) if isinstance(n,ast.FunctionDef)]
        if p.startswith('tests/'):
            old_tree=ast.parse(old)
            old_tests={n.name:ast.dump(n,include_attributes=False) for n in ast.walk(old_tree) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
            new_tests={n.name:ast.dump(n,include_attributes=False) for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
            assert all(new_tests[n]==body for n,body in old_tests.items())
            entry['unchanged_existing_tests']=len(old_tests)
            entry['added_tests']=sorted(set(new_tests)-set(old_tests))
            assert len(entry['added_tests'])==8
    review[p]=entry
    diff.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='before/'+p,tofile='after/'+p))
    out=base/'reviewed'/p;out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('xb') as f:f.write((root/p).read_bytes())
with (base/'FILE_REVIEW.json').open('x') as f:json.dump(review,f,indent=2,sort_keys=True);f.write('\n')
with (base/'SOURCE_DIFF.patch').open('x') as f:f.write(''.join(diff))
print(json.dumps(review,indent=2,sort_keys=True))
