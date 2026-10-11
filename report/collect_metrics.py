#!/usr/bin/env python3
"""Collect separate deterministic sort counts/RSS using the existing metrics CLI."""
import argparse
import hashlib
import json
from pathlib import Path
import statistics
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ALGORITHMS = ['std_sort', 'quick_sort', 'pdq_sort', 'tim_sort', 'merge_sort']
SIZES = [1000, 10000, 100000, 1000000]
DISTRIBUTIONS = ['uniform', 'nearly_sorted', 'reverse_sorted', 'duplicate_heavy']
SEEDS = [1729, 42, 2718]


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path, value):
    with path.open('x') as stream: json.dump(value, stream, sort_keys=True, indent=2, allow_nan=False); stream.write('\n')
def require(ok, message):
    if not ok: raise ValueError(message)


def collect(binary, output):
    binary = binary.resolve(strict=True); output.mkdir()
    write(output / 'STARTED.json', dict(protocol='count_memory_v1', binary=str(binary), binary_sha256=sha(binary),
        protocol_sha256=sha(ROOT / 'docs/COUNT_MEMORY_STUDY_v1.md'), configurations=240))
    manifest = {}
    for n in SIZES:
        for distribution in DISTRIBUTIONS:
            for seed in SEEDS:
                for algorithm in ALGORITHMS:
                    name = f'n{n}_{distribution}_s{seed}_{algorithm}.json'
                    argv = [str(binary), '--size', str(n), '--seed', str(seed), '--distribution', distribution, '--sort', algorithm]
                    result = subprocess.run(argv, capture_output=True, text=True, timeout=300)
                    record = dict(command=argv, exit_code=result.returncode, stdout=result.stdout, stderr=result.stderr)
                    write(output / name, record); manifest[name] = sha(output / name)
                    require(result.returncode == 0, 'metrics failed: ' + name)
                    parse(record, n, distribution, seed, algorithm)
        print('completed metrics size', n, flush=True)
    write(output / 'COMPLETE.json', dict(complete=True, configurations=240, files_sha256=manifest))


def parse(record, n, distribution, seed, algorithm):
    require(record['exit_code'] == 0, 'failed metrics command')
    value = json.loads(record['stdout'])
    expected = dict(schema_version=1, mode='sort_metrics', status='ok', sort_algorithm=algorithm, size=n, seed=seed,
        distribution=distribution, comparison_convention='key_less_than_v1', dataset_generator='mt19937_64_v1',
        nearly_sorted_swaps=n//100, duplicate_cardinality=16, memory_sample_point='after_instrumented_sort_before_validation')
    require(all(value.get(k) == v for k, v in expected.items()), 'metrics identity/status mismatch')
    require(type(value['key_comparisons']) is int and value['key_comparisons'] >= 0, 'invalid comparison count')
    memory = value['process_memory']
    require(set(memory) == {'status','metric','scope','unit','method','value','error_code'} and
            memory['metric']=='peak_rss' and memory['scope']=='process_lifetime' and memory['unit']=='bytes' and
            memory['error_code'] is None, 'memory schema mismatch')
    require(memory['status'] in ['ok', 'unsupported'], 'memory collection error')
    if memory['status'] == 'ok':
        require(memory['method']=='getrusage_ru_maxrss' and type(memory['value']) is int and memory['value'] >= 0, 'invalid RSS')
    else: require(memory['method']=='none' and memory['value'] is None, 'invalid unsupported RSS')
    return value


def analyze(raw, output):
    complete = json.loads((raw / 'COMPLETE.json').read_text())
    require(complete['complete'] is True and complete['configurations'] == 240 and len(complete['files_sha256']) == 240, 'incomplete metric collection')
    rows = []
    for n in SIZES:
        for distribution in DISTRIBUTIONS:
            for algorithm in ALGORITHMS:
                values = []
                for seed in SEEDS:
                    name = f'n{n}_{distribution}_s{seed}_{algorithm}.json'
                    require(sha(raw / name) == complete['files_sha256'][name], 'raw metrics changed')
                    values.append(parse(json.loads((raw / name).read_text()), n, distribution, seed, algorithm))
                counts = [v['key_comparisons'] for v in values]
                rss = [v['process_memory']['value'] for v in values if v['process_memory']['status'] == 'ok']
                rows.append(dict(size=n, distribution=distribution, algorithm=algorithm, datasets=3,
                    count_median=statistics.median(counts), count_min=min(counts), count_max=max(counts),
                    process_rss_median_bytes=statistics.median(rss) if rss else None,
                    process_rss_min_bytes=min(rss) if rss else None, process_rss_max_bytes=max(rss) if rss else None,
                    unavailable_memory=3-len(rss)))
    output.mkdir()
    write(output / 'summary.json', dict(protocol='count_memory_v1', configurations=240, failed=0, missing=0,
        outlier_policy='retain_all', aggregation='three distinct seed observations, no repeatability claim',
        memory_scope='process lifetime high-water including instrumented sort; not isolated auxiliary storage', groups=rows))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    manifest = []
    for distribution in DISTRIBUTIONS:
        for metric, unit, scale in [('count', 'Key comparisons / N', None), ('process_rss', 'Process lifetime peak RSS (MiB)', 1024**2)]:
            fig, ax = plt.subplots(figsize=(7.2, 4.6), layout='constrained')
            for algorithm in ALGORITHMS:
                data = [r for r in rows if r['distribution'] == distribution and r['algorithm'] == algorithm]
                if metric == 'count':
                    middle = [r['count_median']/r['size'] for r in data]
                    lo = [r['count_min']/r['size'] for r in data]; hi = [r['count_max']/r['size'] for r in data]
                else:
                    data = [r for r in data if r['process_rss_median_bytes'] is not None]
                    middle = [r['process_rss_median_bytes']/scale for r in data]
                    lo = [r['process_rss_min_bytes']/scale for r in data]; hi = [r['process_rss_max_bytes']/scale for r in data]
                ax.errorbar([r['size'] for r in data], middle, yerr=[[m-l for m,l in zip(middle,lo)], [h-m for h,m in zip(hi,middle)]], marker='o', capsize=3, label=algorithm)
            ax.set_xscale('log'); ax.set_ylim(bottom=0); ax.grid(alpha=.25)
            ax.set(xlabel='Input elements (log scale)', ylabel=unit, title=f'{distribution}: separate instrumented runs\nMedian/min–max of 3 seeds; RSS is not auxiliary memory')
            ax.legend(fontsize=8)
            filename=f'{distribution}_{metric}.png'; fig.savefig(output/filename,dpi=220); plt.close(fig)
            manifest.append(dict(file=filename, source='summary.json', distribution=distribution, metric=metric,
                                 aggregation='median/min–max across seed datasets'))
    write(output / 'plots.json', manifest)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__,allow_abbrev=False)
    sub=parser.add_subparsers(dest='mode',required=True)
    p=sub.add_parser('collect');p.add_argument('--binary',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p=sub.add_parser('analyze');p.add_argument('--raw',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.mode=='collect':collect(args.binary,args.output)
    else:analyze(args.raw,args.output)
