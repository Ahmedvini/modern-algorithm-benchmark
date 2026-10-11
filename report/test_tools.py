"""Synthetic count/RSS record checks; no executable or benchmark is launched."""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import collect_metrics as tool

class MetricsTests(unittest.TestCase):
    def setUp(self):
        self.block=patch('subprocess.run',side_effect=AssertionError('no workloads'))
        self.block.start();self.addCleanup(self.block.stop)
        self.value=dict(schema_version=1,mode='sort_metrics',status='ok',sort_algorithm='std_sort',size=1000,seed=1729,
            distribution='uniform',comparison_convention='key_less_than_v1',dataset_generator='mt19937_64_v1',
            nearly_sorted_swaps=10,duplicate_cardinality=16,memory_sample_point='after_instrumented_sort_before_validation',
            key_comparisons=10,process_memory=dict(status='ok',metric='peak_rss',scope='process_lifetime',unit='bytes',
                method='getrusage_ru_maxrss',value=4096,error_code=None))
    def parse(self,value=None,code=0):
        return tool.parse(dict(exit_code=code,stdout=json.dumps(self.value if value is None else value)),1000,'uniform',1729,'std_sort')
    def test_valid(self):self.assertEqual(self.parse()['key_comparisons'],10)
    def test_failed_exit(self):
        with self.assertRaisesRegex(ValueError,'failed metrics'):self.parse(code=1)
    def test_identity(self):
        for k,v in [('size',1001),('seed',42),('sort_algorithm','radix_sort'),('comparison_convention','unknown'),('status','partial')]:
            with self.subTest(k=k),self.assertRaisesRegex(ValueError,'identity/status'):self.parse(dict(self.value,**{k:v}))
    def test_invalid_counts(self):
        for v in [-1,True,'10']:
            with self.subTest(v=v),self.assertRaisesRegex(ValueError,'comparison count'):self.parse(dict(self.value,key_comparisons=v))
    def test_unsupported_memory(self):
        value=copy.deepcopy(self.value);value['process_memory'].update(status='unsupported',method='none',value=None)
        self.assertEqual(self.parse(value)['process_memory']['status'],'unsupported')
    def test_bad_memory(self):
        for v in [dict(status='error'),dict(self.value['process_memory'],value=-1)]:
            value=copy.deepcopy(self.value);value['process_memory']=v
            with self.assertRaises(ValueError):self.parse(value)
    def test_api_field_is_not_wire_schema(self):
        value=copy.deepcopy(self.value);value['process_memory']['peak_rss_bytes']=value['process_memory'].pop('value')
        with self.assertRaisesRegex(ValueError,'memory schema'):self.parse(value)
    def test_malformed_record(self):
        with self.assertRaises(json.JSONDecodeError):tool.parse(dict(exit_code=0,stdout='bad'),1000,'uniform',1729,'std_sort')

if __name__=='__main__':unittest.main()
