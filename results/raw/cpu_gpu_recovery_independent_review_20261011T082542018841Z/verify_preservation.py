"""Review preservation check: standard-library file operations only."""
import hashlib, json
from pathlib import Path

ROOT = Path.cwd()
EVIDENCE = Path(__file__).resolve().parent
def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1048576), b''):
            h.update(chunk)
    return h.hexdigest()
def read(path):
    return json.loads(path.read_text())
baseline = read(EVIDENCE/'BASELINE.json')
historical = {str(p.relative_to(ROOT)): sha(p) for p in sorted((ROOT/'results').rglob('*'))
              if p.is_file() and not p.is_relative_to(EVIDENCE)}
paths = [ROOT/p for p in ['AGENTS.md', 'README.md', 'CMakeLists.txt']]
for directory in ['cmake','docs','include','scripts','src','tests','third_party']:
    paths.extend(p for p in (ROOT/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
project = {str(p.relative_to(ROOT)):sha(p) for p in sorted(set(paths))}
names = {'CMakeCache.txt','CTestTestfile.cmake','DartConfiguration.tcl','Makefile','compile_commands.json'}
build = {str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'build').rglob('*')) if p.is_file() and p.name in names}
comparisons = {}
for label, current, expected in [
    ('historical_results',historical,baseline['results_sha256']),
    ('project',project,baseline['project_sha256']),
    ('build_metadata',build,baseline['build_metadata_sha256'])]:
    comparisons[label] = dict(before_count=len(expected), after_count=len(current),
        removed=sorted(set(expected)-set(current)), added=sorted(set(current)-set(expected)),
        changed=sorted(p for p in set(expected)&set(current) if expected[p]!=current[p]),
        exact_membership_and_sha256_match=current==expected)
for field in ['frozen_sha256','protected_sha256']:
    expected = baseline[field]
    comparisons[field] = dict(count=len(expected), changed=[p for p,h in expected.items()
        if not (ROOT/p).is_file() or sha(ROOT/p)!=h])
recovery = ROOT/'results/raw/cpu_gpu_recovery_20261011T075800444473Z'
comparisons['recovery_seal_unchanged'] = sha(recovery/'FINAL_INTEGRITY.json')==baseline['recovery_seal_sha256']
assert all(c['exact_membership_and_sha256_match'] for c in
           [comparisons['historical_results'],comparisons['project'],comparisons['build_metadata']]), comparisons
assert not comparisons['frozen_sha256']['changed'] and not comparisons['protected_sha256']['changed'], comparisons
assert comparisons['recovery_seal_unchanged'], comparisons
with (EVIDENCE/'FINAL_PRESERVATION.json').open('x') as stream:
    json.dump(comparisons,stream,indent=2,sort_keys=True); stream.write('\n')
print(json.dumps(comparisons,indent=2,sort_keys=True))
