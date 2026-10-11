# Terminal inspections and evidence writes outside record.py

These commands returned overall shell exit 0, observed in the terminal. Their
stdout was not retained as subprocess JSON (some terminal output was truncated).
Individual statements in multiline shells were not separately instrumented.
They read files, list paths, parse JSON or hash/copy bytes; none invokes CTest,
tests, prerequisites, resource checks, timing code or GPU work. The exclusively
created snapshot records exact starting bytes/counts. No reconstructed stdout
is represented as an observed raw log.

```sh
pwd
cat AGENTS.md
cat results/raw/cpu_gpu_repair_review_20261010T185659333607Z/FINAL_AUDIT.md
cat results/raw/cpu_gpu_repair_review_20261010T185659333607Z/COMMANDS.md
```

```sh
pwd
sed -n '1,220p' results/raw/cpu_gpu_repair_review_20261010T185659333607Z/FINAL_AUDIT.md
sed -n '1,210p' scripts/non_timing_tests.py
```

```sh
cat AGENTS.md
sed -n '1,160p' docs/ROADMAP.md
sed -n '1,100p' README.md
sed -n '1,90p' docs/EXPERIMENT_PROTOCOL.md
```

```sh
cat results/raw/cpu_gpu_repair_review_20261010T185659333607Z/COMMANDS.md
sed -n '1,180p' build/cpu_gpu_full_tooling_20261010T121208603276Z/release/CTestTestfile.cmake
rg -n 'select_tests|selected_ctest|show-only|ctest|add_test|set_tests_properties' scripts/validate_cpu_gpu_pilot.py tests/test_cpu_gpu_safety.py tests/test_cpu_gpu_comparison.py CMakeLists.txt
```

```sh
python3 -B - <<'PY'
import json
from pathlib import Path
for p in ['results/raw/cpu_gpu_repair_review_20261010T185659333607Z/FINAL_INTEGRITY.json','docs/NON_TIMING_TEST_SELECTION_v1.json']:
 d=json.loads(Path(p).read_text()); print(p); print({k:(list(v)[:6] if isinstance(v,dict) else v) for k,v in d.items() if k!='tests'})
 if 'tests' in d: print(json.dumps(d['tests'],indent=2))
PY
```

Bootstrap, evidence writes only:

```sh
python3 -B - <<'PY'
from pathlib import Path
import json,hashlib,datetime
r=Path.cwd(); p=r/'results/raw'/('ctest_hook_repair_'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')); p.mkdir()
def hashes(paths): return {str(x.relative_to(r)):hashlib.sha256(x.read_bytes()).hexdigest() for x in sorted(paths) if x.is_file()}
results=hashes((r/'results').rglob('*'))
project=hashes([r/'AGENTS.md',r/'README.md',r/'CMakeLists.txt']+[p for n in ['scripts','tests','docs','include','src','cmake','third_party'] for p in (r/n).rglob('*') if '__pycache__' not in p.parts])
builds=hashes([p for p in (r/'build').rglob('*') if p.name in ['CTestTestfile.cmake','CTestCustom.cmake','CTestCustom.ctest','DartConfiguration.tcl']])
(p/'BEFORE.json').write_text(json.dumps(dict(results_count=len(results),results_sha256=results,project_sha256=project,build_metadata_sha256=builds),indent=2,sort_keys=True)+'\n')
(p/'PATH.txt').write_text(str(p)+'\n')
print(p);print('prior result files:',len(results),'project files:',len(project),'static build metadata:',len(builds))
for path in ['scripts/non_timing_tests.py','tests/test_cpu_gpu_safety.py','tests/test_cpu_gpu_comparison.py','docs/NON_TIMING_TEST_SELECTION_v1.json']:
 out=p/'before'/path;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes((r/path).read_bytes())
PY
```

```sh
rg --files -g AGENTS.md -g '*ctest*' scripts tests docs
cat build/cpu_gpu_full_tooling_20261010T121208603276Z/release/CTestTestfile.cmake
cat cmake/cuda.cmake
sed -n '1,250p' tests/test_cpu_gpu_safety.py
sed -n '425,500p' tests/test_cpu_gpu_comparison.py
```

```sh
sed -n '1,180p' build/cpu_gpu_full_tooling_20261010T121208603276Z/release/DartConfiguration.tcl
rg -n 'CTestTestfile|DartConfiguration|CTestCustom|CTestConfig|include\(|subdirs\(' results/raw/cpu_gpu_repair_review_20261010T185659333607Z/STATIC_INVENTORY.json
sed -n '1,125p' scripts/validate_cpu_gpu_pilot.py
sed -n '1,130p' scripts/cpu_gpu_protocol.py
cat results/raw/cpu_gpu_repair_review_20261010T185659333607Z/COMMANDS.md
```

Additional unwrapped read, exit 0:

```sh
python3 -B - <<'PY'
import sys
from pathlib import Path
print(sys.executable,Path(sys.executable).resolve())
PY
rg -n 'include\(.*cuda' CMakeLists.txt
sed -n '1,120p' results/raw/cpu_gpu_repair_review_20261010T185659333607Z/hook_metadata_review.py
```

```sh
python3 -B - <<'PY'
import json
from pathlib import Path
p=Path('results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/CTEST_DISCOVERY.json');d=json.loads(p.read_text());print(json.dumps(d['tests'][:2],indent=2))
PY
rg -n 'non.timing|selection|prerequisites.only' README.md docs/ROADMAP.md docs/CPU_GPU_SAFETY_REPAIR_v1.md
```

Failed-attempt source preservation, evidence-only, exit 0:

```sh
python3 -B - <<'PY'
from pathlib import Path
base=Path('results/raw/ctest_hook_repair_20261010T223851377458Z/attempt1')
for name in ['scripts/ctest_build_guard.py','tests/test_ctest_build_guard.py','docs/NON_TIMING_TEST_SELECTION_v1.json']:
 out=base/name;out.parent.mkdir(parents=True,exist_ok=True)
 with out.open('xb') as f:f.write(Path(name).read_bytes())
PY
```

Policy pre-correction preservation, evidence-only, exit 0:

```sh
python3 -B - <<'PY'
from pathlib import Path
base=Path('results/raw/ctest_hook_repair_20261010T223851377458Z');out=base/'metadata_policy_before_cuda_stack_review';out.mkdir()
for name,source in [('create_reviewed_policy.py',base/'create_reviewed_policy.py'),('NON_TIMING_TEST_SELECTION_v1.json',Path('docs/NON_TIMING_TEST_SELECTION_v1.json'))]:
 with (out/name).open('xb') as f:f.write(source.read_bytes())
PY
```

Edits used `apply_patch`; their final before/after identities and source diff are
retained in FILE_REVIEW.json and SOURCE_DIFF.patch. One documentation patch was
rejected for a ROADMAP context mismatch, with no files changed; the recorded
documentation_patch_state inspection confirmed that, and the corrected patch
succeeded. apply_patch is a tool operation, not a shell command with an exit code.
No commit, push, Git initialization or historical cleanup command was issued.
