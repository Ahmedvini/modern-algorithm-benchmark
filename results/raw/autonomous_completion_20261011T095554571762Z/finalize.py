"""Consolidated offline preservation audit; executes no tests or measurements."""
import hashlib
import json
from pathlib import Path
import re
import shlex
import sys

E = Path(__file__).resolve().parent
ROOT = E.parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from cpu_gpu_protocol import source_manifest, load_protocol
from cpu_gpu_validation_policy import verify_current_sources
from non_timing_tests import load_manifest


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def read(path): return json.loads(Path(path).read_text())
def write(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')


def main():
    base = read(E / 'BASELINE.json')
    preservation = {}
    for group in ['results_sha256', 'frozen_sha256', 'protected_sha256', 'build_metadata_sha256']:
        missing, changed = [], []
        for name, expected in base[group].items():
            path = ROOT / name
            if not path.is_file(): missing.append(name)
            elif sha(path) != expected: changed.append(name)
        preservation[group] = dict(files=len(base[group]), missing=missing, changed=changed)
        if missing or changed:
            write(E / 'INTEGRITY_FAILURE.json', preservation)
            raise ValueError('Preservation failure: ' + group)
    policy = verify_current_sources()  # Pure static checks, no subprocess/resource probe.
    frozen = load_protocol()
    selection = load_manifest()
    base_selection = read(ROOT / 'docs/NON_TIMING_TEST_SELECTION_v3.json')
    assert all(selection[k] == base_selection[k] for k in ['tests', 'cpu_build_tests', 'cuda_additional_tests', 'build_metadata'])
    defaults = sorted(k for k, v in selection['tests'].items()
                      if v['classification'] == 'cpu_correctness' and not v.get('diagnostic_only'))
    assert len(defaults) == 19 and selection['full_study_eligible'] is False
    before = base_selection['reviewed_source_sha256']; current = source_manifest()
    delta = dict(added=sorted(set(current)-set(before)), removed=sorted(set(before)-set(current)),
                 modified=sorted(k for k in set(before)&set(current) if before[k] != current[k]))
    write(E / 'SELECTION_REVIEW_FINAL.json', dict(default_tests=defaults, selection_sha256=sha(ROOT/'docs/NON_TIMING_TEST_SELECTION_v5.json'),
          source_sha256=current, delta_from_v3=delta, classifications_exactly_v3=True,
          local_correctness_only=True, independent_study_approval_installed=False))

    for name in ['release', 'sanitize']:
        result = read(E / ('cpu_'+name+'.json')); plan = read(E / ('cpu_'+name+'_selection.json'))
        assert result['exit_code'] == 0 and '100% tests passed, 0 tests failed out of 21' in result['stdout']
        assert plan['selected_count'] == 21 and plan['manifest_sha256'] == sha(ROOT/'docs/NON_TIMING_TEST_SELECTION_v5.json')
        assert plan['selected'] == sorted(defaults + ['parallel_workers_correctness', 'validation_policy'])
        assert all(x['classification'] == 'timing' for x in plan['excluded']) and len(plan['excluded']) == 10
    learned = read(ROOT/'results/processed/learned_rank_20261011T095554571762Z/summary.json')
    assert learned['configurations'] == 48 and learned['failed'] == learned['missing'] == 0
    learned_seal = read(E/'learned_study/study.json')
    for name, digest in learned_seal['raw_sha256'].items(): assert sha(E/'learned_study'/name) == digest, name
    count_seal = read(E/'count_memory_retry1/COMPLETE.json')
    assert len(count_seal['files_sha256']) == 240
    for name, digest in count_seal['files_sha256'].items(): assert sha(E/'count_memory_retry1'/name) == digest, name
    for size, expected in [('10m',450), ('100m',150)]:
        data = read(E/('sorting_'+size+'_summary.json'))
        assert data['complete'] and sum(g['successful_trials'] for g in data['groups']) == expected
        assert all(g['failed_trials'] == g['missing_measured_trials'] == 0 and g['run_complete'] for g in data['groups'])
        assert (E/('sorting_'+size+'_summary.json')).read_bytes() == (E/('sorting_'+size+'_regenerated.json')).read_bytes()
    for folder in ['results/processed/learned_rank_20261011T095554571762Z',
                   'results/processed/count_memory_20261011T095554571762Z', 'report/autonomous_20261011T095554571762Z']:
        a=ROOT/folder; b=ROOT/(folder+'_regenerated')
        assert {str(p.relative_to(a)):sha(p) for p in a.rglob('*') if p.is_file()} == {
            str(p.relative_to(b)):sha(p) for p in b.rglob('*') if p.is_file()}, folder
    for name, digest in read(E/'LEARNED_FREEZE.json')['files_sha256'].items(): assert sha(ROOT/name) == digest
    for name, digest in read(E/'CPU_STUDY_IDENTITIES.json')['artifacts_sha256'].items(): assert sha(ROOT/name) == digest

    project_paths = set(base['project_sha256']) | set(current)
    project_paths |= {str(p.relative_to(ROOT)) for p in (ROOT/'docs').rglob('*') if p.is_file()}
    project_paths |= {str(p.relative_to(ROOT)) for p in (ROOT/'report').glob('*') if p.is_file()}
    project = {name:sha(ROOT/name) for name in sorted(project_paths)}
    changed = sorted(k for k,v in base['project_sha256'].items() if project[k] != v)
    allowed_changes = {'README.md','docs/ALGORITHMS.md','docs/AUDIT.md','docs/BENCHMARKING.md','docs/METRICS.md','docs/ROADMAP.md',
                       'scripts/non_timing_tests.py','scripts/run_cpu_gpu_pilot.py','tests/test_evidence_enforcement.py'}
    assert set(changed) == allowed_changes, changed
    added = sorted(set(project)-set(base['project_sha256']))
    inventory = dict(modified=changed, added=added, project_sha256=project)
    write(E/'CHANGES.json', inventory)

    records = [(p, read(p)) for p in sorted(E.glob('command_*.json'))]
    def classification(d):
        c=d['command']; purpose=d['purpose'].lower()
        if c.startswith('colab new'): return 'Cloud allocation request; no remote workload'
        if 'Release only the session' in d['purpose']: return 'Cloud session release; no remote workload'
        if ('run_matrix.py' in c or 'learned_study.py run' in c) and 'Execute' in d['purpose']: return 'Actual authorized CPU performance experiment'
        if 'collect_metrics.py collect' in c: return 'Separate CPU comparison/RSS instrumentation; no timing'
        if 'guarded_validate.py sanitize' in c or 'UBSAN_OPTIONS=' in c and 'test_learned_index' in c: return 'ASan/UBSan correctness'
        if 'guarded_validate.py release' in c or ('test_' in c and ('regressions' in purpose or 'correctness' in purpose or 'tests' in purpose)): return 'Correctness/unit tests (inert Python where stated)'
        if 'cmake -S ' in c or 'cmake --build ' in c: return 'Build/configuration; no timed workloads'
        return 'Inspection/resource diagnostic/derived analysis; no new measured trials'
    with (E/'COMMANDS.md').open('x') as stream:
        stream.write('# Actual command history\n\nAll paths are relative to the repository unless absolute. '
                     'Raw command JSON retains full stdout/stderr; exit codes below are actual shell results. '
                     'Compound commands can contain an earlier failed subcommand despite a final0; known cases are listed in the audit. '
                     'See SUPPLEMENTAL_COMMANDS.md for uncaptured startup/resumption reads and non-terminal editing activity.\n\n')
        for path,d in records:
            stream.write('## '+path.name+'\n\n'+d['purpose']+'\n\n'
                'Class: '+classification(d)+'; exit: '+str(d['exit_code'])+'; started UTC: '+d['started_utc']+
                '; cwd: `'+d['working_directory']+'`.\n\n```sh\n'+d['command']+'\n```\n\n'
                'Full retained output: ['+path.name+']('+path.name+').\n\n')
        stream.write('## Guarded child commands\n\n')
        for name in ['cpu_release_discovery','cpu_release','cpu_sanitize_discovery','cpu_sanitize']:
            d=read(E/(name+'.json'))
            stream.write('`'+shlex.join(d['argv'])+'` — exit'+str(d['exit_code'])+', retained `'+name+'.json`.\n\n')
        stream.write('## Per-configuration child invocations\n\nSorting: `sorting_10m/run_*_command.json` (15) and '
                     '`sorting_100m/run_*_command.json` (5). Learned: `learned_study/*.command.json` (48). '
                     'Separate counts: `count_memory_retry1/n*.json` (240). '
                     'These record every executable invocation and actual exit code; they are not omitted from the evidence. '
                     'The incomplete first counts attempt retains one native exit0 and collector exit1.\n\n'
                     'Final seal command: `python3 -B '+str((E/'finalize.py').relative_to(ROOT))+'`. '
                     'This performs offline hashing and report writes only; status is recorded in FINALIZER_STATUS.json after successful assertions.\n')

    # Keep exact changed source contents available for future review, without
    # pretending a Git diff exists (there is no repository metadata).
    with (E/'SOURCE_REVIEW.md').open('x') as stream:
        stream.write('# Source review inventory\n\nNo Git metadata exists. BASELINE.json retains original digests; '
                     'CHANGES.json lists all additions/modifications and final hashes. '
                     'Only three pre-existing Python source/test files changed.\n\n'
                     '- non_timing_tests.py: additive v5 local snapshot; exact pinned-v3 classifications/commands; '
                     'shared static hook/path guard and rechecks unchanged.\n'
                     '- run_cpu_gpu_pilot.py: full-study evidence retention copies recursively verified nested references, '
                     'without changing algorithm, timing, pilot or launch eligibility.\n'
                     '- test_evidence_enforcement.py: historical snapshot regression explicitly selects immutable v3 '
                     'after authorized local-default activation; failure expectation retained.\n\n'
                     'Existing CMake, native production algorithms, runtime/timing framework, vendor code and licenses '
                     'are unchanged. Learned index is separately compiled and does not alter registries.\n\n')
        for name in sorted(set(current)-set(base['project_sha256']) | (set(changed)&set(current))):
            stream.write('## '+name+'\n\nSHA-256: `'+sha(ROOT/name)+'`\n\n````text\n'+(ROOT/name).read_text()+'\n````\n\n')

    counts = dict(cpu_release=dict(passed=21,failed=0,ctest_skipped=0,internal_gpu_methods_skipped=2),
        cpu_sanitize=dict(passed=21,failed=0,ctest_skipped=0,internal_gpu_methods_skipped=2,leak_detection=True),
        learned_correctness=dict(datasets=153,oracle_checks=45201,observed_fallbacks=12468,release_exit=0,sanitize_exit=0),
        learned_study=dict(configurations=48,distinct_sorted_inputs=24,measured_lookup_batches=480,measured_builds=240,
            warmup_lookup_batches=96,warmup_builds=48,diagnostic_queries=48000,failed=0,missing=0),
        sorting_10m=dict(datasets=15,measured=450,warmups=90,failed=0,missing=0),
        sorting_100m=dict(datasets=5,measured=150,warmups=30,failed=0,missing=0),
        separate_metrics=dict(completed=240,first_partial_native_calls=1,failed_collector_attempts=1),
        actual_gpu_sorting_calls=0,frozen_cpu_gpu_study_measured=0)
    write(E/'RESULT_COUNTS.json',counts)
    with (E/'FINAL_AUDIT.md').open('x') as stream:
        stream.write('''# Autonomous completion audit — 2026-10-11

**NO-GO for the frozen full CPU/GPU comparison. CPU delivery completed for the new matrices; the overall project is not fully complete.**

The user's standing authorization permits implementation, reviewed local selection activation, bounded validation and resource-gated CPU scale studies. It does not create an independent trust artifact or permit paid compute. No commit, push, Git initialization or publication occurred.

## Gate table

|Gate|Status|Evidence|
|---|---|---|
|Frozen protocol/matrix/resources/pin preserved|PASS|BASELINE.json; FINAL_INTEGRITY.json; four frozen/80 existing production/header/vendor files and26 protected anchors|
|Historical preservation|PASS|All12,575 pre-existing result paths and SHA-256 contents match;65 old build-metadata files unchanged|
|Local selection and guard/path safeguards|PASS for local correctness only|SELECTION_REVIEW_FINAL.json; immutable v3/v4; exact19 default tests plus two explicit untimed diagnostics;36 guard +3 selector +3 activation methods|
|Evidence enforcement/compatibility regression|PASS for focused tests, not installed independent approval|command_033:39; command_027:26; command_028:9; command_009:6 retention methods; full CPU framework52 synthetic methods in each root suite|
|Fresh CPU Release / ASan/UBSan|PASS|cpu_release.json / cpu_sanitize.json,21/21 each; leaks enabled; internal GPU methods skipped2 per run|
|Learned index implementation, oracle, held-out evaluation|PASS for declared scope|153 datasets/45,201 checks in both builds;9 analyzer methods;48 configurations/24 distinct vectors; full raw seal checked|
|10M/100M CPU studies|PASS for separate frozen scale protocol|600 measured sorts/120 warm-ups; zero failed/missing; strict CSV/order/oracle/completeness analysis|
|Separate comparisons/process memory|PASS after retained parser repair|240 completed invocations;8 focused parser tests; eight figures; radix count unsupported|
|Report/plots/presentation regeneration|PASS|REGENERATION.json; byte-identical learned8, metric10 and final-report12 files; both scale summary pairs identical|
|Independent full-study evidence approval|BLOCKED|scripts/cpu_gpu_evidence.py TRUSTED_APPROVAL_SHA256=None; docs/CPU_GPU_EVIDENCE_REVIEW_v1.json absent; command_058 exit1 proves fail-closed|
|Current free usable T4, GPU build/framework/resources|BLOCKED|command_006–008: assignment exposed1.07CU/hour and0 balance; released before remote transfer/GPU work; no current identity-matched GPU build|
|Frozen full-study eligibility / launch|BLOCKED|No trusted independent approval, current T4 proof or full positive prerequisite bundle; no study trial launched|

## Repository and reviewed changes

The root is `/home/ahmedelsheikh/Documents/GitHub/modern-algorithm-benchmark`. Git metadata is absent (command_001 exit128), so source identity uses content manifests, not an invented revision/branch. CHANGES.json and SOURCE_REVIEW.md record exact added/modified paths and final source contents/hashes. Existing root CMake and all80 pre-existing native/header/dependency files are unchanged. All prior user work is preserved except the three explicitly repaired Python surfaces and documented updates.

The recursive retention repair validates actual reference bytes, preserves nested evidence, rejects cycles/aliases/conflicts and writes an exclusive destination. It grants no eligibility. Local selection v5 retains the exact pinned-v3 tests/commands/properties/build policy, all hook/include/path checks and boundary rechecks; it requires the exact167-file current source snapshot. Historical v3 and inactive v4 are unchanged. `full_study_eligible=false`; local activation is not an independent full-study approval.

The learned index is an additive standalone CMake project: endpoint affine rank model, fixed correction radius32, certified local lower bound and full binary fallback. It owns its ascending int32 vector, rejects unsorted inputs, returns first equal/nullopt, handles extrema using int64 differences, and exposes separate diagnostic counts/error/fallback. Existing array-search/sort registries and defaults are untouched. No O(1) guarantee is claimed. New AlphaDev documentation uses primary sources and explicitly does not claim training reproduction.

## Actual builds, validation and warnings

COMMANDS.md and command JSON retain every recorded invocation, cwd, timestamp, stdout/stderr and actual exit status. Supplemental read-only/bootstrap/editing activity is explicitly listed in SUPPLEMENTAL_COMMANDS.md. CPU builds use new `build/autonomous_cpu_release` and `build/autonomous_cpu_sanitize`, GNU13.3.0/CMake3.28.3, OpenMP4.5, Release `-O3 -DNDEBUG`, separate Debug address/undefined sanitizers, CUDA disabled. Actual verbose compiler/linker commands and successful aggregate build exits are retained; these are not represented as accepted T4/full-study build provenance.

The static gate ran before each actual CTest discovery. Discovery saw31 groups;21 untimed groups were selected and10 timing groups excluded. No CTest group skipped or failed. The host analysis Python group intentionally skipped2 GPU timing methods per configuration. `cpu_gpu_comparison_framework` prints synthetic1200-row completeness using subprocess doubles; those messages are not actual benchmark executions. Untimed worker checks made12 public/registry calls: sizes0/1/32767 observedteam1, sizes32768/32769/65537 observedteam2. Team size is not task participation, physical-core concurrency or proof of race freedom.

The separate learned Release and ASan/UBSan correctness binaries each passed153 datasets/45,201 oracle queries, with12,468 observed diagnostic fallbacks and exact small-input key-count checks. Sanitizers passed with default leak detection: no detect_leaks=0 retry. One new range-loop-copy compiler warning in the initial learned CLI build was corrected by a const reference; subsequent build output contains no warnings. No CUDA compilation occurred, so the historical341 nvcc/GCC line-marker warnings were neither regenerated nor suppressed. They remain historical evidence, not warnings from this execution.

## Actual experiments, statistics and environment

The new learned matrix contains48 workload configurations but24 distinct sorted input vectors. Uniform/reverse/nearly inputs collapse after preprocessing; labels are kept separate and never pooled as independent datasets. Seeds42/2718/314159 were fixed before timing and held out from performance tuning, not necessarily from correctness testing. Each1000-query batch has500 hits/500 misses. There are480 measured lookup batches,240 measured builds,96 lookup/48 build warm-ups and48,000 untimed diagnostics; no failures/missing rows. Build time includes the owned vector copy/validation. Query timing excludes generation, preprocessing, build, copies, diagnostics, validation and serialization.

Separate CPU scaling uses the existing production runner and sort_timing_v1. At10M:15 datasets/five distributions/three seeds/six sorters,450 measured+90 warm-ups. At100M:five datasets/five distributions/seed1729/six sorters,150 measured+30 warm-ups. Full output equals std::sort outside timing for every row. No outliers are dropped. Repetition median/mean/sampleSD/min/max are retained per dataset; cross-seed medians weight datasets equally. The single100M seed gives no cross-dataset uncertainty. Kernel6.18.7, i5-11400H, six physical/12 logical cores, approximately16.48GB RAM and powersave policy are recorded. Background load, thermals, frequency/cache history remain uncontrolled. Agent-launched builds/timed experiments were serialized; external activity was not controlled.

Preallocation gates observed6,735,044,608 available bytes for100M, against a calculated1,600,000,000-byte array budget plus3GiB headroom. Ancestor cgroups had no finite memory/CPU quota. Disk headroom exceeded2GiB. These are resource snapshots/estimates, not guaranteed physical allocations. The100M command actually elapsed11:17.40 and reported `/usr/bin/time -v` maximumRSS1,602,892KiB (1,641,361,408 bytes). This is a command/process lifetime high-water statistic, not isolated per-sorter memory.

The separate count/RSS retry completed240 instrumented native calls, five supported counted adapters×four sizes×four distributions×three seeds. Radix count remains unsupported. Each native exit0 follows full oracle/normal-sort equality checks. Counts use executed key-less-than predicates, not swaps/moves/bookkeeping. Process RSS includes inputs/runtime/allocator/instrumentation, with no baseline subtraction or auxiliary-memory isolation. It is measured separately from timing.

## Failures and corrections retained

- Missing Git metadata: command_001 exit128. No repository was initialized.
- Inactive historical-v3 regression assumed it was still the default after local v5 activation: command_026 exit1,39 tests/one failure. The test now explicitly selects unchanged v3 and still requires its rejection; command_033 passes39/39. Initial v5 snapshot is retained separately.
- One initial learned compiler range-loop warning was fixed and rebuilt; original output remains.
- A report schema inspection used family `sort` instead of `sorting`, raised StopIteration inside a compound shell command whose final status was0; corrected inspection command_051 succeeds. Earlier missing read paths/initial absent report directory are inspection failures, not build failures.
- An apply_patch context was rejected; EDIT_FAILURE.md preserves the failed attempt. Successful focused edits followed.
- Actual approval() check command_058 exit1 is an expected unresolved trust-root gate, not repaired by inventing an approval.
- First count collector attempt command_066 exit1: it incorrectly read API member `peak_rss_bytes` rather than JSON wire `value`. Its one native call exited0; the first fixture had mirrored that wrong assumption. Real seven-field schema was inspected, parser and fixture repaired, an API-vs-wire regression added, all8 tests passed (command_069), and a new exclusive retry completed240 calls (command_070). The original partial directory remains incomplete and is not merged into results.

## Delivered outputs and reproducibility

- Raw: `learned_study/`, `sorting_10m/`, `sorting_100m/`, `count_memory_retry1/` beneath this evidence directory, with each command/output and all outliers retained.
- Learned: `results/processed/learned_rank_20261011T095554571762Z/` — per-dataset/cross-seed summary, four variability figures, diagnostic/memory aggregates and SHA manifest.
- Counts/RSS: `results/processed/count_memory_20261011T095554571762Z/` — summary/eight figures/plot manifest.
- Report: `report/autonomous_20261011T095554571762Z/FINAL_REPORT.md`, `REPORT.pdf` (15pages), `PRESENTATION.pdf` (12slides), slide Markdown, numerical tables, four main figures and source/plot/hash manifests. Two rendered slide pages were visually inspected.
- Fresh `_regenerated` destinations reproduce all derived files byte-for-byte, including PNG/PDF, with source raw seals unchanged. This reproducibility claim applies to the retained Python/Matplotlib/font environment; different tool versions can render differently.
- Source approval distinctions and exact selected/excluded names are in SELECTION_REVIEW_FINAL.json and cpu_*_selection.json. Build/source/executable identities are in CPU_STUDY_IDENTITIES.json and FINAL_INTEGRITY.json. Genuine CPU command logs are retained, not fabricated strict GPU linker provenance.

## Remaining external dependency and limits

The full frozen CPU/GPU comparison has48 datasets,1200 measured/240 warm-up calls. **None ran in this execution.** Existing T4 correctness/smoke/pilot results remain historical and unchanged. The one authorized replacement allocation returned a READY identifier `gpu-t4-s-kkb-usw4a1-3o0t7oza4apcz` under local alias `autonomous-validation`, then account inspection disclosed0CU and a1.07CU/hour metered rate. It was released immediately before upload, remote diagnostics or GPU workloads. No actual charge is inferred either way from the short assignment; paid execution was not continued.

Two necessary dependencies cannot be manufactured autonomously: an independently protected evidence/selection approval accepted by the unchanged full-study guard, and a confirmed free usable GPU environment with genuine current compiler/linker/executable provenance, framework correctness and all-size resource evidence. The code's fail-closed missing-root rejection is preserved. Standing authorization is not falsely relabeled as independent technical review. Once genuine external artifacts exist, the existing frozen launch guard must still pass; this audit grants no substitute eligibility.

Search individual-query maximum latency remains unmeasured: batch averages/maxima cannot substitute. Structure-specific allocator memory/comparison instrumentation, an optional learned sorter selector and AlphaDev training are not claimed. Current100M is a CPU single-seed feasibility study, not GPU100M or universal performance ranking. Report conclusions are descriptive, with no unsupported significance, race-freedom or universal speedup claims.

The final preservation comparison covers contents and paths, not merely counts. Earlier failed attempts and all12,575 historical result files remain unchanged; additions are confined to reviewed source/docs, fresh builds, this raw directory, new processed directories and report outputs. No credentials/tokens were read or logged. The full CPU/GPU launch remains NO-GO; independent CPU implementation/analysis/report work is complete for its declared scope.
''')
    write(E/'FINALIZER_STATUS.json',dict(command=['python3','-B',str((E/'finalize.py').relative_to(ROOT))],
          validation_assertions_passed=True, preservation=preservation,
          note='Exit0 is independently observable from the terminal result; no workload executed by this finalizer.'))
    new_results = {str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'results').rglob('*')
                   if p.is_file() and str(p.relative_to(ROOT)) not in base['results_sha256']}
    evidence = {str(p.relative_to(ROOT)):sha(p) for p in E.rglob('*') if p.is_file()}
    report = {str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'report').rglob('*') if p.is_file()}
    artifact = {name:sha(ROOT/name) for name in read(E/'CPU_STUDY_IDENTITIES.json')['artifacts_sha256']}
    # Established digest-map seal format; self is deliberately excluded.
    write(E/'FINAL_INTEGRITY.json',dict(schema_version=1,seal_excludes_itself=True,
        seal_command=['python3','-B',str((E/'finalize.py').relative_to(ROOT))],
        verdict='NO-GO — full frozen CPU/GPU study remains externally blocked', study_launched=False,
        history_preservation=preservation, historical_results_sha256=base['results_sha256'],
        frozen_sha256=base['frozen_sha256'], protected_sha256=base['protected_sha256'],
        build_metadata_sha256=base['build_metadata_sha256'],project_sha256=project,
        evidence_sha256=evidence,new_results_sha256=new_results,report_sha256=report,
        executable_sha256=artifact,results=counts,approved_default_test_names=defaults,
        independent_approval_fabricated=False))
    print('Final seal written; preserved',len(base['results_sha256']),'historical result files,',
          len(base['protected_sha256']),'existing production/header/vendor files,',len(base['build_metadata_sha256']),'old build metadata files.')
    print('Changed existing files:',len(changed),'Added project files:',len(added))
    print('No frozen CPU/GPU study launched; external trust/runtime gates remain blocked.')


if __name__ == '__main__': main()
