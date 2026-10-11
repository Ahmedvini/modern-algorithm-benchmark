"""Verify unchanged production paths and retained benchmark evidence."""
import difflib
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

evidence = Path(__file__).resolve().parent
backup = Path('build/benchmark_review')
changed = []
patch = []
for previous in sorted(backup.rglob('*')):
    if not previous.is_file() or '__pycache__' in previous.parts:
        continue
    relative = previous.relative_to(backup)
    current = Path(relative)
    assert current.is_file(), f'removed file: {relative}'
    if previous.read_bytes() != current.read_bytes():
        changed.append(str(relative))
        patch.extend(difflib.unified_diff(previous.read_text().splitlines(True),
                                         current.read_text().splitlines(True),
                                         fromfile='before/' + str(relative),
                                         tofile='after/' + str(relative)))
allowed = {'CMakeLists.txt', 'README.md', 'docs/ALGORITHMS.md', 'docs/AUDIT.md',
           'docs/ROADMAP.md', 'docs/EXPERIMENT_PROTOCOL.md'}
assert set(changed) == allowed, changed
preserved = []
for prefix in ['src', 'include', 'tests', 'third_party', 'scripts']:
    for previous in sorted((backup / prefix).rglob('*')):
        if previous.is_file() and '__pycache__' not in previous.parts:
            relative = previous.relative_to(backup)
            assert previous.read_bytes() == Path(relative).read_bytes(), str(relative)
            preserved.append(str(relative))
for vendor in ['pdqsort', 'timsort']:
    base = Path('third_party') / vendor
    for name, metadata in json.loads((base / 'UPSTREAM.json').read_text())['files'].items():
        assert hashlib.sha256((base / name).read_bytes()).hexdigest() == metadata['sha256']
for mode, configuration in [('release', 'Release'), ('sanitize', 'Debug')]:
    manifest = json.loads(Path('build', mode, 'generated', configuration, 'source_hashes.json').read_text())
    for row in manifest['files']:
        assert hashlib.sha256(Path(row['path']).read_bytes()).hexdigest() == row['sha256'], row
    tests = json.loads((evidence / f'final_{mode}_ctest.json').read_text())
    assert tests['exit_code'] == 0 and '100% tests passed, 0 tests failed out of 13' in tests['output']
    with (evidence / f'final_{mode}_ctest.log').open('xb') as stream:
        stream.write(Path('build', mode, 'Testing/Temporary/LastTest.log').read_bytes())
link = Path('build/release/CMakeFiles/sort_benchmark.dir/link.txt').read_text()
assert 'libmab_timing' in link and 'libmab_core' in link and 'libmab_metrics' not in link
symbols = subprocess.run(['nm', '-C', 'build/release/sort_benchmark'],
                         check=True, capture_output=True, text=True)
assert not any(name in symbols.stdout for name in ['CountingLess', 'mab::counted_sorters', 'mab::process_memory'])
spec = importlib.util.spec_from_file_location('benchmark_analysis', 'scripts/analyze_results.py')
analysis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analysis)
matrix = evidence / 'smoke_matrix'
summary_path = Path('results/processed/benchmark_smoke_20261009T160450529409Z.json')
summary = json.loads(summary_path.read_text())
assert analysis.analyze(matrix) == summary, 'summary regeneration differs'
assert summary['complete'] and len(summary['groups']) == 40
assert sum(group['successful_trials'] for group in summary['groups']) == 200
assert sum(group['warmup_rows'] for group in summary['groups']) == 40
assert not any(group['failed_trials'] for group in summary['groups'])
env = json.loads((matrix / 'environment.json').read_text())
assert env['benchmark_executable_sha256'] == hashlib.sha256(Path('build/release/sort_benchmark').read_bytes()).hexdigest()
for run in matrix.glob('run_*/source_hashes.json'):
    for row in json.loads(run.read_text())['files']:
        assert hashlib.sha256(Path(row['path']).read_bytes()).hexdigest() == row['sha256']
paths = sorted(path for root in ['include', 'src', 'tests', 'docs', 'third_party', 'scripts', 'cmake']
               for path in Path(root).rglob('*') if path.is_file() and '__pycache__' not in path.parts)
paths.extend([Path('README.md'), Path('CMakeLists.txt')])
added = [str(path) for path in paths if not (backup / path).exists()]
for name in added:
    patch.extend(difflib.unified_diff([], Path(name).read_text().splitlines(True),
                                     fromfile='/dev/null', tofile='after/' + name))
review = {'record_kind': 'sorting_benchmark_source_review', 'modified_existing_files': changed,
          'added_project_files': added, 'preserved_files': preserved,
          'source_sha256': {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths},
          'timing_link_command': link.strip(), 'metrics_symbols_in_timing_binary': False,
          'release_test_groups_passed': 13, 'sanitize_test_groups_passed': 13,
          'leak_detection_disabled': False, 'actual_smoke_configurations': 10,
          'actual_measured_trials': 200, 'actual_warmups': 40, 'actual_summary_groups': 40,
          'largest_performance_input': 10000, 'summary_regenerated_exactly': True}
with (evidence / 'source_review.json').open('x') as stream:
    json.dump(review, stream, indent=2)
    stream.write('\n')
with (evidence / 'changes.patch').open('x') as stream:
    stream.writelines(patch)
print('Preserved original production/metrics/interfaces/tests/vendors/scripts.')
print('Timing binary links only mab_timing/mab_core, without metric symbols.')
print('Source hashes match both builds and all measured smoke bundles.')
print('Regenerated the 40-group/200-measurement/40-warmup summary exactly.')
print('Modified:', ', '.join(changed))
print('Added:', ', '.join(added))
