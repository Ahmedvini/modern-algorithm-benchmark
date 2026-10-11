"""One-time review artifact: derive declarations from inspected static metadata.

NOT a production auto-enrollment path. Each command is checked against the old
reviewed manifest, each backtrace against protected CMake source, and CUDA extra
properties below against the inspected cmake/cuda.cmake. No CMake/CTest runs.
"""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path.cwd()/'scripts'))
from ctest_build_guard import statements
from non_timing_tests import expected_command
root=Path.cwd(); build=root/'build/cpu_gpu_full_tooling_20261010T121208603276Z/release'
path=root/'docs/NON_TIMING_TEST_SELECTION_v1.json'; manifest=json.loads(path.read_text())
props={}
for command,args in statements((build/'CTestTestfile.cmake').read_text()):
    name=args[0]
    if command=='add_test':
        assert [str(Path(a).resolve()) for a in args[1:]]==expected_command(manifest['tests'][name]['command'],build)
    else:
        values=dict(zip(args[2::2],args[3::2])); trace=values['_BACKTRACE_TRIPLES'].split(';')
        assert trace[0]==str(root/'CMakeLists.txt')
        assert 'add_test(NAME '+name in (root/'CMakeLists.txt').read_text().splitlines()[int(trace[1])-1]
        props[name]={k:v.replace(str(root),'@source') for k,v in values.items()}
for name,extra in [('cuda_runtime_smoke',{'SKIP_RETURN_CODE':'77','TIMEOUT':'60'}),
                   ('cuda_sorting',{'SKIP_RETURN_CODE':'77','TIMEOUT':'240'}),
                   ('cuda_benchmark_gpu_framework',{'TIMEOUT':'180'})]:
    lines=(root/'cmake/cuda.cmake').read_text().splitlines()
    number=next(i+1 for i,line in enumerate(lines) if 'add_test(NAME '+name+' ' in line)
    # Include stack is reviewed source metadata, never an executable directive.
    include_line=next(i+1 for i,line in enumerate((root/'CMakeLists.txt').read_text().splitlines())
                      if 'include(cmake/cuda.cmake)' in line)
    trace=f'@source/cmake/cuda.cmake;{number};add_test;@source/CMakeLists.txt;{include_line};include;@source/cmake/cuda.cmake;0;'
    props[name]=dict(extra,_BACKTRACE_TRIPLES=trace)
dart={}
for line in (build/'DartConfiguration.tcl').read_text().splitlines():
    if line and not line.startswith('#'):
        key,value=line.split(': ',1)
        dart[key]=value.replace(str(build),'@build').replace(str(root),'@source')
manifest['build_metadata']=dict(policy='flat_literal_ctest_v1',test_properties=props,dart_defaults=dart,
    dart_inert_metadata=['Site','BuildName','Compiler','CompilerVersion'])
manifest['review_method']+=' Build metadata: literal flat registry commands/properties matched to protected CMake source; all hooks/includes/subdirs rejected before discovery.'
path.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
print('Reviewed root registrations:',len(props),'Dart keys:',len(dart),'no CTest invoked')
