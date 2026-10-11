"""Final read-only preservation checks; writes only new review evidence/seal."""
import datetime
import hashlib
import json
from pathlib import Path
import shlex

ROOT = Path.cwd()
BASE = Path(__file__).resolve().parent

def read(path):
    return json.loads(path.read_text())

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def mapping(paths):
    return {str(p.relative_to(ROOT)): sha(p) for p in sorted(set(paths)) if p.is_file()}

start = read(BASE / 'START_SNAPSHOT.json')
for key in ['prior_results_sha256', 'project_sha256', 'build_metadata_sha256']:
    differences = [p for p, h in start[key].items() if not (ROOT / p).is_file() or sha(ROOT / p) != h]
    assert not differences, (key, differences)
project = mapping([ROOT / 'AGENTS.md', ROOT / 'README.md', ROOT / 'CMakeLists.txt'] +
                  [p for name in ['scripts', 'tests', 'docs', 'include', 'src', 'cmake', 'third_party']
                   for p in (ROOT / name).rglob('*') if '__pycache__' not in p.parts])
assert project == start['project_sha256']
builds = mapping([p for p in (ROOT / 'build').rglob('*') if p.name in
                  ['CTestTestfile.cmake', 'DartConfiguration.tcl', 'CTestCustom.cmake', 'CTestCustom.ctest']])
assert builds == start['build_metadata_sha256']
verification = read(BASE / 'EVIDENCE_VERIFICATION.json')
assert verification['repair_baseline_result_files_verified'] == 11448
assert verification['review_start_result_files_verified'] == 11516
assert verification['differences'] == []
assert read(BASE / 'STATIC_REVIEW.json')['tests_executed_by_this_review'] == 0

commands = ['# Independent review commands and exit statuses\n',
            'Only static inspections and evidence writes ran. No repository Python module, selector, guard, test or validation entry point was executed.\n',
            'Recorder invocation: `python3 -B ' + str(BASE.relative_to(ROOT)) + '/record.py NAME SAFETY CHILD_ARGV...`. '
            'Each JSON contains the exact child argv/cwd, stdout, stderr, safety classification and observed exit code.\n',
            'Early unwrapped commands and evidence-only tool writes: EARLY_COMMANDS.md.\n']
for path in sorted((BASE / 'commands').glob('*.json')):
    record = read(path)
    assert record['exit_code'] == 0, path
    assert record['argv'][0] in ['cat', 'rg', 'sed', 'nl', 'tail', 'python3']
    assert not any(Path(a).name in ['ctest', 'colab', 'nvcc'] for a in record['argv'])
    if record['argv'][0] == 'python3' and '-c' not in record['argv']:
        assert Path(record['argv'][-1]).parent == BASE.relative_to(ROOT), record['argv']
    commands.append('\n## ' + path.stem + '\n\n```sh\n' + shlex.join(record['argv']) +
                    '\n```\n\nExit ' + str(record['exit_code']) + '; safety: ' + record['safety'] +
                    '. Full output: `commands/' + path.name + '`.\n')
seal_command = 'python3 -B ' + str(BASE.relative_to(ROOT)) + '/seal_review.py'
commands.append('\n## Final evidence seal\n\n```sh\n' + seal_command +
                '\n```\n\nExit0 on successful completion; unwrapped terminal command. '
                'Only file hashes, retained log checks and exclusive new evidence writes; no workloads.\n')
with (BASE / 'COMMANDS.md').open('x') as f:
    f.write('\n'.join(commands))
results = mapping((ROOT / 'results').rglob('*'))
added = set(results) - set(start['prior_results_sha256'])
assert all(p.startswith(str(BASE.relative_to(ROOT)) + '/') for p in added)
assert not set(start['prior_results_sha256']) - set(results)
evidence = mapping(BASE.rglob('*'))
assert len(added) == len(evidence)
seal = dict(schema_version=1, decision='NO-GO', study_authorized=False,
            command=seal_command, exit_code=0, utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            scope='independent static review only',
            blocker='Discovery callback uses original potentially relative build path rather than the checked absolute identity.',
            prior_result_files_before=len(start['prior_results_sha256']),
            prior_result_files_after_verified=len(start['prior_results_sha256']),
            changed_or_missing_prior_result_files=[], project_files_verified=len(project),
            project_changes=[], existing_build_metadata_verified=len(builds),
            source_or_historical_writes=0, actual_tests=0, actual_ctest_discovery=0,
            actual_builds=0, actual_prerequisites=0, actual_resource_checks=0,
            actual_timing_trials=0, actual_benchmarks=0, actual_gpu_commands=0,
            historical_regressions_inspected_not_rerun=39,
            new_review_evidence_files=len(evidence)+1, final_result_file_count=len(results)+1,
            evidence_sha256=evidence, manifest_excludes_itself=True)
with (BASE / 'FINAL_INTEGRITY.json').open('x') as f:
    json.dump(seal, f, indent=2, sort_keys=True)
    f.write('\n')
print(json.dumps({k: v for k, v in seal.items() if k != 'evidence_sha256'}, indent=2, sort_keys=True))
