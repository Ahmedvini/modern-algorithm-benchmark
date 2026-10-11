"""Retain exact intended changes and inspected source identities; no workloads."""
import ast
import difflib
import hashlib
import json
from pathlib import Path
root=Path.cwd();base=Path(__file__).resolve().parent
before=json.loads((base/'BEFORE.json').read_text())['project_sha256']
paths=['scripts/ctest_build_guard.py','scripts/non_timing_tests.py','tests/ctest_fixture.py',
       'tests/test_ctest_build_guard.py','tests/test_cpu_gpu_safety.py','tests/test_cpu_gpu_comparison.py',
       'docs/NON_TIMING_TEST_SELECTION_v1.json','README.md','docs/ROADMAP.md','docs/AUDIT.md',
       'docs/CTEST_BUILD_GUARD_v1.md']
report={};diff=[]
for name in paths:
    p=root/name;raw=p.read_bytes();digest=hashlib.sha256(raw).hexdigest()
    assert digest!=before.get(name),name
    report[name]=dict(before_sha256=before.get(name),after_sha256=digest,lines=len(raw.splitlines()))
    if p.suffix=='.py':
        tree=ast.parse(raw,filename=name)
        report[name]['functions']=[dict(name=n.name,line=n.lineno) for n in ast.walk(tree)
                                   if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))]
    old=base/'before'/name
    if old.is_file() or name not in before:
        diff.extend(difflib.unified_diff(old.read_text().splitlines(True) if old.is_file() else [],
                                        raw.decode().splitlines(True),fromfile='before/'+name,tofile='after/'+name))
    else:
        # Documentation before-images were hashed but not copied. Preserve the
        # final full bytes, without pretending to reconstruct a prior diff.
        copy=base/'reviewed'/name;copy.parent.mkdir(parents=True,exist_ok=True)
        with copy.open('xb') as f:f.write(raw)
with (base/'FILE_REVIEW.json').open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
with (base/'SOURCE_DIFF.patch').open('x') as f:f.write(''.join(diff))
for name,entry in report.items():print(('ADDED ' if entry['before_sha256'] is None else 'MODIFIED ')+name)
