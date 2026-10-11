"""Write inert test metadata. Never invokes CMake, CTest or a test executable."""
import json
from pathlib import Path

import non_timing_tests as selector


def write_fixture(build, gpu=False):
    build = Path(build)
    build.mkdir(parents=True, exist_ok=True)
    manifest = selector.load_manifest()
    names = manifest['cpu_build_tests'] + (manifest['cuda_additional_tests'] if gpu else [])
    declarations, tests = [], []
    for name in names:
        command = selector.expected_command(manifest['tests'][name]['command'], build)
        properties = {k:v.replace('@source', str(selector.ROOT.resolve())).replace('@build', str(build))
                      for k,v in manifest['build_metadata']['test_properties'][name].items()}
        declarations.append('add_test(' + name + ' ' + ' '.join(json.dumps(a) for a in command) + ')')
        declarations.append('set_tests_properties(' + name + ' PROPERTIES ' +
                            ' '.join(k+' '+json.dumps(v) for k,v in properties.items()) + ')')
        discovered = [dict(name=k, value=int(v) if k in ['TIMEOUT','SKIP_RETURN_CODE'] else v.split(';'))
                      for k,v in properties.items() if k != '_BACKTRACE_TRIPLES']
        discovered.append(dict(name='WORKING_DIRECTORY', value=str(build)))
        tests.append(dict(name=name, command=command, properties=discovered))
    (build/'CTestTestfile.cmake').write_text('\n'.join(declarations)+'\n')
    return dict(kind='ctestInfo', version=dict(major=1, minor=0), tests=tests)
