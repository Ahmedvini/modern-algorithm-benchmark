#!/usr/bin/env python3
import copy
import csv
import json
import io
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from analyze_parallel_results import read_bundle,analyze,write_analysis,stats
from run_parallel_matrix import preset,make_plan,validate_config,forecast
from experiment_model import tree_hashes,load_json,save_json
BINARY=Path(sys.argv[1]).resolve();sys.argv=sys.argv[:1]
ENV=dict(os.environ,OMP_DYNAMIC='FALSE',OMP_THREAD_LIMIT='8',OMP_WAIT_POLICY='PASSIVE')

class ParallelFramework(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.base=Path(cls.tmp.name)
        cls.config=preset('smoke');cls.config.update(profile='custom',sizes=[0,32768],seeds=[1729],distributions=['uniform'],threads=[1,2],repetitions=2,validation_only=True)
        cls.raw=cls.base/'raw';cls.processed=cls.base/'processed';cls.figures=cls.base/'figures'
        cls.config_path=cls.base/'config.json';save_json(cls.config_path,cls.config)
        cls.command=[sys.executable,str(ROOT/'scripts/run_parallel_matrix.py'),'--binary',str(BINARY),'--config',str(cls.config_path),'--output',str(cls.raw),'--processed',str(cls.processed),'--figures',str(cls.figures)]
        r=subprocess.run(cls.command,capture_output=True,text=True,env=ENV)
        if r.returncode:raise AssertionError(r.stderr)
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()
    def setUp(self):self.temp=tempfile.TemporaryDirectory();self.work=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()
    def cli(self,*args):
        return subprocess.run([str(BINARY),'--output',str(self.work/'run'),'--validation-only',*map(str,args)],capture_output=True,text=True,env=ENV)
    def test_config_and_dry_run(self):
        a=subprocess.run([*self.command,'--dry-run'],capture_output=True,text=True);b=subprocess.run([*self.command,'--dry-run'],capture_output=True,text=True)
        self.assertEqual(a.returncode,0);self.assertEqual(a.stdout,b.stdout)
        plan=json.loads(a.stdout);self.assertEqual(len(plan['cases']),4);self.assertEqual(plan['configuration'],self.config)
        c=copy.deepcopy(self.config);c['threads']=[1,4]
        self.assertNotEqual(make_plan(c,BINARY,self.raw,self.processed,self.figures)['configuration_sha256'],plan['configuration_sha256'])
    def test_invalid_config(self):
        for key,value in [('repetitions',0),('warmups',-1),('seeds',[2**64]),('threads',[2]),('threads',[1,3]),('threads',[1,1]),('sizes',[1000001]),('sizes',[True]),('protocol','wrong'),('distinct',0),('profile','full')]:
            c=copy.deepcopy(self.config);c[key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):validate_config(c)
        c=copy.deepcopy(self.config);c['extra']=1
        with self.assertRaises(ValueError):validate_config(c)
    def test_cli_invalid_and_registry(self):
        for args in [('--threads','0'),('--threads','65'),('--threads','-1'),('--threads','+2'),('--threads','2.5'),('--threads','18446744073709551616'),('--sort','unknown'),('--sort','merge_sort,merge_sort'),('--repetitions','0'),('--seed','-1')]:
            with self.subTest(args=args):self.assertEqual(self.cli(*args).returncode,1)
        r=subprocess.run([str(BINARY),'--list-sorts'],capture_output=True,text=True);self.assertEqual(r.stdout.splitlines(),['merge_sort','parallel_merge_sort'])
        r=self.cli('--sort','all','--threads','4','--size','32768','--repetitions','1','--warmups','0');self.assertEqual(r.returncode,0,r.stderr)
        m,rows,_,done=read_bundle(self.work/'run');self.assertTrue(done);self.assertEqual(m['parallel_threads'],4)
        self.assertEqual({(r['algorithm'],r['requested_threads'],r['actual_threads']) for r in rows},{('merge_sort','1','1'),('parallel_merge_sort','4','4')})
    def test_actual_contracted_team(self):
        env=dict(ENV,OMP_THREAD_LIMIT='2');command=[str(BINARY),'--output',str(self.work/'contracted'),'--validation-only','--sort','all','--size','32768','--threads','8','--repetitions','1','--warmups','0']
        r=subprocess.run(command,capture_output=True,text=True,env=env);self.assertEqual(r.returncode,0,r.stderr)
        _,rows,_,_=read_bundle(self.work/'contracted');par=next(r for r in rows if r['algorithm']=='parallel_merge_sort')
        self.assertEqual((par['requested_threads'],par['actual_threads']),('8','2'))
    def test_schema_and_reproducibility(self):
        summary,rows=analyze(self.raw);self.assertTrue(summary['complete']);self.assertEqual((summary['successful_measured'],summary['warmup_rows']),(16,8))
        self.assertEqual((summary['failed_measured'],summary['missing_measured']),(0,0));self.assertEqual(len(rows),24)
        eligible=[r for r in summary['dataset_ratios'] if r['size']==32768];self.assertEqual(len(eligible),2)
        for row in eligible:self.assertIsNotNone(row['algorithmic_speedup'])
        for row in summary['dataset_ratios']:
            if row['size']==0:self.assertIsNone(row['algorithmic_speedup'])
    def test_malformed_duplicate_and_team(self):
        for field,value in [('protocol','wrong'),('elapsed_ns','nan'),('actual_threads','99'),('implementation_version','wrong'),('trial_index','999')]:
            target=self.work/field;shutil.copytree(self.raw/'run_000002',target)
            path=target/'trials.csv';rows=list(csv.DictReader(io.StringIO(path.read_text())));fields=list(rows[0]);rows[0][field]=value
            with path.open('w',newline='') as f:w=csv.DictWriter(f,fields);w.writeheader();w.writerows(rows)
            with self.subTest(field=field),self.assertRaises(ValueError):read_bundle(target)
        target=self.work/'duplicate';shutil.copytree(self.raw/'run_000002',target);path=target/'trials.csv';lines=path.read_text().splitlines();path.write_text('\n'.join(lines+[lines[1]])+'\n')
        with self.assertRaises(ValueError):read_bundle(target)
    def test_hand_checked_statistics_and_baselines(self):
        self.assertEqual(stats([10,20,30]),dict(count=3,median=20,mean=20,sample_stdev=10.0,minimum=10,maximum=30))
        self.assertIsNone(stats([1])['sample_stdev'])
        # Independent fake timing observations on copied actual schema, never study evidence.
        raw=self.work/'synthetic';shutil.copytree(self.raw,raw)
        plan=load_json(raw/'matrix.json');plan=make_plan(plan['configuration'],BINARY,raw,self.work/'derived',self.work/'figures')
        (raw/'matrix.json').write_text(json.dumps(plan));(raw/'COMPLETE.json').unlink()
        for name,command in zip(plan['runs'],plan['commands']):
            path=raw/name/'run.json';m=load_json(path);m['run_id']=raw.name+':'+name;m['invocation']=command;path.write_text(json.dumps(m))
            path=raw/(name+'_command.json');r=load_json(path);r['command']=command;path.write_text(json.dumps(r))
            path=raw/name/'trials.csv';rows=list(csv.DictReader(io.StringIO(path.read_text())));fields=list(rows[0])
            for row in rows:
                row['run_id']=m['run_id'];row['elapsed_ns']=str(100 if row['algorithm']=='merge_sort' else 80 if m['parallel_threads']==1 else 40)
            with path.open('w',newline='') as f:w=csv.DictWriter(f,fields);w.writeheader();w.writerows(rows)
        s,_=analyze(raw);row=next(r for r in s['dataset_ratios'] if r['size']==32768 and r['threads']==2)
        self.assertEqual((row['algorithmic_speedup'],row['parallel_one_thread_speedup'],row['algorithmic_efficiency']),(2.5,2,1.25))
    def test_partial_missing_and_failed_command(self):
        raw=self.work/'partial';shutil.copytree(self.raw,raw);(raw/'COMPLETE.json').unlink();(raw/'COLLECTED.json').unlink()
        # Missing output is modeled with a compatible absolute plan and existing metadata adjusted.
        plan=make_plan(self.config,BINARY,raw,self.work/'processed',self.work/'figures');(raw/'matrix.json').write_text(json.dumps(plan))
        for name in plan['runs']:shutil.rmtree(raw/name);(raw/(name+'_command.json')).unlink()
        with self.assertRaises(ValueError):analyze(raw)
        s,_=analyze(raw,True);self.assertFalse(s['complete']);self.assertEqual(s['missing_measured'],16);self.assertEqual(len(s['missing_configurations']),4)
        self.assertTrue(all(c['status']=='missing' for c in s['commands']))
    def test_output_safety(self):
        before=tree_hashes(self.raw);r=subprocess.run(self.command,capture_output=True,text=True,env=ENV)
        self.assertNotEqual(r.returncode,0);self.assertEqual(before,tree_hashes(self.raw))
        with self.assertRaises(FileExistsError):write_analysis(self.raw,self.processed,self.figures)
        with self.assertRaises(ValueError):make_plan(self.config,BINARY,self.raw,self.raw/'nested',self.figures)
    def test_summary_plot_report_regeneration(self):
        before=tree_hashes(self.raw);write_analysis(self.raw,self.work/'processed',self.work/'figures')
        self.assertEqual(tree_hashes(self.processed),tree_hashes(self.work/'processed'))
        self.assertEqual(tree_hashes(self.figures),tree_hashes(self.work/'figures'));self.assertEqual(tree_hashes(self.raw),before)
        m=load_json(self.figures/'plot_manifest.json');self.assertEqual(len(m['figures']),4)
        self.assertEqual(m['summary_sha256'],__import__('hashlib').sha256((self.processed/'summary.json').read_bytes()).hexdigest())
    def test_failed_subprocess_retained(self):
        stub=self.work/'stub';stub.write_text('#!/usr/bin/env python3\nimport sys\nif "--list-sorts" in sys.argv: print("merge_sort\\nparallel_merge_sort")\nelse: sys.exit(9)\n');stub.chmod(0o755)
        shutil.copyfile(BINARY.parent/'CMakeCache.txt',self.work/'CMakeCache.txt')
        config=copy.deepcopy(self.config);config.update(sizes=[1],threads=[1]);path=self.work/'c.json';save_json(path,config)
        raw=self.work/'failed';command=[sys.executable,str(ROOT/'scripts/run_parallel_matrix.py'),'--binary',str(stub),'--config',str(path),'--output',str(raw),'--processed',str(self.work/'p'),'--figures',str(self.work/'f')]
        r=subprocess.run(command,capture_output=True,text=True,env=ENV);self.assertEqual(r.returncode,1,r.stderr)
        self.assertTrue((raw/'FAILED.json').exists());self.assertFalse((raw/'COMPLETE.json').exists())
        self.assertEqual(load_json(raw/'run_000000_command.json')['exit_code'],9)
        s,_=analyze(raw,True);self.assertFalse(s['complete']);self.assertEqual(s['missing_measured'],4)
        self.assertEqual(s['commands'][0]['status'],'failed')

    def test_forecast(self):
        f=forecast(self.raw,self.config);self.assertAlmostEqual(f['forecast_seconds'],f['pilot_wall_seconds']*4)
        self.assertTrue(f['runtime_gate_passed'])

    def test_all_distributions_sorted_swap_metadata(self):
        config=copy.deepcopy(self.config)
        config.update(sizes=[100],threads=[1],distributions=preset('full')['distributions'],repetitions=1,warmups=0)
        path=self.work/'all.json';save_json(path,config)
        raw=self.work/'all';processed=self.work/'p';figures=self.work/'f'
        command=[sys.executable,str(ROOT/'scripts/run_parallel_matrix.py'),'--binary',str(BINARY),'--config',str(path),'--output',str(raw),'--processed',str(processed),'--figures',str(figures)]
        r=subprocess.run(command,capture_output=True,text=True,env=ENV);self.assertEqual(r.returncode,0,r.stderr)
        summary,rows=analyze(raw);self.assertTrue(summary['complete']);self.assertEqual(summary['successful_measured'],10)
        self.assertEqual({(r['raw']['distribution'],r['raw']['nearly_sorted_swaps']) for r in rows},
                         {(d,'0' if d=='sorted' else '1') for d in config['distributions']})

if __name__=='__main__':unittest.main()
