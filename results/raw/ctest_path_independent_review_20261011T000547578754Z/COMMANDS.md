# Review commands and statuses

Only file reads, directory listings, JSON/AST parsing, SHA-256 checks and new review-evidence writes occurred. No repository import/helper call, CTest discovery/tests, build, prerequisite/resource check, timer workload, benchmark, pilot, GPU command, or study ran.

## Initial unwrapped commands

Full shell text/argv is retained in EARLY_COMMANDS.json and BEFORE.json. Overall shell statuses were observed; individual commands in multi-read shells were not independently instrumented.

### Early command 1

```sh
bash -lc 'pwd
cat AGENTS.md
cat results/raw/ctest_path_repair_20261010T234224414430Z/FINAL_AUDIT.md
cat results/raw/ctest_path_repair_20261010T234224414430Z/COMMANDS.md
cat results/raw/ctest_path_repair_20261010T234224414430Z/FINAL_INTEGRITY.json
cat results/raw/ctest_guard_review_20261010T232702450912Z/FINAL_AUDIT.md'
```

Observed exit: 0. Initial inspection before recorder; overall shell exit observed, individual cat statuses not separately instrumented; terminal output was truncated.

### Early command 2

```sh
bash -lc 'ls -la results/raw/ctest_path_repair_20261010T234224414430Z
sed -n '"'"'1,240p'"'"' scripts/non_timing_tests.py
sed -n '"'"'1,200p'"'"' scripts/ctest_build_guard.py'
```

Observed exit: 0. Read-only listing and source inspection, before recorder.

### Early command 3

```sh
bash -lc 'python3 -B - <<'"'"'PY'"'"'
import sys,json,hashlib,datetime
from pathlib import Path
root=Path.cwd()
e=root/'"'"'results/raw'"'"'/('"'"'ctest_path_independent_review_'"'"'+datetime.datetime.now(datetime.timezone.utc).strftime('"'"'%Y%m%dT%H%M%S%fZ'"'"'))
e.mkdir(exist_ok=False)
def h(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def scan(paths): return {str(p.relative_to(root)):h(p) for start in paths for p in ([start] if start.is_file() else sorted(start.rglob('"'"'*'"'"'))) if p.is_file() and '"'"'__pycache__'"'"' not in p.parts and not p.is_relative_to(e)}
meta={'"'"'CTestTestfile.cmake'"'"','"'"'CTestCustom.cmake'"'"','"'"'CTestCustom.ctest'"'"','"'"'CTestConfig.cmake'"'"','"'"'DartConfiguration.tcl'"'"'}
data={'"'"'root'"'"':str(root),'"'"'evidence'"'"':str(e.relative_to(root)),'"'"'bootstrap_argv'"'"':sys.orig_argv,'"'"'prior_results_sha256'"'"':scan([root/'"'"'results'"'"']),'"'"'project_sha256'"'"':scan([root/p for p in ['"'"'AGENTS.md'"'"','"'"'README.md'"'"','"'"'CMakeLists.txt'"'"','"'"'scripts'"'"','"'"'tests'"'"','"'"'docs'"'"','"'"'include'"'"','"'"'src'"'"','"'"'cmake'"'"','"'"'third_party'"'"']]),'"'"'build_metadata_sha256'"'"':{str(p.relative_to(root)):h(p) for p in sorted((root/'"'"'build'"'"').rglob('"'"'*'"'"')) if p.is_file() and p.name in meta}}
(e/'"'"'BEFORE.json'"'"').write_text(json.dumps(data,indent=2,sort_keys=True)+'"'"'\n'"'"')
print(json.dumps({'"'"'evidence'"'"':str(e.relative_to(root)),'"'"'counts'"'"':{k:len(v) for k,v in data.items() if k.endswith('"'"'sha256'"'"')}}))
PY'
```

Observed exit: 0. Only own exclusive evidence directory created; hash snapshot; stored stdin program also in BEFORE.bootstrap_argv.

### Early command 4

```sh
bash -lc 'python3 -B - <<'"'"'PY'"'"'
from pathlib import Path
p=Path('"'"'results/raw/ctest_path_independent_review_20261011T000547578754Z'"'"')
(p/'"'"'record.py'"'"').write_text('"'"''"'"''"'"'import datetime,json,subprocess,sys\nfrom pathlib import Path\ne=Path(__file__).resolve().parent\nname=sys.argv[1]; argv=sys.argv[2:]\nr=subprocess.run(argv,capture_output=True,text=True)\nd={'"'"'argv'"'"':argv,'"'"'cwd'"'"':str(Path.cwd()),'"'"'exit_code'"'"':r.returncode,'"'"'stdout'"'"':r.stdout,'"'"'stderr'"'"':r.stderr,'"'"'classification'"'"':'"'"'read-only static inspection/hash/JSON/AST; no repository imports, tests, CTest, builds, probes, or benchmarks'"'"'}\nwith (e/(name+'"'"'.json'"'"')).open('"'"'x'"'"') as f: json.dump(d,f,indent=2); f.write('"'"'\\n'"'"')\nprint(r.stdout,end='"'"''"'"'); print(r.stderr,end='"'"''"'"',file=sys.stderr); print('"'"'RECORDED EXIT'"'"',r.returncode)\nsys.exit(r.returncode)\n'"'"''"'"''"'"')
print(p/'"'"'record.py'"'"')
PY'
```

Observed exit: 0. Only own record.py written.

## Recorded inspection commands

Recorder invocation: `python3 -B results/raw/ctest_path_independent_review_20261011T000547578754Z/record.py NAME CHILD_ARGV...`. Each JSON below retains exact child argv, cwd, full stdout/stderr and observed exit. These are this review's commands; historical test commands read as text were not rerun.

### cub_files.json

```sh
rg --files third_party/cub
```

Observed exit: 0. read-only static inspection/hash/JSON/AST; no repository imports, tests, CTest, builds, probes, or benchmarks

### earlier_audits.json

```sh
bash -c 'cat results/raw/ctest_guard_review_20261010T232702450912Z/FINAL_AUDIT.md docs/CTEST_BUILD_GUARD_v1.md'
```

Observed exit: 0. read-only static inspection/hash/JSON/AST; no repository imports, tests, CTest, builds, probes, or benchmarks

### earlier_context.json

```sh
bash -c 'python3 -B - <<'"'"'PY'"'"'
from pathlib import Path
for name in ['"'"'cpu_gpu_repair_review_20261010T185659333607Z'"'"','"'"'cpu_gpu_safety_repair_20261010T140524185993Z'"'"']:
 p=Path('"'"'results/raw'"'"')/name/'"'"'FINAL_AUDIT.md'"'"'
 text=p.read_text();print(str(p));print(text)
PY'
```

Observed exit: 0. read-only static inspection/hash/JSON/AST; no repository imports, tests, CTest, builds, probes, or benchmarks

### entrypoints_numbered.json

```sh
bash -c 'nl -ba scripts/non_timing_tests.py
nl -ba scripts/validate_cpu_gpu_pilot.py
sed -n '"'"'20,30p'"'"' scripts/run_cpu_gpu_pilot.py'
```

Observed exit: 0. read-only static inspection/hash/JSON/AST; no repository imports, tests, CTest, builds, probes, or benchmarks

### guard_numbered.json

```sh
bash -c 'nl -ba scripts/ctest_build_guard.py'
```

Observed exit: 0. read-only static inspection/hash/JSON/AST; no repository imports, tests, CTest, builds, probes, or benchmarks

### independent_verification.json

```sh
python3 -B results/raw/ctest_path_independent_review_20261011T000547578754Z/verify_static.py
```

Observed exit: 0. read-only static inspection/hash/JSON/AST; no repository imports, tests, CTest, builds, probes, or benchmarks

### repair_audit.json

```sh
cat results/raw/ctest_path_repair_20261010T234224414430Z/FINAL_AUDIT.md results/raw/ctest_path_repair_20261010T234224414430Z/COMMANDS.md
```

Observed exit: 0. read-only static inspection/hash/JSON/AST; no repository imports, tests, CTest, builds, probes, or benchmarks

### repair_runner.json

```sh
cat results/raw/ctest_path_repair_20261010T234224414430Z/run_inert_tests.py scripts/validate_cpu_gpu_pilot.py
```

Observed exit: 0. read-only static inspection/hash/JSON/AST; no repository imports, tests, CTest, builds, probes, or benchmarks

### retained_tests.json

```sh
python3 -B -c 'import json;from pathlib import Path;b=Path("results/raw/ctest_path_repair_20261010T234224414430Z");print((b/"run_inert_tests.py").read_text());
for n in ["inert_reproducer_before_fix","inert_regressions_after_repair","all_inert_selector_regressions"]:
 d=json.loads((b/"commands"/(n+".json")).read_text()); print(n,"ARGV",d["argv"],"EXIT",d["exit_code"]);print(d["stderr"])'
```

Observed exit: 0. read-only static inspection/hash/JSON/AST; no repository imports, tests, CTest, builds, probes, or benchmarks

### runner_imports.json

```sh
bash -c 'cat results/raw/ctest_path_repair_20261010T234224414430Z/run_inert_tests.py tests/ctest_fixture.py
sed -n '"'"'1,95p'"'"' scripts/validate_cpu_gpu_pilot.py
sed -n '"'"'1,55p'"'"' scripts/run_cpu_gpu_pilot.py'
```

Observed exit: 0. read-only static inspection/hash/JSON/AST; no repository imports, tests, CTest, builds, probes, or benchmarks

### seal_structure.json

```sh
bash -c 'python3 -B - <<'"'"'PY'"'"'
import json
from pathlib import Path
b=Path('"'"'results/raw/ctest_path_repair_20261010T234224414430Z'"'"')
for name in ['"'"'FINAL_INTEGRITY.json'"'"','"'"'BEFORE.json'"'"','"'"'FILE_REVIEW.json'"'"','"'"'commands/inert_reproducer_before_fix.json'"'"','"'"'commands/all_inert_selector_regressions.json'"'"']:
 d=json.loads((b/name).read_text()); print(name,[(k,len(v) if isinstance(v,(dict,list,str)) else v) for k,v in d.items()]);
 if name=='"'"'FINAL_INTEGRITY.json'"'"':print(json.dumps({k:v for k,v in d.items() if k!='"'"'evidence_sha256'"'"'},indent=2))
allfiles=[p for p in Path('"'"'results'"'"').rglob('"'"'*'"'"') if p.is_file() and '"'"'ctest_path_independent_review_20261011T000547578754Z'"'"' not in p.parts]
print('"'"'all prior results'"'"',len(allfiles));print('"'"'cache files'"'"',[str(p) for p in allfiles if '"'"'__pycache__'"'"' in p.parts])
PY'
```

Observed exit: 0. read-only static inspection/hash/JSON/AST; no repository imports, tests, CTest, builds, probes, or benchmarks

### selection_class_source.json

```sh
sed -n '/class SelectorTests/,$p' tests/test_cpu_gpu_safety.py
```

Observed exit: 0. read-only static inspection/hash/JSON/AST; no repository imports, tests, CTest, builds, probes, or benchmarks

### selector_surroundings.json

```sh
bash -c 'cat tests/ctest_fixture.py
sed -n '"'"'1,70p'"'"' tests/test_cpu_gpu_safety.py
sed -n '"'"'/class SelectorTests/,/if __name__/p'"'"' tests/test_cpu_gpu_safety.py
sed -n '"'"'1,70p'"'"' scripts/cpu_gpu_protocol.py'
```

Observed exit: 0. read-only static inspection/hash/JSON/AST; no repository imports, tests, CTest, builds, probes, or benchmarks

### source_diff.json

```sh
cat results/raw/ctest_path_repair_20261010T234224414430Z/SOURCE_DIFF.patch
```

Observed exit: 0. read-only static inspection/hash/JSON/AST; no repository imports, tests, CTest, builds, probes, or benchmarks

### static_call_boundaries.json

```sh
bash -c 'rg -n "def source_manifest|def validate_prerequisites|non-timing subset|if __name__|selected_ctest|ctest|cub_version|300001" scripts/cpu_gpu_protocol.py scripts/run_cpu_gpu_pilot.py scripts/validate_cpu_gpu_pilot.py scripts/validate_cuda_sort.py scripts/validate_cuda_timing.py third_party/cub/cub_version.cuh
sed -n "1,42p" scripts/validate_cpu_gpu_pilot.py
sed -n "69,83p" scripts/cpu_gpu_protocol.py
sed -n "334,362p" tests/test_ctest_build_guard.py'
```

Observed exit: 0. read-only static inspection/hash/JSON/AST; no repository imports, tests, CTest, builds, probes, or benchmarks

### test_guards.json

```sh
bash -c 'sed -n '"'"'185,380p'"'"' tests/test_ctest_build_guard.py'
```

Observed exit: 0. read-only static inspection/hash/JSON/AST; no repository imports, tests, CTest, builds, probes, or benchmarks

### test_paths.json

```sh
bash -c 'sed -n '"'"'25,185p'"'"' tests/test_ctest_build_guard.py'
```

Observed exit: 0. read-only static inspection/hash/JSON/AST; no repository imports, tests, CTest, builds, probes, or benchmarks

### tests_source.json

```sh
nl -ba tests/test_ctest_build_guard.py
```

Observed exit: 0. read-only static inspection/hash/JSON/AST; no repository imports, tests, CTest, builds, probes, or benchmarks

## Evidence-authoring operations and qualification

apply_patch authored only verify_static.py, EARLY_COMMANDS.json, FINAL_AUDIT.md and seal_review.py inside this new directory; all tool calls succeeded. The audit received one evidence-only wording correction to avoid claiming an uncaptured individual rg exit status. record.py and BEFORE.json were created by the explicitly retained early commands. No source/test/doc/build/historical artifact was authored or patched.

static_call_boundaries.json: rg named a nonexistent CUB header and emitted an error; the outer read-only shell continued and returned0. The individual rg status was not instrumented. cub_files.json then records the actual directory inventory, exit0. The initial result inventory excluded one historical cache file; the complete retained supplemental inventory and baseline hash comparison account for it.

## Final seal

```sh
python3 -B results/raw/ctest_path_independent_review_20261011T000547578754Z/seal_review.py
```

Direct final command, outside the recorder to avoid adding an unsealed log afterward. Exit0 is confirmed by the terminal on completion; FINAL_INTEGRITY.json is written only after all preservation assertions pass. This program generates this command inventory, repeats read-only preservation checks, and hashes only the new review evidence.
