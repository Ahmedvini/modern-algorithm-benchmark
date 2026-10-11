"""AST, retained log and byte inspection only; never import project modules."""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import re

ROOT = Path.cwd()
BASE = Path(__file__).resolve().parent
REPAIR = ROOT / 'results/raw/ctest_hook_repair_20261010T223851377458Z'

def read(path):
    return json.loads(path.read_text())

def methods(path, name):
    module = ast.parse(path.read_text(), filename=str(path))
    cls = next(n for n in module.body if isinstance(n, ast.ClassDef) and n.name == name)
    return {n.name: n.lineno for n in cls.body if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')}

def logged_methods(name):
    record = read(REPAIR / 'commands' / (name + '.json'))
    lines = record['stderr'].splitlines()
    found = {line.split(' ', 1)[0] for line in lines if line.startswith('test_') and line.endswith(' ... ok')}
    assert record['exit_code'] == 0 and '\nOK\n' in record['stderr']
    return found

guard_methods = methods(ROOT / 'tests/test_ctest_build_guard.py', 'BuildGuardTests')
selector_methods = methods(ROOT / 'tests/test_cpu_gpu_safety.py', 'SelectorTests')
assert len(guard_methods) == 28 and len(selector_methods) == 11
assert logged_methods('inert_regressions_sealed_source') == set(guard_methods)
assert logged_methods('existing_inert_selection_tests_final') == set(selector_methods)

source_files = [
    'AGENTS.md', 'README.md', 'docs/ROADMAP.md', 'docs/EXPERIMENT_PROTOCOL.md',
    'docs/CTEST_BUILD_GUARD_v1.md', 'docs/NON_TIMING_TEST_SELECTION_v1.json',
    'scripts/ctest_build_guard.py', 'scripts/non_timing_tests.py',
    'scripts/cpu_gpu_protocol.py', 'scripts/cpu_gpu_provenance.py',
    'scripts/validate_cpu_gpu_pilot.py', 'scripts/run_cpu_gpu_pilot.py',
    'scripts/validate_cuda_sort.py', 'scripts/validate_cuda_timing.py',
    'tests/test_ctest_build_guard.py', 'tests/ctest_fixture.py',
    'tests/test_cpu_gpu_safety.py', 'tests/test_cpu_gpu_comparison.py',
    'CMakeLists.txt', 'cmake/cuda.cmake',
]
report = {
    'method_counts': {'new_guard': 28, 'existing_selector': 11, 'distinct_total': 39},
    'tests_executed_by_this_review': 0,
    'retained_success_logs_match_current_method_names': True,
    'guard_methods': guard_methods, 'selector_methods': selector_methods,
    'source_inventory': {p: {'sha256': hashlib.sha256((ROOT / p).read_bytes()).hexdigest(),
                             'lines': len((ROOT / p).read_text().splitlines())} for p in source_files},
}
old_guard = (REPAIR / 'attempt1/scripts/ctest_build_guard.py').read_text()
new_guard = (ROOT / 'scripts/ctest_build_guard.py').read_text()
report['initial_guard_correction_diff'] = ''.join(difflib.unified_diff(
    old_guard.splitlines(True), new_guard.splitlines(True), fromfile='retained_attempt1', tofile='current'))
assert "[A-Za-z][A-Za-z0-9]*" in report['initial_guard_correction_diff']
initial = read(REPAIR / 'commands/inert_regressions.json')
assert initial['exit_code'] == 1 and 'Ran 26 tests' in initial['stderr'] and 'FAILED (errors=1)' in initial['stderr']
report['initial_regression_failure'] = {'exit_code': 1, 'methods': 26, 'passed': 25, 'errors': 1,
    'reason': 'Dart key grammar excluded digits; retained error and source correction inspected'}

# Pure path arithmetic describes a public-helper counterexample. This does not
# create a fixture, call a selector/callback, inspect resources or launch a child.
relative = Path('build/REVIEW_PATH_EXAMPLE')
caller = Path('/tmp/REVIEW_CALLER_EXAMPLE')
assert not relative.is_absolute()
report['relative_discovery_path_static_counterexample'] = {
    'kind': 'static control-flow/path analysis, not executed',
    'public_entry': 'scripts/non_timing_tests.py:selected_ctest:133',
    'validator_cwd_example': str(caller), 'relative_argument_example': str(relative),
    'tree_checked_by_guard': str(caller / relative),
    'discovery_argv_argument': str(relative),
    'existing_invoke_callback_cwd': str(ROOT),
    'tree_opened_by_that_callback': str(ROOT / relative),
    'different_tree_identities': (caller / relative) != (ROOT / relative),
    'guard_lines': [106, 107, 156], 'discovery_line': 139,
    'callback_lines': [20, 21, 26],
    'current_prerequisite_calls_supply_absolute_paths': True,
    'existing_tests_use_absolute_temporary_build_paths': True,
    'fix_recommendation_only': 'Pin discovery to guarded[build_dir], or reject nonabsolute paths before any callback; add inert mixed-cwd coverage.',
}
assert report['relative_discovery_path_static_counterexample']['different_tree_identities']
report['legacy_paths_outside_guard'] = {
    'scripts/validate_cpu_gpu_pilot.py': [49, 58, 67, 85],
    'scripts/validate_cuda_sort.py': [113],
    'scripts/validate_cuda_timing.py': [49],
    'scope_note': 'Intentional full/timing workflows do not silently enter prerequisites-only; universal guard coverage is not implemented.',
}
report['concurrency_qualification'] = 'Boundary rechecks detect inter-boundary modifications but are not atomic; exclusive quiescent trees and trusted tools remain unenforced assumptions.'
with (BASE / 'STATIC_REVIEW.json').open('x') as f:
    json.dump(report, f, indent=2, sort_keys=True)
    f.write('\n')
print(json.dumps({k: v for k, v in report.items() if k not in ['source_inventory', 'guard_methods', 'selector_methods']}, indent=2, sort_keys=True))
