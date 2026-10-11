"""Verify preservation/provenance and exclusively save final review evidence."""
import difflib
import hashlib
import json
from pathlib import Path
import subprocess

evidence = Path(__file__).resolve().parent
backup = Path('build/timsort_review')
changed = []
diff = []
for before in sorted(backup.rglob('*')):
    if not before.is_file():
        continue
    relative = before.relative_to(backup)
    current = Path(relative)
    assert current.exists(), f'Removed existing file: {relative}'
    if before.read_bytes() != current.read_bytes():
        changed.append(str(relative))
        diff.extend(difflib.unified_diff(before.read_text().splitlines(True),
                                        current.read_text().splitlines(True),
                                        fromfile='before/' + str(relative),
                                        tofile='after/' + str(relative)))
preserved = ['src/algorithms/quicksort.cpp', 'include/algorithms/detail/quicksort_impl.hpp',
             'src/algorithms/pdqsort.cpp', 'src/datasets/generator.cpp',
             'tests/test_quicksort.cpp', 'tests/test_pdqsort.cpp',
             'tests/test_baselines.cpp', 'tests/test_datasets.cpp']
for name in preserved:
    assert Path(name).read_bytes() == (backup / name).read_bytes(), name
for algorithm in ['pdqsort', 'timsort']:
    root = Path('third_party') / algorithm
    metadata = json.loads((root / 'UPSTREAM.json').read_text())
    for name, info in metadata['files'].items():
        content = (root / name).read_bytes()
        assert hashlib.sha256(content).hexdigest() == info['sha256'], name
        if algorithm == 'timsort':
            committed = subprocess.check_output(['git', '-C', 'build/timsort-upstream',
                                                'show', metadata['revision'] + ':' + name])
            assert content == committed, name
for mode in ['release', 'sanitize']:
    for action in ['configure', 'build', 'ctest']:
        record = json.loads((evidence / f'{mode}_{action}.json').read_text())
        assert record['exit_code'] == 0, record
    record = json.loads((evidence / f'{mode}_ctest.json').read_text())
    assert '100% tests passed, 0 tests failed out of 7' in record['output']
    assert 'Passed 4149 Timsort differential cases' in record['output']
    with (evidence / f'final_{mode}_ctest.log').open('xb') as stream:
        stream.write(Path('build', mode, 'Testing/Temporary/LastTest.log').read_bytes())
with (evidence / 'timsort_upstream.json').open('xb') as stream:
    stream.write(Path('third_party/timsort/UPSTREAM.json').read_bytes())
source_paths = sorted(path for root in ['include', 'src', 'tests', 'docs', 'third_party']
                      for path in Path(root).rglob('*') if path.is_file())
source_paths.extend([Path('README.md'), Path('CMakeLists.txt')])
hashes = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in source_paths}
review = {'record_kind': 'correctness_source_review', 'modified_existing_files': changed,
          'preserved_files': preserved, 'source_sha256': hashes,
          'release_ctest_groups_passed': 7, 'sanitize_ctest_groups_passed': 7,
          'timsort_differential_inputs_per_configuration': 4149,
          'leak_detection_disabled': False, 'benchmark_measurements_collected': False}
with (evidence / 'source_review.json').open('x') as stream:
    json.dump(review, stream, indent=2)
    stream.write('\n')
with (evidence / 'existing_files.patch').open('x') as stream:
    stream.writelines(diff)
print('Verified pinned source hashes and preserved existing algorithms/tests.')
print('Modified existing files:', ', '.join(changed))
print('Saved final CTest logs, provenance, source hashes and review diff.')
