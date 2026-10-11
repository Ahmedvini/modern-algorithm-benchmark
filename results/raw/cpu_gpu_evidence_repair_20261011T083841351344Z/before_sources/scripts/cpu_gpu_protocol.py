"""Frozen CPU/GPU matrix validation and serialization; never launches workloads."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FREEZE = ROOT / 'docs/studies/cpu_gpu_comparison_v1.freeze.json'
MATRIX = ROOT / 'docs/studies/cpu_gpu_comparison_v1.matrix.json'
PROTOCOL = 'cpu_gpu_comparison_v1'
BACKENDS = ['cpu_std_sort', 'cpu_merge_sort', 'cpu_parallel_merge_sort_t2', 'gpu_cub_adapter', 'gpu_cub_prepared']
PRIMARY_PROTOCOL = 'cpu_gpu_host_call_v1'
SIDE_FIELDS = ['dataset_id', 'backend_id', 'phase', 'trial_index', 'execution_order', 'global_trial_index']

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode('ascii')

def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()

def require(condition, message):
    if not condition:
        raise ValueError(message)

def dump_new(path, value):
    with Path(path).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')

def schedule(cell, offset=0):
    rows = []
    for phase, orders in [('warmup', cell['warmup_order']), ('measure', cell['measure_order'])]:
        for trial, order in enumerate(orders):
            for backend in order:
                rows.append(dict(dataset_id=cell['dataset_id'], backend_id=backend, phase=phase,
                                 trial_index=trial, execution_order=len(rows), global_trial_index=offset + len(rows)))
    return rows

def load_protocol():
    freeze = json.loads(FREEZE.read_text())
    require(freeze['protocol'] == PROTOCOL, 'wrong freeze protocol')
    for relative, digest in freeze['files_sha256'].items():
        require(sha(ROOT / relative) == digest, 'frozen asset changed: ' + relative)
    model = json.loads(MATRIX.read_text())
    require(model['protocol'] == PROTOCOL and model['schema_version'] == 1, 'wrong matrix protocol')
    require(model['dependency']['cub_version'] == 300001 and
            model['dependency']['commit'] == 'f19d875da0d8bfb2e38c109b2b40522b8abbbbc3', 'CUB pin changed')
    require(model['warmups'] == 1 and model['repetitions'] == 5, 'wrong repetitions')
    require([b['id'] for b in model['backend_modes']] == BACKENDS, 'wrong backend configuration')
    for name, expected_count in [('pilot', 6), ('study', 48)]:
        cells = model[name]['cells']
        require(len(cells) == expected_count, 'wrong dataset count')
        seen = set()
        for cell in cells:
            r = cell['recipe']
            require(r['size'] in [1025, 65537, 1000000], 'size outside freeze')
            identity = hashlib.sha256(canonical(r)).hexdigest()
            require(cell['dataset_id'] == identity and identity not in seen, 'duplicate/invalid dataset identity')
            seen.add(identity)
            base = sorted(BACKENDS, key=lambda b: (hashlib.sha256(f'314159|{identity}|{b}'.encode()).hexdigest(), b))
            require(cell['warmup_order'] == [base] and cell['measure_order'] == [base[i:]+base[:i] for i in range(5)], 'order changed')
    return model

def primary_fields():
    return load_protocol()['primary_schema']['csv_fields']

def source_manifest():
    paths = [ROOT / 'CMakeLists.txt']
    for directory in ['include', 'src', 'scripts', 'tests', 'cmake', 'third_party']:
        paths.extend(p for p in (ROOT / directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    return {str(p.relative_to(ROOT)): sha(p) for p in sorted(set(paths))}

def verify_source_extension(model, compatibility_policy=None):
    if compatibility_policy is not None:
        from cpu_gpu_framework_compatibility import POLICY_ID, current_review
        require(compatibility_policy == POLICY_ID, 'unknown framework compatibility policy')
        return current_review(model)
    # Only reviewed additive CMake integration can change an existing source anchor.
    # Its exact current hash and the review/diff are captured in run evidence.
    changed = []
    for path, digest in model['source_at_freeze_sha256'].items():
        if sha(ROOT / path) != digest:
            changed.append(path)
    require(set(changed) <= {'CMakeLists.txt'}, 'protected source/pin changed: ' + str(changed))
    review_path=ROOT/'docs/CPU_GPU_DRIVER_REVIEW_v1.json'
    review=json.loads(review_path.read_text())
    require(review.get('reviewed_additive_only') is True and
            review.get('frozen_cmake_sha256')==model['source_at_freeze_sha256']['CMakeLists.txt'] and
            review.get('current_cmake_sha256')==sha(ROOT/'CMakeLists.txt'),'CMake extension differs from reviewed integration')
    return dict(changed_anchors=changed, policy='additive comparison sources and reviewed CMake integration only',
                cmake_review_sha256=sha(review_path),current_source_sha256=source_manifest())
