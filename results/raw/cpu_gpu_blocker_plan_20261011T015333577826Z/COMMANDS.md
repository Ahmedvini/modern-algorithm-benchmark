# Commands and statuses — local design inspection only

No Colab invocation, GPU/resource probe, test, CTest discovery, build, sanitizer, smoke/pilot, warm-up, measured trial or study executed. Proposed future steps were not run.

## Baseline creation

Exit:0; local hashes and exclusive new evidence writes.

```bash
python3 -B - <<'PY'
import datetime,hashlib,json
from pathlib import Path
r=Path.cwd();old=r/'results/raw/cpu_gpu_recovery_design_20261011T014656388000Z';b=json.loads((old/'BEFORE.json').read_text())
e=r/'results/raw'/('cpu_gpu_blocker_plan_'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'));e.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
d={'historical_results_sha256':{str(p.relative_to(r)):sha(p) for p in sorted((r/'results').rglob('*')) if p.is_file() and not p.is_relative_to(e)},'project_sha256':{p:sha(r/p) for p in b['project_sha256']},'build_metadata_sha256':{p:sha(r/p) for p in b['build_metadata_sha256']}}
assert d['project_sha256']==b['project_sha256'];assert d['build_metadata_sha256']==b['build_metadata_sha256']
with (e/'BEFORE.json').open('x') as f:json.dump(d,f,indent=2,sort_keys=True);f.write('\n')
with (e/'record.py').open('xb') as f:f.write((old/'record.py').read_bytes())
print(e.relative_to(r));print('historical_result_files',len(d['historical_results_sha256']))
PY
```

## Baseline creation

Exit:0; local hashes and exclusive new evidence writes.

```bash
pwd
```

## Baseline creation

Exit:0; local hashes and exclusive new evidence writes.

```bash
sed -n '1,260p' results/raw/cpu_gpu_blocker_plan_20261011T015333577826Z/finalize.py
```

## control_record.json

Exit:0; classification: Evidence-only command provenance assembly; no project execution

```bash
python3 -B -c 'import json;from pathlib import Path;p=Path("results/raw/cpu_gpu_blocker_plan_20261011T015333577826Z/CONTROL_COMMANDS.json");f=p.open('"'"'x'"'"');json.dump(json.loads("[{\"command\":\"python3 -B - <<'"'"'PY'"'"'\\nimport datetime,hashlib,json\\nfrom pathlib import Path\\nr=Path.cwd();old=r/'"'"'results/raw/cpu_gpu_recovery_design_20261011T014656388000Z'"'"';b=json.loads((old/'"'"'BEFORE.json'"'"').read_text())\\ne=r/'"'"'results/raw'"'"'/('"'"'cpu_gpu_blocker_plan_'"'"'+datetime.datetime.now(datetime.timezone.utc).strftime('"'"'%Y%m%dT%H%M%S%fZ'"'"'));e.mkdir()\\nsha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()\\nd={'"'"'historical_results_sha256'"'"':{str(p.relative_to(r)):sha(p) for p in sorted((r/'"'"'results'"'"').rglob('"'"'*'"'"')) if p.is_file() and not p.is_relative_to(e)},'"'"'project_sha256'"'"':{p:sha(r/p) for p in b['"'"'project_sha256'"'"']},'"'"'build_metadata_sha256'"'"':{p:sha(r/p) for p in b['"'"'build_metadata_sha256'"'"']}}\\nassert d['"'"'project_sha256'"'"']==b['"'"'project_sha256'"'"'];assert d['"'"'build_metadata_sha256'"'"']==b['"'"'build_metadata_sha256'"'"']\\nwith (e/'"'"'BEFORE.json'"'"').open('"'"'x'"'"') as f:json.dump(d,f,indent=2,sort_keys=True);f.write('"'"'\\\\n'"'"')\\nwith (e/'"'"'record.py'"'"').open('"'"'xb'"'"') as f:f.write((old/'"'"'record.py'"'"').read_bytes())\\nprint(e.relative_to(r));print('"'"'historical_result_files'"'"',len(d['"'"'historical_results_sha256'"'"']))\\nPY\",\"exit_code\":0,\"scope\":\"Local baseline hashing and exclusive evidence creation\"},{\"command\":\"pwd\",\"exit_code\":0,\"scope\":\"Read-only repository identity inspection\"},{\"command\":\"sed -n '"'"'1,260p'"'"' results/raw/cpu_gpu_blocker_plan_20261011T015333577826Z/finalize.py\",\"exit_code\":0,\"scope\":\"Read-only inspection of own evidence assembler\"}]"),f,indent=2);f.write('"'"'\n'"'"');f.close();print('"'"'Recorded local command provenance'"'"')'
```

cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`.

## exact_constraints.json

Exit:0; classification: Read-only frozen identities, selector/provenance paths and retained CLI help

```bash
python3 -B -c 'import json;from pathlib import Path;m=json.loads(Path("docs/studies/cpu_gpu_comparison_v1.matrix.json").read_text());print("PROTECTED ANCHORS",sorted(m["source_at_freeze_sha256"]));print("FROZEN SIZES",[r["size"] for r in m["resources"]["table"]]);print("OMP",m["openmp_policy"]);p=json.loads(Path("docs/NON_TIMING_TEST_SELECTION_v1.json").read_text());print("CORRECTNESS SELECTION",sorted(n for n,t in p["tests"].items() if t["classification"]=="cpu_correctness"));d=Path("results/raw/cpu_gpu_recovery_design_20261011T014656388000Z");print("RETAINED CLI VERSION",json.loads((d/"cli_version.json").read_text())["stdout"]);print("RETAINED CLI SESSION HELP",json.loads((d/"cli_session_help.json").read_text())["stdout"]);print("SELECTION AND SOURCE ENFORCEMENT");fs={"scripts/non_timing_tests.py":[(24,45),(133,175)],"scripts/cpu_gpu_protocol.py":[(70,90)],"scripts/cpu_gpu_provenance.py":[(1,150)]};[(print(f),print("\n".join(f"{i}: {s}" for i,s in enumerate(Path(f).read_text().splitlines(),1) if any(a<=i<=b for a,b in spans)))) for f,spans in fs.items()]'
```

cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`.

## gpu_paths.json

Exit:0; classification: Read-only GPU implementation, oracle and registration inspection

```bash
bash -c 'nl -ba include/benchmark/cuda_timing.hpp; nl -ba src/cuda/cub_timing.cu; nl -ba tests/test_cuda_sorting.cpp; nl -ba cmake/cuda.cmake | sed -n '"'"'25,100p'"'"'; nl -ba src/cuda/cub_sort.cu'
```

cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`.

## required_evidence.json

Exit:0; classification: Read-only latest audit, command log and integrity manifest

```bash
cat results/raw/cpu_gpu_recovery_design_20261011T014656388000Z/FINAL_AUDIT.md results/raw/cpu_gpu_recovery_design_20261011T014656388000Z/COMMANDS.md results/raw/cpu_gpu_recovery_design_20261011T014656388000Z/FINAL_INTEGRITY.json
```

cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`.

## worker_policy_paths.json

Exit:0; classification: Read-only actual-worker API and prerequisite policy inspection

```bash
bash -c 'nl -ba include/algorithms/parallel_mergesort.hpp; nl -ba src/algorithms/parallel_mergesort.cpp; nl -ba include/algorithms/detail/parallel_mergesort_impl.hpp | sed -n '"'"'65,92p'"'"'; nl -ba scripts/analyze_cpu_gpu.py | sed -n '"'"'60,110p'"'"'; nl -ba scripts/run_cpu_gpu_pilot.py | sed -n '"'"'100,140p'"'"'; nl -ba scripts/validate_cpu_gpu_pilot.py | sed -n '"'"'75,114p'"'"''
```

cwd: `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`.

## Evidence-only tool action and final assembly

apply_patch added only this new directory's finalize.py; tool returned success. No project implementation or proposed test was added.

```bash
python3 -B results/raw/cpu_gpu_blocker_plan_20261011T015333577826Z/finalize.py
```

Exit:0 upon successful completion; local reads/hashes and exclusive evidence writes only, no subprocesses or project imports.

Recorder wrapper: `python3 -B results/raw/cpu_gpu_blocker_plan_20261011T015333577826Z/record.py NAME SCOPE TIMEOUT CHILD_ARGV...`.
Shell read batches have recorded overall statuses. Terminal polling only retrieved baseline-hash output. Per-command JSON preserves output and cwd; copied recorder redacts URL-shaped text.
