#!/usr/bin/env python3
"""Exclusive real-GPU correctness -> smallest smoke -> matrix and regeneration."""
import argparse
import datetime
import json
from pathlib import Path
import subprocess
import sys
import time
import capture_environment
from validate_cuda_sort import ROOT, digest, write_json


def run(output, processed):
    output=Path(output).absolute();processed=Path(processed).absolute()
    output.mkdir()
    try:
        processed.mkdir()
        sources={str(p.relative_to(ROOT)):digest(p) for base in ['include','src','tests','scripts','cmake','docs','third_party']
                 for p in sorted((ROOT/base).rglob('*')) if p.is_file() and '__pycache__' not in p.parts}
        for name in ['CMakeLists.txt','README.md','AGENTS.md']:sources[name]=digest(ROOT/name)
        write_json(output/'source_sha256.json',sources)
        write_json(output/'run.json',dict(protocol='cuda_sort_timing_v1',started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   source=str(ROOT),processed=str(processed),size_cap=65537,matrix_configurations=48,measured_trials=240,warmup_trials=48))
        def invoke(name,argv,timeout=600):
            write_json(output/(name+'_started.json'),dict(argv=argv,cwd=str(ROOT)))
            start=time.monotonic()
            try:r=subprocess.run(argv,cwd=ROOT,capture_output=True,text=True,timeout=timeout,check=False)
            except subprocess.TimeoutExpired as error:
                def text(v):return v.decode(errors='replace') if isinstance(v,bytes) else v or ''
                write_json(output/(name+'.json'),dict(argv=argv,status='timeout',exit_code=None,stdout=text(error.stdout),stderr=text(error.stderr)))
                raise RuntimeError(name+' timeout') from error
            write_json(output/(name+'.json'),dict(argv=argv,cwd=str(ROOT),status='completed',exit_code=r.returncode,
                       stdout=r.stdout,stderr=r.stderr,wall_seconds=time.monotonic()-start))
            if r.returncode:raise RuntimeError(name+' exit '+str(r.returncode))
        invoke('correctness',[sys.executable,str(ROOT/'scripts/validate_cuda_sort.py'),'--output',str(output/'correctness')],900)
        build=output/'correctness/build'
        invoke('build_benchmark',['cmake','--build',str(build),'--target','cuda_sort_benchmark','--parallel','2'])
        executable=build/'cuda_sort_benchmark'
        env=capture_environment.capture(build,'validate_cuda_timing.py')
        env.update(record_kind='cuda_timing_environment',gpu_status='see fresh correctness/preflight/report.json',
                   workload_note='prepared GPU timing smoke only; exact per-run CSV/metadata retained')
        write_json(output/'environment.json',env)
        write_json(output/'binary_sha256.json',dict(executable=str(executable),sha256=digest(executable)))
        invoke('smallest_smoke',[str(executable),'--output',str(output/'smallest'),'--size','1025',
               '--distribution','uniform','--seed','1729','--warmups','1','--repetitions','5'])
        analyze=ROOT/'scripts/analyze_cuda_results.py'
        invoke('analyze_smallest',[sys.executable,str(analyze),str(output/'smallest'),'--output',str(processed/'smallest.json')])
        invoke('gpu_framework',['ctest','--test-dir',str(build),'--output-on-failure','-V','-R','^cuda_benchmark_gpu_framework$'])
        invoke('smoke_matrix',[sys.executable,str(ROOT/'scripts/run_cuda_matrix.py'),'--executable',str(executable),
               '--output',str(output/'matrix'),'--sizes','0,1,1025,65537','--seeds','1729,42',
               '--distributions','uniform,sorted,reverse_sorted,duplicate_heavy,nearly_sorted,signed_edges',
               '--warmups','1','--repetitions','5'])
        raw_hashes={str(p.relative_to(output)):digest(p) for base in ['smallest','matrix']
                    for p in sorted((output/base).rglob('*')) if p.is_file()}
        write_json(output/'timing_raw_sha256.json',raw_hashes)
        invoke('analyze_matrix',[sys.executable,str(analyze),str(output/'matrix'),'--output',str(processed/'matrix.json')])
        for name in ['smallest','matrix']:
            invoke('regenerate_'+name,[sys.executable,str(analyze),str(output/name),'--output',str(processed/(name+'_regenerated.json'))])
            if (processed/(name+'.json')).read_bytes()!=(processed/(name+'_regenerated.json')).read_bytes():
                raise ValueError('summary regeneration mismatch')
        if any(digest(output/name)!=sha for name,sha in raw_hashes.items()):raise ValueError('raw changed during analysis')
        if any(digest(ROOT/name)!=sha for name,sha in sources.items()):raise ValueError('source changed during run')
        summary=json.loads((processed/'matrix.json').read_text());groups=summary['groups']
        if not summary['complete'] or len(groups)!=48 or sum(g['successful_trials'] for g in groups)!=240 or \
                sum(g['warmup_rows'] for g in groups)!=48 or any(g['failed_trials'] or g['missing_trials'] or
                g['failed_warmups'] or g['missing_warmups'] for g in groups):raise ValueError('incomplete smoke matrix')
        write_json(output/'COMPLETE.json',dict(protocol='cuda_sort_timing_v1',complete=True,configurations=48,
                   measured_trials=240,warmups=48,smallest_measured_trials=5,smallest_warmups=1,
                   failed_trials=0,missing_trials=0,summary_regeneration_identical=True,
                   summaries_sha256={p.name:digest(p) for p in sorted(processed.glob('*.json'))},
                   source_manifest_sha256=digest(output/'source_sha256.json')))
        return 0
    except KeyboardInterrupt:
        write_json(output/'INTERRUPTED.json',dict(complete=False));return 130
    except Exception as error:
        write_json(output/'FAILED.json',dict(complete=False,error=str(error)));print(str(error),file=sys.stderr);return 1


def main():
    p=argparse.ArgumentParser(description=__doc__,allow_abbrev=False)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--processed',type=Path,required=True);args=p.parse_args()
    try:return run(args.output,args.processed)
    except OSError as error:print(str(error),file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
