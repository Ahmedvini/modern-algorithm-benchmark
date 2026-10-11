"""Offline source provenance anchored to the accepted freeze, never retained claims."""
import json
from pathlib import Path, PurePosixPath
import re

from cpu_gpu_protocol import FREEZE, MATRIX, PROTOCOL, ROOT, require, sha

# Identities independently retained in the accepted pilot and tooling-review seals.
# These pin the trust roots, not an adapter digest copied from a run's source map.
TRUSTED_FREEZE_SHA256 = '518ac535473e50fb61dab3a70858bdfe42dfdb43570f649174f44bffe40e1ac6'
TRUSTED_CMAKE_REVIEW_SHA256 = 'b6a63a7e65827970d6b27e872e738052cd5faf94d88ee711dbccd5f77f90ef2a'
CMAKE_REVIEW = ROOT / 'docs/CPU_GPU_DRIVER_REVIEW_v1.json'
FROZEN_ASSETS = {'docs/CPU_GPU_COMPARISON_PROTOCOL_v1.md',
                 'docs/studies/cpu_gpu_comparison_v1.matrix.json',
                 'docs/studies/cpu_gpu_comparison_v1.resources.csv'}


def strict_json(text):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, 'ambiguous provenance JSON field: ' + key)
            result[key] = value
        return result
    def invalid(value):
        raise ValueError('nonfinite provenance JSON value: ' + value)
    return json.loads(text, object_pairs_hook=unique, parse_constant=invalid)


def valid_digest(value):
    return isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value) is not None


def validate_digest_map(mapping, label):
    require(isinstance(mapping, dict) and bool(mapping), 'missing ' + label)
    for path, digest in mapping.items():
        require(isinstance(path, str) and path and '\\' not in path, 'malformed path in ' + label)
        relative = PurePosixPath(path)
        require(not relative.is_absolute() and '..' not in relative.parts and
                str(relative) == path and path != '.', 'ambiguous path in ' + label)
        require(valid_digest(digest), 'malformed digest in ' + label + ': ' + path)


def trusted_source_anchors(model):
    require(FREEZE.is_file() and not FREEZE.is_symlink() and sha(FREEZE) == TRUSTED_FREEZE_SHA256,
            'trusted freeze identity missing/changed')
    freeze = strict_json(FREEZE.read_text())
    require(isinstance(freeze, dict) and freeze.get('protocol') == PROTOCOL, 'invalid trusted freeze')
    assets = freeze.get('files_sha256')
    validate_digest_map(assets, 'trusted frozen assets')
    require(set(assets) == FROZEN_ASSETS, 'missing/ambiguous trusted frozen assets')
    for path, digest in assets.items():
        source = ROOT / path
        require(source.is_file() and not source.is_symlink() and sha(source) == digest,
                'trusted frozen asset missing/changed: ' + path)
    frozen_model = strict_json(MATRIX.read_text())
    require(isinstance(frozen_model, dict) and frozen_model.get('protocol') == PROTOCOL and
            type(frozen_model.get('schema_version')) is int and frozen_model['schema_version'] == 1,
            'invalid trusted matrix')
    anchors = frozen_model.get('source_at_freeze_sha256')
    validate_digest_map(anchors, 'trusted source anchors')
    require({'src/cuda/cub_sort.cu', 'src/cuda/cub_timing.cu', 'third_party/cub/UPSTREAM.json',
             'CMakeLists.txt'} <= set(anchors), 'required trusted source anchor absent')
    require(isinstance(model, dict) and model.get('source_at_freeze_sha256') == anchors,
            'analysis model differs from trusted source anchors')
    require(CMAKE_REVIEW.is_file() and not CMAKE_REVIEW.is_symlink() and
            sha(CMAKE_REVIEW) == TRUSTED_CMAKE_REVIEW_SHA256, 'trusted CMake review missing/changed')
    review = strict_json(CMAKE_REVIEW.read_text())
    require(isinstance(review, dict) and review.get('protocol') == PROTOCOL and
            type(review.get('schema_version')) is int and review['schema_version'] == 1 and
            review.get('reviewed_additive_only') is True and
            review.get('frozen_cmake_sha256') == anchors['CMakeLists.txt'] and
            valid_digest(review.get('current_cmake_sha256')), 'inconsistent trusted CMake review')
    expected = dict(anchors)
    expected['CMakeLists.txt'] = review['current_cmake_sha256']
    return expected


def validate_retained_source(source_review, model):
    expected = trusted_source_anchors(model)
    require(isinstance(source_review, dict), 'invalid retained source review')
    actual = source_review.get('current_source_sha256')
    validate_digest_map(actual, 'retained source digests')
    for path, digest in expected.items():
        require(actual.get(path) == digest, 'retained protected source differs from trusted anchor: ' + path)
    require(source_review.get('cmake_review_sha256') == TRUSTED_CMAKE_REVIEW_SHA256 and
            source_review.get('changed_anchors') == ['CMakeLists.txt'], 'retained CMake exception differs from trusted review')
