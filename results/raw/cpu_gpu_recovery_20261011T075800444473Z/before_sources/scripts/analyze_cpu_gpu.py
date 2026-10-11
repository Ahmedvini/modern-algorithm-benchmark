#!/usr/bin/env python3
"""Independent strict paired host-call analysis; prepared metrics are diagnostics."""
import argparse
import csv
import hashlib
import json
import math
import statistics
from pathlib import Path
from analyze_cuda_results import FIELDS as PREPARED_FIELDS, METRICS, read_bundle as read_prepared_bundle
from analyze_results import summarize_samples
from cpu_gpu_provenance import validate_retained_source
from cpu_gpu_protocol import (BACKENDS, FREEZE, MATRIX, PRIMARY_PROTOCOL, PROTOCOL, SIDE_FIELDS,
                              canonical, dump_new, load_protocol, require, schedule, sha)

def table(path, fields):
    with path.open(newline='', encoding='utf-8') as stream:
        reader = csv.DictReader(stream, strict=True)
        require(reader.fieldnames == fields, 'wrong CSV schema: ' + str(path))
        rows = list(reader)
    require(all(set(r) == set(fields) and all(isinstance(v, str) for v in r.values()) for r in rows), 'malformed CSV row')
    return rows

def uint(value, label):
    require(isinstance(value, str) and value.isascii() and value.isdecimal(), 'invalid unsigned ' + label)
    result=int(value)
    require(result<2**64,'unsigned overflow '+label)
    return result

def duration(value, integral=False):
    if integral:
        return uint(value, 'duration')
    try:
        number = float(value)
    except (ValueError, TypeError) as error:
        raise ValueError('invalid duration') from error
    require(math.isfinite(number) and number >= 0, 'nonfinite/negative duration')
    return number

def validate_resources(document, size):
    for key in ['size','prepared_query_bytes','adapter_query_bytes','free_device_bytes_before_buffers',
                'prepared_diagnostic_cudaMalloc_requested_bytes','adapter_diagnostic_cudaMalloc_requested_bytes',
                'combined_device_payload_bytes','known_host_peak_payload_bytes']:
        require(type(document.get(key)) is int and document[key]>=0,'invalid resource '+key)
    require(document['size']==size and document.get('gpu_name')=='Tesla T4' and
            (document.get('compute_major'),document.get('compute_minor'))==(7,5),'resource device/size mismatch')
    wp=document['prepared_query_bytes'];wa=document['adapter_query_bytes']
    require(max(wp,wa)<=64*1024**2,'workspace policy cap exceeded')
    require(document['prepared_diagnostic_cudaMalloc_requested_bytes']==max(wp,1) and
            document['adapter_diagnostic_cudaMalloc_requested_bytes']==max(wa,1),'query/allocation mismatch')
    peak=16*size+max(wp,1)+max(wa,1)
    require(document['combined_device_payload_bytes']==peak and peak<=256*1024**2 and
            peak<=document['free_device_bytes_before_buffers']//2,'combined resource gate failed')
    require(document['known_host_peak_payload_bytes']==24*size,'host payload formula mismatch')

def strict_json(text):
    def unique(pairs):
        result={}
        for key,value in pairs:
            require(key not in result,'duplicate JSON field: '+key)
            result[key]=value
        return result
    def invalid(value):raise ValueError('nonfinite JSON value: '+value)
    return json.loads(text,object_pairs_hook=unique,parse_constant=invalid)

def read_json(path):return strict_json(Path(path).read_text())

def validate_study_metadata(root, meta, model):
    require(meta.get('freeze_sha256')==sha(FREEZE),'freeze identity mismatch')
    for source,name in [(MATRIX,MATRIX.name),(FREEZE,FREEZE.name),
                        (MATRIX.parents[1]/'CPU_GPU_COMPARISON_PROTOCOL_v1.md','CPU_GPU_COMPARISON_PROTOCOL_v1.md')]:
        require(sha(root/name)==sha(source),'retained frozen asset mismatch: '+name)
    if meta['run_kind']=='performance':
        # Import only at call time: the runner shares this independent analyzer.
        from run_cpu_gpu_pilot import environment_gate
        build=read_json(root/'build.json');d=build['description']
        require(d['build_type']=='Release' and d['sanitizers'] is False and d['cub_version']==300001 and
                d['cuda_architectures']=='75' and d['cxx_standard']==17,'incompatible study build')
        require(d['global_flags']=='' and d['cuda_flags']=='' and
                d['configuration_flags'].split()==['-O3','-DNDEBUG'] and
                d['cuda_release_flags'].split()==['-O3','-DNDEBUG'],'incompatible study flags')
        require(sha(root/'compile_commands.json')==build['compile_commands_sha256'],'compile commands changed')
        require(sha(root/'source_review.json')==build['source_review_sha256'],'source review changed')
        source_review=read_json(root/'source_review.json')
        validate_retained_source(source_review,model)
        environment=read_json(root/'environment.json');environment_gate(environment)
        require(environment['omp_environment']==model['openmp_policy']['environment'],'OpenMP environment mismatch')
        prerequisite=read_json(root/'prerequisites.json')
        require(prerequisite.get('complete') is True and prerequisite.get('protocol')==PROTOCOL,'study prerequisites incomplete')
        require(prerequisite.get('validation_scope','full_protocol_v1')=='full_protocol_v1' and
                prerequisite.get('study_eligible',True) is True,'non-timing subset is not full study prerequisites')
        required={'cpu_release_ctest','cpu_sanitize_ctest','cuda_ctest','cuda_correctness','preflight'}
        require(required<=set(prerequisite['records']),'missing study prerequisite commands')
        for record in prerequisite['records'].values():
            relative=Path(record['file'])
            require(not relative.is_absolute() and '..' not in relative.parts,'unsafe prerequisite record path')
            path=root/'prerequisite_commands'/relative
            require(sha(path)==record['sha256'],'prerequisite command hash mismatch')
            result=read_json(path)
            require(result.get('exit_code')==0 and result.get('status')=='completed','failed study prerequisite command')
        require(prerequisite['binary_sha256']==build['binary_sha256'] and
                prerequisite['input_tool_sha256']==build['input_tool_sha256'],'prerequisite binary mismatch')
        require(prerequisite['source_sha256']==source_review['current_source_sha256'],'prerequisite source mismatch')
        for backend,reference in meta['implementations'].items():
            require(reference==dict(source_review='source_review.json',build='build.json',
                cub_pin=model['dependency'] if backend.startswith('gpu_') else None),'implementation provenance mismatch')

def validate_raw_manifest(root):
    manifest=read_json(root/'RAW_SHA256.json')
    files={str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and p!=root/'RAW_SHA256.json'}
    require(set(manifest)==files,'raw manifest coverage mismatch')
    for relative,digest in manifest.items():
        path=Path(relative)
        require(not path.is_absolute() and '..' not in path.parts,'unsafe raw manifest path')
        require(sha(root/path)==digest,'raw manifest hash mismatch: '+relative)

def analyze(directory, allow_incomplete=False, require_marker=True, allow_synthetic=False):
    root = Path(directory)
    model = load_protocol()
    meta = read_json(root / 'run.json')
    part=meta.get('matrix_part')
    require(meta.get('protocol') == PROTOCOL and meta.get('schema_version') == 1 and part in ['pilot','study'], 'wrong run protocol/part')
    require(meta.get('run_kind') == 'performance' or (allow_synthetic and meta.get('run_kind') == 'synthetic_test_fixture'), 'not performance evidence')
    require(meta.get('matrix_sha256') == sha(MATRIX), 'matrix hash mismatch')
    require(isinstance(meta.get('run_id'), str) and bool(meta['run_id']), 'invalid run identity')
    cells = model[part]['cells'];expected_counts=model[part]['expected']
    per_dataset=len(BACKENDS)*(model['warmups']+model['repetitions'])
    require(meta.get('dataset_ids') == [c['dataset_id'] for c in cells], 'matrix coverage/order mismatch')
    for name in ['build', 'environment']:
        document = read_json(root / (name + '.json'))
        require(hashlib.sha256(canonical(document)).hexdigest() == meta[name + '_id'], name + ' identity mismatch')
    require(set(meta.get('implementations', {})) == set(BACKENDS), 'missing implementation identities')
    require(meta.get('prerequisites_passed') is True, 'prerequisites not validated')
    if part=='study':validate_study_metadata(root,meta,model)
    elif meta['run_kind']=='performance':validate_retained_source(read_json(root/'source_review.json'),model)
    queries=read_json(root/'workspace_queries.json')
    require(set(queries)=={str(c['recipe']['size']) for c in cells},'missing/unexpected workspace queries')
    for size,query in queries.items():validate_resources(query,int(size))
    require(not ((root/'COMPLETE.json').exists() and ((root/'FAILED.json').exists() or (root/'INTERRUPTED.json').exists())), 'contradictory completion markers')
    require(not root.is_symlink() and not any(p.is_symlink() for p in root.rglob('*')),'symlink raw artifact')
    if part=='study' and require_marker and (root/'COMPLETE.json').exists():validate_raw_manifest(root)
    all_groups, raw_hashes, row_identities = [], {}, set()
    actual_global = []
    interrupted_total = failed_total = missing_total = successful_total = warmups_ok = 0
    calibration_by_dataset = {}
    for dataset_index, cell in enumerate(cells):
        identity = cell['dataset_id']; recipe = cell['recipe']; base = root / ('data_' + identity)
        plan = schedule(cell, dataset_index * per_dataset)
        expected_by_order = {r['execution_order']: r for r in plan}
        observed, attempted = {}, {}
        content_sha = None
        require(not base.is_symlink(),'symlink dataset directory')
        if base.exists() and not (base/'dataset.json').exists():
            require(not (base/'measurements').exists(),'measurements without input identity')
        if (base/'dataset.json').exists():
            require(not base.is_symlink(), 'symlink dataset directory')
            dataset = read_json(base / 'dataset.json')
            require(dataset['dataset_id'] == identity and dataset['recipe'] == recipe, 'dataset recipe mismatch')
            binary = base / 'input.bin'
            require(binary.stat().st_size == recipe['size'] * 4, 'input size mismatch')
            content_sha = sha(binary)
            require(content_sha == dataset['input_sha256'], 'input SHA256 mismatch')
            fingerprint = dataset['input_hash_fnv1a64']
            require(uint(fingerprint, 'FNV') < 2**64, 'invalid FNV')
            if part=='study':
                generated=read_json(base/'input.json')
                require(all(generated.get(k)==v for k,v in recipe.items() if k!='key_type') and
                        generated.get('input_hash_fnv1a64')==fingerprint,'input-generation metadata mismatch')
            measurements = base / 'measurements'
            attempt_path = measurements / 'attempts.jsonl'
            if attempt_path.exists():
                for line in attempt_path.read_text().splitlines():
                    attempt = strict_json(line)
                    order = attempt.get('execution_order')
                    require(type(order) is int and order == len(attempted) and order < per_dataset, 'attempt order/duplicate')
                    require(attempt == {k: v for k, v in expected_by_order[order].items() if k != 'dataset_id'}, 'attempt identity mismatch')
                    attempted[order] = attempt
            primary = measurements / 'primary.csv'
            if primary.exists():
                for row in table(primary, model['primary_schema']['csv_fields']):
                    order = uint(row['execution_order'], 'order')
                    require(order in expected_by_order and order not in observed and order in attempted, 'duplicate/unexpected/unattempted trial')
                    expected = expected_by_order[order]
                    backend = expected['backend_id']
                    require(backend != 'gpu_cub_prepared', 'prepared data in primary scope')
                    mode = next(b for b in model['backend_modes'] if b['id'] == backend)
                    shared = dict(schema_version='1', protocol=PRIMARY_PROTOCOL, run_id=meta['run_id'], matrix_sha256=meta['matrix_sha256'],
                                  build_id=meta['build_id'], environment_id=meta['environment_id'], dataset_id=identity,
                                  input_sha256=content_sha, input_hash_fnv1a64=fingerprint, backend_id=backend, algorithm=mode['algorithm'],
                                  implementation_identity_ref=backend, scope='host_vector_api_call_v1', elapsed_unit='ns')
                    shared.update({k: str(recipe[k]) for k in ['size', 'distribution', 'seed', 'dataset_generator', 'nearly_sorted_swaps', 'duplicate_cardinality']})
                    shared.update({k: str(expected[k]) for k in ['phase', 'trial_index', 'execution_order', 'global_trial_index']})
                    require(all(row[k] == value for k, value in shared.items()), 'primary identity/scope mismatch')
                    if row['status'] == 'ok':
                        require(row['correctness'] == 'passed' and row['error'] == '', 'contradictory primary success')
                        metrics = {'host_call_e2e_ns': duration(row['elapsed_ns'], True)}
                        if backend == 'gpu_cub_adapter':
                            require(all(row[k] == '' for k in ['requested_cpu_threads', 'actual_cpu_threads', 'parallel_region']), 'invented GPU worker count')
                        else:
                            parallel = backend == 'cpu_parallel_merge_sort_t2'
                            actual = 2 if parallel and recipe['size'] >= 32768 else 1
                            require(row['requested_cpu_threads'] == ('2' if parallel else '1') and row['actual_cpu_threads'] == str(actual) and
                                    row['parallel_region'] == ('true' if actual == 2 else 'false'), 'wrong actual CPU team')
                    else:
                        require(row['status'] == 'error' and row['correctness'] in ['failed', 'not_checked'] and bool(row['error']) and row['elapsed_ns'] == '', 'malformed primary failure')
                        metrics = {}
                    observed[order] = dict(expected, status=row['status'], metrics=metrics)
            prepared = measurements / 'prepared/trials.csv'
            sidecar = measurements / 'prepared_order.csv'
            if prepared.exists():
                rows = table(prepared, PREPARED_FIELDS)
                sides = table(sidecar, SIDE_FIELDS)
                require(len(rows) == len(sides), 'prepared sidecar coverage mismatch')
                for row, side in zip(rows, sides):
                    order = uint(side['execution_order'], 'prepared order')
                    require(order in expected_by_order and order not in observed and order in attempted, 'duplicate/unexpected prepared trial')
                    expected = expected_by_order[order]
                    require(expected['backend_id'] == 'gpu_cub_prepared' and side == {k: str(expected[k]) for k in SIDE_FIELDS}, 'prepared sidecar identity mismatch')
                    shared = dict(schema_version='1', protocol='cuda_sort_timing_v1', run_id=meta['run_id'], algorithm='cub_radix_sort',
                                  implementation_version='cub_radix_sort_v1', input_hash_fnv1a64=fingerprint, elapsed_unit='ns',
                                  phase=expected['phase'], trial_index=str(expected['trial_index']))
                    shared.update({k: str(recipe[k]) for k in ['size', 'distribution', 'seed', 'dataset_generator', 'nearly_sorted_swaps', 'duplicate_cardinality']})
                    require(all(row[k] == value for k, value in shared.items()), 'prepared identity mismatch')
                    if row['status'] == 'ok':
                        require(row['correctness'] == 'passed' and not row['error'], 'contradictory prepared success')
                        metrics = {m: duration(row[m], m == 'end_to_end_ns') for m in METRICS}
                    else:
                        require(row['status'] == 'error' and row['correctness'] in ['failed', 'not_checked'] and bool(row['error']) and all(row[m] == '' for m in METRICS), 'malformed prepared failure')
                        metrics = {}
                    observed[order] = dict(expected, status=row['status'], metrics=metrics)
            clock_path = measurements/'timer_calibration.json'
            if clock_path.exists():
                clock = read_json(clock_path)
                require(clock.get('pairs') == 1000 and clock.get('policy') == 'diagnostic_only_no_subtraction', 'invalid timer calibration')
                require(type(clock['median_ns']) in [float, int] and math.isfinite(clock['median_ns']) and clock['median_ns'] >= 0, 'invalid clock duration')
                calibration_by_dataset[identity] = clock['median_ns']
            if (measurements/'COMPLETE.json').exists():
                require(not any((measurements/name).exists() for name in ['FAILED.json','INTERRUPTED.json']),'contradictory dataset markers')
                marker=read_json(measurements/'COMPLETE.json')
                require(marker.get('complete') is True and marker.get('rows')==per_dataset,'invalid dataset completion marker')
                require(len(observed) == per_dataset and len(attempted) == per_dataset and all(r['status'] == 'ok' for r in observed.values()), 'contradictory dataset completion')
                require(identity in calibration_by_dataset, 'missing calibration')
                resource=read_json(measurements/'resources.json')
                validate_resources(resource,recipe['size'])
                query=queries[str(recipe['size'])]
                require(all(resource[k]==query[k] for k in ['prepared_query_bytes','adapter_query_bytes']),'workspace query changed between preflight and timing')
                require(resource.get('prepared_session_query_bytes')==resource['prepared_query_bytes'] and
                        resource.get('prepared_session_cudaMalloc_requested_bytes')==max(resource['prepared_query_bytes'],1),'prepared session allocation mismatch')
                if meta['run_kind']=='performance':
                    prepared_meta,_=read_prepared_bundle(measurements/'prepared')
                    require(prepared_meta['run_id']==meta['run_id'] and prepared_meta['input_hash_fnv1a64']==fingerprint,'prepared metadata mismatch')
                    if part=='study':
                        description=read_json(root/'build.json')['description']
                        require(all(prepared_meta.get(k)==v for k,v in description.items() if k!='implementation_version'),
                                'prepared build differs from primary build')
                        require(prepared_meta['gpu_name']==resource['gpu_name'] and
                                prepared_meta['workspace_bytes']==resource['prepared_query_bytes'] and
                                (prepared_meta['compute_major'],prepared_meta['compute_minor'])==(7,5),
                                'prepared device/workspace mismatch')
            for path in base.rglob('*'):
                if path.is_file():
                    require(not path.is_symlink(), 'symlink raw artifact')
                    raw_hashes[str(path.relative_to(root))] = sha(path)
        for order, row in observed.items():
            trial_id = (identity, row['backend_id'], row['phase'], row['trial_index'])
            require(trial_id not in row_identities, 'duplicate trial identity')
            row_identities.add(trial_id)
        actual_global.extend(r['global_trial_index'] for _, r in sorted(observed.items()))
        for backend in BACKENDS:
            measured = [r for r in plan if r['backend_id'] == backend and r['phase'] == 'measure']
            warmup = next(r for r in plan if r['backend_id'] == backend and r['phase'] == 'warmup')
            success = [observed[r['execution_order']] for r in measured if r['execution_order'] in observed and observed[r['execution_order']]['status'] == 'ok']
            failed = sum(r['execution_order'] in observed and observed[r['execution_order']]['status'] != 'ok' for r in measured)
            interrupted = sum(r['execution_order'] in attempted and r['execution_order'] not in observed for r in measured)
            missing = model['repetitions'] - len(success) - failed - interrupted
            warm = observed.get(warmup['execution_order'])
            wstatus = warm['status'] if warm else 'interrupted' if warmup['execution_order'] in attempted else 'missing'
            warmups_ok += wstatus == 'ok'
            metrics = METRICS if backend == 'gpu_cub_prepared' else ['host_call_e2e_ns']
            all_groups.append(dict(dataset_id=identity, input_sha256=content_sha, recipe=recipe, backend_id=backend,
                                   scope='diagnostics_only' if backend == 'gpu_cub_prepared' else 'host_vector_api_call_v1',
                                   successful_trials=len(success), failed_trials=failed, interrupted_trials=interrupted, missing_trials=missing,
                                   warmup_status=wstatus, metrics={m: summarize_samples([r['metrics'][m] for r in success]) for m in metrics}))
            successful_total += len(success); failed_total += failed; interrupted_total += interrupted; missing_total += missing
    require(actual_global == sorted(actual_global), 'global execution order mismatch')
    expected_dirs = {'data_'+c['dataset_id'] for c in cells}
    require(not any(p.name.startswith('data_') and p.name not in expected_dirs for p in root.iterdir()), 'unexpected dataset directory')
    complete = successful_total == expected_counts['measured_invocations'] and warmups_ok == expected_counts['warmup_invocations'] and not (failed_total or interrupted_total or missing_total)
    complete = complete and all((root/('data_'+c['dataset_id'])/'measurements/COMPLETE.json').is_file() for c in cells)
    if (root/'FAILED.json').exists() or (root/'INTERRUPTED.json').exists():complete = False
    if (root/'COMPLETE.json').exists():
        marker=read_json(root/'COMPLETE.json')
        require(marker.get('complete') is True and complete, 'root completion contradicts raw records')
        if part=='study':
            require(marker.get('measured')==dict(successful=successful_total,failed=failed_total,interrupted=interrupted_total,missing=missing_total) and
                    marker.get('warmups')==dict(successful=warmups_ok,failed=0,interrupted=0,missing=0),'root marker count mismatch')
    if require_marker and not (root/'COMPLETE.json').exists():complete = False
    require(complete or allow_incomplete, 'incomplete '+part+'; use --allow-incomplete to report retained failures/missing records')
    ratios = []
    if complete:
        by_key = {(g['dataset_id'],g['backend_id']):g for g in all_groups}
        for cell in cells:
            d = cell['dataset_id'];denominator=by_key[d,'gpu_cub_adapter']['metrics']['host_call_e2e_ns']['median_ns']
            clock = calibration_by_dataset[d]
            for backend in BACKENDS[:3]:
                numerator=by_key[d,backend]['metrics']['host_call_e2e_ns']['median_ns']
                resolution_limited = numerator < 10*clock or denominator < 10*clock or denominator <= 0
                ratios.append(dict(dataset_id=d,recipe=cell['recipe'],baseline=backend,denominator='gpu_cub_adapter',scope='host_vector_api_call_v1',
                                   ratio=None if resolution_limited else numerator/denominator,resolution_limited=resolution_limited))
    cross = []
    for size,distribution in sorted({(g['recipe']['size'],g['recipe']['distribution']) for g in all_groups}):
        for backend in BACKENDS:
            groups=[g for g in all_groups if g['recipe']['size']==size and g['recipe']['distribution']==distribution and g['backend_id']==backend]
            for metric in (METRICS if backend=='gpu_cub_prepared' else ['host_call_e2e_ns']):
                distinct={}
                for group in groups:
                    if group['successful_trials']==model['repetitions']:
                        distinct.setdefault(group['input_sha256'],[]).append(group['metrics'][metric]['median_ns'])
                values=[statistics.median(v) for v in distinct.values()]
                cross.append(dict(size=size,distribution=distribution,backend_id=backend,metric=metric,unit='ns',
                                  distinct_inputs=len(values),aggregation='equal-weight distinct-input medians; identical-input seed medians collapsed by median',
                                  statistics=summarize_samples(values)))
    cross_ratios=[]
    for size,distribution,backend in sorted({(r['recipe']['size'],r['recipe']['distribution'],r['baseline']) for r in ratios}):
        distinct={}
        for ratio in ratios:
            if (ratio['recipe']['size'],ratio['recipe']['distribution'],ratio['baseline'])==(size,distribution,backend) and ratio['ratio'] is not None:
                content=next(g['input_sha256'] for g in all_groups if g['dataset_id']==ratio['dataset_id'])
                distinct.setdefault(content,[]).append(ratio['ratio'])
        values=[statistics.median(v) for v in distinct.values()]
        cross_ratios.append(dict(size=size,distribution=distribution,baseline=backend,denominator='gpu_cub_adapter',
                                 unit='dimensionless',distinct_inputs=len(values),
                                 statistics=dict(count=len(values),median=statistics.median(values) if values else None,
                                    mean=statistics.mean(values) if values else None,stdev=statistics.stdev(values) if len(values)>1 else None,
                                    minimum=min(values) if values else None,maximum=max(values) if values else None)))
    for name in ['run.json','build.json','environment.json','workspace_queries.json']:
        raw_hashes[name]=sha(root/name)
    if part=='study' and not complete:cross=[]
    return dict(schema_version=1,protocol=PROTOCOL,matrix_part=part,run_id=meta['run_id'],complete=complete,
                measured=dict(successful=successful_total,failed=failed_total,interrupted=interrupted_total,missing=missing_total),
                warmups=dict(successful=warmups_ok,failed=sum(g['warmup_status']=='error' for g in all_groups),
                    interrupted=sum(g['warmup_status']=='interrupted' for g in all_groups),missing=sum(g['warmup_status']=='missing' for g in all_groups)),unit='ns',groups=all_groups,
                paired_host_call_ratios=ratios,cross_dataset=cross,cross_dataset_paired_ratios=cross_ratios,raw_sha256=raw_hashes,
                interpretation='descriptive only; retain all outliers; repetitions are not independent datasets; no confidence intervals/significance')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('raw',type=Path);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--allow-incomplete',action='store_true')
    args=parser.parse_args()
    try:
        report=analyze(args.raw,args.allow_incomplete)
        dump_new(args.output,report)
        return 0 if report['complete'] else 1
    except (OSError,ValueError,KeyError,TypeError,csv.Error) as error:
        print('analysis error:',error);return 1
if __name__=='__main__':raise SystemExit(main())
