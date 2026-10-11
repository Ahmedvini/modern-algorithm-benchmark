"""Verify downloaded resource evidence independently; no GPU work launched."""
import json
from pathlib import Path, PurePosixPath
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[3]
E = Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts'))
from cpu_gpu_protocol import load_protocol, verify_source_extension, sha
from analyze_cpu_gpu import validate_resources
from run_cpu_gpu_pilot import environment_gate

def save(name, value):
    with (E/name).open('x') as stream:
        json.dump(value,stream,indent=2,sort_keys=True)
        stream.write('\n')

remote = json.loads((E/'commands/remote_resource_validation.json').read_text())
result = json.loads(next(line.removeprefix('REMOTE_RESULT ') for line in remote['stdout'].splitlines() if line.startswith('REMOTE_RESULT ')))
assert remote['exit_code']==0 and result['exit_code']==0
assert sha(E/'workspace_evidence.tar.gz') == result['sha256']
destination = E/'downloaded'
destination.mkdir()
with tarfile.open(E/'workspace_evidence.tar.gz') as tar:
    members = tar.getmembers()
    for member in members:
        p=PurePosixPath(member.name)
        assert not p.is_absolute() and '..' not in p.parts and p.parts[0]=='evidence'
        assert member.isfile() or member.isdir()
    tar.extractall(destination,filter='data')
evidence = destination/'evidence'
manifest=json.loads((evidence/'SHA256.json').read_text())
assert set(manifest)=={str(p.relative_to(evidence)) for p in evidence.rglob('*') if p.is_file() and p.name!='SHA256.json'}
for name,digest in manifest.items():
    assert sha(evidence/name)==digest,name
assert json.loads((evidence/'COMPLETE.json').read_text())==dict(complete=True,exit_code=0,size=65537,benchmark_trials=0)
assert not (evidence/'FAILED.json').exists()
commands={}
for name in ['gpu_initial','gpu_processes_initial','configure','build','describe','resources_65537','gpu_after']:
    record=json.loads((evidence/(name+'.json')).read_text())
    assert record['exit_code']==0,name
    commands[name]=dict(argv=record['argv'],exit_code=record['exit_code'])
resource=json.loads((evidence/'workspace_queries.json').read_text())
assert resource==json.loads(json.loads((evidence/'resources_65537.json').read_text())['stdout'])
validate_resources(resource,65537)
environment=json.loads((evidence/'environment.json').read_text())
environment_gate(environment)
freeze=json.loads((E/'freeze_verified.json').read_text())
for name,digest in freeze['files'].items():assert sha(ROOT/name)==digest
assert json.loads((evidence/'frozen_sha256.json').read_text())==freeze['files']
current=verify_source_extension(load_protocol())
assert current==json.loads((E/'source_before.json').read_text())
assert current==json.loads((evidence/'source_before.json').read_text())
old=json.loads((ROOT/'results/raw/cpu_gpu_pilot_20261010T001232473460Z/remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/dependency_sha256.json').read_text())['files']
tree=json.loads((evidence/'installed_cccl_tree_sha256.json').read_text())
assert tree==old,'installed dependency tree differs from accepted pilot'
warnings=[line for line in json.loads((evidence/'build.json').read_text())['stderr'].splitlines() if 'warning:' in line]
assert all('style of line directive is a GCC extension' in line for line in warnings),'new warning category'
save('INDEPENDENT_VERIFICATION.json',dict(complete=True,archive_sha256=result['sha256'],
    archive_members=len(members),hashed_evidence_files=len(manifest),
    installed_dependency_files=len(tree),dependency_tree_matches_pilot=True,
    frozen_files_match=True,production_source_unchanged=True,resource_gate_passed=True,
    warning_count=len(warnings),warning_category='nvcc generated GCC line-directive extension only',
    commands=commands,benchmark_trials=0))
print(json.dumps(resource,indent=2))
print('Independent verification passed; warnings',len(warnings),'dependency files',len(tree))
