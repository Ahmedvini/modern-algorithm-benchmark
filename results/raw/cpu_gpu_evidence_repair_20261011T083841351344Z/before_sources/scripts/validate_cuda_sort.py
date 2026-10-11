#!/usr/bin/env python3
"""Exclusive cloud correctness handoff. No timing or CPU substitution."""
import argparse
import datetime
import hashlib
import json
import os
import re
from pathlib import Path
import subprocess
import sys
import time

import cuda_preflight
ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = 'cuda_sort_correctness_v2'
EXPECTED_CASES = 475
EXPECTED_CHECKS = 1900


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    def clean(x):
        if isinstance(x, str): return cuda_preflight.scrub(x, dict(os.environ))
        if isinstance(x, list): return [clean(v) for v in x]
        if isinstance(x, dict): return {clean(k): clean(v) for k, v in x.items()}
        return x
    with Path(path).open('x', encoding='utf-8') as f:
        json.dump(clean(value), f, indent=2, sort_keys=True, allow_nan=False)
        f.write('\n')


def verify_result(value):
    if not isinstance(value, dict): raise ValueError('sort result must be an object')
    required = dict(schema_version=1, protocol=PROTOCOL, algorithm='cub_radix_sort',
                    implementation_version='cub_radix_sort_v1', status='ok',
                    cases=EXPECTED_CASES, output_checks=EXPECTED_CHECKS, cub_version=300001)
    for key, expected in required.items():
        if type(value.get(key)) is not type(expected) or value[key] != expected:
            raise ValueError('incorrect or incomplete sort result: ' + key)
    for key in ['runtime_api_version', 'driver_api_version', 'compute_major', 'compute_minor', 'device']:
        if type(value.get(key)) is not int or value[key] < 0: raise ValueError('invalid ' + key)
    if value['runtime_api_version'] < 13000: raise ValueError('unsupported runtime')
    if value['compute_major'] < 1: raise ValueError('invalid compute capability')
    return value


def verify_ctest(text):
    if 'Skipped' in text or not re.search(r'1/1 Test\s+#\d+: cuda_sorting .*Passed',text):
        raise ValueError('cuda_sorting CTest must actually pass, not skip or select no tests')


def run(output, runner=subprocess.run):
    # Preserve the final path component so mkdir rejects even dangling symlinks.
    output = Path(output).absolute()
    output.mkdir()  # Atomic claim: never touch existing paths, including symlinks.
    try:
        sources = {str(p.relative_to(ROOT)): digest(p)
                   for base in ['include', 'src', 'tests', 'scripts', 'cmake', 'docs', 'third_party']
                   for p in sorted((ROOT / base).rglob('*'))
                   if p.is_file() and '__pycache__' not in p.parts}
        for name in ['CMakeLists.txt', 'AGENTS.md', 'README.md']:
            sources[name] = digest(ROOT / name)
        write_json(output / 'source_sha256.json', sources)
        write_json(output / 'run.json', dict(protocol=PROTOCOL, source=str(ROOT), output=str(output),
                   started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   primary_timing=False, cloud_location='not inferred; inspect recorded environment'))
        def invoke(name, argv, timeout=600):
            write_json(output / (name + '_started.json'), dict(argv=argv, cwd=str(ROOT)))
            start=time.monotonic()
            try:
                result = runner(argv, cwd=ROOT, capture_output=True, text=True, timeout=timeout, check=False)
            except subprocess.TimeoutExpired as error:
                def text(s): return s.decode(errors='replace') if isinstance(s, bytes) else s or ''
                write_json(output / (name + '.json'), dict(argv=argv, status='timeout', exit_code=None,
                           stdout=text(error.stdout), stderr=text(error.stderr)))
                raise RuntimeError(name + ' timed out') from error
            write_json(output / (name + '.json'), dict(argv=argv, cwd=str(ROOT), status='completed',
                       exit_code=result.returncode, stdout=result.stdout, stderr=result.stderr,
                       wall_seconds=time.monotonic()-start))
            if result.returncode != 0:
                raise RuntimeError(name + ' exit ' + str(result.returncode) + '; inspect retained diagnostics')
            return result
        invoke('preflight', [sys.executable, str(ROOT/'scripts/cuda_preflight.py'),
                            '--output', str(output/'preflight'), '--timeout-seconds', '180'])
        preflight=json.loads((output/'preflight/report.json').read_text())
        if not preflight['classification']['device0_kernel_verified'] or preflight['classification']['state']!='operational':
            raise ValueError('operational runtime required')
        device=next(d for d in preflight['runtime_probe']['devices'] if d['ordinal']==0)
        architecture=str(device['compute_major'])+str(device['compute_minor'])
        build=output/'build'
        invoke('configure', ['cmake','-S',str(ROOT),'-B',str(build),'-DCMAKE_BUILD_TYPE=Release',
              '-DMAB_ENABLE_CUDA=ON','-DMAB_ENABLE_CUDA_SORT=ON','-DMAB_ENABLE_OPENMP=OFF',
              '-DMAB_ENABLE_SANITIZERS=OFF','-DBUILD_TESTING=ON',
              '-DCMAKE_CUDA_COMPILER='+preflight['discovery']['tools']['nvcc'],
              '-DCMAKE_CUDA_ARCHITECTURES='+architecture])
        # Record all installed dependency files, not just a version claim.
        cache=(build/'CMakeCache.txt').read_text()
        include=Path(next(line.split('=',1)[1] for line in cache.splitlines()
                          if line.startswith('MAB_CUB_INCLUDE_DIR:PATH=')))
        dependency={str(p.relative_to(include)):digest(p) for name in ['cub','thrust','cuda']
                    for p in sorted((include/name).rglob('*')) if p.is_file()}
        if not dependency: raise ValueError('dependency snapshot empty')
        write_json(output/'dependency_sha256.json',dict(include_root=str(include),files=dependency,
                   absent_trees=[n for n in ['cub','thrust','cuda'] if not (include/n).is_dir()]))
        invoke('build', ['cmake','--build',str(build),'--target','test_cuda_sorting','--parallel','2'])
        result=verify_result(json.loads(invoke('sorting', [str(build/'test_cuda_sorting')],timeout=240).stdout))
        if result['device']!=0 or (result['compute_major'],result['compute_minor'])!=(device['compute_major'],device['compute_minor']):
            raise ValueError('sorter device differs from preflight')
        ctest=invoke('ctest', ['ctest','--test-dir',str(build),'--output-on-failure','-V','-R','^cuda_sorting$'])
        verify_ctest(ctest.stdout)
        if any(digest(ROOT/name)!=sha for name,sha in sources.items()): raise ValueError('source changed during validation')
        write_json(output/'COMPLETE.json', dict(protocol=PROTOCOL,sorting_validated=True,
                   result=result,source_manifest_sha256=digest(output/'source_sha256.json'),
                   dependency_manifest_sha256=digest(output/'dependency_sha256.json'),
                   preflight_sha256=digest(output/'preflight/report.json')))
        return 0
    except KeyboardInterrupt:
        write_json(output/'INTERRUPTED.json', dict(complete=False,sorting_validated=False))
        return 130
    except Exception as error:
        write_json(output/'FAILED.json',dict(complete=False,sorting_validated=False,error=str(error)))
        print(cuda_preflight.scrub(str(error),dict(os.environ)),file=sys.stderr)
        return 1


def main():
    parser=argparse.ArgumentParser(description=__doc__,allow_abbrev=False)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    try: return run(args.output)
    except OSError as error:
        print(cuda_preflight.scrub(str(error),dict(os.environ)),file=sys.stderr)
        return 1
if __name__=='__main__': sys.exit(main())
