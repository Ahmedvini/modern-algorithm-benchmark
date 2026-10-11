"""Accept/reject a metadata-only hook fixture; NEVER invoke CTest or a test."""
import copy
import json
from pathlib import Path
import sys
from unittest import mock
ROOT=Path.cwd();BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts'))
import non_timing_tests as selector

old=ROOT/'build/cpu_gpu_full_tooling_20261010T121208603276Z/release'
fixture=BASE/'UNEXECUTED_MATCHING_CTEST_METADATA';fixture.mkdir()
# Preserve all29 actual registrations/commands, rebased as in a different build.
# The binaries are not copied, inspected by execution, or invoked.
text=(old/'CTestTestfile.cmake').read_text().replace(str(old),str(fixture))
text+='\ninclude("'+str(fixture/'unreviewed.cmake')+'")\n'
with (fixture/'CTestTestfile.cmake').open('x') as stream:stream.write(text)
with (fixture/'unreviewed.cmake').open('x') as stream:
    stream.write('# Inert review content. Directory includes may contain arbitrary CMake statements.\n')
with (fixture/'CTestCustom.cmake').open('x') as stream:
    stream.write('set(CTEST_CUSTOM_PRE_TEST "/unexecuted/forbidden-timing-command")\n')
data=json.loads((ROOT/'results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/CTEST_DISCOVERY.json').read_text())
with mock.patch('subprocess.run',side_effect=AssertionError('forbidden subprocess')), \
     mock.patch('subprocess.Popen',side_effect=AssertionError('forbidden subprocess')):
    manifest=selector.load_manifest()
    for entry in data['tests']:
        entry['command']=selector.expected_command(manifest['tests'][entry['name']]['command'],fixture)
    plan=selector.select_tests(data,fixture)
result=dict(kind='static_matching_registration_hook_review',registrations_preserved=29,
    actual_ctest_discovery_executed=False,ctest_executed=False,tests_executed=False,hook_executed=False,
    reviewed_source_unchanged=True,selection_accepted=True,selected=plan['selected'],
    metadata_directory=str(fixture.relative_to(ROOT)),
    limitation='Build metadata is copied/rebased as text; no runtime CTest hook behavior is claimed to have been exercised.')
with (BASE/'HOOK_METADATA_REVIEW.json').open('x') as stream:
    json.dump(result,stream,indent=2,sort_keys=True);stream.write('\n')
assert len(plan['selected'])==19
print(json.dumps(result,indent=2,sort_keys=True))
