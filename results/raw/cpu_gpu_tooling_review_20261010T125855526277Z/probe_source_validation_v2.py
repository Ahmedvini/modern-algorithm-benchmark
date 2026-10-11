"""Synthetic metadata-only rejection probe. Never launches a sorter or CUDA call."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile

root = Path.cwd()
sys.path.insert(0, str(root / 'scripts'))
from analyze_cpu_gpu import validate_study_metadata
from cpu_gpu_protocol import BACKENDS, FREEZE, MATRIX, PROTOCOL, load_protocol, sha, verify_source_extension

base = Path(__file__).resolve().parent
old = root / 'results/raw/cpu_gpu_full_tooling_20261010T121208603276Z'
model = load_protocol()
report = dict(kind='synthetic_metadata_only_review_probe', sorting_calls=0,
              hardware_validation=False, baseline_accepted=False, protected_source_change_rejected=False)
with tempfile.TemporaryDirectory(prefix='mab_metadata_review_') as temporary:
    directory = Path(temporary)
    def write(path, document):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(document, sort_keys=True))
    for path in [FREEZE, MATRIX, root / 'docs/CPU_GPU_COMPARISON_PROTOCOL_v1.md']:
        (directory / path.name).write_bytes(path.read_bytes())
    # Retained observations are used as input fixtures, not a fresh environment claim.
    environment = json.loads((old / 'downloaded/evidence/environment.json').read_text())
    environment['omp_environment'] = model['openmp_policy']['environment'] # Synthetic required-policy fixture.
    write(directory / 'environment.json', environment)
    source = verify_source_extension(model)
    write(directory / 'source_review.json', source)
    (directory / 'compile_commands.json').write_text('[]')
    build = dict(description=dict(build_type='Release', sanitizers=False, cub_version=300001,
                 cuda_architectures='75', cxx_standard=17, global_flags='', cuda_flags='',
                 configuration_flags='-O3 -DNDEBUG', cuda_release_flags='-O3 -DNDEBUG'),
                 binary_sha256='1'*64, input_tool_sha256='2'*64,
                 compile_commands_sha256=sha(directory / 'compile_commands.json'),
                 source_review_sha256=sha(directory / 'source_review.json'))
    records = {}
    for name in ['cpu_release_ctest','cpu_sanitize_ctest','cuda_ctest','cuda_correctness','preflight']:
        relative = 'commands/' + name + '.json'
        path = directory / 'prerequisite_commands' / relative
        write(path, dict(exit_code=0, status='completed', fixture='synthetic metadata; command never executed'))
        records[name] = dict(file=relative, sha256=sha(path))
    prerequisite = dict(complete=True, protocol=PROTOCOL, records=records,
                        source_sha256=source['current_source_sha256'],
                        binary_sha256=build['binary_sha256'], input_tool_sha256=build['input_tool_sha256'])
    meta = dict(run_kind='performance', freeze_sha256=sha(FREEZE), implementations={b: dict(
        source_review='source_review.json', build='build.json',
        cub_pin=model['dependency'] if b.startswith('gpu_') else None) for b in BACKENDS})
    write(directory / 'build.json', build)
    write(directory / 'prerequisites.json', prerequisite)
    validate_study_metadata(directory, meta, model)
    report['baseline_accepted'] = True
    target = 'src/cuda/cub_sort.cu'
    altered = copy.deepcopy(source)
    altered['current_source_sha256'][target] = '0'*64
    write(directory / 'source_review.json', altered)
    build['source_review_sha256'] = sha(directory / 'source_review.json')
    prerequisite['source_sha256'] = altered['current_source_sha256']
    write(directory / 'build.json', build)
    write(directory / 'prerequisites.json', prerequisite)
    try:
        validate_study_metadata(directory, meta, model)
    except (ValueError, KeyError, TypeError) as error:
        report.update(protected_source_change_rejected=True, rejection=str(error))
    report.update(target=target, frozen_digest=model['source_at_freeze_sha256'][target],
                  fixture_digest='0'*64,
                  note='Only disposable fixture metadata was changed; the actual production adapter was not modified.')
with (base / 'SOURCE_VALIDATION_PROBE.json').open('x') as stream:
    json.dump(report, stream, indent=2, sort_keys=True)
    stream.write('\n')
print(json.dumps(report, indent=2))
raise SystemExit(0 if report['protected_source_change_rejected'] else 1)
