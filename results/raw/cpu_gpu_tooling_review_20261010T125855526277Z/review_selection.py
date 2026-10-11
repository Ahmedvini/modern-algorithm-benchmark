"""Inspect recorded selection and current source without executing a CTest."""
import ast
import json
from pathlib import Path
import re

root = Path.cwd()
base = Path(__file__).resolve().parent
old = root / 'results/raw/cpu_gpu_full_tooling_20261010T121208603276Z'
names = ['release_ctest_non_timing','release_ctest_final','sanitize_ctest_final']
report = dict(selections={}, actual_timing_rows=6, measured_rows=4, warmup_rows=2,
              timing_value_serialization=False, initial_exit_code=None)
for name in names:
    record = json.loads((old / 'commands' / (name + '.json')).read_text())
    pattern = record['argv'][record['argv'].index('-R')+1]
    report['selections'][name] = dict(argv=record['argv'], exit_code=record['exit_code'],
        selects_parallel_mergesort=bool(re.search(pattern, 'parallel_mergesort')))
    if name == names[0]:
        report['initial_exit_code'] = record['exit_code']
        report['initial_observed_stdout'] = [line for line in record['stdout'].splitlines()
            if 'test_parallel_mergesort' in line or '6 timing rows passed' in line or 'tests failed' in line]
source = (root / 'tests/test_parallel_mergesort.cpp').read_text().splitlines()
begin = next(i for i, line in enumerate(source) if 'c.dataset.size=32768;c.repetitions=2;c.warmups=1' in line)
report['test_source_excerpt'] = {str(i+1): source[i] for i in range(begin, min(begin+14, len(source)))}
remote = ast.parse((old / 'remote_non_timing_validation.py').read_text())
remote_names = next(ast.literal_eval(n.value) for n in ast.walk(remote) if isinstance(n, ast.Assign)
    and any(isinstance(t, ast.Name) and t.id=='names' for t in n.targets))
report['remote_corrected_allowlist'] = remote_names
validator = ast.parse((root / 'scripts/validate_cpu_gpu_pilot.py').read_text())
ctests = []
for node in ast.walk(validator):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id=='call' and node.args:
        if isinstance(node.args[0], ast.Constant) and 'ctest' in str(node.args[0].value):
            ctsets = dict(name=node.args[0].value, line=node.lineno, source=ast.unparse(node))
            ctsets['selection_filter_present'] = any(isinstance(x, ast.Constant) and x.value in ['-R','-E','--tests-regex','--exclude-regex'] for x in ast.walk(node))
            ctests.append(ctsets)
report['future_prerequisites_ctest_calls'] = ctests
tests = ast.parse((root / 'tests/test_cpu_gpu_comparison.py').read_text())
report['selection_related_test_names'] = [n.name for n in ast.walk(tests) if isinstance(n, ast.FunctionDef)
    and n.name.startswith('test_') and any(s in n.name for s in ['selection','allowlist','prerequisites_only'])]
report['conclusion'] = ('Recorded later allowlists exclude parallel_mergesort; no repository regression test protects a non-timing selector. '
    'The prerequisites-only validator intentionally runs full timing-bearing CTest suites, as its guide warns; it is unsafe under the current no-timing instruction.')
with (base / 'SELECTION_REVIEW.json').open('x') as stream:
    json.dump(report, stream, indent=2, sort_keys=True); stream.write('\n')
assert report['selections'][names[0]]['selects_parallel_mergesort']
assert all(not report['selections'][n]['selects_parallel_mergesort'] for n in names[1:])
assert 'parallel_mergesort' not in remote_names
assert len([n for n in report['initial_observed_stdout'] if '6 timing rows passed' in n]) == 1
print(json.dumps(report, indent=2))
