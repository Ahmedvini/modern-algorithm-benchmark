#!/usr/bin/env python3
"""Exclusive sequential prepared-CUB smoke matrix; no resume or CPU fallback."""
import argparse
import datetime
import itertools
import json
from pathlib import Path
import subprocess
import sys
import time
from analyze_cuda_results import DISTRIBUTIONS, PROTOCOL, read_bundle


def write(path, value):
    with path.open('x') as stream:json.dump(value, stream, indent=2, allow_nan=False);stream.write('\n')


def numbers(text, maximum):
    values = text.split(',')
    if not values or any(not v or any(c not in '0123456789' for c in v) for v in values):
        raise ValueError('expected comma-separated unsigned decimals')
    result = [int(v) for v in values]
    if len(set(result)) != len(result) or any(v > maximum for v in result):
        raise ValueError('duplicate or out-of-range integer')
    return result


def plan(sizes, distributions, seeds, warmups, repetitions):
    if any(type(n) is not int or n < 0 or n > 1000000 for n in sizes) or any(type(s) is not int or s < 0 or s > 2**64-1 for s in seeds) or len(set(sizes)) != len(sizes) or len(set(seeds)) != len(seeds):
        raise ValueError('invalid matrix sizes/seeds')
    if not sizes or not seeds or not distributions or len(set(distributions)) != len(distributions) or \
            any(d not in DISTRIBUTIONS for d in distributions) or not 0 <= warmups <= 1000 or not 1 <= repetitions <= 10000:
        raise ValueError('invalid CUDA matrix configuration')
    if len(sizes) * len(distributions) * len(seeds) > 1000:
        raise ValueError('matrix exceeds1000 configurations')
    return [dict(name=f'run_{i:04d}', size=n, distribution=d, seed=s, warmups=warmups, repetitions=repetitions)
            for i, (n, d, s) in enumerate(itertools.product(sizes, distributions, seeds))]


def run(executable, output, configurations, runner=subprocess.run):
    executable = str(Path(executable).resolve()); output = Path(output).absolute()
    output.mkdir()  # Must not exist, including dangling symlinks.
    (output / 'commands').mkdir()
    write(output / 'matrix.json', dict(schema_version=1, protocol=PROTOCOL,
          started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), executable=executable,
          order='size_distribution_seed_product_sequential', configurations=configurations))
    try:
        for c in configurations:
            argv = [executable, '--output', str(output/c['name']), '--run-id', c['name'],
                    '--size', str(c['size']), '--distribution', c['distribution'], '--seed', str(c['seed']),
                    '--warmups', str(c['warmups']), '--repetitions', str(c['repetitions'])]
            write(output/'commands'/(c['name']+'_started.json'), dict(argv=argv, cwd=str(Path.cwd())))
            start = time.monotonic()
            try:
                r = runner(argv, capture_output=True, text=True, timeout=180, check=False)
                record = dict(argv=argv, exit_code=r.returncode, stdout=r.stdout, stderr=r.stderr,
                              wall_seconds=time.monotonic()-start, status='completed')
            except subprocess.TimeoutExpired as error:
                def text(v):return v.decode(errors='replace') if isinstance(v, bytes) else v or ''
                record = dict(argv=argv, exit_code=None, stdout=text(error.stdout), stderr=text(error.stderr), status='timeout')
                write(output/'commands'/(c['name']+'.json'), record)
                raise RuntimeError(c['name']+' timed out') from error
            write(output/'commands'/(c['name']+'.json'), record)
            if r.returncode != 0:raise RuntimeError(c['name']+' exit '+str(r.returncode))
            meta, result = read_bundle(output/c['name'])
            if any(meta[k] != c[k] for k in ['size','distribution','seed','warmups','repetitions']) or meta['run_id'] != c['name']:
                raise ValueError('subprocess configuration mismatch')
            assert result['complete']
        write(output/'COMPLETE.json', dict(complete=True, runs=len(configurations)))
        return 0
    except KeyboardInterrupt:
        write(output/'INTERRUPTED.json', dict(complete=False)); return 130
    except Exception as error:
        write(output/'FAILED.json', dict(complete=False, error=str(error))); print(str(error), file=sys.stderr); return 1


def main():
    p=argparse.ArgumentParser(description=__doc__,allow_abbrev=False)
    p.add_argument('--executable',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--sizes',default='0,1,1025,65537');p.add_argument('--seeds',default='1729,42')
    p.add_argument('--distributions',default=','.join(DISTRIBUTIONS))
    p.add_argument('--warmups',type=int,default=1);p.add_argument('--repetitions',type=int,default=5)
    args=p.parse_args()
    try:
        configs=plan(numbers(args.sizes,1000000),args.distributions.split(','),numbers(args.seeds,2**64-1),args.warmups,args.repetitions)
        return run(args.executable,args.output,configs)
    except (OSError,ValueError) as error:print(str(error),file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
