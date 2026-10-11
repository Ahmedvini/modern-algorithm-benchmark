#!/usr/bin/env python3
"""Host tooling tests; no GPU sorting success is simulated or claimed."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import validate_cuda_sort as handoff


def record():
    return dict(schema_version=1,protocol=handoff.PROTOCOL,algorithm='cub_radix_sort',
                implementation_version='cub_radix_sort_v1',status='ok',cases=475,
                output_checks=1900,cub_version=300001,runtime_api_version=13000,
                driver_api_version=13000,compute_major=7,compute_minor=5,device=0)


class HandoffTests(unittest.TestCase):
    def test_ctest_must_select_and_pass(self):
        handoff.verify_ctest('1/1 Test #26: cuda_sorting ........ Passed  1.0 sec')
        for text in ['No tests were found', '1/1 Test #26: cuda_sorting ... ***Skipped',
                     '1/1 Test #26: cuda_sorting ... ***Failed', '1/1 Test #26: other ... Passed']:
            with self.subTest(text=text),self.assertRaises(ValueError):handoff.verify_ctest(text)
    def test_schema(self):
        self.assertEqual(handoff.verify_result(record())['cases'],475)
    def test_bad_records(self):
        for key,value in [('cases',0),('cases',True),('output_checks',1899),('status','unavailable'),
                          ('protocol','other'),('protocol','cuda_sort_correctness_v1'),
                          ('cub_version',300000),('cub_version',300002),('runtime_api_version',12000),
                          ('device',-1),('compute_major',0)]:
            r=record();r[key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):handoff.verify_result(r)
        with self.assertRaises(ValueError):handoff.verify_result([])
    def test_existing_output(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'old';p.mkdir();sentinel=p/'sentinel';sentinel.write_text('preserved')
            with self.assertRaises(FileExistsError):handoff.run(p,runner=lambda *a,**k:self.fail('executed'))
            self.assertEqual(sentinel.read_text(),'preserved')
    def test_symlink_collision(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/'target';target.mkdir();link=Path(d)/'link';link.symlink_to(target)
            with self.assertRaises(FileExistsError):handoff.run(link)
            self.assertEqual(list(target.iterdir()),[])
    def test_dangling_symlink_collision(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/'absent';link=Path(d)/'link';link.symlink_to(target)
            with self.assertRaises(FileExistsError):
                handoff.run(link,runner=lambda *a,**k:self.fail('executed'))
            self.assertFalse(target.exists())
            self.assertTrue(link.is_symlink())
    def test_unavailable_is_failure_not_complete(self):
        with tempfile.TemporaryDirectory() as d:
            def unavailable(argv,**kwargs):return subprocess.CompletedProcess(argv,2,'unavailable','no GPU')
            p=Path(d)/'attempt';self.assertEqual(handoff.run(p,runner=unavailable),1)
            self.assertTrue((p/'FAILED.json').exists());self.assertFalse((p/'COMPLETE.json').exists())
            self.assertEqual(json.loads((p/'preflight.json').read_text())['exit_code'],2)
    def test_timeout_diagnostics(self):
        with tempfile.TemporaryDirectory() as d:
            def timeout(argv,**kwargs):raise subprocess.TimeoutExpired(argv,1,output=b'partial',stderr=b'detail')
            p=Path(d)/'attempt';self.assertEqual(handoff.run(p,runner=timeout),1)
            r=json.loads((p/'preflight.json').read_text());self.assertEqual(r['stdout'],'partial')
            self.assertEqual(r['status'],'timeout');self.assertTrue((p/'FAILED.json').exists())
    def test_interrupted(self):
        with tempfile.TemporaryDirectory() as d:
            def stop(*a,**k):raise KeyboardInterrupt()
            p=Path(d)/'attempt';self.assertEqual(handoff.run(p,runner=stop),130)
            self.assertTrue((p/'INTERRUPTED.json').exists());self.assertFalse((p/'COMPLETE.json').exists())
    def test_redaction(self):
        with tempfile.TemporaryDirectory() as d,patch.dict('os.environ',{'API_TOKEN':'secret_fixture_value'}):
            p=Path(d)/'record.json';handoff.write_json(p,dict(text='secret_fixture_value',count=475))
            self.assertEqual(json.loads(p.read_text()),dict(text='<redacted>',count=475))
    def test_sort_option_requires_cuda(self):
        with tempfile.TemporaryDirectory() as d:
            r=subprocess.run(['cmake','-S',str(ROOT),'-B',d,'-DMAB_ENABLE_CUDA=OFF',
                              '-DMAB_ENABLE_CUDA_SORT=ON'],capture_output=True,text=True)
            self.assertNotEqual(r.returncode,0)
            self.assertIn('MAB_ENABLE_CUDA_SORT requires MAB_ENABLE_CUDA=ON',r.stdout+r.stderr)
    def test_invalid_cli(self):
        r=subprocess.run([sys.executable,str(ROOT/'scripts/validate_cuda_sort.py'),'--bad'],capture_output=True,text=True)
        self.assertEqual(r.returncode,2)

if __name__=='__main__':unittest.main()
