"""Write audit from retained command results; does not execute benchmarks."""
import difflib
import json
from pathlib import Path
import shlex
import sys

E=Path(__file__).resolve().parent;ROOT=E.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from cpu_gpu_protocol import sha,load_protocol,verify_source_extension
def read(path):return json.loads(path.read_text())
def save(name,value):
    with (E/name).open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
prior=read(E/'prior_artifacts_sha256.json')
for name,digest in prior.items():assert sha(ROOT/name)==digest,name
freeze=read(E/'freeze_verified.json')
for name,digest in freeze['files'].items():assert sha(ROOT/name)==digest,name
source=verify_source_extension(load_protocol());bundle=read(E/'source_bundle.json')
assert source['current_source_sha256']==bundle['source_sha256']
before=read(E/'source_before.json')['current_source_sha256']
changed=[p for p,h in before.items() if source['current_source_sha256'].get(p)!=h]
added=sorted(set(source['current_source_sha256'])-set(before))
assert set(changed)=={'scripts/run_cpu_gpu_pilot.py','scripts/analyze_cpu_gpu.py','scripts/validate_cpu_gpu_pilot.py','tests/test_cpu_gpu_comparison.py'}
assert added==['scripts/run_cpu_gpu_study.py']
gpu=read(E/'INDEPENDENT_GPU_VERIFICATION.json');assert gpu['complete'] and gpu['source_matches_current']
remote=E/'downloaded/evidence';manifest=read(remote/'SHA256.json')
for name,digest in manifest.items():assert sha(remote/name)==digest,name
assert sha(E/'pilot_compatibility_summary.json')=='07e69e2e0c8853f93d3f3da895337b5e4b72e5e2dd0ff0577db3cbd1f7053a22'
for name in ['release_configure','release_build','release_ctest_final','sanitize_configure','sanitize_build',
             'sanitize_ctest_final','framework_final_release','framework_final_sanitize','full_dry_run','gpu_validation','download_gpu_evidence']:
    assert read(E/'commands'/ (name+'.json'))['exit_code']==0,name
for name in ['framework_final_release','framework_final_sanitize']:
    record=read(E/'commands'/(name+'.json'));assert 'Ran 50 tests' in record['stderr'] and 'skipped=' not in record['stderr']
save('VALIDATION_SUMMARY.json',dict(complete=True,tooling_implemented=True,full_study_launch='NO-GO',
    local_release_selected_groups=19,local_sanitize_selected_groups=19,final_framework_methods_each=50,
    gpu_selected_groups=21,cuda_inputs=475,cuda_output_checks=1900,
    prior_artifacts_unchanged=len(prior),protected_frozen_files_match=True,
    production_source_unchanged=True,changed_existing_source_files=changed,added_source_files=added,
    pilot_rerun=False,full_study_run=False,gpu_benchmark_run=False,
    scope_deviation=dict(test='parallel_mergesort',size=32768,rows=6,measured=4,warmups=2,
        evidence='commands/release_ctest_non_timing.json',durations_serialized=False,
        mitigation='Disclosed; group excluded from all subsequent validation.')))
lines=['# Exact recorded commands and exit statuses','',
    'Read-only initial audit used pwd, cat/sed/rg and Python seal/hash inspection; initial verification returned0 before edits. '
    'Snapshots and verified frozen identities are retained separately. Each command below retains full stdout/stderr, argv, cwd and status.','']
for path in sorted((E/'commands').glob('*.json')):
    if path.name.endswith('_started.json'):continue
    record=read(path);lines.append(f"- `{shlex.join(record['argv'])}` — exit{record['exit_code']}; [{path.name}](commands/{path.name}).")
lines+=['','Remote inner commands (CLI exit0 alone was not accepted):','']
for name in ['gpu_initial','nvcc','configure','build','ctest_non_timing']:
    record=read(remote/(name+'.json'));lines.append(f"- `{shlex.join(record['argv'])}` — exit{record['exit_code']}; [full log](downloaded/evidence/{name}.json).")
lines+=['','Evidence-only audit generation and sealing commands: `python3 '+str(E/'finalize_audit.py')+'` and `python3 '+str(E/'seal_integrity.py')+'`. '
        'Their observed exits are recorded by the invoking tool/manifest. No future execution command in the documentation was run.','']
with (E/'COMMANDS.md').open('x') as f:f.write('\n'.join(lines))
diff=[]
for name in changed+['README.md','docs/AUDIT.md','docs/ROADMAP.md']:
    diff.extend(difflib.unified_diff((E/'before'/name).read_text().splitlines(True),(ROOT/name).read_text().splitlines(True),
        fromfile='before/'+name,tofile='current/'+name))
with (E/'FINAL_REVIEW.diff').open('x') as f:f.write(''.join(diff))
audit=f'''# Full frozen CPU/GPU matrix tooling: final audit

**Implementation and selected correctness/synthetic validation passed. Full-study
launch: NO-GO pending review, separate authorization and fresh complete study
prerequisites/resource gates. No pilot or comparison study executed.**

## Audit and preservation

Read AGENTS/current project guidance, frozen protocol/matrix/resource/freeze,
accepted pilot report/audit and latest N65537 resource audit; inspected driver,
analyzer, prerequisite runner, CMake, worker/input/timing interfaces and tests.
Git status128: no Git metadata; no initialization/commit/push/destructive cleanup.
Verified latest resource seal and accepted pilot evidence/source identities before
editing. All four frozen files match initial hashes; freeze execution_authorized
remainsfalse. All{len(prior)} earlier result artifacts remain unchanged.
Protected C++/CUDA sources, adapters, registries/defaults, CMake integration,
third-party files/licenses and reviewed CUB3.0.1 pin remain unchanged.

Exact frozen study:48 datasets atN1025/65537/1000000, five seeded distributions
uniform/sorted/reverse_sorted/duplicate_heavy/nearly_sorted with1729/42/2718,
plus one fixed signed_edges input per size; five modes, W1/R5.
Stored dataset and per-cell base/cyclic orders are consumed unchanged, offsets0..1410.
Expected1200 measured+240 warm-ups; primary960+192 rows, prepared240+48 rows
with four diagnostic values per call. No new experimental records exist here.

## Implementation and decisions

- New run_cpu_gpu_study.py wraps shared orchestration with matrix_part=study;
  pilot entry point remains pilot-only. Dry-run emits48 command pairs/counts/
  resource policies without creating outputs. Actual execution needs explicit
  --execute-study and compatible fresh prerequisites after separate authorization.
- Existing frozen worker and normal adapters/timing code are reused unchanged.
  Full resources query all three sizes and validate unchanged64MiB/workspace,
  256MiB combined, half-free device and host/disk/CPU gates before workers.
  Serial per-dataset60s and main1800s limits come from frozen policy.
- Exclusive output paths, no resume/retry/overwrite (required by freeze). Full
  plan/attempt/command records survive failure/interruption. Parsable partial data
  produces explicit counts; malformed evidence produces an analysis-error record,
  not guessed completion. Source/environment are rechecked before completion.
- Analyzer selects the recorded matrix part and demands exact coverage/identities,
  schemas, input bytes/hash/recipe metadata, phases/order, actual CPU teams,
  correctness, finite nonnegative metrics, calibration and resource observations.
  Complete studies require retained frozen copies and exact raw-manifest hashes.
  Performance metadata additionally checks build/flags/environment, provenance,
  hashed prerequisite commands and prepared-versus-primary build/device identity.
- Only production GPU host-call timing supplies paired denominators. Prepared
  H2D/device/D2H/E2E remain diagnostics. Incomplete studies retain failure/missing/
  interruption counts and suppress paired/cross-input comparisons. Five-repeat
  summaries use median/mean/sampleSD/min/max in ns, then equal-weight distinct-
  input summaries; identical contents collapse. No outliers discarded or CI claimed.
- Prerequisites-only option permits future full validation without automatically
  launching a pilot. It was tested with explicit mocks only, not invoked here;
  its established full suites include timing-framework tests and require later
  authorization. Synthetic results require API opt-in and public CLI rejects them.

## Actual validation and command outcomes

Exact commands/exits/full output: COMMANDS.md and commands/*.json; remote inner
logs: downloaded/evidence/*.json. All configure/build/selected-test/analysis/
transfer/verification commands passed0; git128 is expected for absent metadata.

| Check | Observed result |
|---|---|
| Fresh local CPU Release configure/build | exit0; compiler warnings0 |
| Selected Release CTest |19/19 groups,0 failures;15.24s |
| Fresh local Debug ASan/UBSan configure/build | exit0; warnings0 |
| Selected sanitizer CTest |19/19 groups,0 failures;45.93s; leaks enabled |
| Final Python framework, Release input tool |50/50 methods,0 skips/failures |
| Final Python framework, sanitizer input tool |50/50 methods,0 skips/failures |
| Full dry-run |48 command pairs; no run directory/workload created |
| Accepted pilot reanalysis | byte-identical SHA25607e69e2e0c8853f93d3f3da895337b5e4b72e5e2dd0ff0577db3cbd1f7053a22 |
| Fresh Colab CUDA/OpenMP Release configure/build | exit0, pinned headers match |
| GPU-enabled selected non-timing CTest |21/21 groups,0 failures/CTest skips;31.78s |
| Actual CUB correctness in CTest |475 inputs/1900 output checks, passed |
| Actual CUDA runtime kernel | passed, result1729 |
| GPU VM framework |50/50 methods,0 skips/failures |

The local19-group selections included48 framework methods before the final two
prerequisite-only tests; both final local50-method rechecks and cloud21-group run
cover the final code. Initial standalone41-method run skipped one missing input-tool
case and emitted two unclosed-file ResourceWarnings; the file handling was fixed,
and supplied-tool final runs have no such warnings/skips. Expected injected
exit9/timeouts/interruptions/failures are test assertions, not validation failures.
Host-only CUDA analysis explicitly skips two GPU timing methods in all selected
suites, including the GPU VM. GPU timing framework14-method suite was NOT run.
No LeakSanitizer ptrace issue; no leak-detection suppression. CPU sanitizers do
not cover device code; Compute Sanitizer was not run.

## Scope deviation and exclusions

Initial Release20-group selection inadvertently included parallel_mergesort,
whose correctness test also executes **six CPU timing rows atN32768**: sequential
and parallel Merge Sort, W1/R2, four measured calls/two warm-ups. This was overlooked,
disclosed immediately and excluded from every subsequent suite. Durations were
not serialized; no values are used or reported as experiment results. Original
commands/release_ctest_non_timing.json is retained unchanged. It is therefore
incorrect to claim this milestone executed zero CPU timing calls.

Final CPU allowlist excludes10/29 registered groups (parallel_mergesort ran only
in that initial selection); final GPU allowlist excludes11/32. Exclusions:
experiment_pipeline, structure_timing, structure_framework, search_timing,
search_framework, timing, benchmark_framework, parallel_mergesort, parallel_framework,
comparison_engine, plus cuda_benchmark_gpu_framework on GPU. All contain timing
paths or benchmark execution. No full29/32-group suite, pilot, main1200-call study,
GPU timing matrix or100M experiment ran. The actual GPU operations were correctness
and runtime tests, not performance measurements. Synthetic console completion
messages from mocked orchestration are explicitly labelled and never evidence of
a real completed study.

## GPU/environment and retained evidence

Colab initially had no active sessions; reconnected new T4 session
cpu-gpu-full-tooling-20261010T121208Z, servergpu-t4-s-kkb-usw4b2-1s2udk9w4e2zy.
Tesla T4 compute7.5, driver580.82.07/runtime13000/nvcc13.0.88,
GCC13.3.0,CMake3.31.10,OpenMP4.5/libgomp, Linux6.6.122+/glibc2.39.
Release C++17/CUDA17,-O3 -DNDEBUG,arch75. Actual environment, CPU topology,
RAM/cgroup/disk/load/clock observations are in downloaded/evidence/environment.json;
no clock/thermal/cache/background exclusivity control claimed.

Source archive167 members SHA256{bundle['sha256']}, matches local/remote;
all137 current source hashes match GPU-tested archive and extracted source.
All1688 installed CCCL files match accepted pilot; CUB3.0.1 commit
f19d875da0d8bfb2e38c109b2b40522b8abbbbc3 unchanged. CUDA build341 warnings,
exclusively known generated GCC line-directive extensions under existing-Wpedantic;
no new category, suppression or incompatibility.

Downloaded archive SHA256{gpu['download_sha256']},17 members/15 inner hashed files
verified, including inner command statuses, completion marker, absence of failure,
source identity, actual GPU test JSON and dependency manifest. CLI0 alone was not
accepted. See INDEPENDENT_GPU_VERIFICATION.json, source_bundle.json and downloaded/.
New test fixtures are deterministic synthetic records; full1440-record coverage,
missing/failed/interrupted/duplicate/identity/scope/thread/resource/provenance
rejections, known sample statistics, no prepared substitution, ordering, exclusive
outputs and deterministic regeneration are covered. They are not benchmarks.

## Changed files and next step

Modified: scripts/run_cpu_gpu_pilot.py (shared orchestration),
scripts/analyze_cpu_gpu.py (full strict analysis), scripts/validate_cpu_gpu_pilot.py
(prerequisite-only option), tests/test_cpu_gpu_comparison.py (50-method suite),
README.md, docs/ROADMAP.md and docs/AUDIT.md (scope/commands/status/evidence).
Added scripts/run_cpu_gpu_study.py and docs/CPU_GPU_FULL_MATRIX_TOOLING_v1.md.
This unique evidence directory adds before snapshots, exact command logs, manifests,
source/downloaded bundles, compatibility summary, reviews and final audit/integrity.
No production, CMake, vendor, frozen input or earlier raw/processed result changed.

**NO-GO for full-study launch.** Tooling passed the recorded synthetic/non-timing
validation, but no real full-matrix performance run was authorized or executed.
Review the focused diff, tests and timing-test deviation; then separately authorize
fresh complete study prerequisites (including timing-framework validation),
all-size resource gates and main execution on the actual VM. No current fresh
complete PREREQUISITES.json was issued by the selected-suite validation. Shared
cloud/SMT/frequency/thermal/load and pilot single-seed variability remain risks;
no performance ranking/significance claim. No frozen-protocol change is required.
'''
with (E/'FINAL_AUDIT.md').open('x') as f:f.write(audit)
print('Audit written; prior artifacts verified',len(prior),'changed existing source',changed,'added',added)
