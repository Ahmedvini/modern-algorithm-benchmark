# Exact executed commands

All recorded commands are read-only local inspection, account/session metadata, filename searches or offline byte/hash validation. No remote code, upload, build, test, GPU workload or study timing ran. Raw command JSON retains exact working directories, timestamps, stdout/stderr and exit codes.

## command_001.json

Inspect launch protocol, matrix, bundle and trust guard from actual files; read only

UTC: 2026-10-11T13:07:47.611512+00:00; cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`; exit: 0.

```sh
python3 -B - <<'PY'
import pathlib,subprocess,json
p=subprocess.run(['git','status','--short','--branch'],capture_output=True,text=True);print('git status exit',p.returncode);print(p.stdout);print(p.stderr)
for name in ['docs/CPU_GPU_COMPARISON_PROTOCOL_v1.md','scripts/run_cpu_gpu_study.py','docs/CPU_GPU_EVIDENCE_ENFORCEMENT_v1.md']:
 print('FILE',name);print(pathlib.Path(name).read_text())
for name in ['docs/studies/cpu_gpu_comparison_v1.matrix.json','docs/studies/cpu_gpu_comparison_v1.freeze.json']:
 v=json.loads(pathlib.Path(name).read_text());print('FILE',name);print(json.dumps(v,indent=2))
print('RESOURCE CSV');print(pathlib.Path('docs/studies/cpu_gpu_comparison_v1.resources.csv').read_text())
PY
sed -n '1,59p' scripts/cpu_gpu_evidence.py
sed -n '1,190p' scripts/run_cpu_gpu_pilot.py
colab exec --help
colab upload --help
```

Output: [command_001.json](command_001.json).

## command_002.json

Verify existing benchmark-t4 session identity and account billing without creating or executing a GPU workload

UTC: 2026-10-11T13:07:47.610898+00:00; cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`; exit: 0.

```sh
colab version
colab sessions
colab status --session benchmark-t4
colab usage
```

Output: [command_002.json](command_002.json).

## command_003.json

Inspect documented billing-rate interpretation and exact trust dependency before any remote execution; no credentials/workloads

UTC: 2026-10-11T13:08:14.221102+00:00; cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`; exit: 0.

```sh
cat /home/ahmedelsheikh/.local/share/uv/tools/google-colab-cli/lib/python3.12/site-packages/colab_cli/consumption.py
rg -n 'usage|consumption|balance|free|paid|subscription' /home/ahmedelsheikh/.local/share/uv/tools/google-colab-cli/lib/python3.12/site-packages/colab_cli/commands /home/ahmedelsheikh/.local/share/uv/tools/google-colab-cli/lib/python3.12/site-packages/colab_cli/client.py --glob '*.py'
cat results/raw/gpu_external_resolution_20261011T121306863461Z/REQUIRED_EXTERNAL_ARTIFACT.json
sed -n '1,110p' docs/CPU_GPU_FRAMEWORK_COMPATIBILITY_v1.md
sed -n '195,305p' scripts/run_cpu_gpu_pilot.py
```

Output: [command_003.json](command_003.json).

## command_004.json

Verify frozen inputs, current source, preserved source archive and production trust refusal; offline only

UTC: 2026-10-11T13:09:13.023269+00:00; cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`; exit: 0.

```sh
python3 -B - <<'PY'
import hashlib,json,pathlib,sys,tarfile
sys.path.insert(0,'scripts')
from cpu_gpu_protocol import load_protocol,source_manifest
from cpu_gpu_framework_compatibility import current_review
from non_timing_tests import load_manifest
import cpu_gpu_evidence
r=pathlib.Path.cwd();e=pathlib.Path("/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/benchmark_t4_diagnostics_20261011T130731794078Z");model=load_protocol();current_review(model);selection=load_manifest()
old=r/'results/raw/gpu_final_resolution_20261011T111957067481Z'
bundle=json.loads((old/'SOURCE_BUNDLE.json').read_text());archive=r/bundle['archive']
assert hashlib.sha256(archive.read_bytes()).hexdigest()==bundle['archive_sha256']
assert source_manifest()==bundle['source_sha256']
for name,digest in bundle['files_sha256'].items():assert hashlib.sha256((r/name).read_bytes()).hexdigest()==digest,name
with tarfile.open(archive,'r:gz') as t:
 members=t.getmembers();assert len(members)==217
 for m in members:
  assert m.isfile();n=m.name.removeprefix('modern-algorithm-benchmark/')
  assert hashlib.sha256(t.extractfile(m).read()).hexdigest()==bundle['files_sha256'][n]
try:cpu_gpu_evidence.approval()
except ValueError as error:approval=dict(accepted=False,error=str(error),artifact=str(cpu_gpu_evidence.APPROVAL),exists=cpu_gpu_evidence.APPROVAL.exists(),trusted_pin=cpu_gpu_evidence.TRUSTED_APPROVAL_SHA256)
else:raise AssertionError('Unexpected approval acceptance; investigate before launching')
names=sorted(n for n,v in selection['tests'].items() if v['classification']=='cpu_correctness' and not v.get('diagnostic_only'))
assert len(names)==19 and len(model['study']['cells'])==48
value=dict(protocol=model.get('protocol'),frozen_hashes_verified=True,production_anchors_verified=True,source_sha256=source_manifest(),bundle_files=217,bundle_sha256=bundle['archive_sha256'],bundle_hashes_verified=True,default_correctness_names=names,selection_policy=selection['policy'],selection_full_study_eligible=selection.get('full_study_eligible'),approval=approval,study_datasets=48,expected=model['study']['expected'],mode_names=sorted(model['study']['cells'][0]['warmup_order'][0]),gpu_build_attempted=False,tests_run=0,benchmarks_run=0)
with (e/'OFFLINE_GATES.json').open('x') as f:json.dump(value,f,indent=2,sort_keys=True)
print('Freeze/current production anchors/source/bundle all match;48 datasets and19 default test names unchanged.')
print(json.dumps(approval,indent=2));print('Source unchanged; no study launch or validation workload.')
PY
```

Output: [command_004.json](command_004.json).

## command_005.json

Look for newly available genuine approval in authorized home/configuration locations; credential stores excluded

UTC: 2026-10-11T13:09:13.237264+00:00; cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`; exit: 0.

```sh
python3 -B '/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/benchmark_t4_diagnostics_20261011T130731794078Z/search_authority.py'
```

Output: [command_005.json](command_005.json).

## Startup and final seal

STARTUP.md records the complete instruction/latest-audit/log read and prior-seal verification/bootstrap, terminal exit0 each. Startup output was observed rather than saved separately. Git status executed through subprocess.run in the first inspection returned128: no Git metadata; inspection continued without initialization. It is printed explicitly in the command log, whose enclosing shell exit was0.

A local terminal copy-only helper (exit0) copied the already inspected search_authority.py into this new evidence directory; the old helper was not edited. apply_patch created this finalizer only under the new directory. No source files changed.

Final command: `python3 -B results/raw/benchmark_t4_diagnostics_20261011T130731794078Z/finalize.py`; it only reads/hashes files and writes this additive audit/seal. Assertion results are in FINALIZER_STATUS.json; the terminal reports its actual exit status.
