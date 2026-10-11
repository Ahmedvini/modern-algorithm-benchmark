import ast
import difflib
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,'scripts')
from cpu_gpu_protocol import source_manifest, load_protocol, verify_source_extension
from cpu_gpu_provenance import trusted_source_anchors, validate_retained_source
from non_timing_tests import load_manifest
base=Path(__file__).resolve().parent
before=json.loads((base/'BEFORE.json').read_text())
current=source_manifest()
changed=sorted(p for p,h in before['current_source_sha256'].items() if current.get(p)!=h)
added=sorted(set(current)-set(before['current_source_sha256']))
expected=['scripts/analyze_cpu_gpu.py','scripts/run_cpu_gpu_pilot.py','scripts/validate_cpu_gpu_pilot.py','tests/test_cpu_gpu_comparison.py']
assert changed==expected,changed
expected_added=['scripts/cpu_gpu_provenance.py','scripts/non_timing_tests.py','tests/fixtures/cpu_gpu_provenance_reproducer.py','tests/test_cpu_gpu_safety.py']
assert added==expected_added,added
for name in changed+added:
    text=Path(name).read_text()
    ast.parse(text,filename=name)
    compile(text,name,'exec')
model=load_protocol()
validate_retained_source(verify_source_extension(model),model)
trusted_source_anchors(model)
load_manifest()
pilot=base/'PILOT_REANALYSIS.json'
old=Path('results/raw/cpu_gpu_tooling_review_20261010T125855526277Z/PILOT_REANALYSIS.json')
assert pilot.read_bytes()==old.read_bytes()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(pilot)=='07e69e2e0c8853f93d3f3da895337b5e4b72e5e2dd0ff0577db3cbd1f7053a22'
patch=[]
for path in sorted((base/'before').rglob('*')):
    if path.is_file():
        name=str(path.relative_to(base/'before'))
        patch.extend(difflib.unified_diff(path.read_text().splitlines(True),Path(name).read_text().splitlines(True),fromfile='before/'+name,tofile='after/'+name))
with (base/'REVIEWED_CHANGES.patch').open('x') as stream:stream.write(''.join(patch))
result=dict(changed_source=changed,added_source=added,syntax_files_checked=len(changed+added),
    source_manifest_exact=True,independent_frozen_provenance=True,pilot_summary_byte_identical=True,
    pilot_summary_sha256=sha(pilot),benchmark_execution=False,gpu_execution=False)
with (base/'STATIC_REVIEW.json').open('x') as stream:json.dump(result,stream,indent=2,sort_keys=True);stream.write('\n')
print(json.dumps(result,indent=2,sort_keys=True))
