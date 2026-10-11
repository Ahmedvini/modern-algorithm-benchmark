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
from cpu_gpu_protocol import BACKENDS,FREEZE,MATRIX,PROTOCOL,SIDE_FIELDS,canonical,dump_new,load_protocol,schedule,sha
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

def fixture(root,part='pilot'):
    model=load_protocol();root.mkdir();build={'fixture':'explicit synthetic metadata'};environment={'fixture':'not hardware evidence'}
    dump_new(root/'build.json',build);dump_new(root/'environment.json',environment)
    meta=dict(schema_version=1,protocol=PROTOCOL,matrix_part=part,run_kind='synthetic_test_fixture',run_id='fixture',matrix_sha256=sha(MATRIX),freeze_sha256=sha(FREEZE),
              dataset_ids=[c['dataset_id'] for c in model[part]['cells']],build_id=hashlib.sha256(canonical(build)).hexdigest(),
              environment_id=hashlib.sha256(canonical(environment)).hexdigest(),prerequisites_passed=True,implementations={b:{} for b in BACKENDS})
    dump_new(root/'run.json',meta);dump_new(root/'workspace_queries.json',{str(n):resource(n) for n in sorted({c['recipe']['size'] for c in model[part]['cells']})})
    for i,cell in enumerate(model[part]['cells']):
        r=cell['recipe'];base=root/('data_'+cell['dataset_id']);base.mkdir()
        # Fixed zero bytes solely to exercise retained-file identity checks; not generated benchmark data.
        (base/'input.bin').write_bytes(bytes(4*r['size']))
        if part=='study':
            # Distinct synthetic seed tags, not generator-v1 samples or measured outputs.
            with (base/'input.bin').open('r+b') as f:f.write(int(r['seed']).to_bytes(8,'little'))
        input_hash=sha(base/'input.bin')
        if part=='study':dump_new(base/'input.json',dict({k:v for k,v in r.items() if k!='key_type'},input_hash_fnv1a64='1'))
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
    dump_new(root/'COMPLETE.json',dict(complete=True,**(dict(measured=dict(successful=1200,failed=0,interrupted=0,missing=0),
        warmups=dict(successful=240,failed=0,interrupted=0,missing=0)) if part=='study' else {})))
    if part=='study':
        for source in [MATRIX,FREEZE,ROOT/'docs/CPU_GPU_COMPARISON_PROTOCOL_v1.md']:
            shutil.copyfile(source,root/source.name)
        seal_fixture(root)

def seal_fixture(root):
    (root/'RAW_SHA256.json').write_text(json.dumps({str(p.relative_to(root)):sha(p)
        for p in root.rglob('*') if p.is_file() and p!=root/'RAW_SHA256.json'}))

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

class StudyAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary=tempfile.TemporaryDirectory();cls.template=Path(cls.temporary.name)/'template';fixture(cls.template,'study')
    @classmethod
    def tearDownClass(cls):cls.temporary.cleanup()
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)/'raw';shutil.copytree(self.template,self.root)
        self.model=load_protocol();self.cells=self.model['study']['cells']
        self.first=self.root/('data_'+self.cells[0]['dataset_id'])/'measurements'
    def tearDown(self):self.temp.cleanup()
    def analyze(self,**kwargs):return analyze(self.root,allow_synthetic=True,**kwargs)
    def edit(self,path,operation):
        with path.open(newline='') as f:reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
        operation(rows);write_table(path,fields,rows);seal_fixture(self.root)
    def unseal(self):
        (self.root/'COMPLETE.json').unlink();(self.first/'COMPLETE.json').unlink()
    def test_full_counts_statistics_hierarchy_and_regeneration(self):
        report=self.analyze();self.assertTrue(report['complete']);self.assertEqual(report['matrix_part'],'study')
        self.assertEqual(report['measured'],dict(successful=1200,failed=0,interrupted=0,missing=0))
        self.assertEqual(report['warmups'],dict(successful=240,failed=0,interrupted=0,missing=0))
        self.assertEqual(len(report['groups']),240);self.assertEqual(len(report['paired_host_call_ratios']),144)
        self.assertEqual(len(report['cross_dataset']),144);self.assertEqual(len(report['cross_dataset_paired_ratios']),54)
        self.assertTrue(all(r['ratio']==1 and r['denominator']=='gpu_cub_adapter' for r in report['paired_host_call_ratios']))
        for g in report['cross_dataset']:
            self.assertEqual(g['distinct_inputs'],1 if g['distribution']=='signed_edges' else 3)
            self.assertEqual(g['statistics']['median_ns'],300)
        s=report['groups'][0]['metrics']['host_call_e2e_ns'];self.assertAlmostEqual(s['stdev_ns'],158.11388300841898)
        self.assertEqual(canonical(report),canonical(self.analyze()))
    def test_public_cli_rejects_synthetic_full_results(self):
        with self.assertRaises(ValueError):analyze(self.root)
    def test_missing_dataset_and_no_partial_ratios_or_cross_summary(self):
        (self.root/'COMPLETE.json').unlink();shutil.rmtree(self.root/('data_'+self.cells[-1]['dataset_id']))
        with self.assertRaises(ValueError):self.analyze()
        report=self.analyze(allow_incomplete=True);self.assertEqual(report['measured']['missing'],25)
        self.assertEqual(report['warmups']['missing'],5)
        self.assertEqual(report['paired_host_call_ratios'],[]);self.assertEqual(report['cross_dataset'],[])
    def test_failed_measured_trial_retained(self):
        self.unseal();self.edit(self.first/'primary.csv',lambda rows:rows[-1].update(status='error',correctness='failed',error='wrong output',elapsed_ns=''))
        with self.assertRaises(ValueError):self.analyze()
        self.assertEqual(self.analyze(allow_incomplete=True)['measured']['failed'],1)
    def test_interrupted_trial_and_root_interruption(self):
        self.unseal();self.edit(self.first/'primary.csv',lambda rows:rows.pop())
        dump_new(self.root/'INTERRUPTED.json',dict(complete=False))
        report=self.analyze(allow_incomplete=True);self.assertFalse(report['complete']);self.assertEqual(report['measured']['interrupted'],1)
    def test_missing_unattempted_trial(self):
        self.unseal()
        with (self.first/'primary.csv').open() as f:rows=list(csv.DictReader(f))
        order=int(rows[-1]['execution_order'])
        # Trim the complete tail from attempts and both CSV families, preserving their prefix.
        attempts=[json.loads(line) for line in (self.first/'attempts.jsonl').read_text().splitlines()]
        (self.first/'attempts.jsonl').write_text(''.join(json.dumps(a)+'\n' for a in attempts if a['execution_order']<order))
        self.edit(self.first/'primary.csv',lambda rows:rows.__setitem__(slice(None),[r for r in rows if int(r['execution_order'])<order]))
        self.edit(self.first/'prepared_order.csv',lambda rows:rows.__setitem__(slice(None),[r for r in rows if int(r['execution_order'])<order]))
        with (self.first/'prepared_order.csv').open() as f:sides=list(csv.DictReader(f))
        self.edit(self.first/'prepared/trials.csv',lambda rows:rows.__setitem__(slice(len(sides),None),[]))
        self.assertGreater(self.analyze(allow_incomplete=True)['measured']['missing'],0)
    def test_duplicate_primary_and_attempt_identity(self):
        self.edit(self.first/'primary.csv',lambda rows:rows.append(dict(rows[0])))
        with self.assertRaises(ValueError):self.analyze()
    def test_duplicate_attempt(self):
        p=self.first/'attempts.jsonl';lines=p.read_text().splitlines();p.write_text('\n'.join(lines+[lines[-1]])+'\n');seal_fixture(self.root)
        with self.assertRaises(ValueError):self.analyze()
    def test_primary_schema_and_nonfinite_duration(self):
        self.edit(self.first/'primary.csv',lambda rows:rows[0].update(elapsed_ns='NaN'))
        with self.assertRaises(ValueError):self.analyze()
    def test_identity_scope_and_threads(self):
        for key,value in [('input_sha256','0'*64),('dataset_id','wrong'),('scope','device_sort'),('elapsed_unit','us'),
                          ('global_trial_index','9999'),('trial_index','7'),('actual_cpu_threads','8')]:
            with self.subTest(key=key):
                original=(self.first/'primary.csv').read_bytes()
                self.edit(self.first/'primary.csv',lambda rows:next(r for r in rows if r['backend_id']=='cpu_parallel_merge_sort_t2').update({key:value}))
                with self.assertRaises(ValueError):self.analyze()
                (self.first/'primary.csv').write_bytes(original)
        seal_fixture(self.root)
    def test_prepared_cannot_replace_production_primary(self):
        self.edit(self.first/'primary.csv',lambda rows:next(r for r in rows if r['backend_id']=='gpu_cub_adapter').update(backend_id='gpu_cub_prepared'))
        with self.assertRaises(ValueError):self.analyze()
    def test_prepared_metrics_never_supply_ratio_denominator(self):
        for cell in self.cells:
            path=self.root/('data_'+cell['dataset_id'])/'measurements/prepared/trials.csv'
            with path.open(newline='') as f:rows=list(csv.DictReader(f))
            for row in rows:row.update(h2d_ns='1',device_sort_ns='1',d2h_ns='1',end_to_end_ns='1')
            write_table(path,PREPARED_FIELDS,rows)
        seal_fixture(self.root);report=self.analyze()
        self.assertTrue(all(r['ratio']==1 for r in report['paired_host_call_ratios']))
    def test_prepared_sidecar_and_malformed_metrics(self):
        self.edit(self.first/'prepared_order.csv',lambda rows:rows[0].update(backend_id='gpu_cub_adapter'))
        with self.assertRaises(ValueError):self.analyze()
    def test_unexpected_dataset_and_matrix_identity(self):
        (self.root/'data_unexpected').mkdir()
        with self.assertRaises(ValueError):self.analyze()
    def test_workspace_missing_middle_size_and_limit(self):
        p=self.root/'workspace_queries.json';original=p.read_text();data=json.loads(original);data.pop('65537');p.write_text(json.dumps(data));seal_fixture(self.root)
        with self.assertRaises(ValueError):self.analyze()
        data=json.loads(original);data['65537']['adapter_query_bytes']=67108865;p.write_text(json.dumps(data));seal_fixture(self.root)
        with self.assertRaises(ValueError):self.analyze()
    def test_raw_hash_and_retained_freeze_tampering(self):
        p=self.first/'primary.csv';p.write_text(p.read_text()+'\n')
        with self.assertRaises(ValueError):self.analyze()
        seal_fixture(self.root);p=self.root/MATRIX.name;p.write_text('{}');seal_fixture(self.root)
        with self.assertRaises(ValueError):self.analyze()
    def test_duplicate_json_keys_and_wrong_freeze_identity(self):
        p=self.root/'run.json';original=p.read_text();p.write_text(original.rstrip()[:-1]+',"matrix_part":"study"}')
        with self.assertRaises(ValueError):self.analyze()
        data=json.loads(original);data['freeze_sha256']='0'*64;p.write_text(json.dumps(data));seal_fixture(self.root)
        with self.assertRaises(ValueError):self.analyze()
    def test_false_dataset_completion_and_contradictory_markers(self):
        dump_new(self.first/'FAILED.json',dict(complete=False));seal_fixture(self.root)
        with self.assertRaises(ValueError):self.analyze()
    def test_root_counts_and_input_recipe_must_match(self):
        p=self.root/'COMPLETE.json';original=p.read_text();data=json.loads(original);data['measured']['successful']=1199
        p.write_text(json.dumps(data));seal_fixture(self.root)
        with self.assertRaises(ValueError):self.analyze()
        p.write_text(original);p=self.first.parent/'input.json';data=json.loads(p.read_text());data['seed']=999;p.write_text(json.dumps(data));seal_fixture(self.root)
        with self.assertRaises(ValueError):self.analyze()
    def test_performance_metadata_envelope_and_invalid_builds(self):
        from analyze_cpu_gpu import validate_study_metadata
        meta=json.loads((self.root/'run.json').read_text());meta['run_kind']='performance'
        meta['implementations']={b:dict(source_review='source_review.json',build='build.json',
            cub_pin=self.model['dependency'] if b.startswith('gpu_') else None) for b in BACKENDS}
        source={'current_source_sha256':{'explicit_synthetic_source':'0'*64}}
        (self.root/'source_review.json').write_text(json.dumps(source));(self.root/'compile_commands.json').write_text('[]')
        description=dict(build_type='Release',sanitizers=False,cub_version=300001,cuda_architectures='75',cxx_standard=17,
                         global_flags='',cuda_flags='',configuration_flags='-O3 -DNDEBUG',cuda_release_flags='-O3 -DNDEBUG')
        build=dict(description=description,binary_sha256='1'*64,input_tool_sha256='2'*64,
                   compile_commands_sha256=sha(self.root/'compile_commands.json'),source_review_sha256=sha(self.root/'source_review.json'))
        environment=dict(omp_environment=self.model['openmp_policy']['environment'])
        (self.root/'environment.json').write_text(json.dumps(environment))
        records={}
        for name in ['cpu_release_ctest','cpu_sanitize_ctest','cuda_ctest','cuda_correctness','preflight']:
            relative='commands/'+name+'.json';p=self.root/'prerequisite_commands'/relative;p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text(json.dumps(dict(exit_code=0,status='completed',fixture='synthetic command only')))
            records[name]=dict(file=relative,sha256=sha(p))
        prerequisite=dict(complete=True,protocol=PROTOCOL,records=records,source_sha256=source['current_source_sha256'],
                          binary_sha256='1'*64,input_tool_sha256='2'*64)
        (self.root/'prerequisites.json').write_text(json.dumps(prerequisite))
        with mock.patch('run_cpu_gpu_pilot.environment_gate'):
            (self.root/'build.json').write_text(json.dumps(build));validate_study_metadata(self.root,meta,self.model)
            for key,value in [('cub_version',300000),('sanitizers',True),('cuda_architectures','80'),
                              ('configuration_flags','-O0'),('build_type','Debug')]:
                bad=copy.deepcopy(build);bad['description'][key]=value;(self.root/'build.json').write_text(json.dumps(bad))
                with self.subTest(key=key),self.assertRaises(ValueError):validate_study_metadata(self.root,meta,self.model)
            (self.root/'build.json').write_text(json.dumps(build))
            p=self.root/'prerequisite_commands/commands/cuda_correctness.json';p.write_text('{}')
            with self.assertRaises(ValueError):validate_study_metadata(self.root,meta,self.model)
    def test_full_plan_determinism_and_explicit_execution_latch(self):
        command=[sys.executable,str(ROOT/'scripts/run_cpu_gpu_study.py'),'--executable','unused','--input-tool','unused','--output',str(self.root),'--dry-run']
        a=subprocess.run(command,capture_output=True,text=True);b=subprocess.run(command,capture_output=True,text=True)
        self.assertEqual(a.returncode,0,a.stderr);self.assertEqual(a.stdout,b.stdout)
        plan=json.loads(a.stdout);self.assertEqual(plan['part'],'study');self.assertEqual(len(plan['commands']),48)
        self.assertEqual(plan['expected']['total_invocations'],1440)
        for i,cell in enumerate(self.cells):
            argv=plan['commands'][i]['worker'];self.assertEqual(argv[argv.index('--global-offset')+1],str(i*30))
            self.assertEqual(argv[argv.index('--base-order')+1],','.join(cell['warmup_order'][0]))
        rejected=subprocess.run(command[:-1],capture_output=True,text=True);self.assertEqual(rejected.returncode,2)
        self.assertFalse((self.root/'FAILED.json').exists())

class StudyOrchestrationTests(unittest.TestCase):
    """Subprocesses below are mocks; no sorting or performance observations occur."""
    def setUp(self):
        import types
        self.temp=tempfile.TemporaryDirectory();self.base=Path(self.temp.name)
        self.args=types.SimpleNamespace(output=self.base/'output',executable=self.base/'worker',input_tool=self.base/'input',
                                       prerequisites=self.base/'prerequisites.json',dry_run=False)
        self.model=load_protocol();self.calls=[];self.failure=None
        self.build=self.base/'build';self.build.mkdir()
        (self.build/'compile_commands.json').write_text('[]');(self.build/'CMakeCache.txt').write_text('synthetic test cache')
        self.args.executable.write_text('synthetic worker, never executed');self.args.input_tool.write_text('synthetic input, never executed')
        self.description=dict(build_type='Release',sanitizers=False,cub_version=300001,global_flags='',configuration_flags='-O3 -DNDEBUG',
                              cuda_flags='',cuda_release_flags='-O3 -DNDEBUG',cuda_architectures='75',binary_dir=str(self.build))
    def tearDown(self):self.temp.cleanup()
    def invoke(self,directory,name,argv,timeout=600):
        self.calls.append((name,argv,timeout))
        if name=='describe':return dict(stdout=json.dumps(self.description))
        if name.startswith('resources_'):return dict(stdout=json.dumps(resource(int(argv[-1]))))
        if name.startswith('input_'):
            cell=self.model['study']['cells'][int(name.split('_')[1])];r=cell['recipe']
            destination=Path(argv[argv.index('--output')+1]);destination.mkdir()
            (destination/'input.bin').write_bytes(bytes(r['size']*4))
            dump_new(destination/'input.json',dict({k:v for k,v in r.items() if k!='key_type'},input_hash_fnv1a64='1'))
        if name.startswith('dataset_') and self.failure:raise self.failure
        return dict(stdout='')
    def execute(self):
        import run_cpu_gpu_pilot as runner
        print('SYNTHETIC ORCHESTRATION MOCK: no sorting or timing call executed')
        def report(*args,**kwargs):
            complete=not self.failure
            return dict(complete=complete,measured=dict(successful=1200 if complete else 0,failed=0,interrupted=0,missing=0 if complete else 1200),
                        warmups=dict(successful=240 if complete else 0,failed=0,interrupted=0,missing=0 if complete else 240))
        with mock.patch.object(runner,'validate_prerequisites',return_value={'explicit_fixture':True}),\
             mock.patch.object(runner,'snapshot',return_value={'explicit_fixture':'not hardware metadata'}),\
             mock.patch.object(runner,'environment_gate'),mock.patch.object(runner,'invoke',side_effect=self.invoke),\
             mock.patch.object(runner,'analyze',side_effect=report):
            return runner.run(self.args,part='study')
    def test_all_48_worker_commands_and_3_resource_sizes(self):
        self.assertEqual(self.execute(),0)
        workers=[call for call in self.calls if call[0].startswith('dataset_')]
        self.assertEqual(len(workers),48)
        self.assertEqual([call[0] for call in self.calls if call[0].startswith('resources_')],['resources_1025','resources_65537','resources_1000000'])
        for i,(_,argv,timeout) in enumerate(workers):
            self.assertEqual(argv[argv.index('--global-offset')+1],str(i*30));self.assertGreater(timeout,0);self.assertLessEqual(timeout,60)
        plan=json.loads((self.args.output/'plan.json').read_text())
        self.assertEqual(len(plan['trials']),1440);self.assertEqual([r['global_trial_index'] for r in plan['trials']],list(range(1440)))
        self.assertEqual(json.loads((self.args.output/'run.json').read_text())['matrix_part'],'study')
        self.assertTrue((self.args.output/'RAW_SHA256.json').exists())
    def test_failure_stops_and_preserves_plan_and_partial_accounting(self):
        self.failure=RuntimeError('explicit injected worker failure');self.assertEqual(self.execute(),1)
        self.assertEqual(len([c for c in self.calls if c[0].startswith('dataset_')]),1)
        self.assertTrue((self.args.output/'FAILED.json').exists());self.assertFalse((self.args.output/'COMPLETE.json').exists())
        self.assertTrue((self.args.output/'PARTIAL_ANALYSIS.json').exists())
    def test_interrupt_stops_without_completion(self):
        self.failure=KeyboardInterrupt();self.assertEqual(self.execute(),130)
        self.assertTrue((self.args.output/'INTERRUPTED.json').exists());self.assertFalse((self.args.output/'COMPLETE.json').exists())
    def test_output_collision_and_no_resume(self):
        self.args.output.mkdir();(self.args.output/'user_file').write_text('preserve')
        with self.assertRaises(FileExistsError):self.execute()
        self.assertEqual((self.args.output/'user_file').read_text(),'preserve');self.assertEqual(self.calls,[])
    def test_study_deadline_stops_before_worker(self):
        with mock.patch('run_cpu_gpu_pilot.time.monotonic',side_effect=[0,1801,1801]):
            self.assertEqual(self.execute(),1)
        self.assertFalse(any(c[0].startswith('dataset_') for c in self.calls))
        self.assertTrue((self.args.output/'FAILED.json').exists())
    def test_prerequisites_only_parser_does_not_require_pilot_outputs(self):
        import validate_cpu_gpu_pilot as validator
        checkout=self.base/'checkout';checkout.mkdir()
        argv=['validator','--output',str(checkout/'validation'),'--prerequisites-only']
        with mock.patch.object(validator,'ROOT',checkout),mock.patch.object(validator,'verify_source_extension',return_value={}),\
             mock.patch.object(validator,'invoke',side_effect=RuntimeError('synthetic stop before preflight')),mock.patch.object(sys,'argv',argv):
            self.assertEqual(validator.main(),1)
        self.assertEqual(json.loads((checkout/'validation/FAILED.json').read_text())['error'],'synthetic stop before preflight')
    def test_prerequisites_only_success_never_calls_pilot(self):
        import validate_cpu_gpu_pilot as validator
        checkout=self.base/'checkout';checkout.mkdir();output=checkout/'validation';calls=[]
        include=checkout/'synthetic_headers';(include/'cub').mkdir(parents=True);(include/'cub/fake.cuh').write_text('synthetic')
        def invoke(directory,name,argv,timeout):
            calls.append(name);text=''
            if name=='preflight':
                p=output/'preflight';p.mkdir();dump_new(p/'report.json',dict(classification=dict(device0_kernel_verified=True,state='operational'),
                    runtime_probe=dict(devices=[dict(ordinal=0,name='Tesla T4',compute_major=7,compute_minor=5)])))
            if name=='cuda_configure':
                gpu=checkout/'build/validation/gpu-release';gpu.mkdir()
                (gpu/'CMakeCache.txt').write_text('MAB_CUB_INCLUDE_DIR:PATH='+str(include))
                for executable in ['cpu_gpu_comparison','comparison_input']:(gpu/executable).write_text('synthetic binary, never executed')
            if name in ['cpu_release_ctest','cpu_sanitize_ctest']:text='0 tests failed out of 29'
            if name=='cuda_ctest':text='0 tests failed out of 32\nRan 14 tests'
            if name=='cuda_correctness':text='{}'
            result=dict(exit_code=0,status='completed',stdout=text,stderr='',fixture='synthetic mocked validation, not hardware evidence')
            dump_new(directory/(name+'.json'),result);return result
        argv=['validator','--output',str(output),'--prerequisites-only']
        with mock.patch.object(validator,'ROOT',checkout),mock.patch.object(validator,'verify_source_extension',return_value={'current_source_sha256':{}}),\
             mock.patch.object(validator,'invoke',side_effect=invoke),mock.patch.object(validator,'verify_result',return_value={'fixture':True}),mock.patch.object(sys,'argv',argv):
            self.assertEqual(validator.main(),0)
        self.assertNotIn('pilot',calls);self.assertNotIn('analyze',calls)
        self.assertTrue((output/'PREREQUISITES.json').exists())
        self.assertFalse(json.loads((output/'COMPLETE.json').read_text())['pilot_run'])

if __name__=='__main__':unittest.main()
