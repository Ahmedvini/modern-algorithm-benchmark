#!/usr/bin/env python3
"""Fast, deterministic orchestration/analysis/plot integration and negative tests."""
import copy
import csv
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from contextlib import contextmanager

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import experiment_model as model
import run_experiments as runner
import analyze_experiment as analysis
import plot_results
import assess_experiment

BUILD=Path(sys.argv.pop(1)).resolve() if len(sys.argv)>1 else ROOT/'build/release'


@contextmanager
def altered(path, data=None):
    original=path.read_bytes()
    if data is None:path.unlink()
    else:path.write_bytes(data)
    try:yield
    finally:path.write_bytes(original)


class Experiments(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.base=Path(cls.temp.name)
        for p in ['raw','processed','figures']:(cls.base/p).mkdir()
        cls.config=model.preset('smoke');cls.config.update(profile='custom',sizes=[0,8],seeds=[0,1],
            distributions=['uniform'],queries=4,repetitions=3,warmups=1,categories=['hit_first','mixed_50','miss_empty'],validation_only=True)
        cls.study=model.plan(cls.config,'fixture',cls.base/'raw',cls.base/'processed',cls.base/'figures',BUILD)
        cls.raw=Path(cls.study['raw_path']);cls.raw.mkdir()
        model.save_json(cls.raw/'experiment.json',cls.study)
        for entry in cls.study['families']:
            record=runner.run_child(entry['command']);model.save_json(cls.raw/(entry['family']+'_command.json'),record)
            if record['exit_code']!=0:raise RuntimeError(record['stderr'])
        validated=model.validate_study(cls.raw)
        model.save_json(cls.raw/'COLLECTED.json',dict(protocol=model.PROTOCOL,complete=True,
            configuration_sha256=cls.study['configuration_sha256'],observations=len(validated['observations'])))
        # Retain synthetic timing fixtures ONLY in this temporary test directory.
        for family_entry in cls.study['families']:
            for child in family_entry['children']:
                bundle=cls.raw/family_entry['family']/child['name'];path=bundle/'trials.csv'
                with path.open(newline='') as f:r=csv.DictReader(f);fields=r.fieldnames;rows=list(r)
                for row in rows:
                    row['elapsed_ns']=str([10,20,30][int(row['trial_index'])]+(100 if child['seed']==1 else 0))
                with path.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def bundle(self,family='sorting',index=0):return self.raw/family/f'run_{index:06d}'

    def test_config_and_fingerprints(self):
        c=model.preset('full');model.validate_config(c)
        self.assertEqual(model.fingerprint(c),model.fingerprint(dict(reversed(list(c.items())))))
        self.assertEqual(model.load_json(self.raw/'experiment.json'),self.study)
        self.assertEqual(model.resources(c)['measured_row_upper_bounds'],dict(sorting=1800,search=8100,structures=15000))
        c['algorithms']['sorting'].pop();self.assertEqual(len(model.ALGORITHMS['sorting']),6)

    def test_runtime_forecast_model(self):
        c=copy.deepcopy(self.config)
        self.assertEqual(assess_experiment.forecast(c,c,safety_factor=1),dict.fromkeys(model.FAMILIES,1.0))
        self.assertEqual(assess_experiment.forecast(c,c),dict.fromkeys(model.FAMILIES,4.0))
        c["repetitions"]=7;c["warmups"]=1
        self.assertEqual(assess_experiment.forecast(self.config,c,safety_factor=1),dict.fromkeys(model.FAMILIES,2.0))
        with self.assertRaises(ValueError):assess_experiment.forecast(c,c,float("nan"))

    def test_invalid_configs_protocols(self):
        cases=[('sizes',[1000001]),('sizes',[True]),('sizes',[1,1]),('queries',3),('queries',0),('seeds',[-1]),
               ('repetitions',0),('warmups',1001),('distinct',0),('swaps',10000001),('protocol','future'),('memory_limit_mib',0)]
        for key,value in cases:
            c=copy.deepcopy(self.config);c[key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):model.validate_config(c)
        c=model.preset('smoke');c['sizes']=[1]
        with self.assertRaises(ValueError):model.validate_config(c)
        c=copy.deepcopy(self.config);c['unknown']=1
        with self.assertRaises(ValueError):model.validate_config(c)
        c=copy.deepcopy(self.config);c['algorithms']['sorting']=['invented']
        with self.assertRaises(ValueError):model.validate_config(c)

    def test_dry_run_stability_no_outputs(self):
        config=self.base/'config.json'
        if not config.exists():model.save_json(config,self.config)
        cmd=[sys.executable,str(ROOT/'scripts/run_experiments.py'),'--config',str(config),'--run-id','dry',
             '--raw-root',str(self.base/'raw'),'--processed-root',str(self.base/'processed'),'--figure-root',str(self.base/'figures'),'--build-dir',str(BUILD),'--dry-run']
        a=subprocess.run(cmd,capture_output=True);b=subprocess.run(cmd,capture_output=True)
        self.assertEqual(a.returncode,0,a.stderr);self.assertEqual(a.stdout,b.stdout)
        data=json.loads(a.stdout);self.assertEqual(len(data['families']),3)
        self.assertFalse((self.base/'raw/dry').exists());self.assertEqual(data['resources'],model.resources(self.config))
        self.assertEqual(data['families'][0]['children'][0]['command'],self.study['families'][0]['children'][0]['command'][:1]+[x.replace('/fixture/','/dry/') for x in self.study['families'][0]['children'][0]['command'][1:]])

    def test_json_duplicate_nonfinite(self):
        p=self.base/'invalid.json'
        for text in ['{"x":1,"x":2}','{"x":NaN}','{"x":Infinity}']:
            p.write_text(text)
            with self.assertRaises(ValueError):model.load_json(p)

    def test_public_workloads_traceability(self):
        v=model.validate_study(self.raw);self.assertTrue(v['complete'])
        identities=set()
        for o in v['observations']:
            key=(o['family'],o['run_id'],o['algorithm'],o['operation'],o['query_category'],o['phase'],o['trial_index'])
            self.assertNotIn(key,identities);identities.add(key)
            self.assertEqual(o['elapsed_unit'],'ns');self.assertTrue(Path(o['source_csv']).exists())
            self.assertEqual(o['elapsed_ns'],int(o['raw']['elapsed_ns']))
            if o['operation']=='lookup':self.assertEqual(o['batch_size'],4)
            else:self.assertIsNone(o['batch_size'])
        self.assertEqual(len(identities),len(v['observations']))

    def test_hand_checked_hierarchy(self):
        s=model.aggregate(model.validate_study(self.raw))
        g=next(g for g in s['per_dataset'] if g['family']=='sorting' and g['size']==8 and g['seed']==0)
        self.assertEqual(g['statistics'],dict(count=3,median=20,mean=20,sample_stdev=10,minimum=10,maximum=30))
        c=next(g for g in s['cross_dataset'] if g['family']=='sorting' and g['size']==8)
        self.assertEqual(c['statistics']['count'],2);self.assertEqual(c['statistics']['median'],70)
        self.assertAlmostEqual(c['statistics']['sample_stdev'],100/(2**0.5))
        empty=next(g for g in s['cross_dataset'] if g['family']=='sorting' and g['size']==0)
        self.assertEqual(empty['declared_datasets'],2);self.assertEqual(empty['distinct_input_datasets'],1)
        self.assertIsNone(empty['statistics']['sample_stdev'])
        self.assertEqual(model.stats([])['median'],None)
        self.assertIsNone(model.stats([10])['sample_stdev'])
        for bad in [[float('nan')],[-1],[True]]:
            with self.assertRaises(ValueError):model.stats(bad)

    def test_malformed_and_duplicate_trial(self):
        path=self.bundle()/'trials.csv';content=path.read_bytes();lines=content.splitlines(keepends=True)
        for changed in [content+lines[-1],content.replace(b',ns,',b',ms,',1),content.replace(b',10,ns,',b',-1,ns,',1),content.replace(b',sort_timing_v1,',b',future,',1)]:
            with altered(path,changed),self.assertRaises(ValueError):model.validate_study(self.raw)

    def test_extra_configuration_rejected(self):
        p=self.raw/"sorting/run_extra";p.mkdir()
        try:
            with self.assertRaises(ValueError):model.validate_study(self.raw)
        finally:p.rmdir()

    def test_mismatched_configuration(self):
        path=self.bundle()/'run.json';m=model.load_json(path);m['duplicate_cardinality']=99
        with altered(path,json.dumps(m).encode()),self.assertRaises(ValueError):model.validate_study(self.raw)

    def test_failed_and_missing_rows(self):
        bundle=self.bundle();path=bundle/'trials.csv'
        with path.open(newline='') as f:r=csv.DictReader(f);fields=r.fieldnames;rows=list(r)
        row=rows[0];row.update(status='error',correctness='not_checked',error='synthetic fault',elapsed_ns='')
        from io import StringIO
        f=StringIO();w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerow(row)
        with altered(path,f.getvalue().encode()),altered(bundle/'COMPLETE.json'),altered(self.raw/'sorting/COMPLETE.json'),altered(self.raw/'COLLECTED.json'):
            with self.assertRaises(ValueError):model.validate_study(self.raw)
            v=model.validate_study(self.raw,True);s=model.aggregate(v)
            self.assertFalse(s['complete']);self.assertEqual(s['counts']['sorting']['failed_warmups'],1)
            self.assertGreater(s['counts']['sorting']['missing_measured_known'],0)

    def test_missing_configuration_unknown_lookup_counts(self):
        bundle=self.bundle('search');moved=self.base/'moved_bundle';bundle.rename(moved)
        try:
            with altered(self.raw/'search/COMPLETE.json'),altered(self.raw/'COLLECTED.json'):
                s=model.aggregate(model.validate_study(self.raw,True))
                self.assertEqual(s['counts']['search']['missing_configurations'],1)
                self.assertGreater(s['counts']['search']['unknown_lookup_missing_upper_bound'],0)
                self.assertFalse(s['complete'])
        finally:moved.rename(bundle)

    def test_malformed_command_exit_and_completed_child_interruption(self):
        path=self.raw/'search_command.json';c=model.load_json(path)
        for code in [False,'0',1.5,9]:
            bad=dict(c,exit_code=code)
            with altered(path,json.dumps(bad).encode()),self.assertRaises(ValueError):model.validate_study(self.raw,True)
        interrupted=dict(c,status='interrupted',exit_code=0,stderr='Parent interrupted after child completed')
        with altered(path,json.dumps(interrupted).encode()),altered(self.raw/'COLLECTED.json'):
            v=model.validate_study(self.raw,True);self.assertFalse(v['complete'])
            self.assertEqual(v['commands'][1]['status'],'interrupted')

    def test_interrupted_command_context(self):
        path=self.raw/'search_command.json';c=model.load_json(path);c.update(status='interrupted',exit_code=-15)
        with altered(path,json.dumps(c).encode()),altered(self.raw/'COLLECTED.json'):
            v=model.validate_study(self.raw,True);s=model.aggregate(v)
            self.assertFalse(v['complete']);self.assertTrue(any(g['interrupted_context'] for g in s['per_dataset'] if g['family']=='search'))

    def test_subprocess_failures_and_signal(self):
        r=runner.run_child([sys.executable,'-c','import sys; print("diagnostic");sys.exit(9)'])
        self.assertEqual(r['exit_code'],9);self.assertEqual(r['status'],'failed');self.assertIn('diagnostic',r['stdout'])
        r=runner.run_child([sys.executable,'-c','import os,signal;os.kill(os.getpid(),signal.SIGTERM)'])
        self.assertEqual(r['status'],'interrupted');self.assertEqual(r['exit_code'],-15)
        r=runner.run_child([str(self.base/'missing_executable')]);self.assertIsNone(r['exit_code']);self.assertEqual(r['status'],'failed')

    def test_fatal_signal_is_failure_not_interruption(self):
        command=[sys.executable,"-c","import os,signal,resource;resource.setrlimit(resource.RLIMIT_CORE,(0,0));os.kill(os.getpid(),signal.SIGABRT)"]
        r=runner.run_child(command)
        self.assertEqual(r["exit_code"],-signal.SIGABRT);self.assertEqual(r["status"],"failed")

    def test_parent_interrupt_terminates_process_group(self):
        script=self.base/'interrupt.py'
        script.write_text('import sys,signal\nsys.path.insert(0,'+repr(str(ROOT/'scripts'))+')\nimport run_experiments as r,json\nsignal.signal(signal.SIGTERM,r.interrupted)\nprint("ready",flush=True)\nprint(json.dumps(r.run_child([sys.executable,"-c","import time;time.sleep(60)"])),flush=True)\n')
        p=subprocess.Popen([sys.executable,str(script)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        self.assertEqual(p.stdout.readline().strip(),'ready');time.sleep(0.15);p.send_signal(signal.SIGTERM)
        try:
            out,err=p.communicate(timeout=10)
        finally:
            if p.poll() is None:p.kill()
            if p.poll() is None:p.wait(timeout=5)
            p.stdout.close();p.stderr.close()
        self.assertEqual(p.returncode,0,err)
        self.assertEqual(json.loads(out)['status'],'interrupted')

    def test_output_safety_collision_symlink(self):
        with self.assertRaises(FileExistsError):runner.run(self.study)
        for ident in ['../escape','','/absolute','..']:
            with self.assertRaises(ValueError):model.safe_id(ident)
        with self.assertRaises(ValueError):model.plan(self.config,'id',self.base,self.base,self.base/'figures',BUILD)
        a=model.plan(self.config,'race',self.base/'raw',self.base/'processed',self.base/'figures',BUILD)
        raw=Path(a['raw_path']);raw.mkdir()
        with self.assertRaises(FileExistsError):runner.run(a)
        link=self.base/'raw/link';link.symlink_to(self.raw,target_is_directory=True)
        a=model.plan(self.config,'link',self.base/'raw',self.base/'processed',self.base/'figures',BUILD)
        with self.assertRaises(FileExistsError):runner.run(a)

    def test_concurrent_atomic_directory_ownership(self):
        target=self.base/'race_atomic'
        cmd=[sys.executable,'-c','from pathlib import Path;import sys;Path(sys.argv[1]).mkdir(exist_ok=False)',str(target)]
        a=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE);b=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        a.communicate();b.communicate();self.assertEqual(sorted([a.returncode,b.returncode]),[0,1])

    def test_raw_symlink_rejected(self):
        p=self.bundle()/'injected';p.symlink_to(self.base/'invalid.json')
        try:
            with self.assertRaises(ValueError):model.validate_study(self.raw)
        finally:p.unlink()

    def test_resource_gates(self):
        e=model.resources(self.config);snapshot=runner.resource_snapshot(self.base)
        good=copy.deepcopy(snapshot);good.update(available_memory_bytes=10**12,disk_free_bytes=10**12,cgroups=[])
        runner.check_resources(good,e)
        for k in ['available_memory_bytes','disk_free_bytes']:
            bad=copy.deepcopy(good);bad[k]=0
            with self.assertRaises(ValueError):runner.check_resources(bad,e)
        bad=copy.deepcopy(good);bad['cgroups']=[dict(headroom_bytes=1)]
        with self.assertRaises(ValueError):runner.check_resources(bad,e)

    def test_plots_report_summary_byte_regeneration(self):
        before=model.tree_hashes(self.raw)
        a=self.base/'derived_a';fa=self.base/'plots_a';b=self.base/'derived_b';fb=self.base/'plots_b'
        summary=analysis.analyze(self.raw,a,fa);analysis.analyze(self.raw,b,fb)
        self.assertEqual(model.tree_hashes(a),model.tree_hashes(b));self.assertEqual(model.tree_hashes(fa),model.tree_hashes(fb))
        self.assertEqual(before,model.tree_hashes(self.raw))
        manifest=model.load_json(fa/'plot_manifest.json');self.assertTrue(manifest['figures'])
        for plot in manifest['figures']:
            for name in plot['outputs'].values():self.assertTrue((fa/name).is_file());self.assertEqual(model.sha256(fa/name),manifest['output_sha256'][name])
            if plot['kind']!='completeness':
                for point in plot['points']:
                    self.assertLessEqual(point['lower'],point['center']);self.assertLessEqual(point['center'],point['upper'])
                    if point['size']==8 and plot['filters']['family']=='sorting':self.assertEqual(point['center'],70/1e6)
        self.assertEqual(len(manifest['unavailable_figures']),2)
        self.assertIn('not individual-query latency',(a/'REPORT.md').read_text())
        with self.assertRaises(FileExistsError):analysis.analyze(self.raw,a,fa)

    def test_failed_orchestrator_retains_output(self):
        # A stub implements registry probes but fails real execution, in a copied tiny cache directory.
        build=self.base/'stub_build';build.mkdir();(build/'CMakeCache.txt').write_text((BUILD/'CMakeCache.txt').read_text())
        for family,name in model.BINARIES.items():
            p=build/name;p.write_text('#!/usr/bin/env python3\nimport sys\nif any(x.startswith("--list-") for x in sys.argv):\n print('+repr('\n'.join(model.ALGORITHMS[family]))+')\nelse:\n sys.exit(9)\n');p.chmod(0o755)
        study=model.plan(self.config,'failed',self.base/'raw',self.base/'processed',self.base/'figures',build)
        with self.assertRaises(RuntimeError):runner.run(study)
        raw=Path(study['raw_path']);self.assertTrue((raw/'FAILED.json').exists());self.assertFalse((raw/'COMPLETE.json').exists())
        self.assertEqual(model.load_json(raw/'sorting_command.json')['status'],'failed')
        s=model.aggregate(model.validate_study(raw,True));self.assertFalse(s['complete']);self.assertGreater(s['counts']['sorting']['missing_configurations'],0)


if __name__=='__main__':unittest.main()
