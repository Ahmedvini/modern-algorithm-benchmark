#!/usr/bin/env python3
"""Fail-closed CTest selection; CLI prints a plan and never executes tests."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

from cpu_gpu_protocol import ROOT, dump_new, require, sha, source_manifest
from cpu_gpu_provenance import strict_json, validate_digest_map
from ctest_build_guard import validate_build_tree

# v1 remains immutable history. v2 binds this authorized diagnostic revision.
MANIFEST = ROOT / 'docs/NON_TIMING_TEST_SELECTION_v2.json'
SAFE_CLASSES = {'cpu_correctness', 'gpu_correctness'}
CLASSES = SAFE_CLASSES | {'timing'}
# Fixtures/dependencies can implicitly schedule tests outside an -R expression.
SAFE_PROPERTIES = {'WORKING_DIRECTORY', 'TIMEOUT', 'SKIP_RETURN_CODE', 'LABELS'}
TIMING_ENTRY_POINTS = {'test_experiments.py', 'test_structure_timing', 'test_structure_benchmark.py',
    'test_search_timing', 'test_search_benchmark.py', 'test_timing', 'test_benchmark.py',
    'test_parallel_mergesort', 'test_parallel_benchmark.py', 'test_comparison'}


def load_manifest():
    manifest = strict_json(MANIFEST.read_text())
    require(isinstance(manifest, dict) and type(manifest.get('schema_version')) is int and
            manifest['schema_version'] in [1, 2] and manifest.get('policy') in
            ['non_timing_correctness_v1', 'non_timing_correctness_v2'],
            'invalid non-timing manifest')
    hashes = manifest.get('reviewed_source_sha256')
    validate_digest_map(hashes, 'reviewed non-timing source snapshot')
    require(hashes == source_manifest(), 'non-timing source snapshot changed; review and reclassify before execution')
    tests = manifest.get('tests')
    require(isinstance(tests, dict) and bool(tests), 'missing test classifications')
    for name, entry in tests.items():
        require(isinstance(name, str) and re.fullmatch('[a-z_]+', name) and isinstance(entry, dict),
                'invalid test classification')
        require(entry.get('classification') in CLASSES and isinstance(entry.get('reason'), str) and entry['reason'],
                'unclassified test: ' + name)
        require(isinstance(entry.get('command'), list) and bool(entry['command']) and
                all(isinstance(a, str) and a for a in entry['command']), 'missing reviewed command: ' + name)
    cpu = manifest.get('cpu_build_tests'); gpu = manifest.get('cuda_additional_tests')
    require(isinstance(cpu, list) and isinstance(gpu, list) and cpu and gpu and
            all(isinstance(n, str) for n in cpu + gpu) and len(set(cpu + gpu)) == len(cpu + gpu) and
            set(cpu + gpu) == set(tests), 'invalid discovery coverage manifest')
    return manifest


def expected_command(pattern, build_dir):
    result = []
    for token in pattern:
        if token == '@python':
            result.append(str(Path(sys.executable).resolve()))
        elif token == '@build':
            result.append(str(build_dir.resolve()))
        elif token == '@source':
            result.append(str(ROOT.resolve()))
        elif token.startswith('@build/'):
            relative = token[len('@build/'):]
            require(Path(relative).name == relative and relative not in ['.', '..'], 'unsafe reviewed binary')
            result.append(str((build_dir / relative).resolve()))
        elif token.startswith('@source/'):
            relative = token[len('@source/'):]
            require(not Path(relative).is_absolute() and '..' not in Path(relative).parts, 'unsafe reviewed source')
            result.append(str((ROOT / relative).resolve()))
        else:
            raise ValueError('unreviewed command token: ' + token)
    return result


def pre_discovery_gate(build_dir):
    """Shared static gate; never invokes CTest or evaluates CMake code."""
    manifest = load_manifest()
    return manifest, validate_build_tree(build_dir, manifest, expected_command)


def select_tests(discovery, build_dir, allow_gpu=False, allow_diagnostics=False):
    manifest, guard = pre_discovery_gate(build_dir)
    build_dir = Path(guard['build_dir'])
    require(isinstance(discovery, dict) and discovery.get('kind') == 'ctestInfo' and
            discovery.get('version') == {'major': 1, 'minor': 0} and isinstance(discovery.get('tests'), list),
            'invalid CTest JSON discovery')
    tests = discovery['tests']; names = [t.get('name') if isinstance(t, dict) else None for t in tests]
    require(all(isinstance(n, str) for n in names) and len(set(names)) == len(names), 'duplicate/malformed discovered tests')
    expected_cpu = set(manifest['cpu_build_tests']); expected_gpu = set(manifest['cuda_additional_tests'])
    require(set(names) in [expected_cpu, expected_cpu | expected_gpu], 'unknown/missing/unclassified discovered tests')
    require(set(names) == set(guard['test_names']), 'discovery differs from guarded registry coverage')
    if allow_gpu:
        require(set(names) == expected_cpu | expected_gpu, 'GPU correctness requested from non-CUDA build')
    selected, excluded = [], []
    for test in tests:
        name = test['name']; entry = manifest['tests'][name]; classification = entry['classification']
        command = test.get('command')
        require(isinstance(command, list) and all(isinstance(a, str) for a in command) and
                [str(Path(a).resolve()) for a in command] ==
                [str(Path(a).resolve()) for a in guard['commands'][name]],
                'discovery differs from guarded registry: ' + name)
        if (classification == 'timing' or (classification == 'gpu_correctness' and not allow_gpu)
                or (entry.get('diagnostic_only') is True and not allow_diagnostics)):
            excluded.append(dict(name=name, classification=classification, reason=entry['reason']))
            continue
        command = test.get('command')
        require(isinstance(command, list) and all(isinstance(a, str) for a in command), 'missing discovered command: ' + name)
        entry_points = {Path(a).name for a in command}
        require(not (entry_points & TIMING_ENTRY_POINTS) and
                not ('test_cuda_benchmark.py' in entry_points and len(command) != 2),
                'timing entry point cannot be selected: ' + name)
        require([str(Path(a).resolve()) for a in command] == expected_command(entry['command'], build_dir),
                'unreviewed CTest command/arguments: ' + name)
        properties = test.get('properties', [])
        require(isinstance(properties, list) and all(isinstance(p, dict) and p.get('name') in SAFE_PROPERTIES
                for p in properties), 'unsafe/unreviewed CTest properties: ' + name)
        require(len({p['name'] for p in properties}) == len(properties), 'duplicate discovered property: ' + name)
        expected_properties = guard['properties'][name]
        for prop in properties:
            key, value = prop['name'], prop.get('value')
            if key == 'WORKING_DIRECTORY':
                require(value == str(build_dir), 'unreviewed discovery working directory: ' + name)
            elif key in ['TIMEOUT', 'SKIP_RETURN_CODE']:
                require(key in expected_properties and value == int(expected_properties[key]),
                        'unreviewed discovery numeric property: ' + name)
            else:
                raise ValueError('unreviewed discovered property: ' + key)
        selected.append(name)
    require(bool(selected), 'empty non-timing selection')
    expression = '^(' + '|'.join(re.escape(n) for n in sorted(selected)) + ')$'
    argv = ['ctest', '--test-dir', str(build_dir), '--output-on-failure', '-V', '--parallel', '1', '-R', expression]
    return dict(schema_version=1, policy=manifest['policy'], manifest_sha256=sha(MANIFEST),
                allow_gpu_correctness=allow_gpu, selected=sorted(selected), excluded=excluded,
                discovered_count=len(tests), selected_count=len(selected), ctest_argv=argv,
                build_metadata=guard,
                tests_executed=False, full_protocol_prerequisites=False)


def selected_ctest(call, output, name, build_dir, allow_gpu=False, prefix=None, allow_diagnostics=False):
    """Discover and save the exact safe selection before the caller executes it."""
    require(list(prefix or []) in [[],
        ['env', '-u', 'ASAN_OPTIONS', '-u', 'LSAN_OPTIONS', 'UBSAN_OPTIONS=halt_on_error=1'],
        ['env', 'ASAN_OPTIONS=detect_leaks=0', 'UBSAN_OPTIONS=halt_on_error=1']], 'unreviewed CTest wrapper')
    _, guarded = pre_discovery_gate(build_dir)
    # Retain the exact checked identity; the callback may use a different cwd.
    build_dir = Path(guarded['build_dir'])
    discovery = call(name + '_discovery', ['ctest', '--test-dir', str(build_dir), '-N', '--show-only=json-v1'], 60)
    require(discovery.get('exit_code', 0) == 0, 'CTest discovery failed')
    plan = select_tests(strict_json(discovery['stdout']), build_dir, allow_gpu, allow_diagnostics)
    require(plan['build_metadata'] == guarded, 'build metadata changed during discovery')
    dump_new(output / (name + '_selection.json'), plan)
    # Repeat source AND generated-metadata checks at the execution boundary.
    _, final_guard = pre_discovery_gate(build_dir)
    require(final_guard == guarded, 'build metadata changed before execution')
    result = call(name, list(prefix or []) + plan['ctest_argv'], 900)
    require(re.search(r'0 tests failed out of ' + str(plan['selected_count']) + r'(?:\s|$)', result['stdout']) and
            '***Skipped' not in result['stdout'], 'non-timing correctness coverage failed/skipped')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument('--build-dir', type=Path, required=True)
    parser.add_argument('--discovery-json', type=Path, help='Read retained discovery without invoking CTest')
    parser.add_argument('--allow-gpu-correctness', action='store_true')
    parser.add_argument('--allow-diagnostics', action='store_true', help='Include separately reviewed untimed diagnostics')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        _, guarded = pre_discovery_gate(args.build_dir)
        build_dir = Path(guarded['build_dir'])
        if args.discovery_json:
            discovery = strict_json(args.discovery_json.read_text())
        else:
            child = subprocess.run(['ctest', '--test-dir', str(build_dir), '-N', '--show-only=json-v1'],
                                   capture_output=True, text=True, check=True, timeout=60)
            discovery = strict_json(child.stdout)
        plan = select_tests(discovery, build_dir, args.allow_gpu_correctness, args.allow_diagnostics)
        require(plan['build_metadata'] == guarded, 'build metadata changed during discovery')
        if args.output:
            dump_new(args.output, plan)
        print(json.dumps(plan, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print('selection error: ' + str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
