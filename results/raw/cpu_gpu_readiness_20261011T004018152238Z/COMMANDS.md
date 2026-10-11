# Exact diagnostic commands and observed exit statuses

Scope: static inspection and authorized non-benchmark tool/resource diagnostics only. No tests, CTest discovery, configure/build, CUDA execution, sorting calls, warmups or measured trials. A diagnostic command exit0 does not imply GPU availability or study eligibility.

## Initial unwrapped commands

```sh
bash -lc 'pwd
cat AGENTS.md
cat results/raw/ctest_path_independent_review_20261011T000547578754Z/FINAL_AUDIT.md
cat results/raw/ctest_path_independent_review_20261011T000547578754Z/COMMANDS.md
cat results/raw/ctest_path_independent_review_20261011T000547578754Z/FINAL_INTEGRITY.json'
```

Observed exit: 0. Pre-check file reads only; overall shell status observed; terminal rendering truncated.

```sh
bash -lc 'python3 -B - <<'"'"'PY'"'"'
import datetime,hashlib,json,sys
from pathlib import Path
r=Path.cwd();e=r/'"'"'results/raw'"'"'/('"'"'cpu_gpu_readiness_'"'"'+datetime.datetime.now(datetime.timezone.utc).strftime('"'"'%Y%m%dT%H%M%S%fZ'"'"'));e.mkdir()
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def scan(paths,cache=False):return {str(p.relative_to(r)):h(p) for b in paths for p in ([b] if b.is_file() else sorted(b.rglob('"'"'*'"'"'))) if p.is_file() and not p.is_relative_to(e) and not(cache and '"'"'__pycache__'"'"' in p.parts)}
names={'"'"'CTestTestfile.cmake'"'"','"'"'CTestCustom.cmake'"'"','"'"'CTestCustom.ctest'"'"','"'"'CTestConfig.cmake'"'"','"'"'DartConfiguration.tcl'"'"','"'"'CMakeCache.txt'"'"','"'"'build.ninja'"'"','"'"'Makefile'"'"','"'"'compile_commands.json'"'"'}
before={'"'"'command_argv'"'"':sys.orig_argv,'"'"'cwd'"'"':str(r),'"'"'prior_results_sha256'"'"':scan([r/'"'"'results'"'"']),'"'"'project_sha256'"'"':scan([r/p for p in ['"'"'AGENTS.md'"'"','"'"'README.md'"'"','"'"'CMakeLists.txt'"'"','"'"'docs'"'"','"'"'scripts'"'"','"'"'tests'"'"','"'"'include'"'"','"'"'src'"'"','"'"'cmake'"'"','"'"'third_party'"'"']],True),'"'"'build_metadata_sha256'"'"':{str(p.relative_to(r)):h(p) for p in sorted((r/'"'"'build'"'"').rglob('"'"'*'"'"')) if p.is_file() and p.name in names}}
with (e/'"'"'BEFORE.json'"'"').open('"'"'x'"'"') as f:json.dump(before,f,indent=2,sort_keys=True);f.write('"'"'\n'"'"')
print(e.relative_to(r));print({k:len(v) for k,v in before.items() if k.endswith('"'"'sha256'"'"')})
PY'
```

Observed exit: 0. Exclusive evidence directory and hash snapshot only; complete program also in BEFORE.command_argv.

## Recorded child commands

Recorder: `python3 -B results/raw/cpu_gpu_readiness_20261011T004018152238Z/record.py NAME CATEGORY CHILD_ARGV...`. Each listed JSON contains exact argv, cwd, timestamp, stdout/stderr and observed child status. The recorder itself writes only this new evidence directory.

### build_requirements.json

```sh
bash -c 'sed -n '"'"'1,42p'"'"' CMakeLists.txt
sed -n '"'"'1,112p'"'"' cmake/cuda.cmake
cat third_party/cub/README.md'
```

Observed child exit: 0. Category: static-inspection-only.

### cgroup_mounts.json

```sh
cat /proc/self/mountinfo
```

Observed child exit: 0. Category: read-only-existing-procedure.

### cmake_version.json

```sh
cmake --version
```

Observed child exit: 0. Category: non-benchmark-version-or-read-only-inventory.

### colab_help.json

```sh
colab --help
```

Observed child exit: 0. Category: non-benchmark-version-or-read-only-inventory.

### colab_procedures.json

```sh
rg -n 'colab sessions|colab status|colab exec|colab run|colab --|nvidia-smi|nvcc --version' docs/CUDA_EXECUTION_GUIDE_v1.md results/raw/cub_workspace_65537_20261010T110457531249Z/COMMANDS.md
```

Observed child exit: 0. Category: static-read.

### colab_sessions.json

```sh
colab sessions
```

Observed child exit: 0. Category: non-benchmark-version-or-read-only-inventory.

### colab_version.json

```sh
colab version
```

Observed child exit: 0. Category: CLI-version-only.

### cpu_inventory.json

```sh
lscpu
```

Observed child exit: 0. Category: non-benchmark-version-or-read-only-inventory.

### gate_definitions.json

```sh
sed -n 40,104p scripts/run_cpu_gpu_pilot.py
```

Observed child exit: 0. Category: static-read.

### gcc_version.json

```sh
gcc --version
```

Observed child exit: 0. Category: non-benchmark-version-or-read-only-inventory.

### general_protocol.json

```sh
cat docs/EXPERIMENT_PROTOCOL.md
```

Observed child exit: 0. Category: static-inspection-only.

### gxx_version.json

```sh
g++ --version
```

Observed child exit: 0. Category: non-benchmark-version-or-read-only-inventory.

### library_cache.json

```sh
/usr/sbin/ldconfig -p
```

Observed child exit: 0. Category: non-benchmark-version-or-read-only-inventory.

### local_observations.json

```sh
python3 -B results/raw/cpu_gpu_readiness_20261011T004018152238Z/observe_local.py
```

Observed child exit: 0. Category: read-only-resource-diagnostics.

### openmp_library.json

```sh
g++ -print-file-name=libgomp.so
```

Observed child exit: 0. Category: non-benchmark-version-or-read-only-inventory.

### prior_resource_audit.json

```sh
bash -c 'cat results/raw/cub_workspace_65537_20261010T110457531249Z/FINAL_AUDIT.md
cat docs/studies/cpu_gpu_comparison_v1.resources.csv
cat docs/studies/cpu_gpu_comparison_v1.freeze.json'
```

Observed child exit: 0. Category: static inspection only.

### procedures_code.json

```sh
bash -c 'sed -n '"'"'1,230p'"'"' scripts/run_cpu_gpu_study.py
sed -n '"'"'1,200p'"'"' scripts/validate_cpu_gpu_pilot.py
sed -n '"'"'1,180p'"'"' scripts/capture_environment.py'
```

Observed child exit: 0. Category: static inspection only.

### procedures_docs.json

```sh
bash -c 'rg -n -i '"'"'prerequis|resource|memory|workspace|readiness|free |df |lscpu|nvidia-smi|colab (sessions|status|exec)'"'"' docs/CPU_GPU_COMPARISON_PROTOCOL_v1.md docs/CUDA_TIMING_PROTOCOL_v1.md docs/CTEST_BUILD_GUARD_v1.md README.md docs/ROADMAP.md'
```

Observed child exit: 0. Category: static inspection only.

### protocol_gates.json

```sh
sed -n 247,286p docs/CPU_GPU_COMPARISON_PROTOCOL_v1.md
```

Observed child exit: 0. Category: static-read.

### python_version.json

```sh
python3 --version
```

Observed child exit: 0. Category: non-benchmark-version-or-read-only-inventory.

### readiness_flags.json

```sh
python3 -B -c 'import json;from pathlib import Path;e=Path('"'"'results/raw/cpu_gpu_readiness_20261011T004018152238Z'"'"');d=json.loads((e/'"'"'STATIC_READINESS.json'"'"').read_text());print('"'"'\n'"'"'.join(x['"'"'cache'"'"']+'"'"' '"'"'+str({k:v for k,v in x['"'"'metadata'"'"'].items() if k in ['"'"'CMAKE_BUILD_TYPE:STRING'"'"','"'"'MAB_ENABLE_CUDA:BOOL'"'"','"'"'MAB_ENABLE_CUDA_SORT:BOOL'"'"','"'"'MAB_ENABLE_CPU_GPU_COMPARISON:BOOL'"'"','"'"'MAB_ENABLE_OPENMP:BOOL'"'"','"'"'MAB_ENABLE_SANITIZERS:BOOL'"'"']}) for x in d['"'"'build_caches'"'"']))'
```

Observed child exit: 0. Category: static-inspection-only.

### readiness_summary.json

```sh
python3 -B -c 'import json;from pathlib import Path;e=Path("results/raw/cpu_gpu_readiness_20261011T004018152238Z");d=json.loads((e/"STATIC_READINESS.json").read_text());r=json.loads((e/"LOCAL_OBSERVATIONS.json").read_text());print("cache count",len(d["build_caches"]));print("present comparison binaries",[str(p) for p in Path("build").rglob("cpu_gpu_comparison") if p.is_file()]);print("frozen",d["frozen"],"anchors",d["protected_anchors"],"source",d["reviewed_source"]);print("governors",{v.get("text") for v in r["governors"].values()});print("cgroup accessible settings",[(p,k,v["text"]) for p,rows in r["cgroup_ancestors"].items() for k,v in rows.items() if v.get("available")]);print("RAM available GiB",r["memory_bytes"]["MemAvailable"]/1024**3,"disk free GiB",r["disk"]["free_bytes"]/1024**3);print("mount entries",[x for x in json.loads((e/"cgroup_mounts.json").read_text())["stdout"].splitlines() if "cgroup" in x])'
```

Observed child exit: 0. Category: static-evidence-summary.

### resource_paths.json

```sh
bash -c 'rg -n '"'"'def validate_resources|mem_available|disk_free|workspace|memory_cap|available|affinity|OMP_|nvidia|CUB'"'"' scripts/analyze_cpu_gpu.py scripts/run_cpu_gpu_pilot.py scripts/cuda_preflight.py CMakeLists.txt cmake/cuda.cmake'
```

Observed child exit: 0. Category: static inspection only.

### static_readiness.json

```sh
python3 -B results/raw/cpu_gpu_readiness_20261011T004018152238Z/inspect_static.py
```

Observed child exit: 0. Category: static-hashes-only.

## Not executed

No nvcc/nvidia-smi command ran locally because they are absent. No colab status/exec followed the empty session inventory. No session creation/reconnect, upload, install, kernel/runtime probe, CUB query/allocation, test, project binary, prerequisite runner, CTest, configure/build or benchmark was invoked. The Colab inventory reported pruning one stale external local session-cache entry.

## Evidence authoring

apply_patch created only record.py, PERMITTED_CHECKS.md, inspect_static.py, observe_local.py, EARLY_COMMANDS.json, FINAL_AUDIT.md and seal_validation.py inside this exclusive new evidence directory; all tool calls succeeded. BEFORE.json was created by the retained exclusive bootstrap. The static inspector and observation collector wrote their own JSON outputs here. No project or historical file was changed.

## Final preservation/seal command

```sh
python3 -B results/raw/cpu_gpu_readiness_20261011T004018152238Z/seal_validation.py
```

Executed directly to avoid writing an unsealed recorder log afterward. Successful terminal exit0 confirms all preservation assertions passed before the final seal was written. It creates this command inventory and the final manifest only.
