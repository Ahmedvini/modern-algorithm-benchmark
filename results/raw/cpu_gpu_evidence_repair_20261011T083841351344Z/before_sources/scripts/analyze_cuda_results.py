#!/usr/bin/env python3
"""Strict prepared CUB timing summaries; retain failures and every outlier."""
import argparse
import csv
import json
import math
from pathlib import Path
from analyze_results import integer, summarize_samples

PROTOCOL = 'cuda_sort_timing_v1'
METRICS = ['h2d_ns', 'device_sort_ns', 'd2h_ns', 'end_to_end_ns']
SHARED = ['schema_version', 'protocol', 'run_id', 'algorithm', 'implementation_version',
          'distribution', 'size', 'seed', 'nearly_sorted_swaps', 'duplicate_cardinality',
          'dataset_generator', 'input_hash_fnv1a64']
FIELDS = SHARED + ['phase', 'trial_index'] + METRICS + ['elapsed_unit', 'status', 'correctness', 'error']
DISTRIBUTIONS = ['uniform', 'sorted', 'reverse_sorted', 'duplicate_heavy', 'nearly_sorted', 'signed_edges']


def require(condition, message):
    if not condition:
        raise ValueError(message)


def uint_meta(meta, key, low, high):
    value = meta.get(key)
    require(type(value) is int and low <= value <= high, 'invalid metadata ' + key)
    return value


def read_bundle(path, allow_incomplete=False):
    meta = json.loads((path / 'run.json').read_text())
    require(type(meta.get('schema_version')) is int and meta['schema_version'] == 1 and
            meta.get('protocol') == PROTOCOL and meta.get('algorithm') == 'cub_radix_sort' and
            meta.get('implementation_version') == 'cub_radix_sort_v1', 'incompatible identity')
    require(meta.get('elapsed_unit') == 'ns' and meta.get('allocation_policy') == 'prepared_pinned_reuse_v1' and
            meta.get('stream_policy') == 'private_nonblocking_serial' and
            meta.get('end_to_end_clock') == 'steady_clock' and
            meta.get('phase_clock') == 'cuda_event_float_ms_to_ns', 'incompatible timing semantics')
    require(meta.get('distribution') in DISTRIBUTIONS, 'unknown distribution')
    require(meta.get('dataset_generator') == ('signed_edges_v1' if meta['distribution'] == 'signed_edges'
                                            else 'mt19937_64_v1'), 'generator mismatch')
    uint_meta(meta, 'size', 0, 1000000); uint_meta(meta, 'seed', 0, 2**64-1)
    uint_meta(meta, 'nearly_sorted_swaps', 0, 10000000); uint_meta(meta, 'duplicate_cardinality', 1, 2**32)
    repetitions = uint_meta(meta, 'repetitions', 1, 10000)
    warmups = uint_meta(meta, 'warmups', 0, 1000)
    require(uint_meta(meta, 'expected_rows', 1, 11000) == warmups + repetitions, 'row plan mismatch')
    require(meta.get('cub_version') == 300001 and type(meta['cub_version']) is int, 'unreviewed CUB')
    require(meta.get('run_kind') in ['validation', 'performance'], 'invalid run kind')
    require(meta.get('sanitizers') is False, 'CUDA sanitizer build unsupported')
    if meta['run_kind'] == 'performance':
        require(meta.get('build_type') == 'Release', 'performance must be Release')
    for key in ['compiler_id', 'compiler_version', 'build_type', 'platform', 'architecture', 'gpu_name',
                'cuda_compiler_version', 'cuda_toolkit_version', 'run_id']:
        require(isinstance(meta.get(key), str) and bool(meta[key]), 'missing metadata ' + key)
    for key in ['runtime_api_version', 'driver_api_version']:
        uint_meta(meta, key, 13000, 2**31-1)
    require(uint_meta(meta, 'requested_device', 0, 2**31-1) == uint_meta(meta, 'actual_device', 0, 2**31-1),
            'device mismatch')
    uint_meta(meta, 'compute_major', 1, 100); uint_meta(meta, 'compute_minor', 0, 100)
    uint_meta(meta, 'device_memory_bytes', 1, 2**64-1)
    uint_meta(meta, 'workspace_bytes', 0, 2**64-1)
    require(isinstance(meta.get('input_hash_fnv1a64'), str), 'invalid fingerprint')
    integer(meta['input_hash_fnv1a64'])
    rows = []
    with (path / 'trials.csv').open(newline='') as stream:
        reader = csv.DictReader(stream, strict=True)
        require(reader.fieldnames == FIELDS, 'CSV schema mismatch')
        for row in reader:
            require(set(row) == set(FIELDS) and all(x is not None for x in row.values()), 'malformed row')
            require(all(row[k] == str(meta[k]) for k in SHARED), 'CSV metadata mismatch')
            require(row['elapsed_unit'] == 'ns', 'invalid unit')
            phase = 'warmup' if len(rows) < warmups else 'measure'
            trial = len(rows) if phase == 'warmup' else len(rows) - warmups
            require(row['phase'] == phase and integer(row['trial_index']) == trial and
                    trial < (warmups if phase == 'warmup' else repetitions), 'duplicate/misordered/excess trial')
            if row['status'] == 'ok':
                require(row['correctness'] == 'passed' and not row['error'], 'contradictory correctness')
                for key in METRICS:
                    value = float(row[key])
                    require(math.isfinite(value) and value >= 0, 'invalid timing')
                    if meta['size'] < 2 and key != 'end_to_end_ns':
                        require(value == 0, 'trivial input should skip GPU phases')
            else:
                require(row['status'] == 'error' and row['correctness'] in ['failed', 'not_checked'] and
                        bool(row['error']) and all(row[k] == '' for k in METRICS), 'invalid failure row')
            require(not rows or rows[-1]['status'] == 'ok', 'rows after failure')
            rows.append(row)
    complete = (path / 'COMPLETE.json').exists()
    if complete:
        done = json.loads((path / 'COMPLETE.json').read_text())
        require(done.get('schema_version') == 1 and done.get('complete') is True and
                done.get('rows') == meta['expected_rows'] and len(rows) == meta['expected_rows'] and
                all(r['status'] == 'ok' for r in rows) and not (path / 'FAILED.json').exists() and
                not (path / 'INTERRUPTED.json').exists(), 'contradictory completion')
    require(complete or allow_incomplete, 'incomplete/failed bundle')
    measured = [r for r in rows if r['phase'] == 'measure']
    successes = [r for r in measured if r['status'] == 'ok']
    group = {key: meta[key] for key in SHARED + ['repetitions', 'warmups', 'gpu_name', 'cub_version',
                                                'build_type', 'run_kind']}
    group.update(complete=complete, successful_trials=len(successes), failed_trials=len(measured)-len(successes),
                 missing_trials=repetitions-len(measured), warmup_rows=len(rows)-len(measured),
                 failed_warmups=sum(r['phase'] == 'warmup' and r['status'] != 'ok' for r in rows),
                 missing_warmups=warmups-sum(r['phase'] == 'warmup' for r in rows),
                 metrics={key: summarize_samples([float(r[key]) for r in successes]) for key in METRICS})
    return meta, group


def analyze(source, allow_incomplete=False):
    source = Path(source)
    groups = []; missing = []; complete = True
    if (source / 'matrix.json').exists():
        matrix = json.loads((source / 'matrix.json').read_text())
        require(matrix.get('schema_version') == 1 and matrix.get('protocol') == PROTOCOL, 'invalid matrix')
        configs = matrix['configurations']
        require(isinstance(configs, list) and bool(configs), 'empty matrix')
        names = [c['name'] for c in configs]
        identities = [(c['size'], c['distribution'], c['seed']) for c in configs]
        require(len(set(names)) == len(names) and len(set(identities)) == len(identities) and
                all(Path(n).name == n and n not in ['.', '..'] for n in names), 'invalid/duplicate configuration')
        complete = (source / 'COMPLETE.json').exists()
        if complete:
            marker = json.loads((source / 'COMPLETE.json').read_text())
            require(marker.get('complete') is True and marker.get('runs') == len(configs) and
                    not (source / 'FAILED.json').exists() and not (source / 'INTERRUPTED.json').exists(), 'invalid matrix completion')
        require(complete or allow_incomplete, 'incomplete matrix')
        for c in configs:
            path = source / c['name']
            if not (path / 'run.json').is_file():
                require(allow_incomplete, 'missing configuration')
                missing.append(c); complete = False; continue
            meta, group = read_bundle(path, allow_incomplete)
            require(all(meta[k] == c[k] for k in ['size', 'distribution', 'seed', 'warmups', 'repetitions']) and
                    meta['run_id'] == c['name'], 'configuration differs from plan')
            complete = complete and group['complete']; groups.append(group)
    else:
        _, group = read_bundle(source, allow_incomplete); groups.append(group); complete = group['complete']
    require(complete or allow_incomplete, 'incomplete experiment')
    return dict(schema_version=1, protocol=PROTOCOL, source=str(source.resolve()), complete=complete,
                elapsed_unit='ns', aggregation='within_dataset; sample stdev ddof1; retain all outliers',
                groups=groups, missing_configurations=missing)


def main():
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument('source', type=Path); parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--allow-incomplete', action='store_true'); args = parser.parse_args()
    try:
        result = analyze(args.source, args.allow_incomplete)
        with args.output.open('x') as stream:json.dump(result, stream, indent=2, allow_nan=False);stream.write('\n')
        return 0 if result['complete'] else 1
    except (OSError, ValueError, KeyError, TypeError, csv.Error) as error:
        print('CUDA analysis failed: ' + str(error)); return 1
if __name__ == '__main__': raise SystemExit(main())
