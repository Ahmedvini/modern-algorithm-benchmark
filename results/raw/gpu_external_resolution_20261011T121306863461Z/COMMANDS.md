# Commands and observed status

All commands were inspection, filename searches, offline byte/hash validation or audit creation. No tests, builds, CTest, GPU work, allocations or study trials ran.

## command_001.json

Inspect current repository identity and actual trust enforcement/approved record schema; read only

UTC: 2026-10-11T12:13:23.828926+00:00; cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`; shell exit: 0.

```sh
git status --short --branch
sed -n '1,150p' scripts/cpu_gpu_evidence.py
sed -n '290,440p' scripts/cpu_gpu_evidence.py
cat docs/CPU_GPU_EVIDENCE_ENFORCEMENT_v1.md
cat docs/CPU_GPU_FRAMEWORK_COMPATIBILITY_v1.md
cat README.md
cat docs/ROADMAP.md
cat docs/EXPERIMENT_PROTOCOL.md
```

Full stdout/stderr: [command_001.json](command_001.json).

## command_002.json

Check current supported Colab sessions and account capacity without allocation

UTC: 2026-10-11T12:13:23.829693+00:00; cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`; shell exit: 0.

```sh
colab version
colab sessions
colab usage
colab new --help
colab --help
```

Full stdout/stderr: [command_002.json](command_002.json).

## command_003.json

Inspect exact independent authority dependency, positive/adversarial tests, supported free-compute paths, and existing bundle identities; no workloads

UTC: 2026-10-11T12:14:23.505106+00:00; cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`; shell exit: 0.

```sh
nl -ba docs/CPU_GPU_EVIDENCE_ENFORCEMENT_v1.md | sed -n '10,65p'
rg -n 'approval|TRUSTED_APPROVAL|mock.patch|patch.object|valid_bundle|positive' tests/test_evidence_enforcement.py scripts/cpu_gpu_evidence.py scripts/cpu_gpu_framework_compatibility.py
rg -n 'colab|free|trust|approval|signature' docs/CPU_GPU_COMPARISON_DRIVER_v1.md docs/CUDA_EXECUTION_GUIDE_v1.md docs/CPU_GPU_FRAMEWORK_COMPATIBILITY_v1.md
sed -n '1,200p' tests/test_evidence_enforcement.py
cat results/raw/gpu_final_resolution_20261011T111957067481Z/EXTERNAL_DEPENDENCIES.md
cat results/raw/gpu_final_resolution_20261011T111957067481Z/SOURCE_BUNDLE.json | head -15
```

Full stdout/stderr: [command_003.json](command_003.json).

## command_004.json

Search additional authorized home/configuration locations for real approval/trust artifacts; credentials excluded

UTC: 2026-10-11T12:14:23.506333+00:00; cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`; shell exit: 0.

```sh
python3 -B '/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/gpu_external_resolution_20261011T121306863461Z/search_authority.py'
```

Full stdout/stderr: [command_004.json](command_004.json).

## command_005.json

Inspect supplementary configuration filenames and distinguish existing driver anchor from missing current independent approval; no credentials or workloads

UTC: 2026-10-11T12:14:58.996184+00:00; cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`; shell exit: 0.

```sh
python3 -B - <<'PY'
import hashlib,json,os,pathlib
e=pathlib.Path("/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/gpu_external_resolution_20261011T121306863461Z")
roots=[pathlib.Path.home()/'.local/share',pathlib.Path('/etc'),pathlib.Path('/usr/local/etc'),pathlib.Path('/opt'),pathlib.Path('/mnt'),pathlib.Path('/media')]
exclude={'google-colab-cli','uv','pip','Trash','containers','node_modules','site-packages','keyrings','password-store','.git','build','sessions','history','colab-cli','chromium','google-chrome'}
out=[];found=[];errors=[]
for root in roots:
 n=0;ds=0
 def err(exc):errors.append({'root':str(root),'path':str(exc.filename),'error':type(exc).__name__})
 if root.exists():
  for f,dirs,files in os.walk(root,followlinks=False,onerror=err):
   ds+=1;dirs[:]=[d for d in dirs if d not in exclude and not (pathlib.Path(f)/d).is_symlink()]
   for name in files:
    n+=1
    if name=='CPU_GPU_EVIDENCE_REVIEW_v1.json' or ('cpu_gpu' in name.lower() and any(s in name.lower() for s in ['trust','approval','review'])):found.append(str(pathlib.Path(f)/name))
 out.append(dict(root=str(root),exists=root.exists(),directories=ds,filenames=n))
v=dict(roots=out,candidates=found,errors=errors,excluded_directory_names=sorted(exclude),contents_read=False,scope='Supplementary filename-only search; package stores and credential/session directories excluded.')
with (e/'SUPPLEMENTARY_CONFIGURATION_SEARCH.json').open('x') as f:json.dump(v,f,indent=2,sort_keys=True)
print(json.dumps(v,indent=2))
p=pathlib.Path('docs/CPU_GPU_DRIVER_REVIEW_v1.json');d=json.loads(p.read_text())
print('Existing driver review SHA256',hashlib.sha256(p.read_bytes()).hexdigest());print('Existing driver review keys',sorted(d));print(json.dumps({k:v for k,v in d.items() if k!='source_sha256'},indent=2))
PY
sed -n '1,85p' scripts/cpu_gpu_framework_compatibility.py
sed -n '264,282p' tests/test_evidence_enforcement.py
sed -n '310,338p' tests/test_evidence_enforcement.py
rg -n 'DRIVER_REVIEW|TRUSTED_REVIEW|REVIEW_SHA256' scripts/cpu_gpu_protocol.py scripts/cpu_gpu_provenance.py scripts/cpu_gpu_framework_compatibility.py
```

Full stdout/stderr: [command_005.json](command_005.json).

## command_006.json

Verify frozen/source identities and existing bundle without regeneration; invoke only pure production approval check

UTC: 2026-10-11T12:15:31.218105+00:00; cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`; shell exit: 0.

```sh
python3 -B - <<'PY'
import hashlib,json,pathlib,sys,tarfile
sys.path.insert(0,'scripts')
from cpu_gpu_protocol import load_protocol,source_manifest
from cpu_gpu_framework_compatibility import current_review
from non_timing_tests import load_manifest
import cpu_gpu_evidence as guard
r=pathlib.Path.cwd();e=pathlib.Path("/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/gpu_external_resolution_20261011T121306863461Z");old=r/'results/raw/gpu_final_resolution_20261011T111957067481Z'
model=load_protocol();review=current_review(model);selection=load_manifest()
bundle=json.loads((old/'SOURCE_BUNDLE.json').read_text());archive=r/bundle['archive']
assert hashlib.sha256(archive.read_bytes()).hexdigest()==bundle['archive_sha256']
assert bundle['source_sha256']==source_manifest()
for name,d in bundle['files_sha256'].items():assert hashlib.sha256((r/name).read_bytes()).hexdigest()==d,name
with tarfile.open(archive,'r:gz') as t:
 members=t.getmembers();assert len(members)==217
 for m in members:
  assert m.isfile();n=m.name.removeprefix('modern-algorithm-benchmark/')
  assert n in bundle['files_sha256'] and hashlib.sha256(t.extractfile(m).read()).hexdigest()==bundle['files_sha256'][n]
try:guard.approval()
except ValueError as exc:approval=dict(accepted=False,message=str(exc),artifact=str(guard.APPROVAL),exists=guard.APPROVAL.exists(),trusted_pin=guard.TRUSTED_APPROVAL_SHA256)
else:raise AssertionError('Unexpected approval acceptance')
names=sorted(n for n,v in selection['tests'].items() if v['classification']=='cpu_correctness' and not v.get('diagnostic_only'))
assert len(names)==19
value=dict(frozen_inputs_verified=True,compatible_protected_anchors_verified=True,
 source_bundle_reused=True,bundle_sha256=bundle['archive_sha256'],bundle_files=217,
 bundle_actual_bytes_verified=True,source_sha256=bundle['source_sha256'],
 default_test_names=names,selection_policy=selection['policy'],
 selection_full_study_eligible=selection.get('full_study_eligible'),
 approval=approval,study_launched=False,measured_trials=0,warmups=0,gpu_workloads=0,
 new_builds=0,new_tests=0,new_cloud_assignments=0,
 note='Passing offline inspection does not constitute study eligibility; actual production approval refusal retained.')
with (e/'OFFLINE_VERIFICATION.json').open('x') as f:json.dump(value,f,indent=2,sort_keys=True)
print('Frozen inputs, protected compatible anchors, current source and217 archive members match actual bytes.')
print(json.dumps(approval,indent=2));print('Exact19 default test names unchanged; no tests launched.')
PY
```

Full stdout/stderr: [command_006.json](command_006.json).

## command_007.json

Close discovery gap for generically named approval/review/trust configuration; exclude secret/session/credential material

UTC: 2026-10-11T12:23:38.132151+00:00; cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`; shell exit: 0.

```sh
python3 -B - <<'PY'
import json,os,pathlib
e=pathlib.Path("/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/gpu_external_resolution_20261011T121306863461Z");home=pathlib.Path.home()
roots=[home/'.config',home/'.agents',home/'.codex',home/'.local/share',pathlib.Path('/etc'),pathlib.Path('/usr/local/etc')]
exclude={'.cache','.git','node_modules','site-packages','uv','pip','Trash','sessions','history','keyrings','password-store','colab-cli','google-colab-cli','chromium','google-chrome','Code','Code - Insiders','Cursor','mozilla','BraveSoftware'}
candidates=[];matches=[];errors=[];counts=[]
for root in roots:
 count=0
 if not root.exists():continue
 def error(exc):errors.append({'path':str(exc.filename),'error':type(exc).__name__})
 for folder,dirs,names in os.walk(root,followlinks=False,onerror=error):
  dirs[:]=[d for d in dirs if d not in exclude and not (pathlib.Path(folder)/d).is_symlink()]
  for n in names:
   count+=1;low=n.lower();p=pathlib.Path(folder)/n
   if not any(w in low for w in ['approval','review','trust','benchmark','mab_']):continue
   if any(w in low for w in ['token','oauth','credential','cookie','private','auth','session','account']):continue
   if p.suffix.lower() not in ['.json','.yaml','.yml','.toml','.pub','.pem']:continue
   item=dict(file=str(p),contents_read=False)
   if not p.is_symlink() and p.suffix=='.json' and p.stat().st_size<=1048576:
    try:
     raw=p.read_text();v=json.loads(raw);item['contents_read']=True
     if any(w in raw for w in ['cpu_gpu_evidence_enforcement_v1','CPU_GPU_EVIDENCE_REVIEW_v1','modern-algorithm-benchmark','cpu_gpu_comparison_v1']):
      item['project_reference']=True;matches.append(str(p))
    except (OSError,ValueError,UnicodeError) as exc:item['parse_error']=type(exc).__name__
   candidates.append(item)
 counts.append(dict(root=str(root),filenames=count))
result=dict(scope='Generic non-secret approval/review/trust configuration filenames, supplementary to exact project-name search',counts=counts,candidates=candidates,project_matches=matches,errors=errors,excluded_directory_names=sorted(exclude),credential_files_read=False)
with (e/'GENERIC_CONFIGURATION_SEARCH.json').open('x') as f:json.dump(result,f,indent=2,sort_keys=True)
print(json.dumps(result,indent=2))
PY
```

Full stdout/stderr: [command_007.json](command_007.json).

## command_008.json

Statically parse preservation-only finalizer before final sealing; no helper execution or workload

UTC: 2026-10-11T12:24:00.719566+00:00; cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`; shell exit: 0.

```sh
python3 -B -c "import ast,pathlib; p=pathlib.Path('/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/gpu_external_resolution_20261011T121306863461Z/finalize.py'); t=ast.parse(p.read_text()); assert not any(isinstance(n,ast.Import) and any(a.name in ['subprocess','os'] for a in n.names) for n in ast.walk(t)); print('Finalizer AST parsed; only hashlib/json/pathlib imports; no subprocess/workload execution.')"
```

Full stdout/stderr: [command_008.json](command_008.json).

## Startup and finalization

STARTUP.md records the first complete instructions/audit/log read and prior-seal verification/bootstrap commands, both terminal exit0. Raw startup output was observed in the terminal rather than retained. The first recorded compound inspection contains `git status --short --branch` exit128 (Git metadata absent), though the final shell exit0; it was not repaired or initialized. Supplementary searches retained nine PermissionError entries and did not escalate or read those directories. No credential contents were read.

Available-tool metadata was filtered for GPU/Colab/browser/notebook capabilities: only a worktree-status tool matched; no alternate runtime/browser capability was invoked. This metadata inspection is not a terminal command and has no shell exit code.

Final command: `python3 -B results/raw/gpu_external_resolution_20261011T121306863461Z/finalize.py`. This helper only reads/hashes files and creates additive audit records; no subprocess or workload. Successful assertions are retained in FINALIZER_STATUS.json; actual terminal exit status must be observed, not inferred from this document.
