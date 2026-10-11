"""Explicit, pinned compatibility for three approved framework files only.

Legacy evidence remains legacy. Compatibility never grants execution authority
or substitutes correctness for timing/framework/pilot coverage.
"""
import hashlib
import re

from cpu_gpu_protocol import ROOT, PROTOCOL, canonical, require, sha, source_manifest
from cpu_gpu_provenance import (TRUSTED_CMAKE_REVIEW_SHA256, TRUSTED_FREEZE_SHA256,
                                strict_json, trusted_source_anchors, validate_digest_map)
from cpu_gpu_validation_policy import trusted_policy, classify, TRUSTED_POLICY_SHA256
from cpu_gpu_build_identity import validate_document

POLICY_ID = 'cpu_gpu_framework_compatibility_v1'
POLICY = ROOT / 'docs/CPU_GPU_FRAMEWORK_COMPATIBILITY_v1.json'
TRUSTED_COMPATIBILITY_SHA256 = 'b6a0ae4fa3e29394daad84419219020ecf7be1434207c6ad20105eb39ccb5627'


def approved_anchors(model):
    require(POLICY.is_file() and not POLICY.is_symlink() and sha(POLICY) == TRUSTED_COMPATIBILITY_SHA256,
            'framework compatibility trust root missing/changed')
    policy = strict_json(POLICY.read_text())
    parent, approved = trusted_policy()
    expected = trusted_source_anchors(model)
    require(policy.get('schema_version') == 1 and policy.get('policy') == POLICY_ID and
            policy.get('protocol') == PROTOCOL and
            policy.get('parent_validation_policy_sha256') == TRUSTED_POLICY_SHA256 and
            policy.get('authorized_framework_exceptions') == parent['authorized_framework_exceptions'] and
            policy.get('required_evidence_kind') == 'full_study_prerequisites' and
            type(policy.get('required_gpu_framework_methods')) is int and policy['required_gpu_framework_methods'] == 14 and
            policy.get('requires_current_build_identity') is True and
            policy.get('changes_frozen_protocol') is False and policy.get('grants_execution_authorization') is False,
            'inconsistent framework compatibility policy')
    for path, exception in policy['authorized_framework_exceptions'].items():
        require(expected[path] == exception['before_sha256'], 'framework exception base changed')
        expected[path] = exception['after_sha256']
    require(expected == approved, 'framework policy disagrees with protected validation anchors')
    return expected


def validate_review(review, model):
    expected = approved_anchors(model)
    require(isinstance(review, dict) and review.get('framework_compatibility_policy') == POLICY_ID and
            review.get('compatibility_policy_sha256') == TRUSTED_COMPATIBILITY_SHA256 and
            review.get('cmake_review_sha256') == TRUSTED_CMAKE_REVIEW_SHA256 and
            review.get('changed_anchors') == sorted(['CMakeLists.txt', 'include/benchmark/cuda_timing.hpp',
                                                   'src/cuda/cub_timing.cu']),
            'missing/inconsistent framework compatibility review')
    actual = review.get('current_source_sha256')
    validate_digest_map(actual, 'compatible source review')
    for path, digest in expected.items():
        if path.startswith('docs/'):
            require((ROOT / path).is_file() and not (ROOT / path).is_symlink() and
                    sha(ROOT / path) == digest and (path not in actual or actual[path] == digest),
                    'compatible documentation anchor mismatch: ' + path)
        else:
            require(actual.get(path) == digest, 'compatible protected source mismatch: ' + path)


def current_review(model):
    expected = approved_anchors(model)
    for path, digest in expected.items():
        file = ROOT / path
        require(file.is_file() and not file.is_symlink() and sha(file) == digest,
                'compatible current source changed: ' + path)
    review = dict(framework_compatibility_policy=POLICY_ID,
                  compatibility_policy_sha256=TRUSTED_COMPATIBILITY_SHA256,
                  cmake_review_sha256=TRUSTED_CMAKE_REVIEW_SHA256,
                  changed_anchors=sorted(['CMakeLists.txt', 'include/benchmark/cuda_timing.hpp', 'src/cuda/cub_timing.cu']),
                  current_source_sha256=source_manifest())
    validate_review(review, model)
    return review


def validate_evidence(prerequisite, records_root, model, source, binary_digest, input_digest, compile_digest=None):
    """Shared offline launch/analyzer check; never runs measurements.

    The assembler must independently review original command outputs. A v2 full
    coverage assessment is required in addition to legacy full-protocol records.
    Correctness-only bundles cannot be upgraded here. No implicit defaults.
    """
    require(prerequisite.get('framework_compatibility_policy') == POLICY_ID,
            'wrong framework prerequisite policy')
    require(type(prerequisite.get('schema_version')) is int and prerequisite['schema_version'] == 1 and
            prerequisite.get('validation_scope') == 'full_protocol_v1' and
            prerequisite.get('study_eligible') is True,
            'explicit full prerequisite scope required')
    validate_review(source, model)
    identity = validate_document(prerequisite.get('build_identity'), source['current_source_sha256'],
                                 binary_digest, input_digest, compile_digest)
    artifact = prerequisite.get('framework_validation')
    require(isinstance(artifact, dict) and artifact.get('artifact_kind') == 'full_study_prerequisites',
            'full framework evidence required; correctness is insufficient')
    references = prerequisite.get('framework_records')
    require(isinstance(references, dict) and set(references) == set(artifact.get('records', {})),
            'missing/ambiguous retained framework records')
    from pathlib import Path
    hashes = {}
    for name, reference in references.items():
        require(isinstance(reference, dict) and isinstance(reference.get('file'), str), 'missing framework record path')
        relative = Path(reference['file'])
        require(not relative.is_absolute() and '..' not in relative.parts and str(relative) == reference['file'],
                'unsafe framework record path')
        file = records_root / relative
        require(file.absolute() == file.resolve(strict=True) and file.resolve().is_relative_to(records_root.resolve()),
                'aliased framework record path')
        require(file.is_file() and not file.is_symlink() and sha(file) == reference.get('sha256'),
                'retained framework record changed: ' + name)
        hashes[name] = sha(file)
    context = dict(session_id=prerequisite.get('session_id'),
                   source_identity=hashlib.sha256(canonical(source['current_source_sha256'])).hexdigest(),
                   build_identity=hashlib.sha256(canonical(identity)).hexdigest(),
                   binary_identity=binary_digest, freeze_sha256=TRUSTED_FREEZE_SHA256,
                   record_sha256=hashes)
    assessment = classify(artifact, context)
    require(assessment['launch_review_candidate'] is True, 'not a full framework candidate')
    # The legacy cuda_ctest command must still contain the actual GPU framework
    # run, not host-only skips or a renamed untimed diagnostic. Timing execution
    # is NOT performed by this validator; it inspects immutable prior output.
    reference = prerequisite['records']['cuda_ctest']
    result = strict_json((records_root / reference['file']).read_text())
    argv = result.get('argv')
    require(isinstance(argv, list) and len(argv) >= 3 and argv[0] == 'ctest' and
            argv.count('--test-dir') == 1 and
            argv.index('--test-dir') + 1 < len(argv) and
            argv[argv.index('--test-dir') + 1] == identity['build_dir'],
            'GPU framework command build identity mismatch')
    text = result.get('stdout', '') + result.get('stderr', '')
    groups = re.findall(r'Start\s+\d+: cuda_benchmark_gpu_framework\s*\n(.*?)'
                        r'\d+/\d+ Test\s+#\d+: cuda_benchmark_gpu_framework[^\n]*Passed[^\n]*',
                        text, flags=re.DOTALL)
    require(result.get('exit_code') == 0 and result.get('status') == 'completed' and len(groups) == 1 and
            len(re.findall(r'Start\s+\d+: cuda_benchmark_gpu_framework\s*\n', text)) == 1 and
            len(re.findall(r'(?m)^(?:\d+: )?Ran 14 tests(?: in [0-9.]+s)?\s*$', groups[0])) == 1 and
            len(re.findall(r'(?m)^(?:\d+: )?OK\s*$', groups[0])) == 1 and
            not any(term in groups[0] for term in ['skipped=', '***Skipped', 'FAILED', 'ERROR']),
            'current full GPU timing-framework coverage absent')
    production = strict_json((records_root / prerequisite['records']['cuda_correctness']['file']).read_text())
    from validate_cuda_sort import verify_result
    require(production.get('exit_code') == 0 and production.get('status') == 'completed',
            'current production GPU correctness absent')
    require(production.get('argv') == [str(Path(identity['build_dir']) / 'test_cuda_sorting')],
            'production GPU command executable identity mismatch')
    result = verify_result(strict_json(production.get('stdout', '')))
    require((result['compute_major'], result['compute_minor']) == (7, 5), 'production correctness device mismatch')
    return assessment
