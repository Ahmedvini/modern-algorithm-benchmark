# Independent read-only review commands

Literal commands supplied from each reviewer's retained execution history; no rerun.
Every batch below exited0. In metadata batch5, each diff returned1 for expected
content changes, and the final sed returned0. No agent ran tests, CTest, builds,
cloud/GPU commands or workloads. Compound separators are retained verbatim as
historical command evidence.

## metadata_safety_review

```sh
pwd; sed -n '1,240p' results/raw/bounded_validation_20261011T020343203635Z/FINAL_AUDIT.md; sed -n '1,280p' scripts/ctest_build_guard.py; sed -n '1,260p' scripts/non_timing_tests.py
```

```sh
rg -n 'MemoryCheck|TLS|dart|Dart|CTEST_|selected_ctest|pre_discovery_gate' tests/test_ctest_build_guard.py tests/ctest_fixture.py scripts/validate_cpu_gpu_pilot.py scripts/ctest_build_guard.py docs/NON_TIMING_TEST_SELECTION_v2.json; cat results/raw/bounded_validation_20261011T020343203635Z/downloaded/evidence/DART_GUARD_BLOCKER.json; cat results/raw/bounded_validation_20261011T020343203635Z/downloaded/evidence/metadata_cpu-release/DartConfiguration.tcl; sed -n '1,220p' tests/test_ctest_build_guard.py; sed -n '1,170p' tests/ctest_fixture.py
```

```sh
rg -n 'MemoryCheckCommand|CTEST_MEMORYCHECK_COMMAND|TLSVerify|TLSVersion|ctest_memcheck|--test-action|--dashboard|-T <|memcheck' /usr/share/cmake-*/Modules/CTest.cmake /usr/share/cmake-*/Modules/DartConfiguration.tcl.in /usr/share/cmake-*/Help/manual/ctest.1.rst /usr/share/cmake-*/Help/command/ctest_memcheck.rst; nl -ba scripts/non_timing_tests.py | sed -n '110,190p'; nl -ba scripts/ctest_build_guard.py | sed -n '62,164p'; sed -n '1,90p' docs/NON_TIMING_TEST_SELECTION_v2.json; sed -n '320,380p' tests/test_ctest_build_guard.py
```

```sh
sed -n '1260,1298p' /usr/share/cmake-3.28/Help/manual/ctest.1.rst; sed -n '160,190p' /usr/share/cmake-3.28/Modules/CTest.cmake; sed -n '1,110p' scripts/validate_cpu_gpu_pilot.py; sed -n '1,125p' results/raw/bounded_validation_20261011T020343203635Z/remote_selection_review.py; sed -n '1,210p' tests/test_validation_selection.py; rg -n 'selected_ctest\(|select_tests\(|pre_discovery_gate\(|non_timing_tests' scripts tests/test_ctest_build_guard.py
```

```sh
diff -u results/raw/bounded_resume_20261011T024034091796Z/before/scripts/ctest_build_guard.py scripts/ctest_build_guard.py; diff -u results/raw/bounded_resume_20261011T024034091796Z/before/scripts/non_timing_tests.py scripts/non_timing_tests.py; cat tests/test_ctest_dart_compatibility.py docs/CTEST_COLAB_METADATA_v2.md; sed -n '1,120p' docs/NON_TIMING_TEST_SELECTION_v3.json
```

```sh
python3 -B - <<'PY'
from pathlib import Path
import json,hashlib
v2=json.loads(Path('docs/NON_TIMING_TEST_SELECTION_v2.json').read_text());v3=json.loads(Path('docs/NON_TIMING_TEST_SELECTION_v3.json').read_text())
print('Top-level changed keys:', [k for k in set(v2)|set(v3) if v2.get(k)!=v3.get(k)])
print('build_metadata changed keys:', [k for k in set(v2['build_metadata'])|set(v3['build_metadata']) if v2['build_metadata'].get(k)!=v3['build_metadata'].get(k)])
print('test table unchanged:',v2['tests']==v3['tests'])
print('registry memberships unchanged:',v2['cpu_build_tests']==v3['cpu_build_tests'],v2['cuda_additional_tests']==v3['cuda_additional_tests'])
old=v2['reviewed_source_sha256'];new=v3['reviewed_source_sha256'];print('source snapshot modified:',sorted(k for k in old if old[k]!=new.get(k)));print('source snapshot additions:',sorted(set(new)-set(old)));print('snapshot missing/mismatch:',[k for k,v in new.items() if not Path(k).is_file() or hashlib.sha256(Path(k).read_bytes()).hexdigest()!=v])
PY
```

## validation_resume_review

```sh
pwd; sed -n '1,240p' scripts/non_timing_tests.py; sed -n '1,200p' docs/CPU_GPU_VALIDATION_POLICY_v2.md; cat results/raw/bounded_validation_20261011T020343203635Z/FINAL_AUDIT.md
```

```sh
sed -n '1,320p' scripts/ctest_build_guard.py; cat tests/test_validation_selection.py; cat tests/test_validation_policy.py; cat tests/test_parallel_workers.cpp; cat tests/test_cuda_prepared_correctness.cpp
```

```sh
python3 -B - <<'PY'
import json
m=json.load(open('docs/NON_TIMING_TEST_SELECTION_v2.json'))
for k,v in m['tests'].items():
 if v['classification']=='cpu_correctness':print(k,v['command'], 'diagnostic_only',v.get('diagnostic_only'))
print('dart',json.dumps(m['build_metadata']['dart_defaults'],sort_keys=True))
PY
rg -n 'subprocess|Popen|run\(|check_output|ctest|cmake|benchmark|sample\(|warmup|Clock|timeit|perf_counter' tests/test_cli.py tests/test_metrics_cli.py tests/test_cpu_gpu_comparison.py tests/test_cuda_benchmark.py tests/test_cuda_preflight.py tests/test_cuda_sort_handoff.py tests/test_environment.py tests/test_parallel_workers.cpp scripts/cpu_gpu_validation_policy.py scripts/validate_cpu_gpu_pilot.py; sed -n '1,220p' tests/test_cuda_sort_handoff.py; sed -n '1,180p' tests/test_cuda_preflight.py
```

```sh
sed -n '1,220p' tests/test_cpu_gpu_comparison.py; sed -n '430,510p' tests/test_cpu_gpu_comparison.py; sed -n '1,150p' tests/test_cuda_benchmark.py; sed -n '1,180p' tests/test_environment.py; cat CMakeLists.txt; cat cmake/cuda.cmake; cat scripts/cpu_gpu_validation_policy.py
```

```sh
rg -n 'Clock|chrono|clock\(|time\(|sample\(|warmup|run_trial|run_benchmark' tests/test_baselines.cpp tests/test_comparisons.cpp tests/test_datasets.cpp tests/test_memory.cpp tests/test_mergesort.cpp tests/test_pdqsort.cpp tests/test_quicksort.cpp tests/test_radixsort.cpp tests/test_searching.cpp tests/test_structures.cpp tests/test_timsort.cpp tests/test_cli.py tests/test_metrics_cli.py tests/test_environment.py; cat results/raw/bounded_validation_20261011T020343203635Z/remote_validate.py; cat results/raw/bounded_validation_20261011T020343203635Z/downloaded/evidence/DART_GUARD_BLOCKER.json; sed -n '130,185p' tests/test_cuda_benchmark.py; sed -n '1,150p' scripts/cpu_gpu_protocol.py; sed -n '1,140p' cmake/benchmark_metadata.cmake
```

```sh
nl -ba scripts/ctest_build_guard.py | sed -n '60,170p'; nl -ba scripts/non_timing_tests.py | sed -n '65,180p'; nl -ba tests/test_cuda_preflight.py | sed -n '124,150p'; nl -ba tests/test_cuda_benchmark.py | sed -n '142,172p'; nl -ba tests/test_cuda_sort_handoff.py | sed -n '73,86p'; nl -ba tests/test_parallel_workers.cpp | sed -n '36,73p'; nl -ba scripts/validate_cpu_gpu_pilot.py | sed -n '75,115p'
```

```sh
cat results/raw/bounded_resume_20261011T024034091796Z/remote_validate.py; cat results/raw/bounded_resume_20261011T024034091796Z/remote_selection_review.py; cat scripts/non_timing_tests.py; sed -n '1,190p' scripts/ctest_build_guard.py
```

```sh
python3 -B - <<'PY'
from pathlib import Path
import difflib
old=Path('results/raw/bounded_validation_20261011T020343203635Z')
new=Path('results/raw/bounded_resume_20261011T024034091796Z')
for name in ['remote_validate.py','remote_selection_review.py']:
 print(name)
 print(''.join(difflib.unified_diff((old/name).read_text().splitlines(keepends=True),(new/name).read_text().splitlines(keepends=True),fromfile='retained/'+name,tofile='resume/'+name)))
PY
```

```sh
cat results/raw/bounded_resume_20261011T024034091796Z/FAILED_CPU_RELEASE.json; sed -n '290,510p' tests/test_cpu_gpu_comparison.py; sed -n '1,180p' scripts/run_cpu_gpu_study.py; sed -n '120,280p' scripts/run_cpu_gpu_pilot.py; rg -n 'CTEST_|environment override|verify_source_extension' tests/test_ctest_build_guard.py tests/test_cpu_gpu_comparison.py
```

```sh
sed -n '316,418p' tests/test_cpu_gpu_comparison.py; sed -n '239,265p' tests/test_ctest_build_guard.py; sed -n '1,105p' scripts/validate_cpu_gpu_pilot.py; sed -n '1,100p' scripts/cpu_gpu_provenance.py
```

```sh
python3 -B - <<'PY'
from pathlib import Path
import difflib
p='tests/test_cpu_gpu_comparison.py'
b=Path('results/raw/bounded_resume_20261011T024034091796Z/before')/p
print(''.join(difflib.unified_diff(b.read_text().splitlines(keepends=True),Path(p).read_text().splitlines(keepends=True),fromfile='retained-before/'+p,tofile=p)))
PY
sed -n '360,535p' tests/test_cpu_gpu_comparison.py; cat docs/NON_TIMING_TEST_SELECTION_v3.json | tail -20
```

```sh
python3 -B - <<'PY'
from pathlib import Path
import hashlib,json
m=json.loads(Path('docs/NON_TIMING_TEST_SELECTION_v3.json').read_text())
paths=[Path('CMakeLists.txt')]
for d in ['include','src','scripts','tests','cmake','third_party']:
 paths.extend(p for p in Path(d).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
actual={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))}
print('source snapshot exact',actual==m['reviewed_source_sha256'],'files',len(actual))
print('test fixture sha256',actual['tests/test_cpu_gpu_comparison.py'])
a=json.loads(Path('docs/NON_TIMING_TEST_SELECTION_v2.json').read_text())
print('test classification table unchanged',a['tests']==m['tests'])
print('expected CPU registrations unchanged',a['cpu_build_tests']==m['cpu_build_tests'])
PY
```
