# Commands executed during this review

All statuses below are 0. Only local reads/text parsing/hashing and exclusive writes in this new evidence directory occurred. No tests, CTest, configure/build, GPU/resource commands or workloads were invoked.

Wrapper for each JSON record: `python3 -B results/raw/cpu_gpu_prelaunch_review_20261011T012430643251Z/record.py NAME SCOPE TIMEOUT CHILD_ARGV...`.
Per-command JSON preserves the exact child argv, cwd, scope, timestamps, stdout/stderr and exit status. URL-shaped text is redacted by the copied recorder; original immutable input files remain authoritative.

## Control command

Exit: 0; safety: Read-only local hashing; exclusive creation of new review BEFORE.json

```bash
python3 -B - <<'PY'
import datetime,hashlib,json
from pathlib import Path
r=Path.cwd();e=r/'results/raw'/('cpu_gpu_prelaunch_review_'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'));e.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
prior=r/'results/raw/isolated_colab_revalidation_20261011T011459127026Z'
b=json.loads((prior/'BEFORE.json').read_text())
b={'prior_results_sha256':{str(p.relative_to(r)):sha(p) for p in sorted((r/'results').rglob('*')) if p.is_file() and not p.is_relative_to(e)},'project_sha256':b['project_sha256'],'build_metadata_sha256':b['build_metadata_sha256'],'scope':'read-only review; no tests, build, CTest, resource commands or GPU work'}
with (e/'BEFORE.json').open('x') as f:json.dump(b,f,indent=2,sort_keys=True);f.write('\n')
print(e.relative_to(r));print('historical_results',len(b['prior_results_sha256']))
PY
```

## Control command

Exit: 0; safety: Exclusive evidence-only recorder copy

```bash
python3 -B - <<'PY'
from pathlib import Path
old=Path('results/raw/isolated_colab_revalidation_20261011T011459127026Z/record.py');new=Path('results/raw/cpu_gpu_prelaunch_review_20261011T012430643251Z/record.py')
with new.open('xb') as f:f.write(old.read_bytes())
print('Exclusive evidence-only recorder created')
PY
```

## Control command

Exit: 0; safety: Read-only working-directory identification

```bash
pwd
```

## Control command

Exit: 0; safety: Exclusive creation of evidence-only static inspection program

```bash
python3 -B - <<'PY'
from pathlib import Path
p=Path('results/raw/cpu_gpu_prelaunch_review_20261011T012430643251Z/inspect_retained.py')
code=r'''import collections,hashlib,json,re
from pathlib import Path
R=Path.cwd(); E=Path(__file__).resolve().parent
OLD=R/'results/raw/isolated_colab_revalidation_20261011T011459127026Z'
V=OLD/'remote_evidence/validation'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def verify(mapping,root):
    bad=[k for k,v in mapping.items() if not (root/k).is_file() or sha(root/k)!=v]
    assert not bad,bad
    return len(mapping)
out={}
seal=load(OLD/'FINAL_INTEGRITY.json')['evidence_sha256']
out['isolated_seal_verified']=verify(seal,OLD)
assert set(seal)=={str(p.relative_to(OLD)) for p in OLD.rglob('*') if p.is_file() and p.name!='FINAL_INTEGRITY.json'}
remote=load(V/'EVIDENCE_SHA256.json');out['remote_seal_verified']=verify(remote,V)
assert set(remote)=={str(p.relative_to(V)) for p in V.rglob('*') if p.is_file() and p.name!='EVIDENCE_SHA256.json'}
source=load(OLD/'SOURCE_IDENTITY.json')['files_sha256']
out['transferred_source_matches_local']=verify(source,R)
assert (V/'SOURCE_AFTER.json').read_bytes()==(OLD/'SOURCE_IDENTITY.json').read_bytes()
freeze=load(R/'docs/studies/cpu_gpu_comparison_v1.freeze.json')
out['freeze_members_verified']=verify(freeze['files_sha256'],R)
out['freeze_hashes']=freeze['files_sha256']
matrix=load(R/'docs/studies/cpu_gpu_comparison_v1.matrix.json')
anchors=matrix['source_at_freeze_sha256']
out['anchors_exact_matches']=sum((R/k).is_file() and sha(R/k)==v for k,v in anchors.items())
out['anchor_differences']={k:{'frozen':v,'current':sha(R/k)} for k,v in anchors.items() if sha(R/k)!=v}
out['driver_review']=load(R/'docs/CPU_GPU_DRIVER_REVIEW_v1.json')
out['cub_pin']=load(R/'third_party/cub/UPSTREAM.json')
out['production_adapter_sha256']=sha(R/'src/cuda/cub_sort.cu')
before=load(E/'BEFORE.json')
out['project_files_verified']=verify(before['project_sha256'],R)
out['build_metadata_verified']=verify(before['build_metadata_sha256'],R)
lines=(V/'build.stderr.txt').read_text().splitlines()
warnings=[{'log_line':i+1,'diagnostic':line,'context':lines[i+1:i+3]} for i,line in enumerate(lines) if 'warning:' in line]
out['warning_count']=len(warnings)
out['warning_categories']=dict(collections.Counter(x['diagnostic'].split('warning:',1)[1].strip() for x in warnings))
out['warning_locations']=dict(collections.Counter(re.sub(r':\d+:\d+: warning:.*','',x['diagnostic']) for x in warnings))
out['generated_marker_blocks']=[x for x in warnings if '.cudafe1.' in x['diagnostic']]
out['error_lines']=[{'line':i+1,'text':s} for i,s in enumerate(lines) if re.search(r'\berror:|fatal error',s)]
out['cuda_compile_commands']=[x for x in load(V/'compile_commands.json') if x['file'].endswith('.cu')]
out['source_line_directives']={}
for f in ['src/cuda/comparison_resources.cu','src/cuda/cub_sort.cu','src/cuda/cub_timing.cu']:
    out['source_line_directives'][f]=[{'line':i+1,'text':s} for i,s in enumerate((R/f).read_text().splitlines()) if re.match(r'\s*#\s*(?:line\b|\d)',s)]
result=load(V/'RESULT.json')
out['executed_records']=result['records']
out['coverage']={k:result[k] for k in ['cpu_correctness','cuda_correctness','study_eligible','validation_passed','ctest_invocations','benchmarks','timing_trials']}
env=load(V/'ENVIRONMENT.json')
blocks=env['cpuinfo'].strip().split('\n\n')
out['environment']={k:env[k] for k in ['affinity','cpu_count','disk','environment','platform','python']}
out['cpu_topology']=[{k:v.strip() for line in b.splitlines() if ':' in line for k,v in [line.split(':',1)] if k.strip() in ['processor','model name','cpu MHz','physical id','siblings','core id','cpu cores']} for b in blocks]
out['meminfo_bytes']={m.group(1):int(m.group(2))*1024 for s in env['meminfo'].splitlines() if (m:=re.match(r'(MemTotal|MemAvailable|SwapTotal):\s+(\d+) kB',s))}
out['frozen_resources']=matrix['resources']
out['frozen_launch_gates']=matrix['launch_gates']
out['frozen_openmp_policy']=matrix['openmp_policy']
out['matrix_counts']={k:matrix[k] for k in ['warmups','repetitions','study','pilot']}
with (E/'INDEPENDENT_FINDINGS.json').open('x') as f:json.dump(out,f,indent=2,sort_keys=True);f.write('\n')
with (E/'WARNING_DIAGNOSTICS.json').open('x') as f:json.dump(warnings,f,indent=2);f.write('\n')
print(json.dumps({k:out[k] for k in ['isolated_seal_verified','remote_seal_verified','transferred_source_matches_local','freeze_members_verified','anchors_exact_matches','anchor_differences','project_files_verified','build_metadata_verified','warning_count','warning_categories','generated_marker_blocks','error_lines','coverage','environment','cpu_topology','meminfo_bytes']},indent=2))
'''
with p.open('x') as f:f.write(code)
print('Created evidence-only static inspection program')
PY
```

## Control command

Exit: 0; safety: Exclusive creation of command-provenance JSON in new review directory

```bash
python3 -B -c 'import json;from pathlib import Path;p=Path("results/raw/cpu_gpu_prelaunch_review_20261011T012430643251Z/CONTROL_COMMANDS.json");f=p.open('"'"'x'"'"');json.dump(json.loads("[{\"command\":\"python3 -B - <<'"'"'PY'"'"'\\nimport datetime,hashlib,json\\nfrom pathlib import Path\\nr=Path.cwd();e=r/'"'"'results/raw'"'"'/('"'"'cpu_gpu_prelaunch_review_'"'"'+datetime.datetime.now(datetime.timezone.utc).strftime('"'"'%Y%m%dT%H%M%S%fZ'"'"'));e.mkdir()\\ndef sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()\\nprior=r/'"'"'results/raw/isolated_colab_revalidation_20261011T011459127026Z'"'"'\\nb=json.loads((prior/'"'"'BEFORE.json'"'"').read_text())\\nb={'"'"'prior_results_sha256'"'"':{str(p.relative_to(r)):sha(p) for p in sorted((r/'"'"'results'"'"').rglob('"'"'*'"'"')) if p.is_file() and not p.is_relative_to(e)},'"'"'project_sha256'"'"':b['"'"'project_sha256'"'"'],'"'"'build_metadata_sha256'"'"':b['"'"'build_metadata_sha256'"'"'],'"'"'scope'"'"':'"'"'read-only review; no tests, build, CTest, resource commands or GPU work'"'"'}\\nwith (e/'"'"'BEFORE.json'"'"').open('"'"'x'"'"') as f:json.dump(b,f,indent=2,sort_keys=True);f.write('"'"'\\\\n'"'"')\\nprint(e.relative_to(r));print('"'"'historical_results'"'"',len(b['"'"'prior_results_sha256'"'"']))\\nPY\",\"exit_code\":0,\"scope\":\"Read-only local hashing; exclusive creation of new review BEFORE.json\"},{\"command\":\"python3 -B - <<'"'"'PY'"'"'\\nfrom pathlib import Path\\nold=Path('"'"'results/raw/isolated_colab_revalidation_20261011T011459127026Z/record.py'"'"');new=Path('"'"'results/raw/cpu_gpu_prelaunch_review_20261011T012430643251Z/record.py'"'"')\\nwith new.open('"'"'xb'"'"') as f:f.write(old.read_bytes())\\nprint('"'"'Exclusive evidence-only recorder created'"'"')\\nPY\",\"exit_code\":0,\"scope\":\"Exclusive evidence-only recorder copy\"},{\"command\":\"pwd\",\"exit_code\":0,\"scope\":\"Read-only working-directory identification\"},{\"command\":\"python3 -B - <<'"'"'PY'"'"'\\nfrom pathlib import Path\\np=Path('"'"'results/raw/cpu_gpu_prelaunch_review_20261011T012430643251Z/inspect_retained.py'"'"')\\ncode=r'"'"''"'"''"'"'import collections,hashlib,json,re\\nfrom pathlib import Path\\nR=Path.cwd(); E=Path(__file__).resolve().parent\\nOLD=R/'"'"'results/raw/isolated_colab_revalidation_20261011T011459127026Z'"'"'\\nV=OLD/'"'"'remote_evidence/validation'"'"'\\ndef sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()\\ndef load(p):return json.loads(p.read_text())\\ndef verify(mapping,root):\\n    bad=[k for k,v in mapping.items() if not (root/k).is_file() or sha(root/k)!=v]\\n    assert not bad,bad\\n    return len(mapping)\\nout={}\\nseal=load(OLD/'"'"'FINAL_INTEGRITY.json'"'"')['"'"'evidence_sha256'"'"']\\nout['"'"'isolated_seal_verified'"'"']=verify(seal,OLD)\\nassert set(seal)=={str(p.relative_to(OLD)) for p in OLD.rglob('"'"'*'"'"') if p.is_file() and p.name!='"'"'FINAL_INTEGRITY.json'"'"'}\\nremote=load(V/'"'"'EVIDENCE_SHA256.json'"'"');out['"'"'remote_seal_verified'"'"']=verify(remote,V)\\nassert set(remote)=={str(p.relative_to(V)) for p in V.rglob('"'"'*'"'"') if p.is_file() and p.name!='"'"'EVIDENCE_SHA256.json'"'"'}\\nsource=load(OLD/'"'"'SOURCE_IDENTITY.json'"'"')['"'"'files_sha256'"'"']\\nout['"'"'transferred_source_matches_local'"'"']=verify(source,R)\\nassert (V/'"'"'SOURCE_AFTER.json'"'"').read_bytes()==(OLD/'"'"'SOURCE_IDENTITY.json'"'"').read_bytes()\\nfreeze=load(R/'"'"'docs/studies/cpu_gpu_comparison_v1.freeze.json'"'"')\\nout['"'"'freeze_members_verified'"'"']=verify(freeze['"'"'files_sha256'"'"'],R)\\nout['"'"'freeze_hashes'"'"']=freeze['"'"'files_sha256'"'"']\\nmatrix=load(R/'"'"'docs/studies/cpu_gpu_comparison_v1.matrix.json'"'"')\\nanchors=matrix['"'"'source_at_freeze_sha256'"'"']\\nout['"'"'anchors_exact_matches'"'"']=sum((R/k).is_file() and sha(R/k)==v for k,v in anchors.items())\\nout['"'"'anchor_differences'"'"']={k:{'"'"'frozen'"'"':v,'"'"'current'"'"':sha(R/k)} for k,v in anchors.items() if sha(R/k)!=v}\\nout['"'"'driver_review'"'"']=load(R/'"'"'docs/CPU_GPU_DRIVER_REVIEW_v1.json'"'"')\\nout['"'"'cub_pin'"'"']=load(R/'"'"'third_party/cub/UPSTREAM.json'"'"')\\nout['"'"'production_adapter_sha256'"'"']=sha(R/'"'"'src/cuda/cub_sort.cu'"'"')\\nbefore=load(E/'"'"'BEFORE.json'"'"')\\nout['"'"'project_files_verified'"'"']=verify(before['"'"'project_sha256'"'"'],R)\\nout['"'"'build_metadata_verified'"'"']=verify(before['"'"'build_metadata_sha256'"'"'],R)\\nlines=(V/'"'"'build.stderr.txt'"'"').read_text().splitlines()\\nwarnings=[{'"'"'log_line'"'"':i+1,'"'"'diagnostic'"'"':line,'"'"'context'"'"':lines[i+1:i+3]} for i,line in enumerate(lines) if '"'"'warning:'"'"' in line]\\nout['"'"'warning_count'"'"']=len(warnings)\\nout['"'"'warning_categories'"'"']=dict(collections.Counter(x['"'"'diagnostic'"'"'].split('"'"'warning:'"'"',1)[1].strip() for x in warnings))\\nout['"'"'warning_locations'"'"']=dict(collections.Counter(re.sub(r'"'"':\\\\d+:\\\\d+: warning:.*'"'"','"'"''"'"',x['"'"'diagnostic'"'"']) for x in warnings))\\nout['"'"'generated_marker_blocks'"'"']=[x for x in warnings if '"'"'.cudafe1.'"'"' in x['"'"'diagnostic'"'"']]\\nout['"'"'error_lines'"'"']=[{'"'"'line'"'"':i+1,'"'"'text'"'"':s} for i,s in enumerate(lines) if re.search(r'"'"'\\\\berror:|fatal error'"'"',s)]\\nout['"'"'cuda_compile_commands'"'"']=[x for x in load(V/'"'"'compile_commands.json'"'"') if x['"'"'file'"'"'].endswith('"'"'.cu'"'"')]\\nout['"'"'source_line_directives'"'"']={}\\nfor f in ['"'"'src/cuda/comparison_resources.cu'"'"','"'"'src/cuda/cub_sort.cu'"'"','"'"'src/cuda/cub_timing.cu'"'"']:\\n    out['"'"'source_line_directives'"'"'][f]=[{'"'"'line'"'"':i+1,'"'"'text'"'"':s} for i,s in enumerate((R/f).read_text().splitlines()) if re.match(r'"'"'\\\\s*#\\\\s*(?:line\\\\b|\\\\d)'"'"',s)]\\nresult=load(V/'"'"'RESULT.json'"'"')\\nout['"'"'executed_records'"'"']=result['"'"'records'"'"']\\nout['"'"'coverage'"'"']={k:result[k] for k in ['"'"'cpu_correctness'"'"','"'"'cuda_correctness'"'"','"'"'study_eligible'"'"','"'"'validation_passed'"'"','"'"'ctest_invocations'"'"','"'"'benchmarks'"'"','"'"'timing_trials'"'"']}\\nenv=load(V/'"'"'ENVIRONMENT.json'"'"')\\nblocks=env['"'"'cpuinfo'"'"'].strip().split('"'"'\\\\n\\\\n'"'"')\\nout['"'"'environment'"'"']={k:env[k] for k in ['"'"'affinity'"'"','"'"'cpu_count'"'"','"'"'disk'"'"','"'"'environment'"'"','"'"'platform'"'"','"'"'python'"'"']}\\nout['"'"'cpu_topology'"'"']=[{k:v.strip() for line in b.splitlines() if '"'"':'"'"' in line for k,v in [line.split('"'"':'"'"',1)] if k.strip() in ['"'"'processor'"'"','"'"'model name'"'"','"'"'cpu MHz'"'"','"'"'physical id'"'"','"'"'siblings'"'"','"'"'core id'"'"','"'"'cpu cores'"'"']} for b in blocks]\\nout['"'"'meminfo_bytes'"'"']={m.group(1):int(m.group(2))*1024 for s in env['"'"'meminfo'"'"'].splitlines() if (m:=re.match(r'"'"'(MemTotal|MemAvailable|SwapTotal):\\\\s+(\\\\d+) kB'"'"',s))}\\nout['"'"'frozen_resources'"'"']=matrix['"'"'resources'"'"']\\nout['"'"'frozen_launch_gates'"'"']=matrix['"'"'launch_gates'"'"']\\nout['"'"'frozen_openmp_policy'"'"']=matrix['"'"'openmp_policy'"'"']\\nout['"'"'matrix_counts'"'"']={k:matrix[k] for k in ['"'"'warmups'"'"','"'"'repetitions'"'"','"'"'study'"'"','"'"'pilot'"'"']}\\nwith (E/'"'"'INDEPENDENT_FINDINGS.json'"'"').open('"'"'x'"'"') as f:json.dump(out,f,indent=2,sort_keys=True);f.write('"'"'\\\\n'"'"')\\nwith (E/'"'"'WARNING_DIAGNOSTICS.json'"'"').open('"'"'x'"'"') as f:json.dump(warnings,f,indent=2);f.write('"'"'\\\\n'"'"')\\nprint(json.dumps({k:out[k] for k in ['"'"'isolated_seal_verified'"'"','"'"'remote_seal_verified'"'"','"'"'transferred_source_matches_local'"'"','"'"'freeze_members_verified'"'"','"'"'anchors_exact_matches'"'"','"'"'anchor_differences'"'"','"'"'project_files_verified'"'"','"'"'build_metadata_verified'"'"','"'"'warning_count'"'"','"'"'warning_categories'"'"','"'"'generated_marker_blocks'"'"','"'"'error_lines'"'"','"'"'coverage'"'"','"'"'environment'"'"','"'"'cpu_topology'"'"','"'"'meminfo_bytes'"'"']},indent=2))\\n'"'"''"'"''"'"'\\nwith p.open('"'"'x'"'"') as f:f.write(code)\\nprint('"'"'Created evidence-only static inspection program'"'"')\\nPY\",\"exit_code\":0,\"scope\":\"Exclusive creation of evidence-only static inspection program\"}]"),f,indent=2);f.write('"'"'\n'"'"');f.close();print('"'"'Saved bootstrap/creation command provenance'"'"')'
```

## control_provenance.json

Exit: 0; safety: Evidence-only command-log assembly; no project execution

```bash
python3 -B -c 'import json;from pathlib import Path;p=Path("results/raw/cpu_gpu_prelaunch_review_20261011T012430643251Z/ADDITIONAL_CONTROL_COMMANDS.json");f=p.open('"'"'x'"'"');json.dump(json.loads("[{\"command\":\"python3 -B -c '"'"'import json;from pathlib import Path;p=Path(\\\"results/raw/cpu_gpu_prelaunch_review_20261011T012430643251Z/CONTROL_COMMANDS.json\\\");f=p.open('"'"'\\\"'"'"'\\\"'"'"'x'"'"'\\\"'"'"'\\\"'"'"');json.dump(json.loads(\\\"[{\\\\\\\"command\\\\\\\":\\\\\\\"python3 -B - <<'"'"'\\\"'"'"'\\\"'"'"'PY'"'"'\\\"'"'"'\\\"'"'"'\\\\\\\\nimport datetime,hashlib,json\\\\\\\\nfrom pathlib import Path\\\\\\\\nr=Path.cwd();e=r/'"'"'\\\"'"'"'\\\"'"'"'results/raw'"'"'\\\"'"'"'\\\"'"'"'/('"'"'\\\"'"'"'\\\"'"'"'cpu_gpu_prelaunch_review_'"'"'\\\"'"'"'\\\"'"'"'+datetime.datetime.now(datetime.timezone.utc).strftime('"'"'\\\"'"'"'\\\"'"'"'%Y%m%dT%H%M%S%fZ'"'"'\\\"'"'"'\\\"'"'"'));e.mkdir()\\\\\\\\ndef sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()\\\\\\\\nprior=r/'"'"'\\\"'"'"'\\\"'"'"'results/raw/isolated_colab_revalidation_20261011T011459127026Z'"'"'\\\"'"'"'\\\"'"'"'\\\\\\\\nb=json.loads((prior/'"'"'\\\"'"'"'\\\"'"'"'BEFORE.json'"'"'\\\"'"'"'\\\"'"'"').read_text())\\\\\\\\nb={'"'"'\\\"'"'"'\\\"'"'"'prior_results_sha256'"'"'\\\"'"'"'\\\"'"'"':{str(p.relative_to(r)):sha(p) for p in sorted((r/'"'"'\\\"'"'"'\\\"'"'"'results'"'"'\\\"'"'"'\\\"'"'"').rglob('"'"'\\\"'"'"'\\\"'"'"'*'"'"'\\\"'"'"'\\\"'"'"')) if p.is_file() and not p.is_relative_to(e)},'"'"'\\\"'"'"'\\\"'"'"'project_sha256'"'"'\\\"'"'"'\\\"'"'"':b['"'"'\\\"'"'"'\\\"'"'"'project_sha256'"'"'\\\"'"'"'\\\"'"'"'],'"'"'\\\"'"'"'\\\"'"'"'build_metadata_sha256'"'"'\\\"'"'"'\\\"'"'"':b['"'"'\\\"'"'"'\\\"'"'"'build_metadata_sha256'"'"'\\\"'"'"'\\\"'"'"'],'"'"'\\\"'"'"'\\\"'"'"'scope'"'"'\\\"'"'"'\\\"'"'"':'"'"'\\\"'"'"'\\\"'"'"'read-only review; no tests, build, CTest, resource commands or GPU work'"'"'\\\"'"'"'\\\"'"'"'}\\\\\\\\nwith (e/'"'"'\\\"'"'"'\\\"'"'"'BEFORE.json'"'"'\\\"'"'"'\\\"'"'"').open('"'"'\\\"'"'"'\\\"'"'"'x'"'"'\\\"'"'"'\\\"'"'"') as f:json.dump(b,f,indent=2,sort_keys=True);f.write('"'"'\\\"'"'"'\\\"'"'"'\\\\\\\\\\\\\\\\n'"'"'\\\"'"'"'\\\"'"'"')\\\\\\\\nprint(e.relative_to(r));print('"'"'\\\"'"'"'\\\"'"'"'historical_results'"'"'\\\"'"'"'\\\"'"'"',len(b['"'"'\\\"'"'"'\\\"'"'"'prior_results_sha256'"'"'\\\"'"'"'\\\"'"'"']))\\\\\\\\nPY\\\\\\\",\\\\\\\"exit_code\\\\\\\":0,\\\\\\\"scope\\\\\\\":\\\\\\\"Read-only local hashing; exclusive creation of new review BEFORE.json\\\\\\\"},{\\\\\\\"command\\\\\\\":\\\\\\\"python3 -B - <<'"'"'\\\"'"'"'\\\"'"'"'PY'"'"'\\\"'"'"'\\\"'"'"'\\\\\\\\nfrom pathlib import Path\\\\\\\\nold=Path('"'"'\\\"'"'"'\\\"'"'"'results/raw/isolated_colab_revalidation_20261011T011459127026Z/record.py'"'"'\\\"'"'"'\\\"'"'"');new=Path('"'"'\\\"'"'"'\\\"'"'"'results/raw/cpu_gpu_prelaunch_review_20261011T012430643251Z/record.py'"'"'\\\"'"'"'\\\"'"'"')\\\\\\\\nwith new.open('"'"'\\\"'"'"'\\\"'"'"'xb'"'"'\\\"'"'"'\\\"'"'"') as f:f.write(old.read_bytes())\\\\\\\\nprint('"'"'\\\"'"'"'\\\"'"'"'Exclusive evidence-only recorder created'"'"'\\\"'"'"'\\\"'"'"')\\\\\\\\nPY\\\\\\\",\\\\\\\"exit_code\\\\\\\":0,\\\\\\\"scope\\\\\\\":\\\\\\\"Exclusive evidence-only recorder copy\\\\\\\"},{\\\\\\\"command\\\\\\\":\\\\\\\"pwd\\\\\\\",\\\\\\\"exit_code\\\\\\\":0,\\\\\\\"scope\\\\\\\":\\\\\\\"Read-only working-directory identification\\\\\\\"},{\\\\\\\"command\\\\\\\":\\\\\\\"python3 -B - <<'"'"'\\\"'"'"'\\\"'"'"'PY'"'"'\\\"'"'"'\\\"'"'"'\\\\\\\\nfrom pathlib import Path\\\\\\\\np=Path('"'"'\\\"'"'"'\\\"'"'"'results/raw/cpu_gpu_prelaunch_review_20261011T012430643251Z/inspect_retained.py'"'"'\\\"'"'"'\\\"'"'"')\\\\\\\\ncode=r'"'"'\\\"'"'"'\\\"'"'"''"'"'\\\"'"'"'\\\"'"'"''"'"'\\\"'"'"'\\\"'"'"'import collections,hashlib,json,re\\\\\\\\nfrom pathlib import Path\\\\\\\\nR=Path.cwd(); E=Path(__file__).resolve().parent\\\\\\\\nOLD=R/'"'"'\\\"'"'"'\\\"'"'"'results/raw/isolated_colab_revalidation_20261011T011459127026Z'"'"'\\\"'"'"'\\\"'"'"'\\\\\\\\nV=OLD/'"'"'\\\"'"'"'\\\"'"'"'remote_evidence/validation'"'"'\\\"'"'"'\\\"'"'"'\\\\\\\\ndef sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()\\\\\\\\ndef load(p):return json.loads(p.read_text())\\\\\\\\ndef verify(mapping,root):\\\\\\\\n    bad=[k for k,v in mapping.items() if not (root/k).is_file() or sha(root/k)!=v]\\\\\\\\n    assert not bad,bad\\\\\\\\n    return len(mapping)\\\\\\\\nout={}\\\\\\\\nseal=load(OLD/'"'"'\\\"'"'"'\\\"'"'"'FINAL_INTEGRITY.json'"'"'\\\"'"'"'\\\"'"'"')['"'"'\\\"'"'"'\\\"'"'"'evidence_sha256'"'"'\\\"'"'"'\\\"'"'"']\\\\\\\\nout['"'"'\\\"'"'"'\\\"'"'"'isolated_seal_verified'"'"'\\\"'"'"'\\\"'"'"']=verify(seal,OLD)\\\\\\\\nassert set(seal)=={str(p.relative_to(OLD)) for p in OLD.rglob('"'"'\\\"'"'"'\\\"'"'"'*'"'"'\\\"'"'"'\\\"'"'"') if p.is_file() and p.name!='"'"'\\\"'"'"'\\\"'"'"'FINAL_INTEGRITY.json'"'"'\\\"'"'"'\\\"'"'"'}\\\\\\\\nremote=load(V/'"'"'\\\"'"'"'\\\"'"'"'EVIDENCE_SHA256.json'"'"'\\\"'"'"'\\\"'"'"');out['"'"'\\\"'"'"'\\\"'"'"'remote_seal_verified'"'"'\\\"'"'"'\\\"'"'"']=verify(remote,V)\\\\\\\\nassert set(remote)=={str(p.relative_to(V)) for p in V.rglob('"'"'\\\"'"'"'\\\"'"'"'*'"'"'\\\"'"'"'\\\"'"'"') if p.is_file() and p.name!='"'"'\\\"'"'"'\\\"'"'"'EVIDENCE_SHA256.json'"'"'\\\"'"'"'\\\"'"'"'}\\\\\\\\nsource=load(OLD/'"'"'\\\"'"'"'\\\"'"'"'SOURCE_IDENTITY.json'"'"'\\\"'"'"'\\\"'"'"')['"'"'\\\"'"'"'\\\"'"'"'files_sha256'"'"'\\\"'"'"'\\\"'"'"']\\\\\\\\nout['"'"'\\\"'"'"'\\\"'"'"'transferred_source_matches_local'"'"'\\\"'"'"'\\\"'"'"']=verify(source,R)\\\\\\\\nassert (V/'"'"'\\\"'"'"'\\\"'"'"'SOURCE_AFTER.json'"'"'\\\"'"'"'\\\"'"'"').read_bytes()==(OLD/'"'"'\\\"'"'"'\\\"'"'"'SOURCE_IDENTITY.json'"'"'\\\"'"'"'\\\"'"'"').read_bytes()\\\\\\\\nfreeze=load(R/'"'"'\\\"'"'"'\\\"'"'"'docs/studies/cpu_gpu_comparison_v1.freeze.json'"'"'\\\"'"'"'\\\"'"'"')\\\\\\\\nout['"'"'\\\"'"'"'\\\"'"'"'freeze_members_verified'"'"'\\\"'"'"'\\\"'"'"']=verify(freeze['"'"'\\\"'"'"'\\\"'"'"'files_sha256'"'"'\\\"'"'"'\\\"'"'"'],R)\\\\\\\\nout['"'"'\\\"'"'"'\\\"'"'"'freeze_hashes'"'"'\\\"'"'"'\\\"'"'"']=freeze['"'"'\\\"'"'"'\\\"'"'"'files_sha256'"'"'\\\"'"'"'\\\"'"'"']\\\\\\\\nmatrix=load(R/'"'"'\\\"'"'"'\\\"'"'"'docs/studies/cpu_gpu_comparison_v1.matrix.json'"'"'\\\"'"'"'\\\"'"'"')\\\\\\\\nanchors=matrix['"'"'\\\"'"'"'\\\"'"'"'source_at_freeze_sha256'"'"'\\\"'"'"'\\\"'"'"']\\\\\\\\nout['"'"'\\\"'"'"'\\\"'"'"'anchors_exact_matches'"'"'\\\"'"'"'\\\"'"'"']=sum((R/k).is_file() and sha(R/k)==v for k,v in anchors.items())\\\\\\\\nout['"'"'\\\"'"'"'\\\"'"'"'anchor_differences'"'"'\\\"'"'"'\\\"'"'"']={k:{'"'"'\\\"'"'"'\\\"'"'"'frozen'"'"'\\\"'"'"'\\\"'"'"':v,'"'"'\\\"'"'"'\\\"'"'"'current'"'"'\\\"'"'"'\\\"'"'"':sha(R/k)} for k,v in anchors.items() if sha(R/k)!=v}\\\\\\\\nout['"'"'\\\"'"'"'\\\"'"'"'driver_review'"'"'\\\"'"'"'\\\"'"'"']=load(R/'"'"'\\\"'"'"'\\\"'"'"'docs/CPU_GPU_DRIVER_REVIEW_v1.json'"'"'\\\"'"'"'\\\"'"'"')\\\\\\\\nout['"'"'\\\"'"'"'\\\"'"'"'cub_pin'"'"'\\\"'"'"'\\\"'"'"']=load(R/'"'"'\\\"'"'"'\\\"'"'"'third_party/cub/UPSTREAM.json'"'"'\\\"'"'"'\\\"'"'"')\\\\\\\\nout['"'"'\\\"'"'"'\\\"'"'"'production_adapter_sha256'"'"'\\\"'"'"'\\\"'"'"']=sha(R/'"'"'\\\"'"'"'\\\"'"'"'src/cuda/cub_sort.cu'"'"'\\\"'"'"'\\\"'"'"')\\\\\\\\nbefore=load(E/'"'"'\\\"'"'"'\\\"'"'"'BEFORE.json'"'"'\\\"'"'"'\\\"'"'"')\\\\\\\\nout['"'"'\\\"'"'"'\\\"'"'"'project_files_verified'"'"'\\\"'"'"'\\\"'"'"']=verify(before['"'"'\\\"'"'"'\\\"'"'"'project_sha256'"'"'\\\"'"'"'\\\"'"'"'],R)\\\\\\\\nout['"'"'\\\"'"'"'\\\"'"'"'build_metadata_verified'"'"'\\\"'"'"'\\\"'"'"']=verify(before['"'"'\\\"'"'"'\\\"'"'"'build_metadata_sha256'"'"'\\\"'"'"'\\\"'"'"'],R)\\\\\\\\nlines=(V/'"'"'\\\"'"'"'\\\"'"'"'build.stderr.txt'"'"'\\\"'"'"'\\\"'"'"').read_text().splitlines()\\\\\\\\nwarnings=[{'"'"'\\\"'"'"'\\\"'"'"'log_line'"'"'\\\"'"'"'\\\"'"'"':i+1,'"'"'\\\"'"'"'\\\"'"'"'diagnostic'"'"'\\\"'"'"'\\\"'"'"':line,'"'"'\\\"'"'"'\\\"'"'"'context'"'"'\\\"'"'"'\\\"'"'"':lines[i+1:i+3]} for i,line in enumerate(lines) if '"'"'\\\"'"'"'\\\"'"'"'warning:'"'"'\\\"'"'"'\\\"'"'"' in line]\\\\\\\\nout['"'"'\\\"'"'"'\\\"'"'"'warning_count'"'"'\\\"'"'"'\\\"'"'"']=len(warnings)\\\\\\\\nout['"'"'\\\"'"'"'\\\"'"'"'warning_categories'"'"'\\\"'"'"'\\\"'"'"']=dict(collections.Counter(x['"'"'\\\"'"'"'\\\"'"'"'diagnostic'"'"'\\\"'"'"'\\\"'"'"'].split('"'"'\\\"'"'"'\\\"'"'"'warning:'"'"'\\\"'"'"'\\\"'"'"',1)[1].strip() for x in warnings))\\\\\\\\nout['"'"'\\\"'"'"'\\\"'"'"'warning_locations'"'"'\\\"'"'"'\\\"'"'"']=dict(collections.Counter(re.sub(r'"'"'\\\"'"'"'\\\"'"'"':\\\\\\\\\\\\\\\\d+:\\\\\\\\\\\\\\\\d+: warning:.*'"'"'\\\"'"'"'\\\"'"'"','"'"'\\\"'"'"'\\\"'"'"''"'"'\\\"'"'"'\\\"'"'"',x['"'"'\\\"'"'"'\\\"'"'"'diagnostic'"'"'\\\"'"'"'\\\"'"'"']) for x in warnings))\\\\\\\\nout['"'"'\\\"'"'"'\\\"'"'"'generated_marker_blocks'"'"'\\\"'"'"'\\\"'"'"']=[x for x in warnings if '"'"'\\\"'"'"'\\\"'"'"'.cudafe1.'"'"'\\\"'"'"'\\\"'"'"' in x['"'"'\\\"'"'"'\\\"'"'"'diagnostic'"'"'\\\"'"'"'\\\"'"'"']]\\\\\\\\nout['"'"'\\\"'"'"'\\\"'"'"'error_lines'"'"'\\\"'"'"'\\\"'"'"']=[{'"'"'\\\"'"'"'\\\"'"'"'line'"'"'\\\"'"'"'\\\"'"'"':i+1,'"'"'\\\"'"'"'\\\"'"'"'text'"'"'\\\"'"'"'\\\"'"'"':s} for i,s in enumerate(lines) if re.search(r'"'"'\\\"'"'"'\\\"'"'"'\\\\\\\\\\\\\\\\berror:|fatal error'"'"'\\\"'"'"'\\\"'"'"',s)]\\\\\\\\nout['"'"'\\\"'"'"'\\\"'"'"'cuda_compile_commands'"'"'\\\"'"'"'\\\"'"'"']=[x for x in load(V/'"'"'\\\"'"'"'\\\"'"'"'compile_commands.json'"'"'\\\"'"'"'\\\"'"'"') if x['"'"'\\\"'"'"'\\\"'"'"'file'"'"'\\\"'"'"'\\\"'"'"'].endswith('"'"'\\\"'"'"'\\\"'"'"'.cu'"'"'\\\"'"'"'\\\"'"'"')]\\\\\\\\nout['"'"'\\\"'"'"'\\\"'"'"'source_line_directives'"'"'\\\"'"'"'\\\"'"'"']={}\\\\\\\\nfor f in ['"'"'\\\"'"'"'\\\"'"'"'src/cuda/comparison_resources.cu'"'"'\\\"'"'"'\\\"'"'"','"'"'\\\"'"'"'\\\"'"'"'src/cuda/cub_sort.cu'"'"'\\\"'"'"'\\\"'"'"','"'"'\\\"'"'"'\\\"'"'"'src/cuda/cub_timing.cu'"'"'\\\"'"'"'\\\"'"'"']:\\\\\\\\n    out['"'"'\\\"'"'"'\\\"'"'"'source_line_directives'"'"'\\\"'"'"'\\\"'"'"'][f]=[{'"'"'\\\"'"'"'\\\"'"'"'line'"'"'\\\"'"'"'\\\"'"'"':i+1,'"'"'\\\"'"'"'\\\"'"'"'text'"'"'\\\"'"'"'\\\"'"'"':s} for i,s in enumerate((R/f).read_text().splitlines()) if re.match(r'"'"'\\\"'"'"'\\\"'"'"'\\\\\\\\\\\\\\\\s*#\\\\\\\\\\\\\\\\s*(?:line\\\\\\\\\\\\\\\\b|\\\\\\\\\\\\\\\\d)'"'"'\\\"'"'"'\\\"'"'"',s)]\\\\\\\\nresult=load(V/'"'"'\\\"'"'"'\\\"'"'"'RESULT.json'"'"'\\\"'"'"'\\\"'"'"')\\\\\\\\nout['"'"'\\\"'"'"'\\\"'"'"'executed_records'"'"'\\\"'"'"'\\\"'"'"']=result['"'"'\\\"'"'"'\\\"'"'"'records'"'"'\\\"'"'"'\\\"'"'"']\\\\\\\\nout['"'"'\\\"'"'"'\\\"'"'"'coverage'"'"'\\\"'"'"'\\\"'"'"']={k:result[k] for k in ['"'"'\\\"'"'"'\\\"'"'"'cpu_correctness'"'"'\\\"'"'"'\\\"'"'"','"'"'\\\"'"'"'\\\"'"'"'cuda_correctness'"'"'\\\"'"'"'\\\"'"'"','"'"'\\\"'"'"'\\\"'"'"'study_eligible'"'"'\\\"'"'"'\\\"'"'"','"'"'\\\"'"'"'\\\"'"'"'validation_passed'"'"'\\\"'"'"'\\\"'"'"','"'"'\\\"'"'"'\\\"'"'"'ctest_invocations'"'"'\\\"'"'"'\\\"'"'"','"'"'\\\"'"'"'\\\"'"'"'benchmarks'"'"'\\\"'"'"'\\\"'"'"','"'"'\\\"'"'"'\\\"'"'"'timing_trials'"'"'\\\"'"'"'\\\"'"'"']}\\\\\\\\nenv=load(V/'"'"'\\\"'"'"'\\\"'"'"'ENVIRONMENT.json'"'"'\\\"'"'"'\\\"'"'"')\\\\\\\\nblocks=env['"'"'\\\"'"'"'\\\"'"'"'cpuinfo'"'"'\\\"'"'"'\\\"'"'"'].strip().split('"'"'\\\"'"'"'\\\"'"'"'\\\\\\\\\\\\\\\\n\\\\\\\\\\\\\\\\n'"'"'\\\"'"'"'\\\"'"'"')\\\\\\\\nout['"'"'\\\"'"'"'\\\"'"'"'environment'"'"'\\\"'"'"'\\\"'"'"']={k:env[k] for k in ['"'"'\\\"'"'"'\\\"'"'"'affinity'"'"'\\\"'"'"'\\\"'"'"','"'"'\\\"'"'"'\\\"'"'"'cpu_count'"'"'\\\"'"'"'\\\"'"'"','"'"'\\\"'"'"'\\\"'"'"'disk'"'"'\\\"'"'"'\\\"'"'"','"'"'\\\"'"'"'\\\"'"'"'environment'"'"'\\\"'"'"'\\\"'"'"','"'"'\\\"'"'"'\\\"'"'"'platform'"'"'\\\"'"'"'\\\"'"'"','"'"'\\\"'"'"'\\\"'"'"'python'"'"'\\\"'"'"'\\\"'"'"']}\\\\\\\\nout['"'"'\\\"'"'"'\\\"'"'"'cpu_topology'"'"'\\\"'"'"'\\\"'"'"']=[{k:v.strip() for line in b.splitlines() if '"'"'\\\"'"'"'\\\"'"'"':'"'"'\\\"'"'"'\\\"'"'"' in line for k,v in [line.split('"'"'\\\"'"'"'\\\"'"'"':'"'"'\\\"'"'"'\\\"'"'"',1)] if k.strip() in ['"'"'\\\"'"'"'\\\"'"'"'processor'"'"'\\\"'"'"'\\\"'"'"','"'"'\\\"'"'"'\\\"'"'"'model name'"'"'\\\"'"'"'\\\"'"'"','"'"'\\\"'"'"'\\\"'"'"'cpu MHz'"'"'\\\"'"'"'\\\"'"'"','"'"'\\\"'"'"'\\\"'"'"'physical id'"'"'\\\"'"'"'\\\"'"'"','"'"'\\\"'"'"'\\\"'"'"'siblings'"'"'\\\"'"'"'\\\"'"'"','"'"'\\\"'"'"'\\\"'"'"'core id'"'"'\\\"'"'"'\\\"'"'"','"'"'\\\"'"'"'\\\"'"'"'cpu cores'"'"'\\\"'"'"'\\\"'"'"']} for b in blocks]\\\\\\\\nout['"'"'\\\"'"'"'\\\"'"'"'meminfo_bytes'"'"'\\\"'"'"'\\\"'"'"']={m.group(1):int(m.group(2))*1024 for s in env['"'"'\\\"'"'"'\\\"'"'"'meminfo'"'"'\\\"'"'"'\\\"'"'"'].splitlines() if (m:=re.match(r'"'"'\\\"'"'"'\\\"'"'"'(MemTotal|MemAvailable|SwapTotal):\\\\\\\\\\\\\\\\s+(\\\\\\\\\\\\\\\\d+) kB'"'"'\\\"'"'"'\\\"'"'"',s))}\\\\\\\\nout['"'"'\\\"'"'"'\\\"'"'"'frozen_resources'"'"'\\\"'"'"'\\\"'"'"']=matrix['"'"'\\\"'"'"'\\\"'"'"'resources'"'"'\\\"'"'"'\\\"'"'"']\\\\\\\\nout['"'"'\\\"'"'"'\\\"'"'"'frozen_launch_gates'"'"'\\\"'"'"'\\\"'"'"']=matrix['"'"'\\\"'"'"'\\\"'"'"'launch_gates'"'"'\\\"'"'"'\\\"'"'"']\\\\\\\\nout['"'"'\\\"'"'"'\\\"'"'"'frozen_openmp_policy'"'"'\\\"'"'"'\\\"'"'"']=matrix['"'"'\\\"'"'"'\\\"'"'"'openmp_policy'"'"'\\\"'"'"'\\\"'"'"']\\\\\\\\nout['"'"'\\\"'"'"'\\\"'"'"'matrix_counts'"'"'\\\"'"'"'\\\"'"'"']={k:matrix[k] for k in ['"'"'\\\"'"'"'\\\"'"'"'warmups'"'"'\\\"'"'"'\\\"'"'"','"'"'\\\"'"'"'\\\"'"'"'repetitions'"'"'\\\"'"'"'\\\"'"'"','"'"'\\\"'"'"'\\\"'"'"'study'"'"'\\\"'"'"'\\\"'"'"','"'"'\\\"'"'"'\\\"'"'"'pilot'"'"'\\\"'"'"'\\\"'"'"']}\\\\\\\\nwith (E/'"'"'\\\"'"'"'\\\"'"'"'INDEPENDENT_FINDINGS.json'"'"'\\\"'"'"'\\\"'"'"').open('"'"'\\\"'"'"'\\\"'"'"'x'"'"'\\\"'"'"'\\\"'"'"') as f:json.dump(out,f,indent=2,sort_keys=True);f.write('"'"'\\\"'"'"'\\\"'"'"'\\\\\\\\\\\\\\\\n'"'"'\\\"'"'"'\\\"'"'"')\\\\\\\\nwith (E/'"'"'\\\"'"'"'\\\"'"'"'WARNING_DIAGNOSTICS.json'"'"'\\\"'"'"'\\\"'"'"').open('"'"'\\\"'"'"'\\\"'"'"'x'"'"'\\\"'"'"'\\\"'"'"') as f:json.dump(warnings,f,indent=2);f.write('"'"'\\\"'"'"'\\\"'"'"'\\\\\\\\\\\\\\\\n'"'"'\\\"'"'"'\\\"'"'"')\\\\\\\\nprint(json.dumps({k:out[k] for k in ['"'"'\\\"'"'"'\\\"'"'"'isolated_seal_verified'"'"'\\\"'"'"'\\\"'"'"','"'"'\\\"'"'"'\\\"'"'"'remote_seal_verified'"'"'\\\"'"'"'\\\"'"'"','"'"'\\\"'"'"'\\\"'"'"'transferred_source_matches_local'"'"'\\\"'"'"'\\\"'"'"','"'"'\\\"'"'"'\\\"'"'"'freeze_members_verified'"'"'\\\"'"'"'\\\"'"'"','"'"'\\\"'"'"'\\\"'"'"'anchors_exact_matches'"'"'\\\"'"'"'\\\"'"'"','"'"'\\\"'"'"'\\\"'"'"'anchor_differences'"'"'\\\"'"'"'\\\"'"'"','"'"'\\\"'"'"'\\\"'"'"'project_files_verified'"'"'\\\"'"'"'\\\"'"'"','"'"'\\\"'"'"'\\\"'"'"'build_metadata_verified'"'"'\\\"'"'"'\\\"'"'"','"'"'\\\"'"'"'\\\"'"'"'warning_count'"'"'\\\"'"'"'\\\"'"'"','"'"'\\\"'"'"'\\\"'"'"'warning_categories'"'"'\\\"'"'"'\\\"'"'"','"'"'\\\"'"'"'\\\"'"'"'generated_marker_blocks'"'"'\\\"'"'"'\\\"'"'"','"'"'\\\"'"'"'\\\"'"'"'error_lines'"'"'\\\"'"'"'\\\"'"'"','"'"'\\\"'"'"'\\\"'"'"'coverage'"'"'\\\"'"'"'\\\"'"'"','"'"'\\\"'"'"'\\\"'"'"'environment'"'"'\\\"'"'"'\\\"'"'"','"'"'\\\"'"'"'\\\"'"'"'cpu_topology'"'"'\\\"'"'"'\\\"'"'"','"'"'\\\"'"'"'\\\"'"'"'meminfo_bytes'"'"'\\\"'"'"'\\\"'"'"']},indent=2))\\\\\\\\n'"'"'\\\"'"'"'\\\"'"'"''"'"'\\\"'"'"'\\\"'"'"''"'"'\\\"'"'"'\\\"'"'"'\\\\\\\\nwith p.open('"'"'\\\"'"'"'\\\"'"'"'x'"'"'\\\"'"'"'\\\"'"'"') as f:f.write(code)\\\\\\\\nprint('"'"'\\\"'"'"'\\\"'"'"'Created evidence-only static inspection program'"'"'\\\"'"'"'\\\"'"'"')\\\\\\\\nPY\\\\\\\",\\\\\\\"exit_code\\\\\\\":0,\\\\\\\"scope\\\\\\\":\\\\\\\"Exclusive creation of evidence-only static inspection program\\\\\\\"}]\\\"),f,indent=2);f.write('"'"'\\\"'"'"'\\\"'"'"'\\\\n'"'"'\\\"'"'"'\\\"'"'"');f.close();print('"'"'\\\"'"'"'\\\"'"'"'Saved bootstrap/creation command provenance'"'"'\\\"'"'"'\\\"'"'"')'"'"'\",\"exit_code\":0,\"scope\":\"Exclusive creation of command-provenance JSON in new review directory\"}]"),f,indent=2);f.write('"'"'\n'"'"');f.close();print('"'"'Recorded evidence-only control-command provenance'"'"')'
```

Exact cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`.

## focused_detail.json

Exit: 0; safety: Local JSON/text inspection only; no environment probing or execution

```bash
python3 -B -c 'import json,collections;from pathlib import Path;e=Path("results/raw/cpu_gpu_prelaunch_review_20261011T012430643251Z");d=json.loads((e/"INDEPENDENT_FINDINGS.json").read_text());w=json.loads((e/"WARNING_DIAGNOSTICS.json").read_text());print("warning ranges",[(a,b,sum(a<=x["log_line"]<=b for x in w)) for a,b in [(1,232),(233,520),(521,993)]]);print("CUDA compile commands");[(print(x["command"])) for x in d["cuda_compile_commands"] if any(v in x["file"] for v in ["cub_sort.cu","cub_timing.cu","comparison_resources.cu"])];print("CUB pin",d["cub_pin"]);print("frozen gates",d["frozen_launch_gates"]);print("frozen resources",d["frozen_resources"]);print("OMP policy",d["frozen_openmp_policy"]);v=Path("results/raw/isolated_colab_revalidation_20261011T011459127026Z/remote_evidence/validation");print("BINARIES",(v/"BINARIES.json").read_text());print("PREREQUISITE FILES");[print(str(p)) for p in Path("results/raw").rglob("PREREQUISITES.json")];print("REMOTE DIAGNOSTIC KEYS");p=Path("results/raw/colab_t4_diagnostics_20261011T005409276199Z/REMOTE_DIAGNOSTICS.json");d=json.loads(p.read_text());print(d.keys());print(json.dumps(d)[:9000])'
```

Exact cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`.

## frozen_protocol.json

Exit: 0; safety: Read-only frozen comparison protocol, matrix, freeze, resource table and launch requirements

```bash
cat docs/CPU_GPU_COMPARISON_PROTOCOL_v1.md docs/studies/cpu_gpu_comparison_v1.freeze.json docs/studies/cpu_gpu_comparison_v1.resources.csv
```

Exact cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`.

## historical_pilot_workspace.json

Exit: 0; safety: Read-only accepted pilot variability and previous fresh N65537 resource audit; historical observations only

```bash
cat results/processed/cpu_gpu_pilot_20261010T001232473460Z/REPORT.md results/raw/cub_workspace_65537_20261010T110457531249Z/FINAL_AUDIT.md
```

Exact cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`.

## independent_findings.json

Exit: 0; safety: Local reads, SHA-256, JSON and warning-log parsing only; no project imports or workloads

```bash
python3 -B results/raw/cpu_gpu_prelaunch_review_20261011T012430643251Z/inspect_retained.py
```

Exact cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`.

## inspection_keys.json

Exit: 0; safety: Read-only retained JSON and source inspection

```bash
python3 -B -c 'import json;from pathlib import Path;e=Path("results/raw/isolated_colab_revalidation_20261011T011459127026Z/remote_evidence/validation");[(print(f),print(json.dumps(json.loads((e/f).read_text()),indent=2)[:12000])) for f in ["RESULT.json","ENVIRONMENT.json","EVIDENCE_SHA256.json"]];print("FREEZE");print(Path("docs/studies/cpu_gpu_comparison_v1.freeze.json").read_text());print("MATRIX KEYS");print(json.loads(Path("docs/studies/cpu_gpu_comparison_v1.matrix.json").read_text()).keys())'
```

Exact cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`.

## inspection_shapes.json

Exit: 0; safety: Read-only JSON structure and warning-log inspection; no repository execution

```bash
python3 -B -c 'import json;from pathlib import Path;e=Path("results/raw/isolated_colab_revalidation_20261011T011459127026Z"); fs=["FINAL_INTEGRITY.json","SOURCE_IDENTITY.json","remote_evidence/validation/EVIDENCE_SHA256.json","remote_evidence/validation/RESULT.json","remote_evidence/validation/ENVIRONMENT.json","remote_evidence/validation/compile_commands.json"];[(print(f),print(str(json.loads((e/f).read_text()))[:5500])) for f in fs];p=e/"remote_evidence/validation/build.stderr.txt";s=p.read_text().splitlines();print("WARNING FIRST 90 LINES");print("\n".join(f"{i+1}: {x}" for i,x in enumerate(s[:90])))'
```

Exact cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`.

## latest_validation_evidence.json

Exit: 0; safety: Read-only project instructions and latest isolated validation audit/commands/seal

```bash
cat AGENTS.md results/raw/isolated_colab_revalidation_20261011T011459127026Z/FINAL_AUDIT.md results/raw/isolated_colab_revalidation_20261011T011459127026Z/COMMANDS.md results/raw/isolated_colab_revalidation_20261011T011459127026Z/FINAL_INTEGRITY.json
```

Exact cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`.

## launch_gate_code.json

Exit: 0; safety: Static inspection of runner prerequisites, resource/CPU-team gates and analysis eligibility; no imports/execution

```bash
rg -n 'require\(|prerequis|study_eligible|resource|affinity|cpu_count|actual_threads|warmup|timeout|limit|compatible' scripts/run_cpu_gpu_study.py scripts/run_cpu_gpu_pilot.py scripts/validate_cpu_gpu_pilot.py scripts/analyze_cpu_gpu.py docs/CPU_GPU_COMPARISON_PROTOCOL_v1.md
```

Exact cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`.

## precise_launch_sources.json

Exit: 0; safety: Read-only numbered launch and prerequisite source; no runner execution

```bash
bash -c 'nl -ba scripts/run_cpu_gpu_pilot.py | sed -n "1,195p"; nl -ba scripts/analyze_cpu_gpu.py | sed -n "65,110p"; nl -ba docs/CPU_GPU_COMPARISON_PROTOCOL_v1.md | sed -n "55,90p"; nl -ba cmake/cuda.cmake | sed -n "30,85p"'
```

Exact cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`.

## prerequisite_identity.json

Exit: 0; safety: Read-only historical prerequisite and launch-gate source inspection

```bash
python3 -B -c 'import json;from pathlib import Path;p=Path("results/raw/cpu_gpu_pilot_20261010T001232473460Z/remote_v3/modern-algorithm-benchmark/results/raw/validation_v3/PREREQUISITES.json");d=json.loads(p.read_text());print("PREREQUISITES",p);print("keys",list(d));print("binary_sha256",d.get("binary_sha256"));print("input_tool_sha256",d.get("input_tool_sha256"));print("validation_scope",d.get("validation_scope","legacy default full_protocol_v1"));print("complete",d.get("complete"));print("RECORDS",d.get("records",{}));print("SOURCE DIFF COUNT");m=json.loads(Path("docs/NON_TIMING_TEST_SELECTION_v1.json").read_text());print("policy keys",list(m));print("prior preservation keys",list(json.loads(Path("results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/BEFORE.json").read_text())));print("source gate excerpts");fs={"scripts/run_cpu_gpu_pilot.py":[(107,124),(150,180)],"scripts/analyze_cpu_gpu.py":[(68,104)],"src/benchmark/cpu_gpu_main.cpp":[(84,104)],"scripts/validate_cpu_gpu_pilot.py":[(75,180)]};[(print(f),print("\n".join(f"{i}: {s}" for i,s in enumerate(Path(f).read_text().splitlines(),1) if any(a<=i<=b for a,b in ranges)))) for f,ranges in fs.items()]'
```

Exact cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`.

## preservation_check.json

Exit: 0; safety: Read-only local SHA-256 and membership comparison; writes only new review evidence

```bash
python3 -B -c 'import hashlib,json;from pathlib import Path;r=Path.cwd();e=r/"results/raw/cpu_gpu_prelaunch_review_20261011T012430643251Z";sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();b=json.loads((e/"BEFORE.json").read_text());out={};maps={k:b[k] for k in ["prior_results_sha256","project_sha256","build_metadata_sha256"]};p=json.loads((r/"results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/BEFORE.json").read_text());maps["production_header_dependency_sha256"]={k:v for k,v in p["current_source_sha256"].items() if k.startswith(("src/","include/","third_party/")) or k=="CMakeLists.txt"};policy=json.loads((r/"docs/NON_TIMING_TEST_SELECTION_v1.json").read_text());maps["reviewed_source_sha256"]=policy["reviewed_source_sha256"];m=json.loads((r/"docs/studies/cpu_gpu_comparison_v1.matrix.json").read_text());a=m["source_at_freeze_sha256"].copy();review=json.loads((r/"docs/CPU_GPU_DRIVER_REVIEW_v1.json").read_text());assert sha(r/"docs/CPU_GPU_DRIVER_REVIEW_v1.json")=="b6a63a7e65827970d6b27e872e738052cd5faf94d88ee711dbccd5f77f90ef2a";assert a["CMakeLists.txt"]==review["frozen_cmake_sha256"];a["CMakeLists.txt"]=review["current_cmake_sha256"];maps["effective_protected_anchors_sha256"]=a;assert sha(r/"docs/studies/cpu_gpu_comparison_v1.freeze.json")=="518ac535473e50fb61dab3a70858bdfe42dfdb43570f649174f44bffe40e1ac6";assert sha(r/"third_party/cub/UPSTREAM.json")=="477b1ee70b0a9113c9f98b263c19a31d05ccee54f45ce8476aec4cc98965ced1";[(out.update({k:{"count":len(v),"changed_or_missing":[f for f,h in v.items() if not (r/f).is_file() or sha(r/f)!=h]}})) for k,v in maps.items()];actual={str(p.relative_to(r)) for p in (r/"results").rglob("*") if p.is_file() and not p.is_relative_to(e)};out["historical_membership"]={"before":len(b["prior_results_sha256"]),"after":len(actual),"added":sorted(actual-set(b["prior_results_sha256"])),"missing":sorted(set(b["prior_results_sha256"])-actual)};assert all(not v["changed_or_missing"] for k,v in out.items() if "changed_or_missing" in v);assert not out["historical_membership"]["added"] and not out["historical_membership"]["missing"];out["scope"]="No project/evidence outside this new directory changed. Hashes establish retained contents, not remote lifetime or signed external attestation.";f=(e/"PRESERVATION.json").open("x");json.dump(out,f,indent=2,sort_keys=True);f.write("\n");f.close();print(json.dumps(out,indent=2))'
```

Exact cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`.

## remaining_documentation.json

Exit: 0; safety: Read-only documentation and retained warning-log classification

```bash
python3 -B -c 'from pathlib import Path;import json;r=Path.cwd();e=r/"results/raw/cpu_gpu_prelaunch_review_20261011T012430643251Z";fs=["README.md","docs/ROADMAP.md","docs/EXPERIMENT_PROTOCOL.md","cmake/cuda.cmake"];[(print(f),print("\n".join(f"{i}: {s}" for i,s in enumerate((r/f).read_text().splitlines(),1) if any(t in s.lower() for t in ["cpu/gpu","cpu_gpu","prerequis","cuda","sanitize","pedantic","timing scope"])))) for f in fs];v=r/"results/raw/isolated_colab_revalidation_20261011T011459127026Z/remote_evidence/validation";print("DIAGNOSTIC COUNTS BY LOG");[(print(p.name,sum("warning:" in s for s in p.read_text().splitlines()),sum("error:" in s for s in p.read_text().splitlines()))) for p in sorted(v.glob("*.txt")) if p.name.endswith(("stdout.txt","stderr.txt"))];print("SOURCE_AFTER BYTE EQUALITY",(v/"SOURCE_AFTER.json").read_bytes()==(v/"SOURCE_IDENTITY.json").read_bytes())'
```

Exact cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`.

## warning_and_scope_sources.json

Exit: 0; safety: Read-only numbered source/log inspection

```bash
bash -c 'nl -ba results/raw/isolated_colab_revalidation_20261011T011459127026Z/FINAL_AUDIT.md | sed -n "1,230p"; nl -ba docs/CPU_GPU_COMPARISON_PROTOCOL_v1.md | sed -n "245,285p;345,390p"; nl -ba src/benchmark/cpu_gpu_main.cpp | sed -n "1,185p"; nl -ba tests/test_cuda_sorting.cpp | sed -n "1,210p"; nl -ba CMakeLists.txt | sed -n "192,216p"; cat docs/CPU_GPU_DRIVER_REVIEW_v1.json'
```

Exact cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`.

## Evidence writer tool action

apply_patch added only this directory's seal_review.py; tool returned success. No repository source changes.

## Final evidence assembly and seal

```bash
python3 -B results/raw/cpu_gpu_prelaunch_review_20261011T012430643251Z/seal_review.py
```

Exit: 0 on successful completion; assertion failure would abort. This standard-library program only rehashes local files, writes this audit/command log and seals its own new evidence. Its full source is retained. No subprocesses or repository imports.

Terminal session polling only retrieved output of the already-recorded preservation command; it launched no additional command.
