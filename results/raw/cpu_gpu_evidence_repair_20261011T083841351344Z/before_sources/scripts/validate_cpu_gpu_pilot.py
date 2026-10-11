#!/usr/bin/env python3
"""Fresh CPU/CUDA prerequisites, optionally followed by the frozen six-dataset pilot."""
import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path
from cpu_gpu_protocol import PROTOCOL, ROOT, dump_new, load_protocol, require, sha, verify_source_extension
from run_cpu_gpu_pilot import invoke
from validate_cuda_sort import verify_result
from non_timing_tests import selected_ctest

def main():
    parser=argparse.ArgumentParser(description=__doc__,allow_abbrev=False)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--pilot-output',type=Path)
    parser.add_argument('--processed',type=Path)
    parser.add_argument('--prerequisites-only',action='store_true',help='Only audited non-timing correctness prerequisites; never pilot/study; not full study authorization')
    args=parser.parse_args();output=args.output.absolute()
    if not args.prerequisites_only and (args.pilot_output is None or args.processed is None):
        parser.error('--pilot-output and --processed are required unless --prerequisites-only')
    try:output.mkdir();(output/'commands').mkdir()
    except OSError as error:print(error,file=sys.stderr);return 1
    try:
        model=load_protocol();before=verify_source_extension(model)
        dump_new(output/'source_review.json',before)
        build_root=ROOT/'build'/output.name
        build_root.parent.mkdir(parents=True,exist_ok=True)
        require(not build_root.exists(),'build output already exists');build_root.mkdir()
        cpu=build_root/'cpu-release';san=build_root/'cpu-sanitize';gpu=build_root/'gpu-release'
        commands=output/'commands';records={}
        def call(name,argv,timeout=900):
            result=invoke(commands,name,argv,timeout)
            records[name]=dict(file='commands/'+name+'.json',sha256=sha(commands/(name+'.json')))
            return result
        call('preflight',[sys.executable,str(ROOT/'scripts/cuda_preflight.py'),'--output',str(output/'preflight'),'--timeout-seconds','180'],240)
        probe=json.loads((output/'preflight/report.json').read_text())
        require(probe['classification']['device0_kernel_verified'] and probe['classification']['state']=='operational','fresh kernel preflight failed')
        device=next(d for d in probe['runtime_probe']['devices'] if d['ordinal']==0)
        require(device['name']=='Tesla T4' and (device['compute_major'],device['compute_minor'])==(7,5),'wrong GPU for frozen protocol')
        common=['cmake','-S',str(ROOT),'-DCMAKE_CXX_FLAGS=','-DCMAKE_CXX_FLAGS_RELEASE=-O3 -DNDEBUG','-DMAB_ENABLE_OPENMP=ON','-DBUILD_TESTING=ON']
        call('cpu_release_configure',common+['-B',str(cpu),'-DCMAKE_BUILD_TYPE=Release','-DMAB_ENABLE_CUDA=OFF','-DMAB_ENABLE_CPU_GPU_COMPARISON=OFF'])
        call('cpu_release_build',['cmake','--build',str(cpu),'--parallel','2'])
        if args.prerequisites_only:
            result=selected_ctest(call,output,'cpu_release_ctest',cpu)
        else:
            result=call('cpu_release_ctest',['ctest','--test-dir',str(cpu),'--output-on-failure','-V'],900)
            require('0 tests failed out of 29' in result['stdout'],'CPU regression coverage mismatch')
        call('cpu_sanitize_configure',common+['-B',str(san),'-DCMAKE_BUILD_TYPE=Debug','-DMAB_ENABLE_CUDA=OFF','-DMAB_ENABLE_CPU_GPU_COMPARISON=OFF','-DMAB_ENABLE_SANITIZERS=ON'])
        call('cpu_sanitize_build',['cmake','--build',str(san),'--parallel','2'])
        try:
            prefix=['env','-u','ASAN_OPTIONS','-u','LSAN_OPTIONS','UBSAN_OPTIONS=halt_on_error=1']
            if args.prerequisites_only:
                result=selected_ctest(call,output,'cpu_sanitize_ctest',san,prefix=prefix)
            else:
                result=call('cpu_sanitize_ctest',prefix+['ctest','--test-dir',str(san),'--output-on-failure','-V'],900)
        except RuntimeError:
            record=json.loads((commands/'cpu_sanitize_ctest.json').read_text())
            text=record['stdout']+record['stderr']
            require('LeakSanitizer does not work under ptrace' in text,'unrelated sanitizer failure; stop before pilot')
            prefix=['env','ASAN_OPTIONS=detect_leaks=0','UBSAN_OPTIONS=halt_on_error=1']
            if args.prerequisites_only:
                result=selected_ctest(call,output,'cpu_sanitize_ctest_no_leaks',san,prefix=prefix)
            else:
                result=call('cpu_sanitize_ctest_no_leaks',prefix+['ctest','--test-dir',str(san),'--output-on-failure','-V'],900)
            records['cpu_sanitize_ctest']=records['cpu_sanitize_ctest_no_leaks']
            dump_new(output/'LEAK_LIMITATION.json',dict(reason='LeakSanitizer does not work under ptrace',original_record='commands/cpu_sanitize_ctest.json'))
        if not args.prerequisites_only:require('0 tests failed out of 29' in result['stdout'],'sanitizer coverage mismatch')
        call('cuda_configure',common+['-B',str(gpu),'-DCMAKE_BUILD_TYPE=Release','-DMAB_ENABLE_CUDA=ON','-DMAB_ENABLE_CUDA_SORT=ON',
            '-DMAB_ENABLE_CPU_GPU_COMPARISON=ON','-DMAB_ENABLE_SANITIZERS=OFF','-DCMAKE_CUDA_ARCHITECTURES=75',
            '-DCMAKE_CUDA_FLAGS=','-DCMAKE_CUDA_FLAGS_RELEASE=-O3 -DNDEBUG'])
        cache=(gpu/'CMakeCache.txt').read_text()
        include=Path(next(line.split('=',1)[1] for line in cache.splitlines() if line.startswith('MAB_CUB_INCLUDE_DIR:PATH=')))
        dependency={str(p.relative_to(include)):sha(p) for name in ['cub','thrust','cuda'] for p in sorted((include/name).rglob('*')) if p.is_file()}
        require(bool(dependency),'empty CUB dependency manifest')
        dump_new(output/'dependency_sha256.json',dict(include_root=str(include),files=dependency))
        call('cuda_build',['cmake','--build',str(gpu),'--parallel','2'],1200)
        correctness=call('cuda_correctness',[str(gpu/'test_cuda_sorting')],240)
        result=verify_result(json.loads(correctness['stdout']))
        if args.prerequisites_only:
            ctest=selected_ctest(call,output,'cuda_ctest',gpu,allow_gpu=True)
        else:
            ctest=call('cuda_ctest',['ctest','--test-dir',str(gpu),'--output-on-failure','-V'],900)
            require('0 tests failed out of 32' in ctest['stdout'] and '***Skipped' not in ctest['stdout'],'CUDA regression group skipped/missing')
            require('Ran 14 tests' in ctest['stdout'],'GPU framework coverage absent')
        after=verify_source_extension(model);require(before==after,'source changed during prerequisite validation')
        prereq=dict(schema_version=1,protocol=PROTOCOL,complete=True,records=records,source_sha256=after['current_source_sha256'],
                    binary_sha256=sha(gpu/'cpu_gpu_comparison'),input_tool_sha256=sha(gpu/'comparison_input'),
                    cuda_correctness=result,preflight_sha256=sha(output/'preflight/report.json'),dependency_manifest_sha256=sha(output/'dependency_sha256.json'),
                    validation_scope='non_timing_correctness_v1' if args.prerequisites_only else 'full_protocol_v1',
                    study_eligible=not args.prerequisites_only)
        dump_new(output/'PREREQUISITES.json',prereq)
        if args.prerequisites_only:
            dump_new(output/'COMPLETE.json',dict(complete=True,prerequisites_passed=True,pilot_run=False,full_study_run=False,
                validation_scope='non_timing_correctness_v1',study_eligible=False))
            return 0
        call('pilot',[sys.executable,str(ROOT/'scripts/run_cpu_gpu_pilot.py'),'--output',str(args.pilot_output.absolute()),
             '--executable',str(gpu/'cpu_gpu_comparison'),'--input-tool',str(gpu/'comparison_input'),
             '--prerequisites',str(output/'PREREQUISITES.json')],420)
        args.processed.absolute().mkdir()
        first=args.processed.absolute()/'summary.json';second=args.processed.absolute()/'summary_regenerated.json'
        for name,path in [('analyze',first),('regenerate',second)]:
            call(name,[sys.executable,str(ROOT/'scripts/analyze_cpu_gpu.py'),str(args.pilot_output.absolute()),'--output',str(path)])
        require(first.read_bytes()==second.read_bytes(),'summary regeneration differs')
        raw=args.pilot_output.absolute();manifest=json.loads((raw/'RAW_SHA256.json').read_text())
        require(all(sha(raw/p)==h for p,h in manifest.items()),'raw changed during analysis')
        load_protocol();require(verify_source_extension(model)==before,'source changed during pilot')
        dump_new(output/'COMPLETE.json',dict(complete=True,pilot_passed=True,full_study_run=False,measured=150,warmups=30,
                 summary_sha256=sha(first),summary_regenerated_identically=True,source_unchanged=True))
        return 0
    except KeyboardInterrupt:
        dump_new(output/'INTERRUPTED.json',dict(complete=False));return 130
    except Exception as error:
        dump_new(output/'FAILED.json',dict(complete=False,error=str(error)));print(error,file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
