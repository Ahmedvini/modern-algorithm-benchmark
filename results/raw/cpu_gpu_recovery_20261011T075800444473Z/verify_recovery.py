"""Offline byte/metadata review only; no executable, test or GPU invocation."""
import ast
import hashlib
import json
from pathlib import Path
import re
import sys

r = Path.cwd(); e = Path(__file__).resolve().parent
sys.path.insert(0, str(r / 'scripts'))
from cpu_gpu_protocol import load_protocol, sha, source_manifest, verify_source_extension
from cpu_gpu_framework_compatibility import POLICY_ID
from cpu_gpu_provenance import validate_retained_source
from cpu_gpu_validation_policy import verify_current_sources
import non_timing_tests as selector

before = json.loads((e / 'BEFORE.json').read_text())
model = load_protocol(); verify_current_sources()
for path, digest in before['frozen_sha256'].items(): assert sha(r / path) == digest
review = verify_source_extension(model, POLICY_ID); validate_retained_source(review, model)
for path in ['scripts/ctest_build_guard.py', 'scripts/non_timing_tests.py',
             'docs/NON_TIMING_TEST_SELECTION_v3.json', 'docs/CPU_GPU_VALIDATION_POLICY_v2.json']:
    assert sha(r / path) == before['project_sha256'][path]
manifest = json.loads((r / 'docs/NON_TIMING_TEST_SELECTION_v3.json').read_text())
approved = sorted(n for n in manifest['cpu_build_tests']
                  if manifest['tests'][n]['classification'] == 'cpu_correctness'
                  and not manifest['tests'][n].get('diagnostic_only', False))
assert approved == sorted('baselines cli comparisons cpu_gpu_comparison_framework cuda_benchmark_analysis cuda_preflight cuda_sort_handoff datasets environment_manifest memory memory_unsupported mergesort metrics_cli pdqsort quicksort radixsort searching structures timsort'.split())
try:
    selector.load_manifest()  # File/metadata checks only. Never discovery.
except ValueError as error:
    assert 'source snapshot changed' in str(error)
    selector_result = dict(status='expected fail-closed', error=str(error), ctest_invoked=False)
else:
    raise AssertionError('source changes must require a separately reviewed selection snapshot')

inventory = json.loads((e / 'CHANGE_INVENTORY.json').read_text())
for name in inventory['modified'] + inventory['added']:
    if name.endswith('.py'): ast.parse((r / name).read_text(), filename=name)
raw = r / 'results/raw/bounded_resume_20261011T024034091796Z/downloaded/evidence'
counts = {}
for name in ['cpu_release_ctest', 'cpu_sanitize_ctest']:
    d = json.loads((raw / 'validation_commands' / (name + '.json')).read_text())
    text = d['stdout']; assert d['exit_code'] == 0
    assert '100% tests passed, 0 tests failed out of 21' in text
    passed = re.findall(r'\d+/21 Test\s+#\d+: ([a-z_]+)\s+\.+\s+Passed', text)
    assert len(passed) == 21 and len(set(passed)) == 21
    counts[name] = dict(passed_groups=len(passed), fresh_execution=False)
build = json.loads((raw / 'BUILD_COMPLETE.json').read_text())
assert 'comparison_input' not in build['identities']['gpu-release']
warnings = {}
for file in sorted((raw / 'build_commands').glob('*.json')):
    d = json.loads(file.read_text()); text = d.get('stdout', '') + d.get('stderr', '')
    warnings[file.name] = dict(total=text.count('warning:'),
        line_marker=text.count('warning: style of line directive is a GCC extension'), fresh_execution=False)
facts = dict(approved_cpu_selection=approved, selector=selector_result,
             current_source_files=len(source_manifest()), frozen_sha256=before['frozen_sha256'],
             compatibility_review=review, retained_cpu_results=counts,
             retained_warning_counts=warnings, retained_gpu_build=build['identities']['gpu-release'],
             intended_comparison_input_identity='unavailable; not invented or substituted',
             authentication='colab sessions exit0; no active sessions on server',
             production_or_framework_gpu_execution=0, benchmark_trials=0, warmups=0,
             native_tests=0, ctest_discovery=0, new_builds=0)
with (e / 'OFFLINE_VERIFICATION.json').open('x') as f:
    json.dump(facts, f, indent=2, sort_keys=True); f.write('\n')
print(json.dumps({k: v for k, v in facts.items() if k not in ['compatibility_review', 'retained_gpu_build']}, indent=2))
