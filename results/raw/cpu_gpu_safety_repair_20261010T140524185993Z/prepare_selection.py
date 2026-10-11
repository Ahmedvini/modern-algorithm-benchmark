"""Record the reviewed classification and copy discovery metadata, never execute tests."""
import hashlib
import json
from pathlib import Path
import re
import shlex
import sys

root=Path.cwd();base=Path(__file__).resolve().parent
sys.path.insert(0,str(root/'scripts'))
from cpu_gpu_protocol import source_manifest,sha
build=root/'build/cpu_gpu_full_tooling_20261010T121208603276Z/release'
testfile=build/'CTestTestfile.cmake'
safe_cpp={'structures','searching','baselines','datasets','quicksort','pdqsort','timsort','mergesort',
          'radixsort','comparisons','memory','memory_unsupported'}
safe_python={
 'environment_manifest':'Manifest formatting, unavailable-command and invalid-cache tests; no timing or GPU probe.',
 'cuda_preflight':'Mocks driver/runtime collection; real CMake option probes explicitly disable CUDA; no runtime/kernel execution.',
 'cuda_benchmark_analysis':'Only the two-argument Python command is safe; no benchmark executable supplied; GPU timing methods skip.',
 'cuda_sort_handoff':'Injected unavailable/timeout/interruption handlers; invalid CLI and CUDA-OFF option checks; no actual GPU call.',
 'cli':'Correctness-only algorithm_benchmark CLI; no timer or performance output.',
 'metrics_cli':'Counting-comparator/RSS CLI, no timing measurement or GPU sorter.',
 'cpu_gpu_comparison_framework':'Synthetic CSV/matrix analysis and mocked orchestration/prerequisites; small untimed input generation only.'}
timing={
 'experiment_pipeline':'End-to-end experiment tests invoke benchmark processes.',
 'structure_timing':'Calls real construction and lookup timing engines.',
 'structure_framework':'Launches structure_benchmark.',
 'search_timing':'Calls real search batch timing engine.',
 'search_framework':'Launches search_benchmark.',
 'timing':'Calls real sorting timing engine.',
 'benchmark_framework':'Launches sort_benchmark.',
 'parallel_mergesort':'Embedded N32768, W1/R2, sequential and parallel sort timing: six actual rows.',
 'parallel_framework':'Launches parallel_sort_benchmark.',
 'comparison_engine':'Calls comparison trial timing engine.'}
tests={}
for line in testfile.read_text().splitlines():
    m=re.fullmatch(r'add_test\((\w+) (.*)\)',line)
    if not m:continue
    name=m[1];argv=shlex.split(m[2]);pattern=[]
    for arg in argv:
        p=Path(arg)
        if arg==sys.executable or p.resolve()==Path(sys.executable).resolve():pattern.append('@python')
        elif p==build:pattern.append('@build')
        elif p.is_relative_to(build):pattern.append('@build/'+str(p.relative_to(build)))
        elif p==root:pattern.append('@source')
        elif p.is_relative_to(root):pattern.append('@source/'+str(p.relative_to(root)))
        else:raise ValueError('unreviewed argument '+arg)
    if name in safe_cpp:classification='cpu_correctness';reason='C++ differential/invariant/counting/memory checks; no clock-delimited algorithm invocation or GPU call.'
    elif name in safe_python:classification='cpu_correctness';reason=safe_python[name]
    else:classification='timing';reason=timing[name]
    tests[name]=dict(classification=classification,command=pattern,reason=reason)
assert len(tests)==29 and sum(t['classification']=='cpu_correctness' for t in tests.values())==19
extras={
 'cuda_runtime_smoke':dict(classification='gpu_correctness',command=['@build/cuda_runtime_probe'],reason='Actual device enumeration and tiny correctness kernel; explicit GPU correctness opt-in only.'),
 'cuda_sorting':dict(classification='gpu_correctness',command=['@build/test_cuda_sorting'],reason='Actual475-input/1900-output CUB correctness suite without benchmark timing; explicit GPU correctness opt-in only.'),
 'cuda_benchmark_gpu_framework':dict(classification='timing',command=['@python','@source/tests/test_cuda_benchmark.py','@build/cuda_sort_benchmark'],reason='Executable argument enables actual GPU timing methods; never select.')}
manifest=dict(schema_version=1,policy='non_timing_correctness_v1',
    evidence='results/raw/'+base.name,
    review_method='No safety CTest labels exist. Reviewed source/call paths and exact command arguments; source changes require explicit re-review/reclassification.',
    cpu_build_tests=list(tests),cuda_additional_tests=list(extras),tests={**tests,**extras},reviewed_source_sha256=source_manifest())
path=root/'docs/NON_TIMING_TEST_SELECTION_v1.json'
with path.open('x') as stream:json.dump(manifest,stream,indent=2,sort_keys=True);stream.write('\n')
shadow=base/'discovery';shadow.mkdir()
(shadow/'CTestTestfile.cmake').write_bytes(testfile.read_bytes())
with (base/'DISCOVERY_COPY.json').open('x') as stream:json.dump(dict(source=str(testfile),copied=str(shadow/'CTestTestfile.cmake'),
    source_sha256=sha(testfile),copied_sha256=sha(shadow/'CTestTestfile.cmake'),
    unchanged_absolute_test_commands=True,tests_executed=False),stream,indent=2)
print(json.dumps(dict(classified=32,selected_cpu=19,optional_gpu_correctness=2,blocked_timing=11,manifest=str(path),discovery_copy=str(shadow)),indent=2))
