#!/usr/bin/env python3
"""Host schema/statistics/safety tests; optional real CUDA CLI integration."""
import copy
import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import analyze_cuda_results as analysis
import run_cuda_matrix as matrix
import validate_cuda_timing as validation
EXE=Path(sys.argv.pop(1)).resolve() if len(sys.argv)>1 else None


def fixture(path):
    path.mkdir()
    meta=dict(schema_version=1,protocol=analysis.PROTOCOL,run_id='fixture',algorithm='cub_radix_sort',
        implementation_version='cub_radix_sort_v1',distribution='uniform',size=8,seed=42,
        nearly_sorted_swaps=0,duplicate_cardinality=16,dataset_generator='mt19937_64_v1',input_hash_fnv1a64='123',
        repetitions=3,warmups=1,expected_rows=4,elapsed_unit='ns',allocation_policy='prepared_pinned_reuse_v1',
        stream_policy='private_nonblocking_serial',end_to_end_clock='steady_clock',phase_clock='cuda_event_float_ms_to_ns',
        cub_version=300001,run_kind='performance',build_type='Release',sanitizers=False,compiler_id='GNU',
        compiler_version='13.3',platform='synthetic',architecture='synthetic',gpu_name='synthetic fixture only',
        cuda_compiler_version='13.0',cuda_toolkit_version='13.0',runtime_api_version=13000,driver_api_version=13000,
        requested_device=0,actual_device=0,compute_major=7,compute_minor=5,device_memory_bytes=1024,workspace_bytes=1)
    (path/'run.json').write_text(json.dumps(meta))
    rows=[]
    for phase,trial,value in [('warmup',0,999),('measure',0,10),('measure',1,20),('measure',2,30)]:
        row={k:str(meta[k]) for k in analysis.SHARED}
        row.update(phase=phase,trial_index=str(trial),elapsed_unit='ns',status='ok',correctness='passed',error='')
        row.update({k:str(value*(i+1)) for i,k in enumerate(analysis.METRICS)});rows.append(row)
    save_rows(path,rows)
    (path/'COMPLETE.json').write_text(json.dumps(dict(schema_version=1,complete=True,rows=4)))
    return meta,rows


def save_rows(path,rows):
    with (path/'trials.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,analysis.FIELDS);w.writeheader();w.writerows(rows)


class HostTests(unittest.TestCase):
    def test_exact_statistics_and_warmup_exclusion(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'run';fixture(p);g=analysis.analyze(p)['groups'][0]
            for i,key in enumerate(analysis.METRICS):
                s=g['metrics'][key];self.assertEqual(s['median_ns'],20*(i+1));self.assertEqual(s['mean_ns'],20*(i+1))
                self.assertEqual(s['stdev_ns'],10*(i+1));self.assertEqual(s['min_ns'],10*(i+1));self.assertEqual(s['max_ns'],30*(i+1))
            self.assertEqual(g['successful_trials'],3);self.assertEqual(g['warmup_rows'],1)
    def test_invalid_rows(self):
        for field,value in [('h2d_ns','nan'),('device_sort_ns','inf'),('d2h_ns','-1'),('end_to_end_ns',''),
                            ('protocol','other'),('elapsed_unit','us'),('trial_index','0'),('correctness','failed')]:
            with self.subTest(field=field,value=value),tempfile.TemporaryDirectory() as d:
                p=Path(d)/'run';_,rows=fixture(p);rows[-1][field]=value;save_rows(p,rows)
                with self.assertRaises(ValueError):analysis.analyze(p)
    def test_duplicate_excess_and_missing(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'run';_,rows=fixture(p);save_rows(p,rows+[rows[-1]])
            with self.assertRaises(ValueError):analysis.analyze(p)
            save_rows(p,rows[:-1])
            with self.assertRaises(ValueError):analysis.analyze(p,True)  # COMPLETE contradicts data.
            (p/'COMPLETE.json').unlink()
            with self.assertRaises(ValueError):analysis.analyze(p)
            g=analysis.analyze(p,True)['groups'][0];self.assertEqual(g['missing_trials'],1);self.assertFalse(g['complete'])
    def test_failure_with_csv_escaping(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'run';_,rows=fixture(p);(p/'COMPLETE.json').unlink()
            row=rows[2];row.update(status='error',correctness='not_checked',error='failure,"quoted"\nline')
            row.update({k:'' for k in analysis.METRICS});save_rows(p,rows[:3])
            (p/'FAILED.json').write_text('{}');g=analysis.analyze(p,True)['groups'][0]
            self.assertEqual(g['successful_trials'],1);self.assertEqual(g['failed_trials'],1);self.assertEqual(g['missing_trials'],1)
    def test_protocol_and_metadata(self):
        for key,value in [('cub_version',300000),('size',True),('repetitions',0),('sanitizers',True),
                          ('build_type','Debug'),('allocation_policy','unknown'),('actual_device',1)]:
            with self.subTest(key=key),tempfile.TemporaryDirectory() as d:
                p=Path(d)/'run';meta,_=fixture(p);meta[key]=value;(p/'run.json').write_text(json.dumps(meta))
                with self.assertRaises(ValueError):analysis.analyze(p)
    def test_plan_and_invalid_configs(self):
        self.assertEqual(len(matrix.plan([0,1,1025,65537],analysis.DISTRIBUTIONS,[1729,42],1,5)),48)
        for text in ['-1','+1','1,1','x','1,','1000001']:
            with self.assertRaises(ValueError):matrix.numbers(text,1000000)
        with self.assertRaises(ValueError):matrix.plan([1],['unknown'],[1],1,5)
        with self.assertRaises(ValueError):matrix.plan([1],['uniform'],[1],1,0)
    def test_failed_timeout_interrupted_subprocess(self):
        for kind,code in [('failed',1),('timeout',1),('interrupted',130)]:
            with self.subTest(kind=kind),tempfile.TemporaryDirectory() as d:
                def run(argv,**kwargs):
                    if kind=='timeout':raise subprocess.TimeoutExpired(argv,1,b'partial',b'detail')
                    if kind=='interrupted':raise KeyboardInterrupt()
                    return subprocess.CompletedProcess(argv,9,'out','error')
                p=Path(d)/'run';self.assertEqual(matrix.run('unused',p,matrix.plan([1],['uniform'],[1],1,5),run),code)
                self.assertFalse((p/'COMPLETE.json').exists())
                self.assertTrue((p/('INTERRUPTED.json' if code==130 else 'FAILED.json')).exists())
                summary=analysis.analyze(p,True);self.assertFalse(summary['complete']);self.assertEqual(len(summary['missing_configurations']),1)
    def test_output_collision(self):
        with tempfile.TemporaryDirectory() as d:
            for name in ['existing','link']:
                p=Path(d)/name
                if name=='existing':p.mkdir()
                else:p.symlink_to(Path(d)/'absent')
                with self.assertRaises(FileExistsError):matrix.run('unused',p,[],lambda *a,**k:self.fail('executed'))
            self.assertFalse((Path(d)/'absent').exists())
    def test_deterministic_regeneration_and_exclusive_summary(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'run';fixture(p);outputs=[Path(d)/'a.json',Path(d)/'b.json']
            for output in outputs:
                r=subprocess.run([sys.executable,str(ROOT/'scripts/analyze_cuda_results.py'),str(p),'--output',str(output)],capture_output=True)
                self.assertEqual(r.returncode,0,r.stderr)
            self.assertEqual(outputs[0].read_bytes(),outputs[1].read_bytes())
            r=subprocess.run([sys.executable,str(ROOT/'scripts/analyze_cuda_results.py'),str(p),'--output',str(outputs[0])],capture_output=True)
            self.assertEqual(r.returncode,1)
    def test_trivial_phase_metrics(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'run';meta,rows=fixture(p);meta['size']=1;(p/'run.json').write_text(json.dumps(meta))
            for r in rows:
                r['size']='1'
                for k in analysis.METRICS[:-1]:r[k]='0'
            save_rows(p,rows);self.assertTrue(analysis.analyze(p)['complete'])
            rows[0]['h2d_ns']='1';save_rows(p,rows)
            with self.assertRaises(ValueError):analysis.analyze(p)
    def test_validation_runner_collision(self):
        with tempfile.TemporaryDirectory() as d:
            raw=Path(d)/'raw';processed=Path(d)/'processed';raw.mkdir()
            with patch.object(validation.subprocess,'run') as command:
                with self.assertRaises(FileExistsError):validation.run(raw,processed)
                command.assert_not_called()
            self.assertFalse(processed.exists())
            fresh=Path(d)/'fresh';processed.mkdir();sentinel=processed/'keep';sentinel.write_text('old')
            with patch.object(validation.subprocess,'run') as command:
                self.assertEqual(validation.run(fresh,processed),1);command.assert_not_called()
            self.assertEqual(sentinel.read_text(),'old');self.assertTrue((fresh/'FAILED.json').exists())
    def test_validation_runner_failure_diagnostics(self):
        with tempfile.TemporaryDirectory() as d:
            raw=Path(d)/'raw';processed=Path(d)/'processed'
            with patch.object(validation.subprocess,'run',return_value=subprocess.CompletedProcess(['fixture'],9,'diagnostic','failure')):
                self.assertEqual(validation.run(raw,processed),1)
            record=json.loads((raw/'correctness.json').read_text())
            self.assertEqual(record['exit_code'],9);self.assertEqual(record['stderr'],'failure')
            self.assertTrue((raw/'FAILED.json').exists());self.assertFalse((raw/'COMPLETE.json').exists())


@unittest.skipUnless(EXE,'real CUDA executable not supplied; host tests only')
class GpuCliTests(unittest.TestCase):
    def test_invalid_cli_and_safety(self):
        for args in [['--size','-1'],['--repetitions','0'],['--seed','18446744073709551616'],
                     ['--sort','std_sort'],['--distribution','unknown'],['--size','1000001'],['--size'],['--unknown']]:
            with self.subTest(args=args),tempfile.TemporaryDirectory() as d:
                p=Path(d)/'run';r=subprocess.run([str(EXE),'--output',str(p)]+args,capture_output=True)
                self.assertEqual(r.returncode,1);self.assertFalse(p.exists())
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'old';p.mkdir();sentinel=p/'keep';sentinel.write_text('keep')
            r=subprocess.run([str(EXE),'--output',str(p)],capture_output=True);self.assertEqual(r.returncode,1)
            self.assertEqual(sentinel.read_text(),'keep')
    def test_real_small_edge_and_distribution_runs(self):
        with tempfile.TemporaryDirectory() as d:
            for n in [0,1,2,31,32,33,1023,1024,1025,65537]:
                for dist in analysis.DISTRIBUTIONS:
                    p=Path(d)/(str(n)+dist)
                    r=subprocess.run([str(EXE),'--output',str(p),'--size',str(n),'--distribution',dist,
                                      '--warmups','1','--repetitions','2','--seed','42','--validation-only'],capture_output=True,timeout=60)
                    self.assertEqual(r.returncode,0,r.stderr)
                    summary=analysis.analyze(p);self.assertEqual(summary['groups'][0]['successful_trials'],2)
if __name__=='__main__':unittest.main()
