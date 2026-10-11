"""Offline bounded-validation classification; never executes commands or authorizes runs.

Legacy analyzers/launch gates remain unchanged. This policy cannot make a v1
benchmark eligible and does not promote historical evidence to current coverage.
"""
from pathlib import Path
import hashlib
from cpu_gpu_protocol import ROOT, load_protocol, require, sha
from cpu_gpu_provenance import strict_json, trusted_source_anchors, validate_digest_map

POLICY = ROOT / 'docs/CPU_GPU_VALIDATION_POLICY_v2.json'
# Set once after static review of the explicitly authorized exception inventory.
TRUSTED_POLICY_SHA256 = '084664cad16ee6540323cf6a0514e3ff3420c4d4d1204a5d571d947cd445a32b'
KINDS = {'correctness_validation', 'timing_smoke', 'pilot_measurements', 'full_study_prerequisites'}


def trusted_policy():
    require(POLICY.is_file() and not POLICY.is_symlink() and sha(POLICY) == TRUSTED_POLICY_SHA256,
            'validation policy trust root missing/changed')
    p = strict_json(POLICY.read_text())
    require(p.get('schema_version') == 2 and p.get('policy') == 'cpu_gpu_validation_v2', 'wrong policy')
    expected = trusted_source_anchors(load_protocol())
    exceptions = p.get('authorized_framework_exceptions')
    require(isinstance(exceptions, dict) and set(exceptions) ==
            {'CMakeLists.txt', 'include/benchmark/cuda_timing.hpp', 'src/cuda/cub_timing.cu'},
            'unexpected framework exception inventory')
    for path, record in exceptions.items():
        require(isinstance(record, dict) and record.get('before_sha256') == expected[path] and
                record.get('reason'), 'invalid framework exception: ' + path)
        validate_digest_map({path: record.get('after_sha256')}, 'approved framework identity')
        expected[path] = record['after_sha256']
    require(p.get('study_execution_authorized') is False and p.get('legacy_study_eligibility') is False,
            'policy must not authorize or broaden legacy launches')
    return p, expected


def verify_current_sources():
    p, expected = trusted_policy()
    for path, digest in expected.items():
        file = ROOT / path
        require(file.is_file() and not file.is_symlink() and sha(file) == digest,
                'approved protected source changed: ' + path)
    return p


def classify(artifact, context):
    """Context is supplied by the independent current validation launcher.

    Never derive expected session/build/binary identities from the artifact being
    assessed. No subprocesses, timers, network, implicit freshness or defaults.
    """
    policy, anchors = trusted_policy()
    require(isinstance(artifact, dict) and artifact.get('schema_version') == 2 and
            artifact.get('policy') == policy['policy'], 'missing/wrong artifact policy')
    kind = artifact.get('artifact_kind')
    require(kind in KINDS, 'missing/unknown artifact kind')
    require(artifact.get('study_eligible') is False and artifact.get('execution_authorized') is False,
            'artifact cannot grant eligibility/authorization')
    require(artifact.get('status') == 'passed', 'failed/incomplete/interrupted validation')
    require(isinstance(context, dict), 'independent current validation context required')
    for field in ['session_id', 'source_identity', 'build_identity', 'binary_identity', 'freeze_sha256']:
        value = context.get(field)
        require(isinstance(value, str) and bool(value) and artifact.get(field) == value,
                'missing/stale context identity: ' + field)
    from cpu_gpu_provenance import TRUSTED_FREEZE_SHA256
    require(context['freeze_sha256'] == TRUSTED_FREEZE_SHA256, 'incorrect frozen inputs')
    actual = artifact.get('protected_source_sha256')
    validate_digest_map(actual, 'artifact protected sources')
    require(actual == anchors, 'artifact differs from independently approved source anchors')
    records = artifact.get('records')
    require(isinstance(records, dict) and bool(records), 'missing validation records')
    for name, r in records.items():
        require(isinstance(r, dict) and r.get('status') == 'passed' and type(r.get('exit_code')) is int
                and r['exit_code'] == 0 and r.get('skipped') == 0 and r.get('missing') == 0,
                'failed/skipped/missing record: ' + name)
        validate_digest_map({name: r.get('sha256')}, 'retained record hashes')
        require(context.get('record_sha256', {}).get(name) == r['sha256'], 'record identity mismatch: ' + name)
    expected_records = policy['required_records'].get(kind)
    require(isinstance(expected_records, list) and set(records) == set(expected_records),
            'wrong/missing record coverage for ' + kind)
    # Coverage assertions are explicit and per-gate, not inferred from exit0.
    for name in expected_records:
        for field, expected in policy['coverage'].get(name, {}).items():
            require(type(records[name].get(field)) is type(expected) and records[name][field] == expected,
                    'incomplete gate coverage: ' + name + '/' + field)
    return dict(policy=policy['policy'], artifact_kind=kind, classification_valid=True,
                bounded_validation_ready=kind == 'correctness_validation',
                launch_review_candidate=kind == 'full_study_prerequisites',
                study_eligible=False, execution_authorized=False,
                reasons=['Explicit evidence kind and current independently supplied identities verified.',
                         'Legacy launch policy unchanged; no performance or execution permission inferred.'])
