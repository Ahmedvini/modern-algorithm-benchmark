#!/usr/bin/env python3
"""Validate structures_batch_v1, retaining separate build and lookup statistics."""
import argparse
import csv
import json
from pathlib import Path
from analyze_results import integer, summarize_samples
from analyze_search_results import CATEGORIES, QUERY_FIELDS, rows, fingerprint

ALGORITHMS = ('skip_list', 'btree_m10', 'btree_m16', 'btree_m32', 'btree_m64')
FIELDS = ('schema_version,protocol,run_id,run_kind,algorithm,distribution,size,seed,'
          'insertion_hash_fnv1a64,input_hash_fnv1a64,structure_seed,query_seed,operation,'
          'query_category,query_hash_fnv1a64,batch_size,hit_queries,miss_queries,phase,'
          'trial_index,execution_order,elapsed_ns,elapsed_unit,status,correctness,error,'
          'repetitions,warmups,compiler_id,compiler_version,build_type,sanitizers,platform,architecture').split(',')
IDENTITY = ('run_id', 'run_kind', 'distribution', 'size', 'seed', 'insertion_hash_fnv1a64',
            'input_hash_fnv1a64', 'structure_seed', 'query_seed', 'repetitions', 'warmups',
            'compiler_id', 'compiler_version', 'build_type', 'platform', 'architecture')


def validate_queries(directory, meta):
    categories = meta["categories"]
    names = [entry["category"] for entry in categories]
    if not names or names != [name for name in CATEGORIES if name in names]:
        raise ValueError("invalid category list/order")
    queries = rows(directory / "queries.csv", QUERY_FIELDS)
    cursor = 0
    expected_by_target = {}
    for entry in categories:
        name = entry["category"]
        if type(entry["available"]) is not bool or not isinstance(entry["reason"], str):
            raise ValueError("invalid category availability")
        count = meta["batch_size"] if entry["available"] else 0
        if entry["batch_size"] != count or bool(entry["reason"]) == entry["available"]:
            raise ValueError("unavailable category lacks reason or has invented queries")
        selected = queries[cursor:cursor+count]
        cursor += count
        if len(selected) != count:
            raise ValueError("missing query records")
        hits = 0
        for index, query in enumerate(selected):
            target = query["target"]
            value = int(target)
            if str(value) != target or not -(2**31) <= value < 2**31:
                raise ValueError("invalid signed int32 query target")
            if query["query_category"] != name or integer(query["query_id"]) != index:
                raise ValueError("query identity/order mismatch")
            present = bool(query["expected_position"])
            if query["expected_hit"] != str(present).lower():
                raise ValueError("query hit/expected-position mismatch")
            for field in ("selected_position", "expected_position"):
                if query[field] and integer(query[field]) >= meta["size"]:
                    raise ValueError("query position outside data")
            if bool(query["selected_position"]) != present or (present and
                    integer(query["expected_position"]) > integer(query["selected_position"])):
                raise ValueError("selected/first-match position mismatch")
            if target in expected_by_target and expected_by_target[target] != query["expected_position"]:
                raise ValueError("same key has inconsistent expected answer")
            expected_by_target[target] = query["expected_position"]
            expected_hit = name.startswith("hit_") or (name == "mixed_50" and index % 2 == 0)
            if present != expected_hit:
                raise ValueError("category hit/miss policy mismatch")
            if name == "miss_empty" and meta["size"] != 0:
                raise ValueError("empty-input policy used on nonempty data")
            if name in ("hit_first", "hit_middle", "hit_last"):
                position = {"hit_first": 0, "hit_middle": meta["size"]//2, "hit_last": meta["size"]-1}[name]
                if integer(query["selected_position"]) != position or target != selected[0]["target"]:
                    raise ValueError("fixed-rank query policy mismatch")
            hits += present
        if entry["hit_queries"] != hits or entry["miss_queries"] != count-hits or \
                entry["query_hash_fnv1a64"] != fingerprint(selected):
            raise ValueError("query fingerprint/count mismatch")
    if cursor != len(queries) or meta["query_rows"] != cursor or \
            meta["hit_queries"] != sum(entry["hit_queries"] for entry in categories) or \
            meta["miss_queries"] != sum(entry["miss_queries"] for entry in categories):
        raise ValueError("query plan totals mismatch")
    return categories


def read_bundle(directory, allow_incomplete=False):
    meta = json.loads((directory/'run.json').read_text())
    if meta.get('schema_version') != 1 or meta.get('protocol') != 'structures_batch_v1':
        raise ValueError('unsupported structure schema/protocol')
    algorithms = meta['algorithms']
    if not algorithms or len(set(algorithms)) != len(algorithms) or any(a not in ALGORITHMS for a in algorithms):
        raise ValueError('invalid structure list')
    for field in ('size', 'seed', 'structure_seed', 'query_seed', 'batch_size', 'repetitions', 'warmups', 'unique_keys'):
        if type(meta[field]) is not int or not 0 <= meta[field] <= 2**64-1:
            raise ValueError('invalid metadata integer')
    if meta['unique_keys'] > meta['size'] or bool(meta['unique_keys']) != bool(meta['size']) or \
            not 2 <= meta['batch_size'] <= 100000 or meta['batch_size'] % 2 or \
            not 1 <= meta['repetitions'] <= 10000 or not 0 <= meta['warmups'] <= 1000:
        raise ValueError('invalid size/batch/round bounds')
    if meta['run_kind'] not in ('performance', 'validation') or type(meta['sanitizers']) is not bool or \
            (meta['run_kind'] == 'performance' and (meta['build_type'] != 'Release' or meta['sanitizers'])):
        raise ValueError('invalid build/run kind')
    for field, value in [('dataset_generator', 'mt19937_64_v1'), ('query_generator', 'mt19937_64_queries_v1'),
                         ('input_order', 'ascending_reference_original_insertion'), ('clock', 'steady_clock'),
                         ('order_policy', 'seed_offset_cyclic_v1'), ('elapsed_unit', 'ns')]:
        if meta[field] != value:
            raise ValueError('unsupported generation/timing policy')
    for field in ('input_hash_fnv1a64', 'insertion_hash_fnv1a64'):
        integer(meta[field])
    categories = validate_queries(directory, meta)
    available = [e for e in categories if e['available']]
    operations = [('build', '')] + [('lookup', e['category']) for e in available]
    per_structure = len(operations)
    per_round = per_structure*len(algorithms)
    expected = per_round*(meta['repetitions']+meta['warmups'])
    if meta['expected_rows'] != expected:
        raise ValueError('invalid planned row count')
    data = rows(directory/'trials.csv', FIELDS)
    if len(data) > expected:
        raise ValueError('extra timing rows')
    for index, row in enumerate(data):
        if row['schema_version'] != '1' or row['protocol'] != 'structures_batch_v1' or row['elapsed_unit'] != 'ns':
            raise ValueError('invalid CSV protocol/unit')
        for field in IDENTITY:
            if row[field] != str(meta[field]):
                raise ValueError('trial metadata mismatch: '+field)
        if row['sanitizers'] != str(meta['sanitizers']).lower():
            raise ValueError('sanitizer metadata mismatch')
        warm = meta['warmups']*per_round
        phase = 'warmup' if index < warm else 'measure'
        trial, offset = divmod(index if phase == 'warmup' else index-warm, per_round)
        order, operation_index = divmod(offset, per_structure)
        algorithm = algorithms[(meta['seed'] % len(algorithms)+trial % len(algorithms)+order) % len(algorithms)]
        operation, category = operations[operation_index]
        if (row['phase'], integer(row['trial_index']), integer(row['execution_order']), row['algorithm'],
                row['operation'], row['query_category']) != (phase, trial, order, algorithm, operation, category):
            raise ValueError('trial identity/order mismatch')
        query_fields = ('query_hash_fnv1a64', 'batch_size', 'hit_queries', 'miss_queries')
        if operation == 'build':
            if any(row[field] for field in query_fields):
                raise ValueError('build row contains lookup metadata')
        else:
            entry = available[operation_index-1]
            if any(row[field] != str(entry[field]) for field in query_fields):
                raise ValueError('query batch identity mismatch')
        if row['status'] == 'ok':
            if row['correctness'] != 'passed' or row['error']:
                raise ValueError('successful row lacks correctness')
            integer(row['elapsed_ns'])
        elif row['status'] == 'error':
            if row['correctness'] not in ('failed', 'not_checked') or not row['error'] or \
                    (row['correctness'] == 'failed') != bool(row['elapsed_ns']) or index != len(data)-1:
                raise ValueError('invalid failure/fail-fast row')
            if row['elapsed_ns']:
                integer(row['elapsed_ns'])
        else:
            raise ValueError('unknown status')
    complete = (directory/'COMPLETE.json').exists()
    if complete:
        marker = json.loads((directory/'COMPLETE.json').read_text())
        if marker.get('schema_version') != 1 or marker.get('complete') is not True or marker.get('rows') != expected or \
                len(data) != expected or any(r['status'] != 'ok' for r in data) or (directory/'FAILED.json').exists():
            raise ValueError('completion contradicts observations')
    elif not allow_incomplete:
        raise ValueError('incomplete structure run; raw retained')
    groups = []
    for algorithm in algorithms:
        for operation, category in operations:
            matching = [r for r in data if (r['algorithm'], r['operation'], r['query_category']) == (algorithm, operation, category)]
            measured = [r for r in matching if r['phase'] == 'measure']
            warmups = [r for r in matching if r['phase'] == 'warmup']
            stats = summarize_samples([integer(r['elapsed_ns']) for r in measured if r['status'] == 'ok'])
            group = {field: meta[field] for field in IDENTITY}
            group.update(algorithm=algorithm, operation=operation, query_category=category, run_complete=complete,
                         unique_keys=meta['unique_keys'], batch_size=meta['batch_size'] if operation == 'lookup' else None,
                         successful_trials=stats['successful_trials'], failed_trials=len(measured)-stats['successful_trials'],
                         missing_measured_trials=meta['repetitions']-len(measured), warmup_rows=len(warmups),
                         failed_warmups=sum(r['status'] != 'ok' for r in warmups), missing_warmups=meta['warmups']-len(warmups))
            for name in ('median', 'mean', 'stdev', 'min', 'max'):
                value = stats[name+'_ns'];group[name+'_ns'] = value
                if operation == 'lookup':
                    group[name+'_normalized_ns_per_query'] = value/meta['batch_size'] if value is not None else None
            groups.append(group)
    return complete, groups, [dict(e, run_id=meta['run_id']) for e in categories]


def analyze(source, allow_incomplete=False):
    matrix_path = source/'matrix.json'
    missing, groups, availability = [], [], []
    complete = True
    if matrix_path.exists():
        matrix = json.loads(matrix_path.read_text());names = matrix['runs']
        if matrix.get('schema_version') != 1 or matrix.get('protocol') != 'structures_batch_v1' or not names or \
                len(set(names)) != len(names) or any(Path(n).name != n or n in ('.', '..') for n in names) or \
                len(matrix['commands']) != len(names):
            raise ValueError('invalid matrix plan')
        directories = [source/n for n in names];complete = (source/'COMPLETE.json').exists()
        if complete:
            marker = json.loads((source/'COMPLETE.json').read_text())
            if marker.get('schema_version') != 1 or marker.get('complete') is not True or marker.get('runs') != len(names) or (source/'FAILED.json').exists():
                raise ValueError('invalid matrix completion')
            for name, command in zip(names, matrix['commands']):
                record = json.loads((source/(name+'_command.json')).read_text())
                if record['exit_code'] != 0 or record['command'] != command:
                    raise ValueError('matrix child failed/mismatch')
        elif not allow_incomplete:
            raise ValueError('incomplete matrix')
    else:
        directories = [source]
    for directory in directories:
        if not (directory/'run.json').exists():
            if not allow_incomplete:
                raise ValueError('missing planned run')
            complete = False;missing.append(str(directory));continue
        done, run_groups, plan = read_bundle(directory, allow_incomplete)
        if matrix_path.exists() and json.loads((directory/'run.json').read_text())['invocation'] != matrix['commands'][names.index(directory.name)]:
            raise ValueError('child invocation mismatch')
        complete = complete and done;groups.extend(run_groups);availability.extend(plan)
    return dict(schema_version=1, summary_kind='structures_batch_summary', source=str(source.resolve()),
                complete=complete, elapsed_unit='ns', outlier_policy='retain_all',
                stdev_definition='sample_ddof_1; null below two successes',
                normalized_latency_definition='lookup batch_ns/batch_size; not individual-query latency',
                missing_runs=missing, availability=availability, groups=groups)


def main():
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument('source', type=Path);parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--allow-incomplete', action='store_true');args = parser.parse_args()
    try:
        result = analyze(args.source, args.allow_incomplete)
        serialized = json.dumps(result, indent=2, allow_nan=False)+'\n'
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(serialized)
    except (OSError, ValueError, KeyError, TypeError, csv.Error, ZeroDivisionError, OverflowError) as error:
        parser.exit(1, f'structure analysis failed: {error}\n')
    print(args.output)
    if not result['complete']:
        parser.exit(1, 'incomplete structure results retained\n')


if __name__ == '__main__':
    main()
