"""Retain an inert plan and rejected-hook proof. Never invokes discovery."""
import json
import os
from pathlib import Path
import subprocess
import sys
from unittest import mock
root=Path.cwd();base=Path(__file__).resolve().parent
sys.path[:0]=[str(root/'tests'),str(root/'scripts')]
with mock.patch.object(subprocess,'run',side_effect=AssertionError('forbidden real process')),\
     mock.patch.object(subprocess,'Popen',side_effect=AssertionError('forbidden real process')),\
     mock.patch.object(os,'system',side_effect=AssertionError('forbidden shell')):
    import non_timing_tests as selector
    from ctest_fixture import write_fixture
    build=base/'UNEXECUTED_CLEAN_TREE';assert not build.exists()
    discovery=write_fixture(build)
    plan=selector.select_tests(discovery,build)
    with (base/'SELECTED_TESTS.json').open('x') as f:json.dump(plan,f,indent=2,sort_keys=True);f.write('\n')
    previous=root/'results/raw/cpu_gpu_repair_review_20261010T185659333607Z/UNEXECUTED_MATCHING_CTEST_METADATA'
    calls=[]
    def forbidden(*args):
        calls.append(args);raise AssertionError('rejected fixture reached discovery')
    try:
        selector.selected_ctest(forbidden,base,'never',previous)
    except ValueError as error:
        reason=str(error)
    else:
        raise AssertionError('old unsafe metadata accepted')
    assert calls==[] and 'hook/configuration' in reason
    proof=dict(previous_fixture=str(previous.relative_to(root)),rejected=True,reason=reason,
               discovery_callback_count=len(calls),actual_ctest_calls=0,actual_test_execution=False,
               actual_gpu_execution=False,selected=plan['selected'])
    with (base/'REJECTION_PROOF.json').open('x') as f:json.dump(proof,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps(proof,indent=2,sort_keys=True))
