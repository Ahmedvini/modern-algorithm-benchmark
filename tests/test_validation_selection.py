"""Inert v2 selection regression; no CTest or subprocess execution."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import non_timing_tests as selector
from ctest_fixture import write_fixture

class SelectionTests(unittest.TestCase):
    def test_exact_legacy_19_preserved_and_diagnostics_are_explicit(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(selector.subprocess,'run',side_effect=AssertionError('no execution')):
            b=Path(d)/'fixture'; discovery=write_fixture(b)
            base=selector.select_tests(discovery,b)
            self.assertEqual(base['selected_count'],19)
            self.assertNotIn('parallel_mergesort',base['selected'])
            plan=selector.select_tests(discovery,b,allow_diagnostics=True)
            self.assertEqual(set(plan['selected'])-set(base['selected']),{'parallel_workers_correctness','validation_policy'})
            self.assertEqual(plan['selected_count'],21)
            self.assertNotIn('comparison_engine',plan['selected'])

    def test_gpu_diagnostic_never_selects_timing_framework(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(selector.subprocess,'run',side_effect=AssertionError('no execution')):
            b=Path(d)/'fixture'; discovery=write_fixture(b,gpu=True)
            plan=selector.select_tests(discovery,b,allow_gpu=True,allow_diagnostics=True)
            self.assertIn('cuda_prepared_correctness',plan['selected'])
            self.assertNotIn('cuda_benchmark_gpu_framework',plan['selected'])
            self.assertNotIn('parallel_mergesort',plan['selected'])

    def test_hooks_still_rejected_before_callback(self):
        with tempfile.TemporaryDirectory() as d:
            b=Path(d)/'fixture'; write_fixture(b);(b/'CTestCustom.cmake').write_text('# inert rejected hook\n')
            callback=mock.Mock(side_effect=AssertionError('discovery forbidden'))
            with self.assertRaises(ValueError): selector.selected_ctest(callback,Path(d),'fixture',b)
            callback.assert_not_called()

if __name__=='__main__': unittest.main()
