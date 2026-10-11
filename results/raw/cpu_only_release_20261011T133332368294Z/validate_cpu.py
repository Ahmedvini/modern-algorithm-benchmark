"""Reuse the existing guarded CPU correctness path; never broad CTest."""
from pathlib import Path
import json
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
from non_timing_tests import pre_discovery_gate, selected_ctest
from run_cpu_gpu_pilot import invoke
output=Path(__file__).resolve().parent
build=ROOT/'build/autonomous_cpu_release'
manifest,guard=pre_discovery_gate(build)
names=sorted(n for n,v in manifest['tests'].items() if v['classification']=='cpu_correctness')
assert len(names)==21 and 'parallel_mergesort' not in names
assert all(manifest['tests'][n]['classification']!='timing' for n in names)
with (output/'STATIC_CPU_PLAN.json').open('x') as f:
    json.dump(dict(selected=names,build_metadata=guard,discovery_executed=False),f,indent=2,sort_keys=True)
print('Static source/build/path gate passed; exact21 untimed names:',', '.join(names),flush=True)
def call(name,argv,timeout):return invoke(output,name,argv,timeout)
selected_ctest(call,output,'cpu_release',Path(guard['build_dir']),allow_diagnostics=True)
