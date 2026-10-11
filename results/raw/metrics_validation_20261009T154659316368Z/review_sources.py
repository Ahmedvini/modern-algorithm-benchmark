"""Exclusively save metrics validation source, preservation and linkage evidence."""
import difflib
import hashlib
import json
from pathlib import Path
import subprocess

evidence = Path(__file__).resolve().parent
backup = Path('build/metrics_review')
modified = []
diff = []
for previous in sorted(backup.rglob('*')):
    if not previous.is_file():
        continue
    relative = previous.relative_to(backup)
    current = Path(relative)
    assert current.is_file(), f'Removed existing file: {relative}'
    if previous.read_bytes() != current.read_bytes():
        modified.append(str(relative))
        diff.extend(difflib.unified_diff(previous.read_text().splitlines(True),
                                        current.read_text().splitlines(True),
                                        fromfile='before/' + str(relative),
                                        tofile='after/' + str(relative)))
allowed = {'CMakeLists.txt', 'README.md', 'docs/ALGORITHMS.md', 'docs/AUDIT.md',
           'docs/ROADMAP.md', 'docs/EXPERIMENT_PROTOCOL.md',
           'include/algorithms/detail/quicksort_impl.hpp'}
assert set(modified) == allowed, modified
preserved = []
for prefix in ['src/algorithms', 'src/datasets', 'tests', 'third_party']:
    for previous in sorted((backup / prefix).rglob('*')):
        if previous.is_file():
            relative = previous.relative_to(backup)
            assert previous.read_bytes() == Path(relative).read_bytes(), str(relative)
            preserved.append(str(relative))
for name in ['src/main.cpp', 'include/algorithms/sorting.hpp']:
    assert Path(name).read_bytes() == (backup / name).read_bytes(), name
    preserved.append(name)
for vendor in ['pdqsort', 'timsort']:
    root = Path('third_party') / vendor
    metadata = json.loads((root / 'UPSTREAM.json').read_text())
    for name, info in metadata['files'].items():
        assert hashlib.sha256((root / name).read_bytes()).hexdigest() == info['sha256'], name
link = Path('build/release/CMakeFiles/algorithm_benchmark.dir/link.txt').read_text()
assert 'libmab_core' in link and 'libmab_metrics' not in link, link
nm = subprocess.run(['nm', '-C', 'build/release/algorithm_benchmark'],
                    capture_output=True, text=True, check=True)
for symbol in ['CountingLess', 'mab::counted_sorters', 'mab::process_memory']:
    assert symbol not in nm.stdout, symbol
for mode in ['release', 'sanitize']:
    for action in ['configure', 'build', 'ctest']:
        record = json.loads((evidence / f'metrics_{mode}_{action}.json').read_text())
        assert record['exit_code'] == 0, record
        if action == 'build':
            assert 'warning:' not in record['output'].lower(), record
    tests = json.loads((evidence / f'metrics_{mode}_ctest.json').read_text())['output']
    assert '100% tests passed, 0 tests failed out of 11' in tests
    assert 'Passed 1404 comparison differential' in tests
    with (evidence / f'final_{mode}_ctest.log').open('xb') as output:
        output.write(Path('build', mode, 'Testing/Temporary/LastTest.log').read_bytes())
paths = sorted(path for root in ['include', 'src', 'tests', 'docs', 'third_party']
               for path in Path(root).rglob('*') if path.is_file())
paths.extend([Path('README.md'), Path('CMakeLists.txt')])
added = [str(path) for path in paths if not (backup / path).exists()]
for name in added:
    diff.extend(difflib.unified_diff([], Path(name).read_text().splitlines(True),
                                    fromfile='/dev/null', tofile='after/' + name))
record = {'record_kind': 'metrics_validation_source_review',
          'modified_existing_files': modified, 'added_project_files': added,
          'preserved_files': preserved,
          'source_sha256': {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths},
          'normal_executable_link_command': link.strip(),
          'normal_executable_contains_metrics_symbols': False,
          'nm_command': nm.args, 'nm_exit_code': nm.returncode,
          'release_ctest_passed': 11, 'sanitize_ctest_passed': 11,
          'leak_detection_disabled': False, 'performance_experiments_run': False}
with (evidence / 'source_review.json').open('x') as output:
    json.dump(record, output, indent=2)
    output.write('\n')
with (evidence / 'changes.patch').open('x') as output:
    output.writelines(diff)
print('Preserved original CLI/registry/adapters/tests and every vendored file.')
print('Normal executable links only mab_core and contains no metrics symbols.')
print('Modified existing files:', ', '.join(modified))
print('Added project files:', ', '.join(added))
print('Saved final logs, source hashes and review patch; both suites passed 11/11.')
