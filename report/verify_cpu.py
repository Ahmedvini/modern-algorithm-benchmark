"""Read-only audit of CPU report numbers against retained raw observations.

No executable is launched. Subprocess launch is explicitly forbidden while the
existing raw parsers are used. Historical outputs are never regenerated in place.
"""
import hashlib
import json
from pathlib import Path
import statistics
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(path): return json.loads(Path(path).read_text())
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def json_value(value):
    """Normalize in-memory tuples exactly as the retained JSON writer does."""
    return json.loads(json.dumps(value, allow_nan=False))
def require(ok, message):
    if not ok: raise ValueError(message)


def seed_statistics(groups, seeds):
    """A dataset contributes its repetition median, never its minimum."""
    require(len(groups) == len(seeds) and {r['seed'] for r in groups} == set(seeds), 'seed coverage')
    require(all(r['successful_trials'] == 5 and r['failed_trials'] == 0 and
                r['missing_measured_trials'] == 0 and r['run_complete'] for r in groups), 'failed/incomplete dataset')
    values = [next(r['median_ns'] for r in groups if r['seed'] == s) for s in seeds]
    return dict(seed_medians_ns=[dict(seed=s, median_ns=v) for s, v in zip(seeds, values)],
        median_of_seed_medians_ns=statistics.median(values), mean_of_seed_medians_ns=statistics.mean(values),
        sample_stdev_of_seed_medians_ns=statistics.stdev(values),
        min_seed_median_ns=min(values), max_seed_median_ns=max(values))


def verify(evidence, learned, metrics):
    with patch('subprocess.run', side_effect=AssertionError('report audit cannot launch workloads')), \
         patch('subprocess.Popen', side_effect=AssertionError('report audit cannot launch workloads')):
        return _verify(Path(evidence), Path(learned), Path(metrics))


def _verify(evidence, learned, metrics):
    sys.path.insert(0, str(ROOT/'scripts'))
    from analyze_results import analyze as sorts
    from analyze_parallel_results import analyze as parallel
    from experiment_model import validate_study, aggregate
    from learned_study import cells, validate_cell, samples, MATRIX
    from collect_metrics import parse, SIZES, DISTRIBUTIONS, ALGORITHMS, SEEDS

    processed = ROOT/'results/processed'
    one = processed/'sorting_1m_20261009T172003802655Z'
    cross = load(one/'cross_seed.json')
    parsed = sorts(Path(cross['source']))
    require(parsed == load(one/'per_seed.json'), '1M raw/summary mismatch')
    require(parsed['complete'] and len(parsed['groups']) == 90 and len(cross['groups']) == 30, '1M coverage')
    for row in cross['groups']:
        selected = [r for r in parsed['groups'] if (r['algorithm'],r['distribution']) == (row['algorithm'],row['distribution'])]
        require(all(row[k] == v for k,v in seed_statistics(selected, [1729,42,2718]).items()), '1M seed statistic mismatch')
        require(row['successful_trials'] == 15 and row['failed_trials'] == 0 and row['dataset_count'] == 3, '1M count mismatch')
    counts = {'sorting_1m':dict(measured=450,warmups=90,failed=0,missing=0)}
    for n,measured,warmups in [(10,450,90),(100,150,30)]:
        value = sorts(evidence/f'sorting_{n}m')
        require(value == load(evidence/f'sorting_{n}m_summary.json') and value['complete'], 'scale raw/summary mismatch')
        require(sum(r['successful_trials'] for r in value['groups']) == measured and
                sum(r['warmup_rows'] for r in value['groups']) == warmups and
                all(r['failed_trials'] == r['missing_measured_trials'] == r['failed_warmups'] == 0 for r in value['groups']), 'scale coverage')
        counts[f'sorting_{n}m'] = dict(measured=measured,warmups=warmups,failed=0,missing=0)

    cpu_raw = ROOT/'results/raw/phase5_full_20261009T191000587965Z'
    cpu = aggregate(validate_study(cpu_raw))
    require(cpu == load(processed/cpu_raw.name/'summary.json') and cpu['complete'], 'CPU pipeline raw/summary mismatch')
    counts['all_family'] = cpu['counts']
    omp_raw = ROOT/'results/raw/openmp_scaling_20261009T200852928292Z_retry1'
    omp, _ = parallel(omp_raw)
    require(json_value(omp) == load(processed/omp_raw.name/'summary.json') and omp['complete'], 'OpenMP raw/summary mismatch')
    require(omp['successful_measured'] == 1800 and omp['warmup_rows'] == 360 and
            omp['failed_measured'] == omp['missing_measured'] == omp['failed_warmups'] == omp['missing_warmups'] == 0, 'OpenMP coverage')
    counts['openmp'] = dict(measured=1800,warmups=360,failed=0,missing=0)

    raw = evidence/'learned_study';manifest = load(raw/'study.json')
    require(load(raw/'COMPLETE.json') == dict(complete=True,configurations=48,measured=720,warmups=144), 'learned completion')
    require(manifest['matrix_sha256'] == sha(MATRIX) and manifest['cells'] == cells(), 'learned matrix identity')
    for name,digest in manifest['raw_sha256'].items():
        require(not Path(name).is_absolute() and '..' not in Path(name).parts and sha(raw/name) == digest, 'learned raw seal')
    datasets = [validate_cell(raw/c['id'],c) for c in cells()]
    groups = {}
    for d in datasets:
        for t in d['timings']:groups.setdefault((d['size'],d['distribution'],t['algorithm'],t['operation']),[]).append(t['median'])
    cross_seed = [dict(size=n,distribution=d,algorithm=a,operation=o,unit='ns',aggregation='equal-weight dataset medians',**samples(v))
                  for (n,d,a,o),v in sorted(groups.items())]
    actual = load(learned/'summary.json')
    require(actual == dict(protocol='learned_rank_v1',configurations=48,measured_query_batches=480,warmup_query_batches=96,
        measured_builds=240,warmup_builds=48,failed=0,missing=0,datasets=datasets,cross_seed=cross_seed), 'learned raw/summary mismatch')
    distinct = len({(d['size'],d['input_fingerprint']) for d in datasets})
    require(distinct == 24, 'learned distinct input identity')
    counts['learned'] = dict(configurations=48,distinct_sorted_inputs=distinct,lookup_batches=480,builds=240,warmups=144,
        diagnostic_queries=sum(d['queries'] for d in datasets),failed=0,missing=0)

    raw = evidence/'count_memory_retry1';complete = load(raw/'COMPLETE.json')
    require(complete['complete'] is True and complete['configurations'] == len(complete['files_sha256']) == 240, 'metric coverage')
    rows = []
    for n in SIZES:
        for distribution in DISTRIBUTIONS:
            for algorithm in ALGORITHMS:
                values = []
                for seed in SEEDS:
                    name = f'n{n}_{distribution}_s{seed}_{algorithm}.json'
                    require(sha(raw/name) == complete['files_sha256'][name], 'metric raw seal')
                    values.append(parse(load(raw/name),n,distribution,seed,algorithm))
                comparisons = [v['key_comparisons'] for v in values]
                rss = [v['process_memory']['value'] for v in values if v['process_memory']['status'] == 'ok']
                rows.append(dict(size=n,distribution=distribution,algorithm=algorithm,datasets=3,
                    count_median=statistics.median(comparisons),count_min=min(comparisons),count_max=max(comparisons),
                    process_rss_median_bytes=statistics.median(rss) if rss else None,process_rss_min_bytes=min(rss) if rss else None,
                    process_rss_max_bytes=max(rss) if rss else None,unavailable_memory=3-len(rss)))
    actual = load(metrics/'summary.json')
    require(actual['groups'] == rows and actual['configurations'] == 240 and actual['failed'] == actual['missing'] == 0, 'metric raw/summary mismatch')
    counts['separate_metrics'] = dict(executions=240,failed=0,missing=0,radix_comparisons='unsupported')

    environments = {}
    for label,path in [('cpu_pipeline',cpu_raw/'environment.json'),('openmp',omp_raw/'environment.json')]:
        env = load(path)
        fields = dict(line.split(':',1) for line in env['cpu_probe']['stdout'].splitlines() if ':' in line)
        environments[label] = dict(source=str(path.relative_to(ROOT)),sha256=sha(path),os=env['os'],
            compiler=env['compiler']['stdout'].splitlines()[0],cmake=env['cmake']['stdout'].splitlines()[0],
            cpu_model=fields['Model name'].strip(),logical_cpus=env['logical_cpu_count'],
            mem_total_kib=int(env['linux_meminfo'].splitlines()[0].split()[1]),
            omp_environment=env.get('omp_environment'),captured_at_utc=env['captured_at_utc'])
    return dict(schema_version=1,scope='cpu_only_release_v1',raw_reanalysis_passed=True,
        benchmarks_executed=0,subprocess_execution_forbidden=True,counts=counts,environments=environments,
        gpu_inputs_consumed=False,approval_scope='Local CPU analysis/correctness; no CPU/GPU study eligibility claimed')
