"""Only two statically inspected inert classes. All real process launch blocked."""
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock
import contextlib

root=Path.cwd();sys.path[:0]=[str(root/'tests'),str(root/'scripts')]
with contextlib.ExitStack() as stack:
    for entry in ['run','Popen','call','check_call','check_output']:
        stack.enter_context(mock.patch.object(subprocess,entry,side_effect=AssertionError('real process forbidden')))
    stack.enter_context(mock.patch.object(os,'system',side_effect=AssertionError('shell forbidden')))
    from test_ctest_build_guard import BuildGuardTests
    from test_cpu_gpu_safety import SelectorTests
    mode=sys.argv[1]
    if mode=='new':
        suite=unittest.TestSuite(BuildGuardTests(name) for name in [
            'test_relative_helper_discovery_and_execution_share_guarded_path_across_cwds',
            'test_helper_keeps_guarded_path_after_callback_changes_caller_cwd',
            'test_relative_cli_discovery_uses_guarded_identity_after_fake_cwd_change',
            'test_relative_retained_json_cli_uses_guard_return_without_reresolving_input',
            'test_direct_selection_keeps_guard_return_when_cwd_changes_after_gate',
            'test_relative_unsafe_tree_rejected_before_mixed_cwd_callback',
            'test_relative_symlink_alias_still_rejected_before_callback',
            'test_cli_relative_unsafe_tree_rejected_before_mocked_discovery'])
        assert suite.countTestCases()==8
    elif mode=='all':
        suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(BuildGuardTests),
                                 unittest.defaultTestLoader.loadTestsFromTestCase(SelectorTests)])
        assert suite.countTestCases()==47
    else:raise ValueError('unknown inert test scope')
    result=unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
