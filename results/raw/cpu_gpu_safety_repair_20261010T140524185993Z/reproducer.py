"""Full analyzer rejection probe with synthetic records only; no algorithm execution."""
import copy
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

root = Path.cwd()
base = Path(__file__).resolve().parent
sys.path.insert(0, str(root / 'scripts'))
from analyze_cpu_gpu import analyze
from cpu_gpu_protocol import BACKENDS, canonical, load_protocol, sha, verify_source_extension

spec = importlib.util.spec_from_file_location('fixture_module', root / 'tests/test_cpu_gpu_comparison.py')
fixtures = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixtures)
model = load_protocol()
report = dict(kind='synthetic_full_analysis_review_probe', sorting_calls=0, actual_gpu_calls=0,
              baseline_accepted=False, protected_source_change_rejected=False,
              note='All timings and metadata in disposable fixtures are synthetic; no performance evidence is created.')
with tempfile.TemporaryDirectory(prefix='mab_full_analysis_review_') as temporary:
    directory = Path(temporary) / 'fixture'
    fixtures.fixture(directory, part='study')
    def write(path, document):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(document, sort_keys=True))
    source = verify_source_extension(model)
    write(directory / 'source_review.json', source)
    (directory / 'compile_commands.json').write_text('[]')
    description = dict(build_type='Release', sanitizers=False, cub_version=300001,
        cuda_architectures='75', cxx_standard=17, global_flags='', cuda_flags='',
        configuration_flags='-O3 -DNDEBUG', cuda_release_flags='-O3 -DNDEBUG',
        compiler_id='SYNTHETIC', compiler_version='SYNTHETIC', platform='Linux',
        architecture='x86_64', cuda_compiler_version='SYNTHETIC', cuda_toolkit_version='SYNTHETIC')
    build = dict(description=description, binary_sha256='1'*64, input_tool_sha256='2'*64,
        compile_commands_sha256=sha(directory / 'compile_commands.json'),
        source_review_sha256=sha(directory / 'source_review.json'))
    environment = json.loads((root / 'results/raw/cpu_gpu_full_tooling_20261010T121208603276Z/downloaded/evidence/environment.json').read_text())
    environment['omp_environment'] = model['openmp_policy']['environment']
    write(directory / 'environment.json', environment)
    records = {}
    for name in ['cpu_release_ctest','cpu_sanitize_ctest','cuda_ctest','cuda_correctness','preflight']:
        relative = 'commands/' + name + '.json'
        path = directory / 'prerequisite_commands' / relative
        write(path, dict(exit_code=0, status='completed', fixture='synthetic; never executed'))
        records[name] = dict(file=relative, sha256=sha(path))
    prerequisite = dict(complete=True, protocol=model['protocol'], records=records,
        source_sha256=source['current_source_sha256'], binary_sha256='1'*64, input_tool_sha256='2'*64)
    meta = json.loads((directory / 'run.json').read_text())
    meta['run_kind'] = 'performance' # Exercise the production validation branch using explicitly synthetic data.
    meta['environment_id'] = hashlib.sha256(canonical(environment)).hexdigest()
    meta['implementations'] = {b: dict(source_review='source_review.json', build='build.json',
        cub_pin=model['dependency'] if b.startswith('gpu_') else None) for b in BACKENDS}
    for cell in model['study']['cells']:
        measurement = directory / ('data_' + cell['dataset_id']) / 'measurements'
        prepared = dict(description, **{k:v for k,v in cell['recipe'].items() if k!='key_type'},
            schema_version=1, protocol='cuda_sort_timing_v1', algorithm='cub_radix_sort',
            implementation_version='cub_radix_sort_v1', run_id='fixture', input_hash_fnv1a64='1',
            warmups=1, repetitions=5, expected_rows=6, elapsed_unit='ns', run_kind='performance',
            allocation_policy='prepared_pinned_reuse_v1', stream_policy='private_nonblocking_serial',
            end_to_end_clock='steady_clock', phase_clock='cuda_event_float_ms_to_ns', gpu_name='Tesla T4',
            requested_device=0, actual_device=0, compute_major=7, compute_minor=5,
            runtime_api_version=13000, driver_api_version=13000, device_memory_bytes=2**30, workspace_bytes=123)
        write(measurement / 'prepared/run.json', prepared)
        write(measurement / 'prepared/COMPLETE.json', dict(schema_version=1, complete=True, rows=6))
    def refresh():
        write(directory / 'build.json', build)
        write(directory / 'prerequisites.json', prerequisite)
        meta['build_id'] = hashlib.sha256(canonical(build)).hexdigest()
        write(directory / 'run.json', meta)
        for path in directory.glob('data_*/measurements/primary.csv'):
            with path.open(newline='') as stream:
                reader = csv.DictReader(stream); fields = reader.fieldnames; rows = list(reader)
            for row in rows:
                row.update(build_id=meta['build_id'], environment_id=meta['environment_id'])
            fixtures.write_table(path, fields, rows)
        fixtures.seal_fixture(directory)
    refresh()
    result = analyze(directory)
    report.update(baseline_accepted=result['complete'], synthetic_measured_records=result['measured']['successful'],
                  synthetic_warmup_records=result['warmups']['successful'])
    target = 'src/cuda/cub_sort.cu'
    source['current_source_sha256'][target] = '0'*64
    write(directory / 'source_review.json', source)
    prerequisite['source_sha256'] = source['current_source_sha256']
    build['source_review_sha256'] = sha(directory / 'source_review.json')
    refresh()
    try:
        result = analyze(directory)
        report['altered_source_result_marked_complete'] = result['complete']
    except (ValueError, KeyError, TypeError) as error:
        report.update(protected_source_change_rejected=True, rejection=str(error))
    report.update(target=target, frozen_digest=model['source_at_freeze_sha256'][target], fixture_digest='0'*64)
with (base / 'FULL_ANALYSIS_PROBE.json').open('x') as stream:
    json.dump(report, stream, indent=2, sort_keys=True); stream.write('\n')
print(json.dumps(report, indent=2))
raise SystemExit(0 if report['protected_source_change_rejected'] else 1)
