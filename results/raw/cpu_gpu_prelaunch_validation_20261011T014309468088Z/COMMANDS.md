# Commands and exit statuses

No CTest discovery/tests, configure/build, sanitizer, CUDA workload, workspace allocation, warm-up, measured trial, pilot or study command ran. Exact child argv and cwd are below; recorder JSON retains full outputs.

## Control command

Exit:0; classification: read-only repository identity

```bash
pwd
```

## Control command

Exit:0; classification: read-only repository instructions

```bash
cat AGENTS.md
```

## Control command

Exit:0; classification: read-only evidence-directory listing

```bash
ls results/raw/cpu_gpu_prelaunch_review_20261011T012430643251Z results/raw/isolated_colab_revalidation_20261011T011459127026Z
```

## Control command

Exit:0; classification: read-only source/history hashes; exclusive new evidence-directory creation

```bash
python3 -B - <<'PY'
import datetime,hashlib,json
from pathlib import Path
r=Path.cwd()
e=r/'results/raw'/('cpu_gpu_prelaunch_validation_'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
e.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
old=r/'results/raw/cpu_gpu_prelaunch_review_20261011T012430643251Z'
b=json.loads((old/'BEFORE.json').read_text())
current={'historical_results_sha256':{str(p.relative_to(r)):sha(p) for p in sorted((r/'results').rglob('*')) if p.is_file() and not p.is_relative_to(e)},'project_sha256':{k:sha(r/k) for k in b['project_sha256']},'build_metadata_sha256':{k:sha(r/k) for k in b['build_metadata_sha256']}}
assert all(current['project_sha256'][k]==v for k,v in b['project_sha256'].items()),'source changed since review'
assert all(current['build_metadata_sha256'][k]==v for k,v in b['build_metadata_sha256'].items()),'build metadata changed since review'
with (e/'BEFORE.json').open('x') as f:json.dump(current,f,indent=2,sort_keys=True);f.write('\n')
with (e/'record.py').open('xb') as f:f.write((old/'record.py').read_bytes())
print(str(e.relative_to(r)));print('historical_result_files',len(current['historical_results_sha256']))
PY
```

## colab_sessions.json

Exit:0; classification: Read-only approved Colab session availability; no workload

```bash
colab sessions
```

cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`.

## colab_status.json

Exit:0; classification: Read-only status of existing approved session; no workload

```bash
colab status --session cpu-gpu-validation
```

cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`.

## control_commands.json

Exit:0; classification: Evidence-only audit command assembly; no validation workloads

```bash
python3 -B -c 'import json;from pathlib import Path;p=Path("results/raw/cpu_gpu_prelaunch_validation_20261011T014309468088Z/CONTROL_COMMANDS.json");f=p.open('"'"'x'"'"');json.dump(json.loads("[{\"command\":\"pwd\",\"classification\":\"read-only repository identity\"},{\"command\":\"cat AGENTS.md\",\"classification\":\"read-only repository instructions\"},{\"command\":\"ls results/raw/cpu_gpu_prelaunch_review_20261011T012430643251Z results/raw/isolated_colab_revalidation_20261011T011459127026Z\",\"classification\":\"read-only evidence-directory listing\"},{\"command\":\"python3 -B - <<'"'"'PY'"'"'\\nimport datetime,hashlib,json\\nfrom pathlib import Path\\nr=Path.cwd()\\ne=r/'"'"'results/raw'"'"'/('"'"'cpu_gpu_prelaunch_validation_'"'"'+datetime.datetime.now(datetime.timezone.utc).strftime('"'"'%Y%m%dT%H%M%S%fZ'"'"'))\\ne.mkdir()\\ndef sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()\\nold=r/'"'"'results/raw/cpu_gpu_prelaunch_review_20261011T012430643251Z'"'"'\\nb=json.loads((old/'"'"'BEFORE.json'"'"').read_text())\\ncurrent={'"'"'historical_results_sha256'"'"':{str(p.relative_to(r)):sha(p) for p in sorted((r/'"'"'results'"'"').rglob('"'"'*'"'"')) if p.is_file() and not p.is_relative_to(e)},'"'"'project_sha256'"'"':{k:sha(r/k) for k in b['"'"'project_sha256'"'"']},'"'"'build_metadata_sha256'"'"':{k:sha(r/k) for k in b['"'"'build_metadata_sha256'"'"']}}\\nassert all(current['"'"'project_sha256'"'"'][k]==v for k,v in b['"'"'project_sha256'"'"'].items()),'"'"'source changed since review'"'"'\\nassert all(current['"'"'build_metadata_sha256'"'"'][k]==v for k,v in b['"'"'build_metadata_sha256'"'"'].items()),'"'"'build metadata changed since review'"'"'\\nwith (e/'"'"'BEFORE.json'"'"').open('"'"'x'"'"') as f:json.dump(current,f,indent=2,sort_keys=True);f.write('"'"'\\\\n'"'"')\\nwith (e/'"'"'record.py'"'"').open('"'"'xb'"'"') as f:f.write((old/'"'"'record.py'"'"').read_bytes())\\nprint(str(e.relative_to(r)));print('"'"'historical_result_files'"'"',len(current['"'"'historical_results_sha256'"'"']))\\nPY\",\"classification\":\"read-only source/history hashes; exclusive new evidence-directory creation\"}]"),f,indent=2);f.write('"'"'\n'"'"');f.close();print('"'"'Evidence-only control-command record saved'"'"')'
```

cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`.

## focused_safety_source.json

Exit:0; classification: Read-only numbered validation-path inspection

```bash
bash -c 'nl -ba tests/test_cuda_benchmark.py | sed -n "1,260p"; nl -ba src/cuda/cub_timing.cu | sed -n "80,190p"; nl -ba tests/test_parallel_mergesort.cpp | sed -n "1,200p"; nl -ba scripts/non_timing_tests.py | sed -n "100,210p"'
```

cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`.

## frozen_and_cli_docs.json

Exit:0; classification: Read-only local source/evidence inspection

```bash
bash -c 'cat docs/CPU_GPU_COMPARISON_PROTOCOL_v1.md docs/studies/cpu_gpu_comparison_v1.matrix.json docs/studies/cpu_gpu_comparison_v1.resources.csv docs/studies/cpu_gpu_comparison_v1.freeze.json results/raw/colab_t4_diagnostics_20261011T005409276199Z/COMMANDS.md'
```

cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`.

## required_records.json

Exit:0; classification: Read-only local source/evidence inspection

```bash
bash -c 'cat results/raw/cpu_gpu_prelaunch_review_20261011T012430643251Z/FINAL_AUDIT.md results/raw/cpu_gpu_prelaunch_review_20261011T012430643251Z/COMMANDS.md results/raw/cpu_gpu_prelaunch_review_20261011T012430643251Z/FINAL_INTEGRITY.json results/raw/isolated_colab_revalidation_20261011T011459127026Z/FINAL_AUDIT.md results/raw/isolated_colab_revalidation_20261011T011459127026Z/COMMANDS.md results/raw/isolated_colab_revalidation_20261011T011459127026Z/FINAL_INTEGRITY.json'
```

cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`.

## source_entry_points.json

Exit:0; classification: Read-only local source/evidence inspection

```bash
bash -c 'cat scripts/non_timing_tests.py scripts/ctest_build_guard.py scripts/validate_cpu_gpu_pilot.py tests/test_cuda_benchmark.py src/cuda/cub_timing.cu tests/test_parallel_mergesort.cpp include/algorithms/detail/parallel_mergesort_impl.hpp src/cuda/comparison_resources.cu'
```

cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`.

## Evidence-only tool action and finalization

apply_patch added only this directory's finalize.py and returned success. No project source was patched.

```bash
python3 -B results/raw/cpu_gpu_prelaunch_validation_20261011T014309468088Z/finalize.py
```

Exit:0 upon successful completion; assertions abort on any integrity mismatch. Standard-library reads/hashes and exclusive evidence writes only; no subprocesses or repository imports.

Recorder wrapper: `python3 -B results/raw/cpu_gpu_prelaunch_validation_20261011T014309468088Z/record.py NAME SCOPE TIMEOUT CHILD_ARGV...`.
Terminal polling retrieves already-running evidence-hash command output and starts no additional workload. URL-shaped text is redacted by the copied recorder; original files remain authoritative.
