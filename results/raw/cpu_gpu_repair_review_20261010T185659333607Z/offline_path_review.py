"""Inspect pure validation paths only; all subprocess execution is forbidden."""
import copy
import json
from pathlib import Path
import sys
from unittest import mock

ROOT = Path.cwd()
BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'scripts'))
import cpu_gpu_provenance as provenance
import non_timing_tests as selector
from cpu_gpu_protocol import load_protocol

def write(name,value):
    with (BASE/name).open('x') as stream:
        json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')

report = dict(kind='offline_helper_review_not_test_suite',subprocesses_executed=0,
              ctest_executed=False,prerequisites_executed=False,resource_checks_executed=False,
              timing_executed=False,gpu_executed=False,provenance={},selection={})

def reject(callback):
    try:
        callback()
    except (ValueError,TypeError,KeyError,OSError) as error:
        return dict(rejected=True,error=type(error).__name__+': '+str(error))
    return dict(rejected=False)

with mock.patch('subprocess.run',side_effect=AssertionError('subprocess forbidden in review')), \
     mock.patch('subprocess.Popen',side_effect=AssertionError('subprocess forbidden in review')):
    model = load_protocol()
    # Read immutable accepted-pilot provenance, not new source or hardware probes.
    path=ROOT/'results/raw/cpu_gpu_pilot_20261010T001232473460Z/remote_v3/modern-algorithm-benchmark/results/raw/pilot_v3/source_review.json'
    source=json.loads(path.read_text())
    provenance.validate_retained_source(source,model)
    report['provenance']['accepted_pilot_source_claim_valid']=True
    for target in ['src/cuda/cub_sort.cu','src/cuda/cub_timing.cu','third_party/cub/UPSTREAM.json','CMakeLists.txt']:
        altered=copy.deepcopy(source);altered['current_source_sha256'][target]='0'*64
        result=reject(lambda:provenance.validate_retained_source(altered,model))
        assert result['rejected'],target
        report['provenance'][target]=result
    altered=copy.deepcopy(source);changed_model=copy.deepcopy(model)
    changed_model['source_at_freeze_sha256']['src/cuda/cub_sort.cu']='0'*64
    altered['current_source_sha256']['src/cuda/cub_sort.cu']='0'*64
    result=reject(lambda:provenance.validate_retained_source(altered,changed_model))
    assert result['rejected'];report['provenance']['redefined_model_and_map']=result
    for label,text in [('missing',None),('malformed','{'),('ambiguous','{"files_sha256":{},"files_sha256":{}}')]:
        p=BASE/('untrusted_'+label+'.json')
        if text is not None:
            with p.open('x') as stream:stream.write(text)
        with mock.patch.object(provenance,'FREEZE',p):
            result=reject(lambda:provenance.validate_retained_source(source,model))
        assert result['rejected'];report['provenance']['trusted_freeze_'+label]=result
    result=reject(lambda:provenance.strict_json('{"x":1,"x":2}'))
    assert result['rejected'];report['provenance']['duplicate_json_fields']=result

    build=ROOT/'build/cpu_gpu_full_tooling_20261010T121208603276Z/release'
    retained=ROOT/'results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/CTEST_DISCOVERY.json'
    data=json.loads(retained.read_text())
    plan=selector.select_tests(data,build)
    assert len(plan['selected'])==19 and 'parallel_mergesort' not in plan['selected']
    report['selection']['retained_discovery_plan']=plan
    for label in ['unknown','missing','duplicate','timing_command','fixture','dependency','environment']:
        altered=copy.deepcopy(data)
        first=next(t for t in altered['tests'] if t['name']=='datasets')
        if label=='unknown':altered['tests'].append(dict(name='unclassified',command=['unclassified']))
        if label=='missing':altered['tests'].pop()
        if label=='duplicate':altered['tests'].append(copy.deepcopy(altered['tests'][0]))
        if label=='timing_command':first['command']=[str(build/'test_parallel_mergesort')]
        if label in ['fixture','dependency','environment']:
            name={'fixture':'FIXTURES_REQUIRED','dependency':'DEPENDS','environment':'ENVIRONMENT'}[label]
            first['properties']=[dict(name=name,value='forbidden')]
        result=reject(lambda:selector.select_tests(altered,build))
        assert result['rejected'];report['selection'][label]=result
    with mock.patch.object(selector,'source_manifest',return_value={'modified_source':'0'*64}):
        result=reject(lambda:selector.select_tests(data,build))
    assert result['rejected'];report['selection']['modified_source']=result

    # Inert text fixture only. NEVER invoke CTest in this directory. Test-level
    # JSON discovery cannot represent these directory-level commands/includes.
    hook=BASE/'UNEXECUTED_HOOK_BUILD';hook.mkdir()
    with (hook/'CTestCustom.cmake').open('x') as stream:
        stream.write('set(CTEST_CUSTOM_PRE_TEST "/unexecuted/forbidden-timing-command")\n')
    with (hook/'CTestTestfile.cmake').open('x') as stream:
        stream.write('include("unreviewed.cmake")\n')
    with (hook/'unreviewed.cmake').open('x') as stream:
        stream.write('# Inert review text: no command is executed in this review.\n')
    manifest=selector.load_manifest()
    altered=copy.deepcopy(data)
    for entry in altered['tests']:
        entry['command']=selector.expected_command(manifest['tests'][entry['name']]['command'],hook)
    plan=selector.select_tests(altered,hook)
    report['selection']['unreviewed_build_hooks']=dict(selection_accepted=True,selected=plan['selected'],
        pre_test_hook_text=(hook/'CTestCustom.cmake').read_text(),test_include_text=(hook/'CTestTestfile.cmake').read_text(),
        hook_files_consulted_by_selector=False,hook_execution_performed=False,
        conclusion='Directory-level CTest hooks/includes are outside reviewed source/discovery guards.')
    assert len(plan['selected'])==19

write('OFFLINE_PATH_REVIEW.json',report)
print(json.dumps(report,indent=2,sort_keys=True))
