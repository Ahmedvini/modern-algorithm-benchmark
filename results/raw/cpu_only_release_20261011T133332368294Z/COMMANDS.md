# Commands and actual exit statuses

All commands ran from the repository root unless the retained command record says otherwise.
The complete argv/cwd/stdout/stderr for guarded CTest are in cpu_release*.json.
No performance experiment, collector, GPU CLI or GPU workload was launched.

## command_001.json: exit 0

Inspect read-only raw-analysis APIs, numeric semantics and original CPU environment/provenance before editing reporting

```sh
sed -n '1,205p' scripts/analyze_experiment.py
sed -n '1,225p' scripts/analyze_parallel_results.py
sed -n '100,172p' scripts/learned_study.py
sed -n '110,162p' scripts/analyze_results.py
cat results/raw/autonomous_completion_20261011T095554571762Z/learned_study/COMPLETE.json | head -12
sed -n '1,120p' results/raw/autonomous_completion_20261011T095554571762Z/prepare_cpu_studies.py
cat docs/STRUCTURES_PROTOCOL_v1.md | head -45
cat results/raw/autonomous_completion_20261011T095554571762Z/command_073.json | head -12
```

Working directory: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`; start UTC: `2026-10-11T13:33:45.213008+00:00`.

Full stdout/stderr: [command_001.json](command_001.json).

## command_002.json: exit 0

Verify retained hardware/software and workload counts and inspect analyzer purity before raw-data audit

```sh
python3 -B - <<'PY'
import json,pathlib
r=pathlib.Path('.')
for n in ['results/raw/phase5_full_20261009T191000587965Z/environment.json','results/raw/openmp_scaling_20261009T200852928292Z_retry1/environment.json']:
 d=json.loads((r/n).read_text());print(n);print('OS',d['os']);print('Compiler',d['compiler']);print('CPU',d['cpu_probe']['stdout'][:1900]);print('RAM',d['linux_meminfo'].splitlines()[0]);print('OpenMP',d.get('omp_environment'))
print('Resource keys',list(json.loads((r/'results/raw/autonomous_completion_20261011T095554571762Z/RESOURCES_100m.json').read_text())))
p=json.loads((r/'results/processed/openmp_scaling_20261009T200852928292Z_retry1/summary.json').read_text());print('OMP totals', {k:p[k] for k in ['successful_measured','warmup_rows','failed_measured','missing_measured','failed_warmups','missing_warmups']});print('OMP config',p['configuration'])
PY
rg -n 'subprocess|Popen|os.system|def validate_study|def aggregate' scripts/experiment_model.py scripts/analyze_parallel_results.py scripts/learned_study.py
sed -n '10,110p' scripts/learned_study.py
```

Working directory: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`; start UTC: `2026-10-11T13:34:21.966960+00:00`.

Full stdout/stderr: [command_002.json](command_002.json).

## command_003.json: exit 1

Recompute every CPU report summary from immutable raw observations using existing parsers; subprocess/workload execution blocked

```sh
python3 -B - <<'PY'
import json,pathlib,sys
sys.path.insert(0,'report')
from verify_cpu import verify
p=pathlib.Path('results/raw/autonomous_completion_20261011T095554571762Z')
v=verify(p,pathlib.Path('results/processed/learned_rank_20261011T095554571762Z'),pathlib.Path('results/processed/count_memory_20261011T095554571762Z'))
with pathlib.Path("/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/cpu_only_release_20261011T133332368294Z/RAW_NUMERIC_AUDIT.json").open('x') as f:json.dump(v,f,indent=2,sort_keys=True)
print(json.dumps(v,indent=2))
PY
```

Working directory: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`; start UTC: `2026-10-11T13:37:40.203454+00:00`.

Full stdout/stderr: [command_003.json](command_003.json).

## command_004.json: exit 0

Run focused CPU-release report/statistical regressions and existing synthetic metrics parser tests; subprocess launches blocked

```sh
python3 -B report/test_cpu_release.py -v
python3 -B report/test_tools.py -v
```

Working directory: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`; start UTC: `2026-10-11T13:38:53.874562+00:00`.

Full stdout/stderr: [command_004.json](command_004.json).

## command_005.json: exit 0

Check existing CPU-only Release build and its unchanged flags without configuring or executing any benchmark

```sh
python3 -B - <<'PY'
from pathlib import Path
p=Path('build/autonomous_cpu_release/CMakeCache.txt');lines=p.read_text().splitlines()
for key in ['CMAKE_BUILD_TYPE:STRING=Release','MAB_ENABLE_CUDA:BOOL=OFF','MAB_ENABLE_CUDA_SORT:BOOL=OFF','MAB_ENABLE_CPU_GPU_COMPARISON:BOOL=OFF','MAB_ENABLE_SANITIZERS:BOOL=OFF','MAB_ENABLE_OPENMP:BOOL=ON']:
 assert key in lines,key;print(key)
PY
cmake --build build/autonomous_cpu_release --parallel 2
```

Working directory: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`; start UTC: `2026-10-11T13:38:53.874062+00:00`.

Full stdout/stderr: [command_005.json](command_005.json).

## command_006.json: exit 0

Inspect static source diff and CTest-only helper before correctness execution; no workload

```sh
python3 -B - <<'PY'
import ast,difflib,pathlib
root=pathlib.Path.cwd();e=pathlib.Path("/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/cpu_only_release_20261011T133332368294Z")
for n in ['report/generate.py']:
 old=(e/'before'/n).read_text();new=(root/n).read_text();print(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='before/'+n,tofile=n)));ast.parse(new)
for p in [root/'report/verify_cpu.py',root/'report/test_cpu_release.py',e/'validate_cpu.py']:
 ast.parse(p.read_text());print('Inspected',p);print(p.read_text() if p.name=='validate_cpu.py' else 'AST valid; read-only reporting or mocked regressions')
print('No CMake, test registrations, algorithms, guards or selection manifests changed.')
PY
```

Working directory: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`; start UTC: `2026-10-11T13:39:23.798952+00:00`.

Full stdout/stderr: [command_006.json](command_006.json).

## command_007.json: exit 0

Run existing guarded CPU-only Release correctness suite after static path/source/build classification; excludes all timing tests

```sh
python3 -B '/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark/results/raw/cpu_only_release_20261011T133332368294Z/validate_cpu.py'
```

Working directory: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`; start UTC: `2026-10-11T13:39:23.886415+00:00`.

Full stdout/stderr: [command_007.json](command_007.json).

## command_008.json: exit 0

Diagnose raw OpenMP audit mismatch without launching executables

```sh
python3 -B - <<'PY'
import sys,json,pathlib
sys.path.insert(0,'scripts')
from analyze_parallel_results import analyze
x,_=analyze(pathlib.Path('results/raw/openmp_scaling_20261009T200852928292Z_retry1'))
y=json.loads(pathlib.Path('results/processed/openmp_scaling_20261009T200852928292Z_retry1/summary.json').read_text())
def diff(a,b,p=''):
 if type(a)!=type(b): print(p,type(a),type(b));return
 if isinstance(a,dict):
  for k in a.keys()|b.keys():
   if k not in a or k not in b:print(p,k,'missing')
   elif a[k]!=b[k]:diff(a[k],b[k],p+'/'+k)
 elif isinstance(a,list):
  if len(a)!=len(b):print(p,'length',len(a),len(b))
  else:
   for i,(u,v) in enumerate(zip(a,b)):
    if u!=v:diff(u,v,p+'/'+str(i))
 else:print(p,repr(a),repr(b))
diff(x,y)
PY
```

Working directory: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`; start UTC: `2026-10-11T13:42:31.699150+00:00`.

Full stdout/stderr: [command_008.json](command_008.json).

## command_009.json: exit 0

Correct tuple-versus-JSON-list audit comparison; focused eight inert report tests and full read-only raw reanalysis

```sh
python3 -B report/test_cpu_release.py -v && python3 -B - <<'PY'
import json,pathlib,sys
sys.path.insert(0,'report')
from verify_cpu import verify
v=verify(pathlib.Path('results/raw/autonomous_completion_20261011T095554571762Z'),pathlib.Path('results/processed/learned_rank_20261011T095554571762Z'),pathlib.Path('results/processed/count_memory_20261011T095554571762Z'))
with pathlib.Path('results/raw/cpu_only_release_20261011T133332368294Z/RAW_NUMERIC_AUDIT.json').open('x') as f:json.dump(v,f,indent=2,sort_keys=True)
print(json.dumps(v,indent=2))
PY
```

Working directory: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`; start UTC: `2026-10-11T13:42:50.274623+00:00`.

Full stdout/stderr: [command_009.json](command_009.json).

## command_010.json: exit 0

Verify deferred archive paths, inspect immutable approval scope and retained sanitizer logs

```sh
python3 -B - <<'PY'
import pathlib,json
r=pathlib.Path('.')
for p in ['src/cuda','third_party/cub','scripts/run_cpu_gpu_full.py','results/raw/cub_correctness_colab_20261009T223853955936Z','docs/CUDA_EXECUTION_GUIDE_v1.md','docs/CUDA_SORT_VALIDATION_GUIDE_v2.md']:
 print(p,(r/p).exists())
e=r/'results/raw/autonomous_completion_20261011T095554571762Z'
for n in ['cpu_release.json','cpu_sanitize.json']:
 d=json.loads((e/n).read_text());print(n,'exit',d['exit_code']); print(d['stdout'][-1200:]);print('sanitizer diagnostics',d['stderr']);print('argv',d['argv'])
print('baseline groups', {k:len(v) for k,v in json.loads(pathlib.Path('results/raw/cpu_only_release_20261011T133332368294Z/BASELINE.json').read_text()).items() if isinstance(v,dict)})
PY
rg -n 'def approval|TRUSTED_APPROVAL|def source_manifest|report/' scripts/cpu_gpu_evidence.py scripts/cpu_gpu_protocol.py
rg -n 'approval|full_study_eligible' scripts/non_timing_tests.py scripts/ctest_build_guard.py scripts/cpu_gpu_evidence.py
rg --files scripts | rg 'run_cpu_gpu|full'
```

Working directory: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`; start UTC: `2026-10-11T13:46:03.170202+00:00`.

Full stdout/stderr: [command_010.json](command_010.json).

## command_011.json: exit 0

Generate new CPU-only academic report, seven figures and twelve slides from raw-validated retained data; no benchmark execution

```sh
python3 -B report/generate.py --evidence results/raw/autonomous_completion_20261011T095554571762Z --learned results/processed/learned_rank_20261011T095554571762Z --metrics results/processed/count_memory_20261011T095554571762Z --output report/cpu_only_20261011T133332368294Z
```

Working directory: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`; start UTC: `2026-10-11T13:46:22.201067+00:00`.

Full stdout/stderr: [command_011.json](command_011.json).

## command_012.json: exit 0

Review generated report structure and PDF pagination; no performance workload

```sh
ls report/cpu_only_20261011T133332368294Z
pdfinfo report/cpu_only_20261011T133332368294Z/PRESENTATION.pdf
pdfinfo report/cpu_only_20261011T133332368294Z/REPORT.pdf
sed -n '1,32p' report/cpu_only_20261011T133332368294Z/FINAL_REPORT.md
pdftoppm -f 9 -singlefile -scale-to 1280 -png report/cpu_only_20261011T133332368294Z/PRESENTATION.pdf results/raw/cpu_only_release_20261011T133332368294Z/slide09_review
pdftoppm -f 12 -singlefile -scale-to 1280 -png report/cpu_only_20261011T133332368294Z/PRESENTATION.pdf results/raw/cpu_only_release_20261011T133332368294Z/slide12_review
```

Working directory: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`; start UTC: `2026-10-11T13:47:06.228641+00:00`.

Full stdout/stderr: [command_012.json](command_012.json).

## command_013.json: exit 0

Independently regenerate CPU-only report assets into another new directory for byte comparison; analysis only

```sh
python3 -B report/generate.py --evidence results/raw/autonomous_completion_20261011T095554571762Z --learned results/processed/learned_rank_20261011T095554571762Z --metrics results/processed/count_memory_20261011T095554571762Z --output report/cpu_only_20261011T133332368294Z_regenerated
```

Working directory: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`; start UTC: `2026-10-11T13:47:15.743190+00:00`.

Full stdout/stderr: [command_013.json](command_013.json).

## command_014.json: exit 0

Review final reporting/documentation diff and unchanged source-selection identity; no discovery or workloads

```sh
python3 -B - <<'PY'
import pathlib,json,hashlib,difflib,sys,ast
r=pathlib.Path.cwd();e=r/'results/raw/cpu_only_release_20261011T133332368294Z';b=json.loads((e/'BASELINE.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
allowed={'README.md','docs/ROADMAP.md','docs/AUDIT.md','docs/ALGORITHMS.md','docs/BENCHMARKING.md','docs/METRICS.md'}
changed=[n for n,d in b['project_sha256'].items() if sha(r/n)!=d];assert set(changed)==allowed,changed
report_changed=[n for n,d in b['report_sha256'].items() if sha(r/n)!=d];assert set(report_changed)=={'report/README.md','report/generate.py'},report_changed
chunks=[]
for n in sorted(changed+report_changed):
 old=(e/'before'/n).read_text();new=(r/n).read_text();chunks.extend(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='before/'+n,tofile=n))
(e/'SOURCE_DIFF.patch').write_text(''.join(chunks))
for p in [r/'report/generate.py',r/'report/verify_cpu.py',r/'report/test_cpu_release.py']:ast.parse(p.read_text())
sys.path.insert(0,'scripts')
from cpu_gpu_protocol import source_manifest
from non_timing_tests import load_manifest
m=load_manifest();print('Reviewed source identity valid:',len(source_manifest()),'files');print('manifest keys',list(m))
print('Modified project files',changed);print('Modified report tools',report_changed)
for p in ['docs/CPU_ONLY_RELEASE_v1.md','docs/DEFERRED_GPU.md','report/verify_cpu.py','report/test_cpu_release.py']:
 print('Additive source/doc',p,sha(r/p))
PY
```

Working directory: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`; start UTC: `2026-10-11T13:48:09.301781+00:00`.

Full stdout/stderr: [command_014.json](command_014.json).

## command_015.json: exit 0

Compare every regenerated asset byte-for-byte and verify plot/input manifests and preserved CPU binaries

```sh
python3 -B - <<'PY'
import json,pathlib,hashlib
r=pathlib.Path.cwd();e=r/'results/raw/cpu_only_release_20261011T133332368294Z';a=r/'report/cpu_only_20261011T133332368294Z';b=r/'report/cpu_only_20261011T133332368294Z_regenerated';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
x={p.name:sha(p) for p in a.iterdir() if p.is_file()};y={p.name:sha(p) for p in b.iterdir() if p.is_file()};assert x==y,'regeneration differs'
for directory in [a,b]:
 for f in ['INPUTS_SHA256.json','RENDER_INPUTS_SHA256.json']:
  for n,d in json.loads((directory/f).read_text()).items():assert sha(r/n)==d,(f,n)
 for n,d in json.loads((directory/'SHA256.json').read_text()).items():assert sha(directory/n)==d,n
 assert len(json.loads((directory/'PLOTS.json').read_text()))==7
 t=json.loads((directory/'RESULT_TABLES.json').read_text());assert t['scope']=='cpu_only_release_v1' and 'gpu' not in t
 print(directory.relative_to(r),len(x),'files; 7 figures; all manifests verified')
base=json.loads((e/'BASELINE.json').read_text())
for n,d in base['executable_sha256'].items():assert sha(r/n)==d,n
out=dict(byte_identical=True,files=len(x),sha256=x,figures=7,presentation_pages=12,report_pages=20,workloads_executed=0)
with (e/'REGENERATION.json').open('x') as f:json.dump(out,f,indent=2,sort_keys=True)
print('All17 assets including PDFs/PNGs regenerated byte-identically; nine CPU binary identities unchanged.')
PY
```

Working directory: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`; start UTC: `2026-10-11T13:48:43.461542+00:00`.

Full stdout/stderr: [command_015.json](command_015.json).

## command_016.json: exit 0

Qualify preserved identity map: three native executables plus six metadata/protocol files, not nine binaries; inspect retained sanitizer identity

```sh
python3 -B - <<'PY'
import json,pathlib
r=pathlib.Path('.');e=r/'results/raw/cpu_only_release_20261011T133332368294Z';b=json.loads((e/'BASELINE.json').read_text())
print('Correction to command_015 prose: nine identity-map entries include only three native binaries.')
print(json.dumps(json.loads((r/'results/raw/autonomous_completion_20261011T095554571762Z/CPU_STUDY_IDENTITIES.json').read_text()),indent=2)[:7000])
print('Previous completed sanitizer source selection map keys',json.loads((r/'results/raw/autonomous_completion_20261011T095554571762Z/cpu_sanitize_selection.json').read_text()).keys())
PY
```

Working directory: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`; start UTC: `2026-10-11T13:49:18.195220+00:00`.

Full stdout/stderr: [command_016.json](command_016.json).

## command_017.json: exit 0

Consolidated preservation, frozen-anchor, raw-audit and reused sanitizer source/selection verification; no tests or workloads

```sh
python3 -B results/raw/cpu_only_release_20261011T133332368294Z/final_review.py
```

Working directory: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`; start UTC: `2026-10-11T13:50:12.642664+00:00`.

Full stdout/stderr: [command_017.json](command_017.json).

## Supplemental inspection and editing

Repository/tool inspections also used pwd, rg, ls, sed/cat, read-only Python, process-status inspection, and image viewing; source/document edits used apply_patch. These did not launch algorithms or experiments. Early inspection encountered absent guessed paths (docs/LOCAL_SELECTION_v5.md and several analyzer names); the actual paths were discovered before use. One guessed NEW_CUB_CORRECTNESS path was absent; the preserved actual correctness directory is listed in DEFERRED_GPU.md. These terminal inspection outputs are in the session transcript rather than standalone command JSON. They are not represented as successful validation commands. Git metadata was absent; no Git repository was initialized.

Final evidence generation command (report writing and hashing only):

```sh
python3 -B results/raw/cpu_only_release_20261011T133332368294Z/seal_release.py
```

Its own completion status is recorded in SEAL_STATUS.json; the seal excludes itself explicitly.
