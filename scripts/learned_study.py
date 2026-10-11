#!/usr/bin/env python3
"""Run/analyze the separate held-out learned-rank study; never invokes GPU work."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import statistics
import subprocess

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / 'docs/studies/learned_rank_v1.matrix.json'
ALGORITHMS = ['binary_search', 'learned_rank']
FIELDS = ['algorithm', 'operation', 'phase', 'trial_index', 'execution_order', 'elapsed_ns', 'queries', 'correctness']


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')


def samples(values):
    require(bool(values), 'empty sample')
    return dict(n=len(values), median=statistics.median(values), mean=statistics.mean(values),
                sample_sd=statistics.stdev(values) if len(values) > 1 else None, minimum=min(values), maximum=max(values))


def cells():
    matrix = json.loads(MATRIX.read_text())
    require(matrix['protocol'] == 'learned_rank_v1' and matrix['warmups'] == 1 and matrix['repetitions'] == 5, 'wrong matrix')
    require(len(matrix['cells']) == 48 and len({c['id'] for c in matrix['cells']}) == 48, 'matrix coverage')
    return matrix['cells']


def validate_cell(directory, cell):
    directory = Path(directory)
    require(not (directory / 'FAILED.json').exists(), 'failed configuration')
    complete = json.loads((directory / 'COMPLETE.json').read_text())
    require(complete == dict(complete=True, rows=18, diagnostic_queries=1000), 'incomplete configuration')
    meta = json.loads((directory / 'run.json').read_text())
    expected = dict(schema_version=1, protocol='learned_rank_v1', size=cell['size'], seed=cell['seed'],
                    distribution=cell['distribution'], query_seed=2718, queries=1000, hits=500, misses=500,
                    warmups=1, repetitions=5, radius=32, build_type='Release', clock='steady_clock')
    require(all(meta.get(k) == v for k, v in expected.items()), 'metadata/configuration mismatch')
    require(all(isinstance(meta.get(k), str) and meta[k].isdigit() for k in ['input_fingerprint', 'query_fingerprint']), 'missing dataset/query identity')
    with (directory / 'trials.csv').open(newline='') as stream:
        reader = csv.DictReader(stream)
        require(reader.fieldnames == FIELDS, 'trial schema mismatch')
        rows = list(reader)
    require(len(rows) == 18, 'missing trials')
    seen, groups = set(), {}
    for row in rows:
        require(set(row) == set(FIELDS) and None not in row.values(), 'malformed trial')
        require(row['phase'] in ['warmup', 'measure'] and row['correctness'] == 'passed', 'failed/unknown trial')
        require(all(row[k].isascii() and row[k].isdigit() for k in ['trial_index', 'execution_order', 'elapsed_ns', 'queries']), 'invalid numeric trial')
        trial, order = int(row['trial_index']), int(row['execution_order'])
        require(trial < (1 if row['phase'] == 'warmup' else 5), 'unexpected trial')
        identity = row['phase'], trial, row['algorithm'], row['operation']
        require(identity not in seen, 'duplicate trial'); seen.add(identity)
        if row['operation'] == 'build':
            require(row['algorithm'] == 'learned_rank' and row['queries'] == '0' and order == 0, 'invalid build row')
        else:
            require(row['operation'] == 'lookup_batch' and row['algorithm'] in ALGORITHMS and row['queries'] == '1000', 'invalid query row')
            require(order in [0, 1] and ALGORITHMS[(cell['seed'] % 2 + trial % 2 + order) % 2] == row['algorithm'], 'execution order mismatch')
        if row['phase'] == 'measure':
            groups.setdefault((row['algorithm'], row['operation']), []).append(int(row['elapsed_ns']))
    require(set(groups) == {('learned_rank', 'build'), ('learned_rank', 'lookup_batch'), ('binary_search', 'lookup_batch')} and
            all(len(v) == 5 for v in groups.values()), 'mode coverage incomplete')
    with (directory / 'diagnostics.csv').open(newline='') as stream:
        reader = csv.DictReader(stream)
        require(reader.fieldnames == ['query_id', 'target', 'expected_position', 'actual_position', 'predicted_position',
                'lower_bound_position', 'correction_distance', 'fallback', 'learned_comparisons', 'binary_comparisons'], 'diagnostic schema mismatch')
        diagnostics = list(reader)
    require(len(diagnostics) == 1000, 'missing diagnostics')
    hits, fallback, distances, comparisons = 0, 0, [], []
    for i, row in enumerate(diagnostics):
        require(row['query_id'] == str(i) and row['expected_position'] == row['actual_position'], 'diagnostic identity/output mismatch')
        require(-2**31 <= int(row['target']) < 2**31, 'target outside signed int32')
        if row['expected_position']:
            require(0 <= int(row['expected_position']) < cell['size'], 'invalid hit position'); hits += 1
        prediction, lower = int(row['predicted_position']), int(row['lower_bound_position'])
        require(0 <= prediction < cell['size'] and 0 <= lower <= cell['size'], 'invalid rank')
        distance = int(row['correction_distance'])
        require(distance == abs(prediction - lower) and row['fallback'] in ['true', 'false'], 'invalid correction diagnostic')
        require(int(row['learned_comparisons']) >= 0 and int(row['binary_comparisons']) >= 0, 'invalid comparison counts')
        if row['expected_position']: require(int(row['expected_position']) == lower, 'first-match position mismatch')
        fallback += row['fallback'] == 'true'; distances.append(distance)
        comparisons.append([int(row['learned_comparisons']), int(row['binary_comparisons'])])
    require(hits == 500, 'hit/miss ratio mismatch')
    memory = json.loads((directory / 'memory.json').read_text())
    require(memory['owned_capacity_bytes'] >= 4 * cell['size'] and memory['object_bytes'] > 0, 'invalid memory report')
    return dict(id=cell['id'], size=cell['size'], seed=cell['seed'], distribution=cell['distribution'],
                input_fingerprint=meta['input_fingerprint'], query_fingerprint=meta['query_fingerprint'],
                timings=[dict(algorithm=a, operation=o, unit='ns', **samples(v)) for (a, o), v in sorted(groups.items())],
                fallback_queries=fallback, queries=1000, mean_correction_distance=statistics.mean(distances),
                mean_learned_comparisons=statistics.mean(v[0] for v in comparisons),
                mean_binary_comparisons=statistics.mean(v[1] for v in comparisons), memory=memory)


def analyze(raw, output):
    raw, output = Path(raw), Path(output)
    require((raw / 'COMPLETE.json').is_file(), 'study incomplete')
    manifest = json.loads((raw / 'study.json').read_text())
    require(manifest['matrix_sha256'] == sha(MATRIX), 'matrix changed')
    require(manifest['cells'] == cells(), 'wrong study matrix')
    # Retained raw seal is checked before deriving any statistics.
    for relative, digest in manifest['raw_sha256'].items():
        require(Path(relative).as_posix() == relative and not Path(relative).is_absolute() and '..' not in Path(relative).parts, 'unsafe raw path')
        require(sha(raw / relative) == digest, 'raw record changed: ' + relative)
    datasets = [validate_cell(raw / c['id'], c) for c in cells()]
    aggregate = {}
    for dataset in datasets:
        for timing in dataset['timings']:
            key = dataset['size'], dataset['distribution'], timing['algorithm'], timing['operation']
            aggregate.setdefault(key, []).append(timing['median'])
    cross = [dict(size=n, distribution=d, algorithm=a, operation=o, unit='ns',
                  aggregation='equal-weight dataset medians', **samples(v)) for (n, d, a, o), v in sorted(aggregate.items())]
    output.mkdir()
    write(output / 'summary.json', dict(protocol='learned_rank_v1', configurations=48, measured_query_batches=480,
          warmup_query_batches=96, measured_builds=240, warmup_builds=48, failed=0, missing=0,
          datasets=datasets, cross_seed=cross))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size': 10, 'svg.hashsalt': 'learned_rank_v1'})
    plot_manifest = []
    for distribution in sorted({d['distribution'] for d in datasets}):
        fig, ax = plt.subplots(figsize=(7, 4.5), layout='constrained')
        for algorithm in ALGORITHMS:
            values = [r for r in cross if r['distribution'] == distribution and r['algorithm'] == algorithm and r['operation'] == 'lookup_batch']
            x, y = [r['size'] for r in values], [r['median'] / 1000 for r in values]
            ax.errorbar(x, y, yerr=[[r['median']/1000-r['minimum']/1000 for r in values],
                        [r['maximum']/1000-r['median']/1000 for r in values]], marker='o', capsize=4, label=algorithm)
        ax.set_xscale('log'); ax.set_ylim(bottom=0)
        ax.set(xlabel='Stored keys (log scale)', ylabel='Normalized batch average (ns/query)',
               title=f'{distribution}: median of 3 dataset medians\nBars: min–max across seeds; 5 trials/dataset; 1000 queries/batch')
        ax.legend(); ax.grid(alpha=.25)
        name = distribution + '_lookup.png'
        fig.savefig(output / name, dpi=220); plt.close(fig)
        plot_manifest.append(dict(file=name, source='summary.json', distribution=distribution, operation='lookup_batch',
                                  transformation='median dataset batch nanoseconds / 1000', spread='cross-seed min/max'))
    write(output / 'plots.json', plot_manifest)
    with (output / 'REPORT.md').open('x') as stream:
        stream.write('# Held-out learned rank study\n\n48 datasets; 480 measured lookup batches, 240 measured builds; '
                     '96 lookup and 48 build warm-ups. All outputs passed; zero missing/failed trials. '
                     'Each dataset has 500 hit and 500 miss queries. Repetitions are summarized within a dataset; '
                     'cross-seed values equally weight three dataset medians. All outliers retained.\n\n'
                     '|N|Distribution|Algorithm|Operation|Median of dataset medians (ns)|Cross-seed min–max (ns)|\n'
                     '|---:|---|---|---|---:|---:|\n')
        for r in cross:
            stream.write(f"|{r['size']}|{r['distribution']}|{r['algorithm']}|{r['operation']}|{r['median']:.1f}|{r['minimum']:.1f}–{r['maximum']:.1f}|\n")
        stream.write('\nLogical index capacity excludes allocator metadata. Process lifetime peak RSS includes input, queries, '
                     'index, runtime and allocator; it does not isolate index memory. No individual-query maximum was measured. '
                     'Frequency, thermal state and background load were not controlled. These are descriptive results, '
                     'with no statistical-significance or universal-ranking claim. See diagnostics in summary.json for fallback '
                     'frequency, rank correction distance and separate comparison counts.\n')
    write(output / 'SHA256.json', {p.name: sha(p) for p in sorted(output.iterdir()) if p.is_file()})


def run(binary, output):
    binary, output = Path(binary).resolve(strict=True), Path(output)
    output.mkdir()
    model = dict(protocol='learned_rank_v1', matrix_sha256=sha(MATRIX), binary=str(binary), binary_sha256=sha(binary), cells=cells())
    write(output / 'STARTED.json', model)
    for cell in model['cells']:
        argv = [str(binary), '--output', str((output / cell['id']).absolute()), '--size', str(cell['size']),
                '--seed', str(cell['seed']), '--distribution', cell['distribution']]
        result = subprocess.run(argv, text=True, capture_output=True, timeout=300)
        write(output / (cell['id'] + '.command.json'), dict(argv=argv, exit_code=result.returncode, stdout=result.stdout, stderr=result.stderr))
        print(cell['id'], 'exit', result.returncode, flush=True)
        require(result.returncode == 0, 'failed dataset: ' + cell['id'])
        validate_cell(output / cell['id'], cell)
    require(sha(binary) == model['binary_sha256'], 'executable changed during study')
    model['raw_sha256'] = {str(p.relative_to(output)): sha(p) for p in sorted(output.rglob('*')) if p.is_file()}
    write(output / 'study.json', model)
    write(output / 'COMPLETE.json', dict(complete=True, configurations=48, measured=720, warmups=144))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    sub = parser.add_subparsers(dest='mode', required=True)
    execute = sub.add_parser('run'); execute.add_argument('--binary', type=Path, required=True); execute.add_argument('--output', type=Path, required=True)
    analysis = sub.add_parser('analyze'); analysis.add_argument('--raw', type=Path, required=True); analysis.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.mode == 'run': run(args.binary, args.output)
    else: analyze(args.raw, args.output)
