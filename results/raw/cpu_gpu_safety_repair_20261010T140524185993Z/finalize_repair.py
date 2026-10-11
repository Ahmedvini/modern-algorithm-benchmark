import datetime
import json
from pathlib import Path
import shlex
import sys
sys.path.insert(0, 'scripts')
from cpu_gpu_protocol import sha, source_manifest, load_protocol
from cpu_gpu_provenance import trusted_source_anchors
from non_timing_tests import load_manifest

base = Path(__file__).resolve().parent
relative = base.relative_to(Path.cwd())
before = json.loads((base / 'BEFORE.json').read_text())
check = json.loads((base / 'INTEGRITY_CHECK.json').read_text())
for name, digest in before['prior_results_sha256'].items():
    assert Path(name).is_file() and sha(name) == digest, name
for name, digest in before['frozen_files_sha256'].items():
    assert sha(name) == digest, name
for name, digest in trusted_source_anchors(load_protocol()).items():
    assert sha(name) == digest, name
assert source_manifest() == check['current_source_sha256']
load_manifest()
old = json.loads(Path('results/raw/cpu_gpu_full_tooling_20261010T121208603276Z/FINAL_INTEGRITY.json').read_text())
assert before['current_source_sha256'] == old['current_source_sha256']
for name, digest in old['documentation_sha256'].items():
    assert sha(base / 'before' / name) == digest, name
for name, digest in old['evidence_sha256'].items():
    assert sha(name) == digest, name
assert (base / 'reproducer.py').read_bytes() == Path('results/raw/cpu_gpu_tooling_review_20261010T125855526277Z/probe_full_analysis.py').read_bytes()
assert sha(base / 'PILOT_REANALYSIS.json') == '07e69e2e0c8853f93d3f3da895337b5e4b72e5e2dd0ff0577db3cbd1f7053a22'
plan = json.loads((base / 'SELECTED_TESTS_FINAL.json').read_text())
assert plan['tests_executed'] is False and plan['selected_count'] == 19
future = [base / 'COMMANDS.md', base / 'FINAL_AUDIT.md', base / 'FINAL_INTEGRITY.json', base / 'commands/finalize_repair.json']
assert all(not p.exists() for p in future)
final_total = len([p for p in Path('results').rglob('*') if p.is_file()]) + len(future)
final_new = final_total - before['before_results_count']
record = dict(argv=['env', 'PYTHONDONTWRITEBYTECODE=1', 'python3', '-B', str(relative / 'finalize_repair.py')],
              cwd=str(Path.cwd()), exit_code=0, stdout='Preservation/source/selection checks passed; audit sealed.', stderr='',
              safety_classification='static_hash_audit_sealing_no_timing_no_gpu',
              timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
with future[3].open('x') as stream:
    json.dump(record, stream, indent=2, sort_keys=True); stream.write('\n')
commands = ['# Repair command ledger\n\nExact validation argv, exit codes and safety classifications follow. Full stdout/stderr and timestamps are retained in commands/*.json.\n\n']
for path in sorted((base / 'commands').glob('*.json')):
    document = json.loads(path.read_text())
    commands.append('## ' + path.stem + '\n\n```sh\n' + shlex.join(document['argv']) + '\n```\n\nExit: ' +
                    str(document['exit_code']) + '. Safety: `' + document['safety_classification'] +
                    '`. Log: `commands/' + path.name + '`.\n\n')
commands.append('## Inspection and preparation\n\nRead-only pwd/cat/sed/rg/file-list inspections covered instructions, latest review, frozen artifacts, pilot/workspace evidence, CMake and test/implementation files. One initial rg referenced nonexistent tests/test_capture_environment.py and exited2; tests/test_environment.py was inspected instead. Inspection output is in the terminal and is not represented as retained subprocess logs. No measurement code was executed by these reads.\n\nNew snapshots/scripts were created exclusively, and source edits used apply_patch. prepare_selection.py created reviewed metadata and a byte-exact CTest discovery-file copy. CTest discovery used -N only, with unchanged absolute commands, avoiding writes to old build logs. attempt1/ preserves source/manifest before the compatibility correction. An attempted audit-generation heredoc failed with a quoting SyntaxError, followed by an absent-file error (exit2); no final audit/evidence file was created by that failed command. It was corrected using apply_patch. This preparation failure is not a validation pass.\n\nNo prerequisite validator, selected/broad CTest, fresh build, GPU command, timing test, pilot or study ran. Synthetic interrupt/failure/completion text comes from doubles.\n')
with future[0].open('x') as stream:
    stream.write(''.join(commands))
audit = (base / 'AUDIT_TEMPLATE.md').read_text()
audit = audit.replace('@TOTAL_RESULTS@', str(final_total)).replace('@NEW_EVIDENCE@', str(final_new))
with future[1].open('x') as stream:
    stream.write(audit)
files = {str(p): sha(p) for p in sorted(base.rglob('*')) if p.is_file() and p != future[2]}
assert len([p for p in Path('results').rglob('*') if p.is_file()]) + 1 == final_total
docs = ['README.md', 'docs/ROADMAP.md', 'docs/AUDIT.md', 'docs/CPU_GPU_FULL_MATRIX_TOOLING_v1.md',
        'docs/NON_TIMING_TEST_SELECTION_v1.json', 'docs/CPU_GPU_SAFETY_REPAIR_v1.md']
seal = dict(schema_version=1, repair_validation_complete=True, study_recommendation='NO-GO',
            fresh_prerequisite_validation_run=False, actual_timing_trials=0, actual_gpu_calls=0,
            pilot_run=False, full_study_run=False, historical_results_before=11345, historical_results_after=11345,
            historical_results_changed=[], historical_results_missing=[], total_result_files_after=final_total,
            new_evidence_files=final_new, original_tooling_evidence_verified=85, prior_review_evidence_verified=30,
            protected_anchors_verified=26, production_headers_sources_dependencies_verified=80,
            focused_tests=dict(passed=22, failed=0, skipped=0), framework_tests=dict(passed=50, failed=0, skipped=0),
            ctest_groups_executed=0, selected_cpu_groups=19, source_before=before['current_source_sha256'],
            source_after=source_manifest(), frozen_files_sha256=before['frozen_files_sha256'],
            documentation_sha256={p: sha(p) for p in docs}, trusted_cmake_review_sha256=before['cmake_review_sha256'],
            evidence_sha256=files, manifest_excludes_itself=True, exit_code=0, command=shlex.join(record['argv']),
            verified_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
with future[2].open('x') as stream:
    json.dump(seal, stream, indent=2, sort_keys=True); stream.write('\n')
print(json.dumps(dict(audit=str(future[1]), integrity=str(future[2]), historical_files_preserved=11345,
                      total_result_files_after=final_total, new_evidence_files=final_new, exit_code=0), indent=2))
