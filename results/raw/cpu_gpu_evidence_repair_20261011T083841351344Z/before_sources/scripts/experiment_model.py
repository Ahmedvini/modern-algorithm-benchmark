#!/usr/bin/env python3
"""Strict plans, traceable observations and hierarchical experiment statistics."""
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import statistics
import sys

import analyze_results as sorting
import analyze_search_results as search
import analyze_structure_results as structures
from run_matrix import DISTRIBUTIONS

PROTOCOL = 'experiment_pipeline_v1'
FAMILIES = ('sorting', 'search', 'structures')
ALGORITHMS = {
    'sorting': ['std_sort', 'quick_sort', 'pdq_sort', 'tim_sort', 'merge_sort', 'radix_sort'],
    'search': ['linear_search', 'binary_search', 'exponential_search'],
    'structures': list(structures.ALGORITHMS),
}
FAMILY_PROTOCOL = dict(zip(FAMILIES, ['sort_timing_v1', 'search_batch_v1', 'structures_batch_v1']))
RUNNERS = dict(zip(FAMILIES, ['run_matrix.py', 'run_search_matrix.py', 'run_structure_matrix.py']))
BINARIES = dict(zip(FAMILIES, ['sort_benchmark', 'search_benchmark', 'structure_benchmark']))
OPTIONS = dict(zip(FAMILIES, ['sorts', 'searches', 'structures']))
MODULES = dict(zip(FAMILIES, [sorting, search, structures]))
ROOT = Path(__file__).resolve().parents[1]


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)


def fingerprint(data):
    return hashlib.sha256(canonical(data).encode('utf-8')).hexdigest()


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def unique_object(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError('duplicate JSON key: ' + key)
        obj[key] = value
    return obj


def load_json(path):
    def invalid(value):
        raise ValueError('nonfinite JSON constant: ' + value)
    return json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=unique_object, parse_constant=invalid)


def save_json(path, data):
    content = json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + '\n'
    with Path(path).open('x', encoding='utf-8') as stream:
        stream.write(content)


def tree_hashes(path):
    return {str(p.relative_to(path)): sha256(p) for p in sorted(Path(path).rglob('*')) if p.is_file()}


def preset(name):
    if name not in ('smoke', 'full'):
        raise ValueError('unknown preset')
    full = name == 'full'
    return dict(schema_version=1, protocol=PROTOCOL, profile=name,
                sizes=[1000, 10000, 100000, 1000000] if full else [0, 64, 1000],
                distributions=list(DISTRIBUTIONS) if full else ['uniform', 'duplicate_heavy'],
                seeds=[1729, 42, 2718] if full else [1729, 42], query_seeds=[2718],
                structure_seed=1729, queries=1000 if full else 64, repetitions=5, warmups=1,
                distinct=16, swaps=None, memory_limit_mib=1024, categories=list(search.CATEGORIES),
                algorithms={f:list(a) for f,a in ALGORITHMS.items()}, validation_only=False)


def unsigned(value, low=0, high=2**64-1):
    if type(value) is not int or not low <= value <= high:
        raise ValueError('integer outside permitted bounds')
    return value


def validate_config(config):
    if not isinstance(config, dict) or set(config) != set(preset('smoke')):
        raise ValueError('configuration fields differ from schema1')
    if type(config['schema_version']) is not int or config['schema_version'] != 1 or config['protocol'] != PROTOCOL:
        raise ValueError('incompatible orchestration protocol')
    if config['profile'] not in ('smoke', 'full', 'custom'):
        raise ValueError('invalid profile')
    if config['profile'] != 'custom' and config != preset(config['profile']):
        raise ValueError('changed frozen preset must be labeled custom')
    for key, allowed, numeric in [('sizes', None, True), ('seeds', None, True), ('query_seeds', None, True),
                                  ('distributions', DISTRIBUTIONS, False), ('categories', search.CATEGORIES, False)]:
        values = config[key]
        if not isinstance(values, list) or not 1 <= len(values) <= 256:
            raise ValueError('invalid list: ' + key)
        if numeric:
            for value in values:
                unsigned(value, high=1000000 if key == 'sizes' else 2**64-1)
        elif any(type(v) is not str or v not in allowed for v in values):
            raise ValueError('unknown name: ' + key)
        if len(set(values)) != len(values):
            raise ValueError('duplicate matrix values')
    if config['categories'] != [c for c in search.CATEGORIES if c in config['categories']]:
        raise ValueError('categories must follow frozen registry order')
    if not isinstance(config['algorithms'], dict) or set(config['algorithms']) != set(FAMILIES):
        raise ValueError('all three benchmark families required')
    for family in FAMILIES:
        names = config['algorithms'][family]
        if not isinstance(names, list) or not names or any(type(n) is not str or n not in ALGORITHMS[family] for n in names):
            raise ValueError('unknown algorithm')
        if names != [n for n in ALGORITHMS[family] if n in names]:
            raise ValueError('duplicate or noncanonical algorithm list')
    unsigned(config['structure_seed']); unsigned(config['queries'], 2, 100000)
    if config['queries'] % 2:
        raise ValueError('query batches must be even')
    unsigned(config['repetitions'], 1, 10000); unsigned(config['warmups'], 0, 1000)
    unsigned(config['distinct'], 1, 2**32); unsigned(config['memory_limit_mib'], 1, 65536)
    if config['swaps'] is not None:
        unsigned(config['swaps'], 0, 10000000)
    if type(config['validation_only']) is not bool:
        raise ValueError('invalid validation_only')
    estimates = resources(config)
    if any(n > 256 for n in estimates['configurations'].values()) or estimates['total_row_upper_bound'] > 100000:
        raise ValueError('matrix exceeds configuration/row limits')
    if estimates['workspace_bytes_estimate'] > config['memory_limit_mib'] * 1024**2:
        raise ValueError('workspace exceeds planning budget')
    return config


def configurations(config, family):
    return [(n, seed, query_seed, distribution)
            for n in config['sizes'] for seed in config['seeds']
            for query_seed in ([None] if family == 'sorting' else config['query_seeds'])
            for distribution in config['distributions']]


def resources(config):
    counts = {f: len(configurations(config, f)) for f in FAMILIES}
    categories = len(config['categories'])
    per_config = {f: len(config['algorithms'][f]) * (1 if f == 'sorting' else categories + (f == 'structures')) for f in FAMILIES}
    measured = {f: counts[f]*per_config[f]*config['repetitions'] for f in FAMILIES}
    warmups = {f: counts[f]*per_config[f]*config['warmups'] for f in FAMILIES}
    rows = sum(measured.values()) + sum(warmups.values())
    workspace = 512*max(config['sizes']) + 128*config['queries']*9
    queries = (counts['search']+counts['structures'])*categories*config['queries']
    figure_pairs = len(config['distributions'])*(2 + 2*categories)*2 + 1
    disk = sum(counts.values())*2*1024**2 + rows*4096 + queries*256 + figure_pairs*512*1024 + 32*1024**2
    return dict(configurations=counts, measured_row_upper_bounds=measured, warmup_row_upper_bounds=warmups,
                total_row_upper_bound=rows, query_record_upper_bound=queries, figure_pair_upper_bound=figure_pairs,
                workspace_bytes_estimate=workspace, disk_bytes_allowance=disk,
                required_available_memory_bytes=max(512*1024**2, 2*workspace),
                required_free_disk_bytes=max(128*1024**2, 2*disk),
                runtime_seconds_estimate=None, runtime_method='After validated pilot: assess_experiment.py; overhead-inclusive complexity scaling, safety factor4; no guessed runtime.',
                note='Planning allowances; not measured memory/disk or hard RSS limits. Query availability changes row counts.')


def safe_id(run_id):
    if not isinstance(run_id, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,79}', run_id):
        raise ValueError('run ID must be 1..80 safe characters starting alphanumeric')
    return run_id


def plan(config, run_id, raw_root, processed_root, figure_root, build_dir):
    validate_config(config); safe_id(run_id)
    roots = [Path(p).resolve() for p in (raw_root, processed_root, figure_root)]
    paths = [p/run_id for p in roots]
    resolved = [p.resolve() for p in paths]
    for i, a in enumerate(resolved):
        for b in resolved[i+1:]:
            if a == b or a in b.parents or b in a.parents:
                raise ValueError('raw/derived paths must not overlap')
    build_dir = Path(build_dir).resolve()
    families = []
    for family in FAMILIES:
        binary = build_dir/BINARIES[family]; output = paths[0]/family
        base = [sys.executable, str(ROOT/'scripts'/RUNNERS[family]), '--binary', str(binary), '--output', str(output),
                '--sizes', ','.join(map(str, config['sizes'])), '--seeds', ','.join(map(str, config['seeds'])),
                '--distributions', ','.join(config['distributions']), '--'+OPTIONS[family], ','.join(config['algorithms'][family]),
                '--repetitions', str(config['repetitions']), '--warmups', str(config['warmups']),
                '--memory-limit-mib', str(config['memory_limit_mib']), '--distinct', str(config['distinct'])]
        if family != 'sorting':
            base += ['--query-seeds', ','.join(map(str, config['query_seeds'])), '--queries', str(config['queries']),
                     '--categories', ','.join(config['categories'])]
        if family == 'structures':
            base += ['--structure-seed', str(config['structure_seed'])]
        if config['swaps'] is not None:
            base += ['--swaps', str(config['swaps'])]
        if config['validation_only']:
            base += ['--validation-only']
        children = []
        for i, (n, seed, qseed, distribution) in enumerate(configurations(config, family)):
            name = f'run_{i:06d}'
            selector = {'sorting':'sort', 'search':'search', 'structures':'structure'}[family]
            command = [str(binary), '--output', str(output/name), '--'+selector, ','.join(config['algorithms'][family])]
            if family == 'structures':
                command += ['--structure-seed', str(config['structure_seed'])]
            command += ['--size', str(n), '--seed', str(seed)]
            if family != 'sorting':
                command += ['--query-seed', str(qseed)]
            command += ['--distribution', distribution]
            if family != 'sorting':
                command += ['--categories', ','.join(config['categories']), '--queries', str(config['queries'])]
            command += ['--repetitions', str(config['repetitions']), '--warmups', str(config['warmups']),
                        '--memory-limit-mib', str(config['memory_limit_mib']), '--distinct', str(config['distinct']),
                        '--run-id', family+':'+name]
            if config['swaps'] is not None:
                command += ['--swaps', str(config['swaps'])]
            if config['validation_only']:
                command += ['--validation-only']
            children.append(dict(name=name, size=n, seed=seed, query_seed=qseed, distribution=distribution, command=command))
        families.append(dict(family=family, protocol=FAMILY_PROTOCOL[family], command=base, children=children))
    return dict(schema_version=1, protocol=PROTOCOL, run_id=run_id, configuration=config,
                configuration_sha256=fingerprint(config), raw_path=str(paths[0]), processed_path=str(paths[1]),
                figure_path=str(paths[2]), build_directory=str(build_dir), families=families, resources=resources(config))


def strict_files(path):
    if path.is_symlink():
        raise ValueError('symlink input rejected')
    for p in path.rglob('*'):
        if p.is_symlink():
            raise ValueError('symlink raw artifact rejected')
        if p.suffix == '.json' and p.is_file():
            load_json(p)


def stats(samples):
    values = list(samples)
    if any(type(x) not in (int, float) or not math.isfinite(x) or x < 0 for x in values):
        raise ValueError('invalid statistics sample')
    return dict(count=len(values), median=statistics.median(values) if values else None,
                mean=statistics.mean(values) if values else None,
                sample_stdev=statistics.stdev(values) if len(values)>1 else None,
                minimum=min(values) if values else None, maximum=max(values) if values else None)


def normalize(row, meta, family, bundle, row_index):
    required = ('run_id','run_kind','algorithm','distribution','size','seed','input_hash_fnv1a64',
                'phase','trial_index','execution_order','status','correctness','error','compiler_id','compiler_version',
                'build_type','platform','architecture','protocol')
    obj = {key: row[key] for key in required}
    obj.update(family=family, operation=row.get('operation', 'sort' if family=='sorting' else 'lookup'),
               source_csv=str(bundle/'trials.csv'), source_row_index=row_index, raw=row.copy(),
               elapsed_unit=row['elapsed_unit'], elapsed_ns=sorting.integer(row['elapsed_ns']) if row['elapsed_ns'] else None,
               sanitizers=meta['sanitizers'], dataset_generator=meta['dataset_generator'],
               source_manifest_sha256=sha256(bundle/'source_hashes.json'),
               cmake_flags={k:v for k,v in meta.items() if 'flags' in k},
               cmake_flags_sha256=fingerprint({k:v for k,v in meta.items() if 'flags' in k}),
               nearly_sorted_swaps=meta['nearly_sorted_swaps'], duplicate_cardinality=meta['duplicate_cardinality'])
    for key in ('size','seed','trial_index','execution_order'):
        obj[key]=sorting.integer(obj[key])
    for key in ('query_category','query_hash_fnv1a64','insertion_hash_fnv1a64'):
        obj[key]=row.get(key) or None
    for key in ('query_seed','structure_seed','batch_size','hit_queries','miss_queries'):
        obj[key]=sorting.integer(row[key]) if row.get(key) else None
    if obj['operation']=='build':
        obj['query_seed']=meta['query_seed'] # configuration provenance, not a build input
    return obj


def validate_study(source, allow_incomplete=False):
    source=Path(source).resolve();strict_files(source)
    study=load_json(source/'experiment.json');config=study['configuration'];validate_config(config)
    if study.get('protocol')!=PROTOCOL or study.get('schema_version')!=1 or study['configuration_sha256']!=fingerprint(config):
        raise ValueError('invalid experiment identity')
    expected=plan(config, study['run_id'], Path(study['raw_path']).parent, Path(study['processed_path']).parent,
                  Path(study['figure_path']).parent, study['build_directory'])
    if study!=expected or Path(study['raw_path'])!=source:
        raise ValueError('experiment plan differs from frozen configuration/paths')
    observations=[];availability=[];missing=[];commands=[];complete=True;seen=set();input_identity={};query_identity={}
    for entry in study['families']:
        family=entry['family'];directory=source/family
        command_record=source/(family+'_command.json')
        if command_record.exists():
            cmd=load_json(command_record)
            if cmd['command']!=entry['command'] or cmd['status'] not in ('successful','failed','interrupted'):
                raise ValueError('family command mismatch')
            if cmd['exit_code'] is not None and type(cmd['exit_code']) is not int:
                raise ValueError('command exit code must be integer or null')
            if (cmd['status']=='successful' and cmd['exit_code']!=0) or (cmd['status']=='failed' and cmd['exit_code']==0):
                raise ValueError('command status/exit mismatch')
            # Parent interruption can occur as a child exits successfully; keep
            # the interrupted outcome instead of inventing a nonzero child exit.
            commands.append(dict(family=family,status=cmd['status'],exit_code=cmd['exit_code']))
            if cmd['status']!='successful':complete=False
        else:
            complete=False;commands.append(dict(family=family,status='missing',exit_code=None))
        matrix_path=directory/'matrix.json'
        if matrix_path.exists():
            matrix=load_json(matrix_path)
            if type(matrix['schema_version']) is not int or matrix['schema_version']!=1 or matrix['protocol']!=entry['protocol'] or matrix['invocation']!=entry['command'][1:] or \
                    matrix['runs']!=[x['name'] for x in entry['children']] or matrix['commands']!=[x['command'] for x in entry['children']]:
                raise ValueError('matrix differs from experiment plan')
            if any(p.is_dir() and p.name not in matrix['runs'] for p in directory.iterdir()):
                raise ValueError('unplanned configuration directory')
            # Reuse full family validators, including query definitions and schedules.
            family_summary=MODULES[family].analyze(directory, allow_incomplete=True)
            complete=complete and family_summary['complete']
            availability += [dict(e,family=family) for e in family_summary.get('availability',[])]
        else:
            complete=False
        for child in entry['children']:
            bundle=directory/child['name'];meta_path=bundle/'run.json'
            if not meta_path.exists():
                if (bundle/'trials.csv').exists():raise ValueError('timings without metadata')
                complete=False;missing.append(dict(family=family,configuration=child,
                    known_missing_measured_trials=config['repetitions']*len(config['algorithms'][family]) if family!='search' else 0,
                    lookup_missing_measured_upper_bound=config['repetitions']*len(config['algorithms'][family])*len(config['categories']) if family!='sorting' else 0))
                continue
            if not matrix_path.exists():raise ValueError('bundle without matrix plan')
            meta=load_json(meta_path)
            if type(meta.get('schema_version')) is not int or meta['schema_version']!=1 or meta.get('protocol')!=FAMILY_PROTOCOL[family]:
                raise ValueError('invalid family protocol/schema')
            for key,value in [('size',child['size']),('seed',child['seed']),('distribution',child['distribution']),
                              ('algorithms',config['algorithms'][family]),('repetitions',config['repetitions']),('warmups',config['warmups']),
                              ('duplicate_cardinality',config['distinct']),('memory_limit_mib',config['memory_limit_mib']),
                              ('dataset_generator','mt19937_64_v1'),('order_policy','seed_offset_cyclic_v1'),('clock','steady_clock')]:
                if meta.get(key)!=value or (type(value) is int and type(meta.get(key)) is not int):
                    raise ValueError('configuration metadata mismatch: '+key)
            if meta['invocation']!=child['command'] or meta['run_id']!=family+':'+child['name']:
                raise ValueError('child invocation/run ID mismatch')
            swaps=0 if child['distribution']=='sorted' else (config['swaps'] if config['swaps'] is not None else child['size']//100)
            if meta['nearly_sorted_swaps']!=swaps or meta['run_kind']!=('validation' if config['validation_only'] else 'performance'):
                raise ValueError('dataset/run-kind mismatch')
            if not config['validation_only'] and (meta['build_type']!='Release' or meta['sanitizers'] is not False):
                raise ValueError('primary timing requires Release without sanitizers')
            if type(meta['sanitizers']) is not bool:raise ValueError('invalid sanitizer field')
            for key in ('compiler_id','compiler_version','build_type','platform','architecture'):
                if not isinstance(meta[key],str) or not meta[key]:raise ValueError('invalid build metadata')
            if family!='sorting':
                if meta['query_seed']!=child['query_seed'] or meta['batch_size']!=config['queries'] or \
                        [c['category'] for c in meta['categories']]!=config['categories']:
                    raise ValueError('query configuration mismatch')
            if family=='structures' and meta['structure_seed']!=config['structure_seed']:
                raise ValueError('structure seed mismatch')
            files=load_json(bundle/'source_hashes.json')
            if not isinstance(files,dict) or not files.get('files'):raise ValueError('missing source manifest')
            paths=[f['path'] for f in files['files']]
            if len(set(paths))!=len(paths) or any(not re.fullmatch('[0-9a-f]{64}',f['sha256']) for f in files['files']):
                raise ValueError('invalid source manifest')
            child_record=directory/(child['name']+'_command.json')
            if child_record.exists():
                record=load_json(child_record)
                if record['command']!=child['command'] or type(record['exit_code']) is not int:
                    raise ValueError('child command mismatch')
                if record['exit_code']!=0:complete=False
            else:complete=False
            module=MODULES[family];validated=module.read_bundle(bundle,allow_incomplete=True)
            complete=complete and validated[0]
            rows=search.rows(bundle/'trials.csv',module.FIELDS)
            failed=False
            for index,row in enumerate(rows):
                if failed:raise ValueError('observations after failure')
                failed=row['status']=='error'
                if failed and ((row['correctness']=='failed') != bool(row['elapsed_ns'])):
                    raise ValueError('invalid failure timing semantics')
                obj=normalize(row,meta,family,bundle,index)
                identity=(family,obj['run_id'],obj['algorithm'],obj['operation'],obj['query_category'],obj['phase'],obj['trial_index'])
                if identity in seen:raise ValueError('duplicate unified trial identity')
                seen.add(identity);observations.append(obj)
            identity=(child['size'],child['seed'],child['distribution'])
            if family!='sorting':
                reference=(meta['input_hash_fnv1a64'],(bundle/'queries.csv').read_bytes())
                qkey=identity+(child['query_seed'],)
                if qkey in query_identity and query_identity[qkey]!=reference:raise ValueError('search/structure workloads differ')
                query_identity[qkey]=reference
            if family in ('sorting','structures'):
                source_hash=meta['input_hash_fnv1a64'] if family=='sorting' else meta['insertion_hash_fnv1a64']
                if identity in input_identity and input_identity[identity]!=source_hash:raise ValueError('original inputs differ across families')
                input_identity[identity]=source_hash
    collected=source/'COLLECTED.json'
    if collected.exists():
        marker=load_json(collected)
        if marker.get('protocol')!=PROTOCOL or marker.get('configuration_sha256')!=study['configuration_sha256'] or marker.get('complete') is not True or marker.get('observations')!=len(observations) or not complete:
            raise ValueError('collection marker contradicts observations')
    # Collection may be validated before COLLECTED is written by the orchestrator.
    if (source/'FAILED.json').exists() or (source/'INTERRUPTED.json').exists():complete=False
    if (source/'COMPLETE.json').exists():
        marker=load_json(source/'COMPLETE.json')
        if marker.get('protocol')!=PROTOCOL or marker.get('complete') is not True or marker.get('configuration_sha256')!=study['configuration_sha256'] or not complete:
            raise ValueError('invalid experiment completion')
        actual=tree_hashes(source);actual.pop('COMPLETE.json',None)
        if marker.get('raw_sha256')!=actual:raise ValueError('raw completion hashes differ')
    if not complete and not allow_incomplete:raise ValueError('incomplete experiment; failed/missing records retained')
    return dict(plan=study,complete=complete,observations=observations,availability=availability,
                missing_configurations=missing,commands=commands)


GROUP_FIELDS=('family','operation','algorithm','distribution','size','seed','query_seed','structure_seed',
              'input_hash_fnv1a64','insertion_hash_fnv1a64','query_category','query_hash_fnv1a64','batch_size',
              'nearly_sorted_swaps','duplicate_cardinality','run_kind','compiler_id','compiler_version','build_type',
              'sanitizers','platform','architecture','source_manifest_sha256','cmake_flags_sha256')
CROSS_FIELDS=tuple(f for f in GROUP_FIELDS if f not in ('seed','input_hash_fnv1a64','insertion_hash_fnv1a64','query_hash_fnv1a64'))


def aggregate(validated):
    config=validated['plan']['configuration'];groups={}
    observation_index={}
    for o in validated['observations']:
        key=(o['family'],o['run_id'],o['algorithm'],o['operation'],o['query_category'])
        observation_index.setdefault(key,[]).append(o)
    # Create expected groups even when no rows exist but a query plan is available.
    for family_entry in validated['plan']['families']:
        family=family_entry['family']
        for child in family_entry['children']:
            bundle=Path(validated['plan']['raw_path'])/family/child['name']
            if not (bundle/'run.json').exists():continue
            meta=load_json(bundle/'run.json')
            operations=[('sort',None)] if family=='sorting' else ([('build',None)] if family=='structures' else [])
            if family!='sorting':operations += [('lookup',c['category']) for c in meta['categories'] if c['available']]
            for algorithm in config['algorithms'][family]:
                for operation,category in operations:
                    matched=observation_index.get((family,meta['run_id'],algorithm,operation,category),[])
                    if matched:base={f:matched[0][f] for f in GROUP_FIELDS}
                    else:
                        batch=next((c for c in meta.get('categories',[]) if c['category']==category),{})
                        fake={k:str(v) for k,v in meta.items()};fake.update(algorithm=algorithm,operation=operation,query_category=category or '',
                            query_hash_fnv1a64=batch.get('query_hash_fnv1a64',''),batch_size=str(config['queries']) if category else '',
                            hit_queries=str(batch.get('hit_queries','')),miss_queries=str(batch.get('miss_queries','')),
                            phase='measure',trial_index='0',execution_order='0',status='error',correctness='not_checked',error='',elapsed_ns='',elapsed_unit='ns')
                        base={f:normalize(fake,meta,family,bundle,-1)[f] for f in GROUP_FIELDS}
                    key=tuple(base[f] for f in GROUP_FIELDS)
                    if key in groups:raise ValueError('duplicate dataset group')
                    measured=[o for o in matched if o['phase']=='measure'];warm=[o for o in matched if o['phase']=='warmup']
                    successful=[o['elapsed_ns'] for o in measured if o['status']=='ok']
                    s=stats(successful)
                    group=dict(base,run_id=meta['run_id'],bundle_path=str(bundle),unit='ns',statistics=s,
                        successful_trials=s['count'],failed_trials=sum(o['status']!='ok' for o in measured),
                        missing_trials=config['repetitions']-len(measured),warmup_rows=len(warm),
                        failed_warmups=sum(o['status']!='ok' for o in warm),missing_warmups=config['warmups']-len(warm),
                        interrupted_context=any(c['status']=='interrupted' for c in validated['commands'] if c['family']==family))
                    if category:group['normalized_batch_average_ns_per_query']={k:(v/config['queries'] if v is not None and k!='count' else v) for k,v in s.items()}
                    groups[key]=group
    per_dataset=sorted(groups.values(),key=canonical)
    cross={}
    for g in per_dataset:
        key=tuple(g[f] for f in CROSS_FIELDS);cross.setdefault(key,[]).append(g)
    crossed=[]
    for key,values in cross.items():
        by_input={}
        for g in values:
            if g['statistics']['median'] is not None:
                by_input.setdefault(g['insertion_hash_fnv1a64'] or g['input_hash_fnv1a64'],[]).append(g['statistics']['median'])
        unit_medians=[statistics.median(x) for x in by_input.values()]
        crossed.append(dict(zip(CROSS_FIELDS,key),declared_datasets=len(values),distinct_input_datasets=len(by_input),
            seeds=sorted({g['seed'] for g in values}),dataset_groups=[g['bundle_path']+':'+g['algorithm']+':'+g['operation']+':'+str(g['query_category']) for g in values],
            statistics=stats(unit_medians),unit='ns',successful_trials=sum(g['successful_trials'] for g in values),
            failed_trials=sum(g['failed_trials'] for g in values),missing_trials=sum(g['missing_trials'] for g in values)))
    counts={f:dict(successful_measured=0,failed_measured=0,missing_measured_known=0,warmup_rows=0,failed_warmups=0,missing_warmups_known=0,missing_configurations=0,unknown_lookup_missing_upper_bound=0) for f in FAMILIES}
    for g in per_dataset:
        c=counts[g['family']]
        for target,field in [('successful_measured','successful_trials'),('failed_measured','failed_trials'),('missing_measured_known','missing_trials'),('warmup_rows','warmup_rows'),('failed_warmups','failed_warmups'),('missing_warmups_known','missing_warmups')]:c[target]+=g[field]
    for m in validated['missing_configurations']:
        c=counts[m['family']];c['missing_configurations']+=1;c['missing_measured_known']+=m['known_missing_measured_trials'];c['unknown_lookup_missing_upper_bound']+=m['lookup_missing_measured_upper_bound']
        c['missing_warmups_known']+=config['warmups']*len(config['algorithms'][m['family']]) if m['family']!='search' else 0
    return dict(schema_version=1,protocol=PROTOCOL,summary_kind='experiment_hierarchy_v1',source=validated['plan']['raw_path'],
        configuration_sha256=validated['plan']['configuration_sha256'],complete=validated['complete'],elapsed_unit='ns',
        outlier_policy='retain_all',cross_dataset_method='equal weight distinct input medians; identical fingerprints collapse median of declared-dataset medians',
        confidence_intervals=None,counts=counts,commands=validated['commands'],missing_configurations=validated['missing_configurations'],
        availability=validated['availability'],per_dataset=per_dataset,cross_dataset=sorted(crossed,key=canonical))
