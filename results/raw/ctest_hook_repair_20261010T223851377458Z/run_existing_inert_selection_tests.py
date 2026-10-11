"""Run ONLY the inspected selector class, with all real process launch blocked.

Do not collect ProvenanceTests (its subprocess reproducer is out of this scope),
the framework class, the 19 CTest groups or any prerequisite entry point.
"""
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock
root=Path.cwd();sys.path[:0]=[str(root/'tests'),str(root/'scripts')]
with mock.patch.object(subprocess,'run',side_effect=AssertionError('real process forbidden')),\
     mock.patch.object(subprocess,'Popen',side_effect=AssertionError('real process forbidden')),\
     mock.patch.object(os,'system',side_effect=AssertionError('shell forbidden')):
    from test_cpu_gpu_safety import SelectorTests
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(SelectorTests)
    assert suite.countTestCases()==11
    result=unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
