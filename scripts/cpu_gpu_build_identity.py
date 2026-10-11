"""Read-only comparison-build identities. Capturing a hash does not validate a build.

No executable, compiler, CTest, GPU API or timing path is invoked by this module.
Old manifests are never amended. New snapshots are written exclusively.
"""
import argparse
from pathlib import Path

from cpu_gpu_protocol import ROOT, canonical, dump_new, require, sha, source_manifest
from cpu_gpu_provenance import TRUSTED_FREEZE_SHA256, strict_json, validate_digest_map

EXECUTABLES = ('cpu_gpu_comparison', 'comparison_input', 'test_parallel_workers',
               'test_cuda_prepared_correctness', 'test_cuda_sorting', 'cuda_sort_benchmark')
FILES = EXECUTABLES + ('libmab_parallel.a', 'libmab_cuda_timing.a',
                       'CMakeCache.txt', 'compile_commands.json', 'CTestTestfile.cmake')


def canonical_path(path):
    path = Path(path).absolute()
    require(path == path.resolve(strict=True), 'aliased/symlink build identity path')
    return path


def validate_document(document, source, binary_digest, input_digest, compile_digest=None):
    require(isinstance(document, dict) and type(document.get('schema_version')) is int and document['schema_version'] == 1 and
            document.get('kind') == 'cpu_gpu_build_identity_v1', 'missing/wrong build identity')
    require(document.get('freeze_sha256') == TRUSTED_FREEZE_SHA256, 'build freeze identity mismatch')
    for key in ['build_dir', 'source_dir']:
        path = document.get(key)
        require(isinstance(path, str) and Path(path).is_absolute() and
                str(Path(path)) == path and '..' not in Path(path).parts,
                'ambiguous build identity path: ' + key)
    validate_digest_map(document.get('source_sha256'), 'build source identities')
    require(document['source_sha256'] == source, 'stale build source identity')
    files = document.get('files_sha256')
    validate_digest_map(files, 'build file identities')
    require(set(files) == set(FILES), 'missing/unexpected build file identity')
    require(files['cpu_gpu_comparison'] == binary_digest and files['comparison_input'] == input_digest,
            'comparison/input executable identity mismatch')
    if compile_digest is not None:
        require(files['compile_commands.json'] == compile_digest, 'build compile identity mismatch')
    return document


def capture_snapshot(build_dir):
    """Content snapshot only; cannot satisfy full provenance requirements."""
    from cpu_gpu_validation_policy import verify_current_sources
    verify_current_sources()  # Pinned freeze, CUB and exact approved framework exceptions.
    build = canonical_path(build_dir)
    require(build.is_dir(), 'build identity requires a directory')
    files = {}
    for name in FILES:
        path = canonical_path(build / name)
        require(path.is_file(), 'missing build identity file: ' + name)
        if name in EXECUTABLES:
            require(path.stat().st_mode & 0o111, 'non-executable build identity file: ' + name)
        files[name] = sha(path)
    cache = {}
    for line in (build / 'CMakeCache.txt').read_text().splitlines():
        if line and not line.startswith(('#', '//')) and '=' in line and ':' in line.split('=', 1)[0]:
            field, value = line.split('=', 1); key = field.split(':', 1)[0]
            require(key not in cache, 'ambiguous build cache key: ' + key)
            cache[key] = value
    expected = dict(CMAKE_HOME_DIRECTORY=str(ROOT.resolve()), CMAKE_BUILD_TYPE='Release',
                    MAB_ENABLE_OPENMP='ON', MAB_ENABLE_CUDA='ON', MAB_ENABLE_CUDA_SORT='ON',
                    MAB_ENABLE_CPU_GPU_COMPARISON='ON', MAB_ENABLE_SANITIZERS='OFF',
                    CMAKE_CUDA_ARCHITECTURES='75')
    require(all(cache.get(k) == v for k, v in expected.items()), 'unexpected source/build configuration')
    from cpu_gpu_build_provenance import compile_entries
    compile_entries(strict_json((build / 'compile_commands.json').read_text()),
                    str(ROOT.resolve()), str(build), source_manifest())
    return dict(schema_version=1, kind='cpu_gpu_build_identity_v1', build_dir=str(build),
                source_dir=str(ROOT.resolve()), freeze_sha256=TRUSTED_FREEZE_SHA256,
                source_sha256=source_manifest(), files_sha256=files)


def capture(build_dir, provenance_path):
    """Require actual retained build commands in addition to output hashes."""
    from cpu_gpu_evidence_io import EvidenceStore
    from cpu_gpu_build_provenance import validate_build
    document = capture_snapshot(build_dir)
    build = canonical_path(build_dir)
    provenance = canonical_path(provenance_path)
    require(provenance.is_relative_to(build), 'build provenance outside intended build')
    reference = dict(file=str(provenance.relative_to(build)), sha256=sha(provenance))
    store = EvidenceStore(build)
    proof = validate_build(store, reference, document['source_sha256'],
                           {n: document['files_sha256'][n] for n in EXECUTABLES + ('libmab_parallel.a', 'libmab_cuda_timing.a')},
                           str(build))
    require(all(proof['metadata'][n]['sha256'] == document['files_sha256'][n]
                for n in ['CMakeCache.txt', 'compile_commands.json', 'CTestTestfile.cmake']),
            'stale build metadata provenance')
    document['build_provenance'] = reference
    return document


def verify(document, executable, input_tool):
    build = canonical_path(document['build_dir'])
    require(canonical_path(executable) == build / 'cpu_gpu_comparison' and
            canonical_path(input_tool) == build / 'comparison_input', 'different comparison build/executable path')
    reference = document.get('build_provenance')
    require(isinstance(reference, dict) and isinstance(reference.get('file'), str), 'missing build provenance identity')
    require(capture(build, build / reference['file']) == document, 'stale or mismatched build identity snapshot')


def main():
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument('--build-dir', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--build-provenance', required=True, type=Path,
                        help='Retained actual configure/build/compiler/linker command records; never synthesized')
    args = parser.parse_args()
    document = capture(args.build_dir, args.build_provenance)
    dump_new(args.output, document)
    # Useful content identifier, not an attestation of execution or eligibility.
    import hashlib
    print(hashlib.sha256(canonical(document)).hexdigest())


if __name__ == '__main__':
    main()
