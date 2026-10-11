import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
from non_timing_tests import pre_discovery_gate, selected_ctest
from run_cpu_gpu_pilot import invoke
output=Path(__file__).resolve().parent
kind=sys.argv[1]
build=ROOT/('build/autonomous_cpu_'+kind)
# Static source, hooks, literal registry and canonical path checks BEFORE any discovery.
manifest,guard=pre_discovery_gate(build)
print('Static guard passed:',guard['build_dir'],flush=True)
prefix=[] if kind=='release' else ['env','-u','ASAN_OPTIONS','-u','LSAN_OPTIONS','UBSAN_OPTIONS=halt_on_error=1']
def call(name,argv,timeout): return invoke(output,name,argv,timeout)
selected_ctest(call,output,'cpu_'+kind,build,prefix=prefix,allow_diagnostics=True)
