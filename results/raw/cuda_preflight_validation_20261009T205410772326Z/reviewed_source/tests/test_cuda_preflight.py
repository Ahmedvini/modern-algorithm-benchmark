#!/usr/bin/env python3
"""Readiness tests use fake command results; only CUDA-OFF CMake checks are real."""
import contextlib
import copy
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import cuda_preflight as cuda


def result(stdout='',code=0):return dict(command=[],returncode=code,stdout=stdout,stderr='',status='completed')

def discovery(gpu=False):
    return dict(pci_scan_available=True,pci_gpus=[dict(pci_address='synthetic')] if gpu else [],pci_errors=[],
                driver_file=dict(available=False),tools=dict(nvcc=None,cmake='cmake',nvidia_smi=None,lspci=None),toolkit_files={},driver_library=None,runtime_library=None)

def runtime(status='ok',code=0,count=1,stage='complete'):
    return result(json.dumps(dict(schema_version=1,record_kind='cuda_runtime_probe',status=status,stage=stage,device_count=count,
                   kernel_result=1729,tested_device=0,cuda_error_code=0,devices=[dict(ordinal=i,name='synthetic') for i in range(count)])),code)


class ReadinessTests(unittest.TestCase):
    def setUp(self):self.found=discovery();self.probes=dict(nvidia_smi=result('',127),nvcc=result('',127),lspci=result('',127))
    def state(self):return cuda.classify(self.found,self.probes)['state']
    def test_no_gpu_detected(self):self.assertEqual(self.state(),'no_nvidia_gpu_detected')
    def test_gpu_driver_unavailable(self):
        self.found['pci_gpus']=[{'synthetic':True}];self.assertEqual(self.state(),'gpu_driver_unavailable')
    def test_driver_without_toolkit(self):
        self.probes['nvidia_smi']=result('0, Synthetic GPU, 999.00\n');self.assertEqual(self.state(),'driver_toolkit_unavailable')
    def test_toolkit_without_usable_device(self):
        self.probes.update(nvcc=result('NVIDIA nvcc'),configure=result(),build=result(),runtime=runtime('unavailable',77,0,'enumerate'))
        self.assertEqual(self.state(),'toolkit_no_usable_device')
    def test_operational_requires_kernel_not_version(self):
        self.probes['nvcc']=result('NVIDIA nvcc');self.assertEqual(self.state(),'toolchain_unverified')
        self.probes.update(configure=result(),build=result(),runtime=runtime());self.assertEqual(self.state(),'operational')
        self.assertTrue(cuda.classify(self.found,self.probes)['driver_operational_evidence'])
    def test_inconclusive_visibility(self):
        self.found['pci_scan_available']=False;self.assertEqual(self.state(),'detection_unavailable')
    def test_failed_kernel_is_not_ready(self):
        self.probes.update(nvcc=result(),configure=result(),build=result(),runtime=runtime('error',1,1,'synchronize'))
        self.assertEqual(self.state(),'toolkit_no_usable_device')
    def test_broken_driver_with_toolkit_evidence_retained(self):
        self.found['pci_gpus']=[{}];self.probes.update(nvcc=result(),configure=result(),build=result(),runtime=runtime('unavailable',77,0,'enumerate'))
        c=cuda.classify(self.found,self.probes);self.assertEqual(c['state'],'gpu_driver_unavailable');self.assertTrue(c['project_cuda_target_built'])
    def test_driver_file_alone_does_not_prove_operational(self):
        self.found['driver_file']=dict(available=True,text='kernel module version');self.assertEqual(self.state(),'no_nvidia_gpu_detected')
    def test_lspci_gpu_evidence_excludes_audio(self):
        self.probes['lspci']=result('Audio device: NVIDIA');self.assertEqual(self.state(),'no_nvidia_gpu_detected')
        self.probes['lspci']=result('3D controller: NVIDIA Synthetic');self.assertEqual(self.state(),'gpu_driver_unavailable')
    def test_csv_gpu_name_escaping(self):
        self.assertEqual(cuda.gpu_rows(result('0,"Synthetic, GPU",999\n'))[0]['model'],'Synthetic, GPU')
        self.assertEqual(cuda.gpu_rows(result('NVIDIA-SMI failed',1)),[])
    def test_runtime_malformed_or_contradictory(self):
        for r in [result('not JSON'),result('[]'),runtime(code=1),runtime(count=0),runtime(stage='launch'),result('{"device_count":true}')]:
            with self.subTest(record=r):self.assertIsNone(cuda.runtime_json(r))
    def test_missing_command_and_timeout_diagnostics(self):
        with patch.object(cuda.subprocess,'run',side_effect=FileNotFoundError('missing')):
            r=cuda.command(['unavailable']);self.assertIsNone(r['returncode']);self.assertEqual(r['status'],'unavailable')
        with patch.object(cuda.subprocess,'run',side_effect=subprocess.TimeoutExpired(['fake'],1,output=b'partial',stderr=b'diagnostic')):
            r=cuda.command(['fake'],1);self.assertEqual(r['status'],'timeout');self.assertEqual(r['stdout'],'partial');self.assertEqual(r['stderr'],'diagnostic')
        with patch.object(cuda.subprocess,'run',return_value=subprocess.CompletedProcess(['fake'],9,'out','err')):
            r=cuda.command(['fake']);self.assertEqual((r['returncode'],r['stdout'],r['stderr']),(9,'out','err'))
    def test_collection_gates_no_enabled_config_without_nvcc(self):
        calls=[]
        def runner(argv,timeout):
            calls.append(argv);return result('cmake version 3.28.3' if argv[-1]=='--version' and argv[0]=='cmake' else '',0 if argv[0]=='cmake' else 127)
        r=cuda.collect(runner=runner,environ={},discovery=discovery())
        self.assertFalse(any('-DMAB_ENABLE_CUDA=ON' in c for c in calls));self.assertEqual(r['probes']['configure']['status'],'skipped')
        self.assertEqual(r['classification']['state'],'no_nvidia_gpu_detected')
    def test_full_mocked_collection_and_failure_boundaries(self):
        found=discovery();found['tools']['nvcc']='/synthetic/nvcc'
        for failure in [None,'configure','build','runtime']:
            calls=[]
            def runner(argv,timeout):
                calls.append(argv)
                if '--version' in argv:return result('cmake version 3.28.3' if argv[0]=='cmake' else 'NVIDIA nvcc release 12.0')
                if '-S' in argv:return result('',1 if failure=='configure' else 0)
                if '--build' in argv:return result('',1 if failure=='build' else 0)
                if 'cuda_runtime_probe' in argv[0]:return runtime('error',1,1,'launch') if failure=='runtime' else runtime()
                return result('',127)
            r=cuda.collect(runner=runner,environ={},discovery=found)
            with self.subTest(failure=failure):
                self.assertEqual(r['classification']['device0_kernel_verified'],failure is None)
                if failure=='configure':self.assertEqual(r['probes']['build']['status'],'skipped')
                if failure=='build':self.assertEqual(r['probes']['runtime']['status'],'skipped')
    def test_redaction_allowlist_and_counter_isolation(self):
        env={'SERVICE_TOKEN':'secret-value','PATH':'/ordinary/private/path:/cuda/bin','CUDA_HOME':'https://user:password@example.test/?token=hidden','CUDA_VISIBLE_DEVICES':'0','NOT_RELEVANT':'do-not-print'}
        def runner(argv,timeout):return result('secret-value',127)
        a=cuda.collect(runner=runner,environ=env,discovery=discovery());b=cuda.collect(runner=runner,environ={},discovery=discovery())
        text=json.dumps(a);self.assertNotIn('secret-value',text);self.assertNotIn('do-not-print',text);self.assertNotIn('/ordinary/private/path',text);self.assertNotIn('user:password',text);self.assertNotIn('hidden',text)
        self.assertEqual(a['cuda_path_entries'],['/cuda/bin']);self.assertIsNone(b['environment']['CUDA_HOME'])
        self.assertEqual(cuda.scrub('value=1234',{'API_KEY':'1234'}),'value=<redacted>')
    def test_output_exclusivity_summary_and_status(self):
        r=cuda.collect(runner=lambda a,t:result('',127),environ={},discovery=discovery())
        with tempfile.TemporaryDirectory() as temporary:
            directory=Path(temporary)/'output'
            with contextlib.redirect_stdout(io.StringIO()):code=cuda.execute(directory,collector=lambda **kwargs:r)
            self.assertEqual(code,2);before={f.name:f.read_bytes() for f in directory.iterdir()}
            self.assertFalse(json.loads(before['COMPLETE.json'])['cuda_operational']);self.assertIn('CPU project: unaffected',before['SUMMARY.txt'].decode())
            with self.assertRaises(FileExistsError):cuda.execute(directory,collector=lambda **kwargs:self.fail('must not probe existing output'))
            self.assertEqual(before,{f.name:f.read_bytes() for f in directory.iterdir()})
            r['classification']['device0_kernel_verified']=True
            with contextlib.redirect_stdout(io.StringIO()):self.assertEqual(cuda.execute(Path(temporary)/'ready',collector=lambda **kwargs:r),0)
    def test_interrupt_and_report_errors_are_incomplete(self):
        for error in [KeyboardInterrupt(),ValueError('synthetic')]:
            with tempfile.TemporaryDirectory() as temporary:
                directory=Path(temporary)/'output'
                def collect(**kwargs):raise error
                with self.assertRaises(type(error)):cuda.execute(directory,collector=collect)
                self.assertTrue((directory/'INCOMPLETE.json').exists());self.assertFalse((directory/'COMPLETE.json').exists())
    def test_missing_file_is_explicit(self):
        with tempfile.TemporaryDirectory() as temporary:self.assertFalse(cuda.read_optional(Path(temporary)/'missing')['available'])
    def test_redaction_in_discovered_path_keys_preserves_numeric_json(self):
        found=discovery();found['toolkit_files']={'/cuda/secret-value/version.json':{'sha256':'1234'}}
        r=cuda.collect(runner=lambda a,t:result('',127),environ={'SERVICE_TOKEN':'secret-value','API_KEY':'1234'},discovery=found)
        self.assertNotIn('secret-value',json.dumps(r));self.assertIn('/cuda/<redacted>/version.json',r['discovery']['toolkit_files'])
        self.assertEqual(r['schema_version'],1)
    def test_cli_invalid_timeout(self):
        r=subprocess.run([sys.executable,str(ROOT/'scripts/cuda_preflight.py'),'--output','unused','--timeout-seconds','0'],capture_output=True,text=True)
        self.assertEqual(r.returncode,2);self.assertIn('timeout',r.stderr)


class CudaOffBuildIsolation(unittest.TestCase):
    def test_default_and_explicit_off_ignore_cuda_environment(self):
        env=dict(os.environ,CUDACXX='/nonexistent/mab_nvcc',CUDAToolkit_ROOT='/nonexistent/mab_toolkit')
        with tempfile.TemporaryDirectory() as temporary:
            for mode in ['default','explicit']:
                build=Path(temporary)/mode
                cmd=['cmake','-S',str(ROOT),'-B',str(build),'-DBUILD_TESTING=OFF','-DMAB_ENABLE_OPENMP=OFF']
                if mode=='explicit':cmd.append('-DMAB_ENABLE_CUDA=OFF')
                r=subprocess.run(cmd,capture_output=True,text=True,env=env)
                with self.subTest(mode=mode):
                    self.assertEqual(r.returncode,0,r.stdout+r.stderr)
                    cache=(build/'CMakeCache.txt').read_text();self.assertIn('MAB_ENABLE_CUDA:BOOL=OFF',cache)
                    self.assertNotIn('CMAKE_CUDA_COMPILER:',cache);self.assertNotIn('CUDA compiler',r.stdout)
                    self.assertFalse((build/'CMakeFiles/CheckCUDA').exists())

if __name__=='__main__':unittest.main()
