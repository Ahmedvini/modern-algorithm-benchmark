# Recovery/design inspection commands

No validation workload, GPU/resource probe, CTest discovery, build, benchmark or replacement session was executed. Proposed commands in FINAL_AUDIT.md were not run.

## Baseline creation

Exit:0; local hashing and exclusive new evidence writes.

```bash
python3 -B - <<'PY'
import datetime,hashlib,json
from pathlib import Path
r=Path.cwd();e=r/'results/raw'/('cpu_gpu_recovery_design_'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'));e.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=r/'results/raw/cpu_gpu_prelaunch_validation_20261011T014309468088Z';b=json.loads((old/'BEFORE.json').read_text())
d={'historical_results_sha256':{str(p.relative_to(r)):sha(p) for p in sorted((r/'results').rglob('*')) if p.is_file() and not p.is_relative_to(e)},'project_sha256':{p:sha(r/p) for p in b['project_sha256']},'build_metadata_sha256':{p:sha(r/p) for p in b['build_metadata_sha256']}}
assert d['project_sha256']==b['project_sha256'];assert d['build_metadata_sha256']==b['build_metadata_sha256']
with (e/'BEFORE.json').open('x') as f:json.dump(d,f,indent=2,sort_keys=True);f.write('\n')
with (e/'record.py').open('xb') as f:f.write((old/'record.py').read_bytes())
print(e.relative_to(r));print('historical files',len(d['historical_results_sha256']))
PY
```

## actual_configuration.json

Exit:0; classification: Read-only existing sanitizer definitions, protocols and reviewed test targets

```bash
python3 -B -c 'import json;from pathlib import Path;fs=["CMakeLists.txt","docs/CPU_GPU_COMPARISON_PROTOCOL_v1.md","scripts/cpu_gpu_protocol.py","scripts/ctest_build_guard.py"];terms=["SANITIZER","sanitize","fsanitize","fno-omit","fno-pie","no-pie","source_at_freeze","updated","reviewed","freeze","CTestCustom","include(","subdirs","SYMLINK","symlink","fixture"];[(print(f),print("\n".join(f"{i}: {s}" for i,s in enumerate(Path(f).read_text().splitlines(),1) if any(t in s for t in terms)))) for f in fs];m=json.loads(Path("docs/NON_TIMING_TEST_SELECTION_v1.json").read_text());print("CPU CORRECTNESS");[(print(n,e["command"],e["reason"])) for n,e in sorted(m["tests"].items()) if e["classification"]=="cpu_correctness"];print("EXCLUDED");[(print(n,e["reason"])) for n,e in sorted(m["tests"].items()) if e["classification"]=="timing"];print("FROZEN RESOURCES");m=json.loads(Path("docs/studies/cpu_gpu_comparison_v1.matrix.json").read_text());print(json.dumps(m["resources"],indent=2));print("OMP",m["openmp_policy"])'
```

cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`.

## cli_help.json

Exit:0; classification: Read-only installed CLI help; no session creation

```bash
colab --help
```

cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`.

## cli_readme.json

Exit:0; classification: Read-only bundled public CLI usage documentation

```bash
colab readme
```

cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`.

## cli_session_help.json

Exit:0; classification: Read-only documented session-management help

```bash
bash -c 'colab sessions --help; colab status --help; colab url --help; colab console --help; colab ssh --help'
```

cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`.

## cli_version.json

Exit:0; classification: Read-only installed CLI version

```bash
colab version
```

cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`.

## control_record.json

Exit:0; classification: Evidence-only command provenance assembly

```bash
python3 -B -c 'import json;from pathlib import Path;p=Path("results/raw/cpu_gpu_recovery_design_20261011T014656388000Z/CONTROL_COMMANDS.json");f=p.open('"'"'x'"'"');json.dump(json.loads("[{\"command\":\"python3 -B - <<'"'"'PY'"'"'\\nimport datetime,hashlib,json\\nfrom pathlib import Path\\nr=Path.cwd();e=r/'"'"'results/raw'"'"'/('"'"'cpu_gpu_recovery_design_'"'"'+datetime.datetime.now(datetime.timezone.utc).strftime('"'"'%Y%m%dT%H%M%S%fZ'"'"'));e.mkdir()\\nsha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()\\nold=r/'"'"'results/raw/cpu_gpu_prelaunch_validation_20261011T014309468088Z'"'"';b=json.loads((old/'"'"'BEFORE.json'"'"').read_text())\\nd={'"'"'historical_results_sha256'"'"':{str(p.relative_to(r)):sha(p) for p in sorted((r/'"'"'results'"'"').rglob('"'"'*'"'"')) if p.is_file() and not p.is_relative_to(e)},'"'"'project_sha256'"'"':{p:sha(r/p) for p in b['"'"'project_sha256'"'"']},'"'"'build_metadata_sha256'"'"':{p:sha(r/p) for p in b['"'"'build_metadata_sha256'"'"']}}\\nassert d['"'"'project_sha256'"'"']==b['"'"'project_sha256'"'"'];assert d['"'"'build_metadata_sha256'"'"']==b['"'"'build_metadata_sha256'"'"']\\nwith (e/'"'"'BEFORE.json'"'"').open('"'"'x'"'"') as f:json.dump(d,f,indent=2,sort_keys=True);f.write('"'"'\\\\n'"'"')\\nwith (e/'"'"'record.py'"'"').open('"'"'xb'"'"') as f:f.write((old/'"'"'record.py'"'"').read_bytes())\\nprint(e.relative_to(r));print('"'"'historical files'"'"',len(d['"'"'historical_results_sha256'"'"']))\\nPY\"}]"),f,indent=2);f.write('"'"'\n'"'"');f.close();print('"'"'Recorded baseline command'"'"')'
```

cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`.

## corrected_interfaces.json

Exit:1; classification: Read-only interfaces and selector; independent of CLI Python environment

```bash
bash -c 'nl -ba include/benchmark/cuda_timing.hpp; nl -ba src/cuda/cub_timing.cu | sed -n "1,78p"; nl -ba src/cuda/comparison_resources.cu; nl -ba include/benchmark/cuda_comparison.hpp; nl -ba include/algorithms/parallel_mergesort.hpp; nl -ba scripts/non_timing_tests.py | sed -n "1,82p"; nl -ba scripts/validate_cpu_gpu_pilot.py | sed -n "35,72p"; nl -ba cmake/sanitizers.cmake'
```

cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`.

## current_sessions.json

Exit:0; classification: Documented read-only active-session listing; no provisioning

```bash
colab sessions
```

cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`.

## current_status.json

Exit:0; classification: Documented read-only approved-session lookup; no provisioning

```bash
colab status --session cpu-gpu-validation
```

cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`.

## final_design_sources.json

Exit:0; classification: Read-only exact CPU/GPU metadata gates, workspace CLI and frozen identities

```bash
bash -c 'nl -ba src/benchmark/cpu_gpu_main.cpp | sed -n "80,92p"; nl -ba CMakeLists.txt | sed -n "1,42p"; nl -ba scripts/analyze_cpu_gpu.py | sed -n "85,105p"; nl -ba scripts/cpu_gpu_protocol.py | sed -n "68,94p"; cat docs/studies/cpu_gpu_comparison_v1.freeze.json; cat docs/studies/cpu_gpu_comparison_v1.resources.csv'
```

cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`.

## latest_evidence.json

Exit:0; classification: Read-only latest audit, command log and integrity manifest

```bash
cat results/raw/cpu_gpu_prelaunch_validation_20261011T014309468088Z/FINAL_AUDIT.md results/raw/cpu_gpu_prelaunch_validation_20261011T014309468088Z/COMMANDS.md results/raw/cpu_gpu_prelaunch_validation_20261011T014309468088Z/FINAL_INTEGRITY.json
```

cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`.

## precise_interfaces.json

Exit:1; classification: Read-only local interfaces, metadata and installed CLI locations; no credentials

```bash
python3 -B -c 'import json,importlib.metadata;from pathlib import Path;e=Path("results/raw/cpu_gpu_recovery_design_20261011T014656388000Z");print("CLI VERSION",json.loads((e/"cli_version.json").read_text())["stdout"]);d=importlib.metadata.distribution("google-colab-cli");print("DISTRIBUTION",d.version);print("PUBLIC SOURCE LOCATIONS");[print(d.locate_file(p)) for p in d.files if str(p).endswith(".py") and any(s in str(p) for s in ["session","main","cli","commands"])];print("INTERFACES");fs={"include/benchmark/cuda_timing.hpp":None,"src/cuda/cub_timing.cu":(1,78),"src/cuda/comparison_resources.cu":None,"include/benchmark/cuda_comparison.hpp":None,"include/algorithms/parallel_mergesort.hpp":None,"scripts/non_timing_tests.py":(1,82),"scripts/validate_cpu_gpu_pilot.py":(35,72)};[(print(f),print("\n".join(f"{i}: {s}" for i,s in enumerate(Path(f).read_text().splitlines(),1) if span is None or span[0]<=i<=span[1]))) for f,span in fs.items()]'
```

cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`.

## safe_design_details.json

Exit:0; classification: Read-only numbered build/diagnostic and selector metadata

```bash
bash -c 'nl -ba scripts/validate_cpu_gpu_pilot.py | sed -n "1,100p"; nl -ba scripts/non_timing_tests.py | sed -n "1,100p"; nl -ba src/cuda/comparison_resources.cu | sed -n "1,170p"; nl -ba include/algorithms/detail/parallel_mergesort_impl.hpp | sed -n "1,180p"; nl -ba src/algorithms/parallel_mergesort.cpp; nl -ba src/benchmark/cuda_main.cpp | sed -n "1,245p"'
```

cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`.

## source_design.json

Exit:0; classification: Read-only selector, build, CUDA and OpenMP source inspection

```bash
bash -c 'cat scripts/non_timing_tests.py docs/NON_TIMING_TEST_SELECTION_v1.json scripts/ctest_build_guard.py scripts/validate_cpu_gpu_pilot.py CMakeLists.txt cmake/cuda.cmake src/cuda/cub_timing.cu src/cuda/comparison_resources.cu include/algorithms/detail/parallel_mergesort_impl.hpp tests/test_cuda_benchmark.py tests/test_parallel_mergesort.cpp'
```

cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`.

## Evidence-only tool action and final seal

apply_patch added only this new directory's finalize.py and returned success; no project implementation changed.

```bash
python3 -B results/raw/cpu_gpu_recovery_design_20261011T014656388000Z/finalize.py
```

Exit:0 upon successful completion. Standard-library reads/hashes and exclusive evidence writes only; no subprocesses, project imports or workloads. Its source is retained.

Each recorded command used the evidence recorder wrapper `python3 -B results/raw/cpu_gpu_recovery_design_20261011T014656388000Z/record.py NAME SCOPE TIMEOUT CHILD_ARGV...`.
Terminal polls retrieved output of baseline hashing only. The recorder redacts URL-shaped public documentation text; original local source/help remains authoritative.
