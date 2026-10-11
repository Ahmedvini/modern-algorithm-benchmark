#!/usr/bin/env python3
"""Synthetic parser/scheduler fixtures are NOT GPU observations."""
import copy
import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from analyze_cpu_gpu import analyze
from analyze_cuda_results import FIELDS as PREPARED_FIELDS
from cpu_gpu_protocol import BACKENDS,MATRIX,PROTOCOL,SIDE_FIELDS,canonical,dump_new,load_protocol,schedule,sha
from run_cpu_gpu_pilot import environment_gate,invoke,worker_command
INPUT_TOOL=Path(sys.argv.pop(1)).absolute() if len(sys.argv)>1 and not sys.argv[1].startswith('-') else None

def resource(n):
    return dict(size=n,gpu_name='Tesla T4',compute_major=7,compute_minor=5,prepared_query_bytes=123,adapter_query_bytes=123,
                prepared_diagnostic_cudaMalloc_requested_bytes=123,adapter_diagnostic_cudaMalloc_requested_bytes=123,
                free_device_bytes_before_buffers=1024**3,combined_device_payload_bytes=16*n+246,known_host_peak_payload_bytes=24*n,
                prepared_session_query_bytes=123,prepared_session_cudaMalloc_requested_bytes=123)

def write_table(path,fields,rows):
    with path.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)

def fixture(root):
    model=load_protocol();root.mkdir();build={'fixture':'explicit synthetic metadata'};environment={'fixture':'not hardware evidence'}
    dump_new(root/'build.json',build);dump_new(root/'environment.json',environment)
    meta=dict(schema_version=1,protocol=PROTOCOL,matrix_part='pilot',run_kind='synthetic_test_fixture',run_id='fixture',matrix_sha256=sha(MATRIX),
              dataset_ids=[c['dataset_id'] for c in model['pilot']['cells']],build_id=hashlib.sha256(canonical(build)).hexdigest(),
              environment_id=hashlib.sha256(canonical(environment)).hexdigest(),prerequisites_passed=True,implementations={b:{} for b in BACKENDS})
    dump_new(root/'run.json',meta);dump_new(root/'workspace_queries.json',{str(n):resource(n) for n in [1025,1000000]})
    for i,cell in enumerate(model['pilot']['cells']):
        r=cell['recipe'];base=root/('data_'+cell['dataset_id']);base.mkdir()
        # Fixed zero bytes solely to exercise retained-file identity checks; not generated benchmark data.
        (base/'input.bin').write_bytes(bytes(4*r['size']));input_hash=sha(base/'input.bin')
        dump_new(base/'dataset.json',dict(recipe=r,dataset_id=cell['dataset_id'],input_sha256=input_hash,input_hash_fnv1a64='1'))
        measurement=base/'measurements';measurement.mkdir();(measurement/'prepared').mkdir()
        primary=[];prepared=[];sides=[];attempts=[]
        for row in schedule(cell,i*30):
            attempts.append({k:v for k,v in row.items() if k!='dataset_id'})
            common={k:str(r[k]) for k in ['size','seed','distribution','nearly_sorted_swaps','duplicate_cardinality','dataset_generator']}
            common.update(schema_version='1',run_id='fixture',input_hash_fnv1a64='1',phase=row['phase'],trial_index=str(row['trial_index']),
                          elapsed_unit='ns',status='ok',correctness='passed',error='')
            sample=100*(row['trial_index']+1) # Hand-checkable measured samples100,200,300,400,500.
            if row['backend_id']=='gpu_cub_prepared':
                prepared.append(dict(common,protocol='cuda_sort_timing_v1',algorithm='cub_radix_sort',implementation_version='cub_radix_sort_v1',
                                     h2d_ns=str(sample),device_sort_ns=str(sample),d2h_ns=str(sample),end_to_end_ns=str(sample)))
                sides.append({k:str(row[k]) for k in SIDE_FIELDS})
            else:
                backend=row['backend_id'];mode=next(b for b in model['backend_modes'] if b['id']==backend)
                parallel=backend=='cpu_parallel_merge_sort_t2';gpu=backend=='gpu_cub_adapter';actual=2 if parallel and r['size']>=32768 else 1
                primary.append(dict(common,protocol='cpu_gpu_host_call_v1',matrix_sha256=meta['matrix_sha256'],build_id=meta['build_id'],environment_id=meta['environment_id'],
                    dataset_id=cell['dataset_id'],input_sha256=input_hash,backend_id=backend,algorithm=mode['algorithm'],implementation_identity_ref=backend,
                    scope='host_vector_api_call_v1',execution_order=str(row['execution_order']),global_trial_index=str(row['global_trial_index']),
                    requested_cpu_threads='' if gpu else '2' if parallel else '1',actual_cpu_threads='' if gpu else str(actual),
                    parallel_region='' if gpu else 'true' if actual==2 else 'false',elapsed_ns=str(sample)))
        write_table(measurement/'primary.csv',model['primary_schema']['csv_fields'],primary)
        write_table(measurement/'prepared/trials.csv',PREPARED_FIELDS,prepared)
        write_table(measurement/'prepared_order.csv',SIDE_FIELDS,sides)
        (measurement/'attempts.jsonl').write_text(''.join(json.dumps(a)+'\n' for a in attempts))
        dump_new(measurement/'timer_calibration.json',dict(pairs=1000,median_ns=1,policy='diagnostic_only_no_subtraction'))
        dump_new(measurement/'resources.json',resource(r['size']));dump_new(measurement/'COMPLETE.json',dict(complete=True,rows=30))
    dump_new(root/'COMPLETE.json',dict(complete=True))

class FrameworkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary=tempfile.TemporaryDirectory();cls.template=Path(cls.temporary.name)/'template';fixture(cls.template)
    @classmethod
    def tearDownClass(cls):cls.temporary.cleanup()
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)/'raw';shutil.copytree(self.template,self.root)
        self.first=self.root/('data_'+load_protocol()['pilot']['cells'][0]['dataset_id'])/'measurements'
    def tearDown(self):self.temp.cleanup()
    def analyze(self,**kwargs):return analyze(self.root,allow_synthetic=True,**kwargs)
    def edit_rows(self,operation):
        path=self.first/'primary.csv'
        with path.open(newline='') as f:reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
        operation(rows);write_table(path,fields,rows)
    def remove_markers(self):
        # Only this test's disposable fixture is changed.
        (self.root/'COMPLETE.json').unlink();(self.first/'COMPLETE.json').unlink()
    def test_complete_counts_known_statistics(self):
        report=self.analyze();self.assertTrue(report['complete']);self.assertEqual(report['measured'],dict(successful=150,failed=0,interrupted=0,missing=0))
        summary=report['groups'][0]['metrics']['host_call_e2e_ns']
        self.assertEqual(summary['median_ns'],300);self.assertEqual(summary['mean_ns'],300)
        self.assertAlmostEqual(summary['stdev_ns'],158.11388300841898);self.assertEqual(summary['min_ns'],100);self.assertEqual(summary['max_ns'],500)
        self.assertEqual(len(report['paired_host_call_ratios']),18);self.assertTrue(all(r['denominator']=='gpu_cub_adapter' and r['ratio']==1 for r in report['paired_host_call_ratios']))
        self.assertTrue(all(g['distinct_inputs']==1 for g in report['cross_dataset']))
    def test_reject_synthetic_as_performance(self):
        with self.assertRaises(ValueError):analyze(self.root)
    def test_validator_clean_checkout_creates_build_parent(self):
        import validate_cpu_gpu_pilot as validator
        checkout=Path(self.temp.name)/'clean_checkout';checkout.mkdir()
        output=checkout/'validation'
        argv=['validate_cpu_gpu_pilot.py','--output',str(output),'--pilot-output',str(checkout/'pilot'),'--processed',str(checkout/'processed')]
        with mock.patch.object(validator,'ROOT',checkout),mock.patch.object(validator,'verify_source_extension',return_value={}),\
             mock.patch.object(validator,'invoke',side_effect=RuntimeError('fixture stop before preflight')),mock.patch.object(sys,'argv',argv):
            self.assertEqual(validator.main(),1)
        self.assertTrue((checkout/'build/validation').is_dir())
        self.assertEqual(json.loads((output/'FAILED.json').read_text())['error'],'fixture stop before preflight')
    def test_summary_regeneration(self):self.assertEqual(canonical(self.analyze()),canonical(self.analyze()))
    def test_duplicate_trial(self):
        self.edit_rows(lambda rows:rows.append(copy.deepcopy(rows[0])))
        with self.assertRaises(ValueError):self.analyze()
    def test_missing_trial_is_interrupted_when_attempt_exists(self):
        self.remove_markers();self.edit_rows(lambda rows:rows.pop())
        with self.assertRaises(ValueError):self.analyze()
        report=self.analyze(allow_incomplete=True);self.assertFalse(report['complete']);self.assertEqual(report['measured']['interrupted'],1);self.assertEqual(report['paired_host_call_ratios'],[])
    def test_missing_dataset(self):
        # A partial run may not have started its final dataset.
        (self.root/'COMPLETE.json').unlink();last=load_protocol()['pilot']['cells'][-1]['dataset_id'];shutil.rmtree(self.root/('data_'+last))
        report=self.analyze(allow_incomplete=True);self.assertEqual(report['measured']['missing'],25);self.assertFalse(report['complete'])
    def test_failed_trial_retained(self):
        self.remove_markers()
        def fail(rows):
            rows[-1].update(status='error',correctness='failed',elapsed_ns='',error='fixture wrong output')
        self.edit_rows(fail);report=self.analyze(allow_incomplete=True)
        self.assertEqual(report['measured']['failed'],1);self.assertEqual(report['paired_host_call_ratios'],[])
    def test_malformed_and_nonfinite(self):
        for bad in ['nan','-1','1.5','inf']:
            self.edit_rows(lambda rows:rows[0].update(elapsed_ns=bad))
            with self.assertRaises(ValueError):self.analyze()
    def test_incompatible_primary_scope(self):
        self.edit_rows(lambda rows:rows[0].update(scope='device_sort'))
        with self.assertRaises(ValueError):self.analyze()
    def test_wrong_dataset_identity(self):
        self.edit_rows(lambda rows:rows[0].update(input_sha256='0'*64))
        with self.assertRaises(ValueError):self.analyze()
    def test_wrong_thread_count(self):
        def corrupt(rows):next(r for r in rows if r['backend_id']=='cpu_parallel_merge_sort_t2')['actual_cpu_threads']='8'
        self.edit_rows(corrupt)
        with self.assertRaises(ValueError):self.analyze()
    def test_workspace_gate(self):
        path=self.root/'workspace_queries.json';data=json.loads(path.read_text());data['1000000']['adapter_query_bytes']=64*1024**2+1;path.write_text(json.dumps(data))
        with self.assertRaises(ValueError):self.analyze()
    def test_subprocess_failure_and_timeout_records(self):
        commands=Path(self.temp.name)/'commands';commands.mkdir()
        with self.assertRaises(RuntimeError):invoke(commands,'failed',[sys.executable,'-c','raise SystemExit(9)'],5)
        self.assertEqual(json.loads((commands/'failed.json').read_text())['exit_code'],9)
        with self.assertRaises(RuntimeError):invoke(commands,'timeout',[sys.executable,'-c','import time;time.sleep(10)'],.02)
        self.assertEqual(json.loads((commands/'timeout.json').read_text())['status'],'timeout')
    def test_dry_run_determinism_and_collision(self):
        command=[sys.executable,str(ROOT/'scripts/run_cpu_gpu_pilot.py'),'--executable','unused_worker','--input-tool','unused_input','--output',str(self.root),'--dry-run']
        a=subprocess.run(command,capture_output=True,text=True);b=subprocess.run(command,capture_output=True,text=True)
        self.assertEqual(a.returncode,0);self.assertEqual(a.stdout,b.stdout)
        collision=subprocess.run(command[:-1]+['--prerequisites','unused_prerequisites'],capture_output=True,text=True)
        self.assertEqual(collision.returncode,1);self.assertFalse((self.root/'FAILED.json').exists())
    def test_input_cli_roundtrip_and_invalid(self):
        if INPUT_TOOL is None:self.skipTest('input tool not supplied')
        destination=Path(self.temp.name)/'generated'
        args=[str(INPUT_TOOL),'--output',str(destination),'--size','9','--seed','1729','--distribution','signed_edges','--swaps','0','--distinct','16']
        result=subprocess.run(args,capture_output=True,text=True);self.assertEqual(result.returncode,0,result.stderr)
        import struct
        self.assertEqual(struct.unpack('<9i',(destination/'input.bin').read_bytes()),(-2147483648,2147483647,-1,0,1,-2147483647,2147483646,0,-2147483648))
        before=sha(destination/'input.bin');self.assertNotEqual(subprocess.run(args,capture_output=True).returncode,0);self.assertEqual(sha(destination/'input.bin'),before)
        for option,value in [('--size','-1'),('--size','1000001'),('--seed','+2'),('--distribution','invalid')]:
            invalid=list(args);invalid[invalid.index(option)+1]=value
            self.assertNotEqual(subprocess.run(invalid,capture_output=True).returncode,0)
    def test_prepared_nonfinite_and_sidecar_mismatch(self):
        path=self.first/'prepared/trials.csv'
        with path.open(newline='') as f:rows=list(csv.DictReader(f))
        rows[0]['device_sort_ns']='nan';write_table(path,PREPARED_FIELDS,rows)
        with self.assertRaises(ValueError):self.analyze()
    def test_wrong_protocol_or_warmup_index(self):
        for key,value in [('protocol','wrong'),('trial_index','9')]:
            self.edit_rows(lambda rows:rows[0].update({key:value}))
            with self.assertRaises(ValueError):self.analyze()
    def test_retained_input_tamper(self):
        path=self.first.parent/'input.bin'
        with path.open('r+b') as f:f.write(b'changed')
        with self.assertRaises(ValueError):self.analyze()
    def test_dangling_output_symlink(self):
        link=Path(self.temp.name)/'collision';link.symlink_to(Path(self.temp.name)/'absent')
        command=[sys.executable,str(ROOT/'scripts/run_cpu_gpu_pilot.py'),'--output',str(link),'--executable','unused','--input-tool','unused','--prerequisites','unused']
        result=subprocess.run(command,capture_output=True,text=True)
        self.assertEqual(result.returncode,1);self.assertTrue(link.is_symlink());self.assertFalse(link.exists())
    def test_interrupt_and_unavailable_commands(self):
        commands=Path(self.temp.name)/'interrupt';commands.mkdir()
        child=mock.Mock(pid=12345,returncode=-15);child.communicate.side_effect=[KeyboardInterrupt(),('','')]
        with mock.patch('run_cpu_gpu_pilot.subprocess.Popen',return_value=child),mock.patch('run_cpu_gpu_pilot.os.killpg'):
            with self.assertRaises(KeyboardInterrupt):invoke(commands,'interrupt',['fixture'])
        self.assertEqual(json.loads((commands/'interrupt.json').read_text())['status'],'interrupted')
        with self.assertRaises(RuntimeError):invoke(commands,'absent',['/nonexistent/mab-test-fixture'])
        self.assertEqual(json.loads((commands/'absent.json').read_text())['status'],'unavailable')
    def test_quoted_csv_error_field(self):
        self.remove_markers()
        def fail(rows):rows[-1].update(status='error',correctness='not_checked',elapsed_ns='',error='fixture, "quoted"\nerror')
        self.edit_rows(fail);self.assertEqual(self.analyze(allow_incomplete=True)['measured']['failed'],1)

if __name__=='__main__':unittest.main()
