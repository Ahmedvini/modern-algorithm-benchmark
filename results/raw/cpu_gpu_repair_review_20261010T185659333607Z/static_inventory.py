"""Read source/build metadata; never configure, execute CTest or invoke tests."""
import ast
import hashlib
import json
from pathlib import Path
import re

ROOT=Path.cwd();BASE=Path(__file__).resolve().parent
manifest=json.loads((ROOT/'docs/NON_TIMING_TEST_SELECTION_v1.json').read_text())
selected=sorted(n for n,v in manifest['tests'].items() if v['classification']=='cpu_correctness')
cpp={
 'baselines':'tests/test_baselines.cpp','datasets':'tests/test_datasets.cpp',
 'quicksort':'tests/test_quicksort.cpp','pdqsort':'tests/test_pdqsort.cpp','timsort':'tests/test_timsort.cpp',
 'mergesort':'tests/test_mergesort.cpp','radixsort':'tests/test_radixsort.cpp','comparisons':'tests/test_comparisons.cpp',
 'memory':'tests/test_memory.cpp','memory_unsupported':'tests/test_memory.cpp',
 'searching':'tests/test_searching.cpp','structures':'tests/test_structures.cpp'}
inspected={}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
patterns=re.compile(r'(chrono|steady_clock|system\(|popen\(|exec[vle]*\(|run_.*timing|elapsed_ns|subprocess|Popen|mock\.patch|patch\(|skipUnless|skipTest|runner=|invoke\(|ctest|CTestCustom|FIXTURES_|DEPENDS)')
paths=['AGENTS.md','README.md','docs/ROADMAP.md','docs/EXPERIMENT_PROTOCOL.md',
 'docs/CPU_GPU_COMPARISON_PROTOCOL_v1.md','docs/CPU_GPU_DRIVER_REVIEW_v1.json',
 'docs/CPU_GPU_SAFETY_REPAIR_v1.md','docs/CPU_GPU_FULL_MATRIX_TOOLING_v1.md',
 'docs/studies/cpu_gpu_comparison_v1.matrix.json','docs/studies/cpu_gpu_comparison_v1.freeze.json',
 'docs/studies/cpu_gpu_comparison_v1.resources.csv','docs/NON_TIMING_TEST_SELECTION_v1.json',
 'CMakeLists.txt','cmake/cuda.cmake','scripts/cpu_gpu_provenance.py','scripts/cpu_gpu_protocol.py',
 'scripts/non_timing_tests.py','scripts/validate_cpu_gpu_pilot.py','scripts/run_cpu_gpu_pilot.py','scripts/run_cpu_gpu_study.py',
 'scripts/analyze_cpu_gpu.py','scripts/analyze_cuda_results.py','scripts/analyze_results.py',
 'scripts/capture_environment.py','scripts/cuda_preflight.py','scripts/validate_cuda_sort.py',
 'scripts/run_cuda_matrix.py','scripts/validate_cuda_timing.py','tests/test_cpu_gpu_safety.py',
 'tests/test_cpu_gpu_comparison.py','tests/fixtures/cpu_gpu_provenance_reproducer.py',
 'tests/test_environment.py','tests/test_cli.py','tests/test_metrics_cli.py','tests/test_cuda_preflight.py',
 'tests/test_cuda_sort_handoff.py','tests/test_cuda_benchmark.py','tests/test_parallel_mergesort.cpp',
 'tests/test_integer_sorts.hpp','tests/test_support.hpp','src/main.cpp','src/benchmark/metrics_main.cpp',
 'src/benchmark/comparison_input_main.cpp','src/benchmark/comparison.cpp']+list(cpp.values())
for name in sorted(set(paths)):
    path=ROOT/name;text=path.read_text()
    inspected[name]=dict(sha256=sha(path),lines=len(text.splitlines()),
        relevant_lines=[dict(line=i,text=line) for i,line in enumerate(text.splitlines(),1) if patterns.search(line)])
cpp_risks={n:[x for x in inspected[p]['relevant_lines'] if re.search(r'(chrono|steady_clock|system\(|popen\(|run_.*timing|elapsed_ns)',x['text'])]
           for n,p in cpp.items()}
assert all(not v for v in cpp_risks.values()),cpp_risks
# Existing metadata is inspected as text only: do not ask CTest to interpret it.
builds=[ROOT/'build/cpu_gpu_full_tooling_20261010T121208603276Z/release',
        ROOT/'build/cpu_gpu_full_tooling_20261010T121208603276Z/sanitize']
build_records={}
for build in builds:
    files={}
    if build.is_dir():
        for name in ['CTestCustom.cmake','CTestCustom.ctest','CTestTestfile.cmake','DartConfiguration.tcl']:
            for path in sorted(build.rglob(name)):
                text=path.read_text()
                files[str(path.relative_to(ROOT))]=dict(sha256=sha(path),
                    hook_lines=[dict(line=i,text=line) for i,line in enumerate(text.splitlines(),1)
                                if re.search(r'CTEST_CUSTOM_(PRE|POST)_TEST|execute_process\s*\(|include\s*\(',line,re.I)])
    build_records[str(build.relative_to(ROOT))]=dict(exists=build.is_dir(),metadata=files)

analyzer=ast.parse((ROOT/'scripts/analyze_cpu_gpu.py').read_text())
function_names={n.name:n for n in analyzer.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
provenance_calls=[]
for name in ['analyze','validate_study_metadata','main']:
    node=function_names[name]
    calls=[]
    for call in ast.walk(node):
        if isinstance(call,ast.Call) and isinstance(call.func,ast.Name):
            if call.func.id in ['analyze','validate_study_metadata','validate_retained_source','load_protocol']:
                calls.append(dict(callee=call.func.id,line=call.lineno))
    provenance_calls.append(dict(function=name,line=node.lineno,calls=calls))
report=dict(selected_cpu_tests=selected,selected_cpp_groups=12,cpp_timing_symbol_scan=cpp_risks,
            inspected_files=inspected,existing_build_metadata=build_records,analyzer_paths=provenance_calls,
            no_test_or_ctest_execution=True,
            limitations='Symbol scan supports manual call-path review; it is not a static proof of arbitrary program behavior.')
with (BASE/'STATIC_INVENTORY.json').open('x') as stream:json.dump(report,stream,indent=2,sort_keys=True);stream.write('\n')
print(json.dumps(dict(selected_cpu_tests=selected,inspected_files=len(inspected),selected_cpp_groups=12,
    cpp_timing_symbols_found=cpp_risks,existing_build_metadata=build_records,analyzer_paths=provenance_calls),indent=2,sort_keys=True))
