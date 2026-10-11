"""Write the independent review, commands and final preservation seal; no benchmarks."""
import datetime
import hashlib
import json
from pathlib import Path
import shlex

root=Path.cwd()
base=Path(__file__).resolve().parent
old=root/'results/raw/cpu_gpu_full_tooling_20261010T121208603276Z'
def sha(path):
    d=hashlib.sha256()
    with path.open('rb') as stream:
        for data in iter(lambda:stream.read(1048576),b''):d.update(data)
    return d.hexdigest()
def save(name,value):
    with (base/name).open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
records={p.stem:json.loads(p.read_text()) for p in sorted((base/'commands').glob('*.json'))}
assert records['synthetic_framework']['exit_code']==0 and 'Ran 50 tests' in records['synthetic_framework']['stderr']
probe=json.loads((base/'FULL_ANALYSIS_PROBE.json').read_text())
assert probe['baseline_accepted'] and probe['altered_source_result_marked_complete'] and not probe['protected_source_change_rejected']
commands=['# Review commands and observed exit statuses','',
    'These are new review commands, not a rerun of historical builds or measurements. Full argv/stdout/stderr/timestamps are in commands/*.json.', '']
for name,record in records.items():
    commands += ['- `'+shlex.join(record['argv'])+'` — exit '+str(record['exit_code'])+'; `commands/'+name+'.json`.']
commands += ['', 'Dry-run child invocations are also recorded exactly in PLAN_AND_COMPATIBILITY.json (two identical commands, both exit0); they launched no worker and created no study directory.', '',
    'Before the recorder was created, read-only pwd/cat/sed/rg/Python inspections read AGENTS, protocol, evidence and implementation files. An initial git status reported128. The repository-wide result snapshot command used Python SHA-256 and created START_SNAPSHOT.json, exit0. Evidence-only apply_patch/new-version creation commands created the scripts retained here; no project source was edited.', '',
    'Final command: `python3 -B '+str(base/'finalize_review.py')+'`. Its successful completion and preservation checks are recorded in FINAL_INTEGRITY.json; this command creates that manifest last.', '',
    'The recorded six-row historical CTest command is reproduced in SELECTION_REVIEW.json and the original milestone COMMANDS.md. It was inspected, not executed in this review. Fresh Release/sanitizer/GPU builds, CTest, Colab commands, prerequisites-only validation, pilot, study and all timing trials were NOT executed.']
with (base/'COMMANDS.md').open('x') as stream:stream.write('\n'.join(commands)+'\n')
audit='''# Independent full-matrix tooling review

**Recommendation: NO-GO for subsequent full-study authorization.** The tooling
review found a reproducible independent-analysis provenance gap. No study,
pilot, GPU benchmark, CPU timing trial or 100M experiment ran during this review.
The real production adapters and all historical result artifacts remain unchanged.

Reviewed retained baseline evidence:
`results/raw/cpu_gpu_full_tooling_20261010T121208603276Z/{FINAL_AUDIT.md,COMMANDS.md,FINAL_INTEGRITY.json}`,
`results/processed/cpu_gpu_pilot_20261010T001232473460Z/REPORT.md`,
`results/raw/cub_workspace_65537_20261010T110457531249Z/FINAL_AUDIT.md`,
and all four `docs/CPU_GPU_COMPARISON_PROTOCOL_v1.md` / `docs/studies/cpu_gpu_comparison_v1.*` frozen inputs.

## Finding 1 — frozen source anchors are not independently enforced by analysis

`scripts/analyze_cpu_gpu.py:98` checks equality between the prerequisite source
map and source_review.json. It checks their surrounding hashes, but never checks
the retained protected source digests against the frozen matrix's
source_at_freeze_sha256, nor the explicitly reviewed CMake exception.
The runner separately checks actual local source with verify_source_extension;
that guard works and is not bypassed by this finding. The defect concerns the
independent analyzer's acceptance of internally consistent but protocol-inconsistent
provenance. It is not evidence that actual production code or accepted results changed.

Reproducer: `probe_full_analysis.py` uses disposable synthetic 48-dataset fixtures,
never a sorting call. A baseline passes the normal analyze(directory) performance
branch without allow_synthetic. Then only the *claimed* src/cuda/cub_sort.cu digest
is changed to 64 zeroes, the prerequisite source map is made consistent, and build
IDs/CSV references/raw hashes are refreshed. Frozen inputs remain unchanged.
Analysis still returns complete=true for the synthetic1200 measured/240 warm-up
records. This negative test exits1 because the required rejection did not occur.
See FULL_ANALYSIS_PROBE.json and commands/full_analysis_probe.json.
This is a semantic consistency check after resealing, not a claim that ordinary
unresealed corruption escapes the existing raw-manifest check.

The smaller metadata probe confirms the same gap, exit1. Its first attempt was
invalid because the historical non-timing environment fixture had a different
OpenMP policy; it stopped before its baseline with OpenMP environment mismatch.
The original script/log are preserved. Version2 changes only its disposable
fixture policy to the frozen values; baseline passes and the wrong digest is
accepted. No project source or historical environment record was altered.

Required correction before readiness: independently enforce every frozen protected
source digest and only the exact reviewed CMake exception, then add full analysis
regressions that reseal mismatched adapter/pin/CMake provenance. Internal agreement
between two source maps must not substitute for that anchor check.

## Finding 2 — timing-selection correction is operational, not regression-protected

The initial command is retained verbatim in
results/raw/cpu_gpu_full_tooling_20261010T121208603276Z/commands/release_ctest_non_timing.json.
It ran CTest in the new build/cpu_gpu_full_tooling_20261010T121208603276Z/release
directory with a20-group -R expression including parallel_mergesort; exit0.
CTest launched test_parallel_mergesort (test26). Its stdout explicitly reports
523 inputs/4184 public/registry checks and **6 timing rows passed**.
tests/test_parallel_mergesort.cpp:103-108 selects N32768,W1/R2 and two algorithms:
sequential Merge Sort and four-requested-thread parallel Merge Sort. That produces
four measured calls and two warm-ups. The shared timing engine really times the
calls; they cannot be described as zero CPU timing execution.

The sink only asserts correctness/elapsed presence/thread metadata and increments
a count. It does not serialize duration values. No per-trial CSV/JSON benchmark
dataset or pilot/study output was emitted by this path. The observed artifacts are
CTest/build test logs and the new milestone command record, including the summary
above. CTest bookkeeping lives in the milestone's newly created build directory;
later CTests may replace its Testing logs. No filesystem tracing exists, so this
review does not claim a complete transient filesystem-write trace. Source inspection
and actual hashes independently establish the result/source preservation stated below.

Later local Release and sanitizer19-group expressions exclude parallel_mergesort;
the retained remote21-group allowlist also excludes it. Those later commands really
passed and did not report the six rows. This corrects the recorded selection.
The embedded test itself remains intact, and no checked-in regression protects a
reusable non-timing selector. The two prerequisites-only tests mock CTest results
and check no pilot launch, not absence of timing-bearing tests. SELECTION_REVIEW.json
records the commands, source excerpts, later selections and test names.

The current --prerequisites-only validator intentionally invokes unfiltered full
CPU/GPU CTest suites (including timing-framework tests); the tooling guide explicitly
warns of this. That is its documented full-prerequisite behavior, not a hidden
claim that the option means no timing. It must not be invoked under this review's
no-timing restriction. Add a separately named reusable non-benchmark selection and
regression guard, preserving all tests and the frozen full-prerequisite requirements.

## Independently verified preservation and pin

INDEPENDENT_INTEGRITY.json recomputes actual file bytes against the retained maps:
- 11228 artifacts predating the tooling milestone: no changed/missing files.
- 85 sealed milestone evidence files,137 source files,4 documentation files and
 4 frozen files: all match.
- 11314 result files present at review start: unchanged; rechecked at final sealing.
- 373 accepted pilot evidence/processed files and62 workspace-audit evidence files:
 all match. These counts overlap the prior-artifact snapshot; they are not added.
- 26 protected anchors match their frozen identities, with only the pre-existing
 explicitly reviewed exact CMake integration exception. Production C++/CUDA
 adapters, timing implementation, registries, CUB notices/pin and defaults are intact.

Frozen protocol SHA2567738d21ff0ea611c04a557418182ab562769b568c7dc0b898ca5d50280e21c70;
matrix29f9f2765e466a88fc3a7b6e590b1c38dd1ebe5f4f003a37e02aabc9b7074833;
resources324a67c9668d258366f738348ad853cbadd65ce4edd6f34b3ec16f4baaafeaab;
freeze518ac535473e50fb61dab3a70858bdfe42dfdb43570f649174f44bffe40e1ac6.
The freeze's planning-time execution_authorized=false remains unchanged.
CUB3.0.1, version300001, CCCL commit
f19d875da0d8bfb2e38c109b2b40522b8abbbbc3 is unchanged. The1688-file retained
installed-dependency manifests match between accepted pilot and tooling validation;
this is not a new query of a currently connected GPU installation.
Archive inspection checks167 safe members without extraction; all137 source-file
hashes agree with current actual source. BUNDLE_REVIEW.json independently derives
the prior four modified Python/test files and one added study wrapper.

## Runner/analyzer review and new non-benchmark checks

The frozen main matrix is48 datasets at1025/65537/1000000: five seeded workloads
with1729/42/2718 plus one fixed signed-edge input per size, five backends,W1/R5,
1200 measured/240 warm-ups. Independent planning verification confirms the
SHA314159 dataset order, stored backend order/cyclic rounds and global indices0..1439.
Two dry-runs are byte-identical, exit0, with no study output directory created.

Reviewed the shared runner, study wrapper, protocol loader, analyzer, prerequisite
runner, C++ worker/input/host-timing path, production CUB/query path, prepared
timing path, CMake registrations and all50 framework tests. Existing runner uses
exclusive paths, serial execution, no resume/retry, all-three-size resource gates,
per-dataset60s/main1800s deadlines, durable attempt/command records and stop-on-error.
Analyzer enforces expected48-cell coverage, measured/warm-up counts, CSV/JSON
schemas, recipe/input SHA and row identities, actual OpenMP teams, finite metrics,
resource caps and contradictory completion markers. Partial evidence remains
incomplete and suppresses paired/cross-input conclusions. Raw-manifest integrity
works for unresealed changes. Provenance enforcement needs Finding1's correction.

The50 existing synthetic/framework methods pass freshly,0 failures/0 skips,
using the previously built Release comparison_input for small untimed input
generation. Sort/worker invocations in orchestration tests are mocks. Their
synthetic console completion messages are not a real study. Full command/log:
commands/synthetic_framework.json, exit0. No fresh C++ build or CTest was run here.
The targeted metadata and full-analyzer rejection probes fail as described above,
and are additional review checks, not counted as passing repository tests.

Primary ratios use only CPU host-call medians / production CUB host-call medians.
Prepared H2D/device/D2H/prepared E2E remain diagnostic-only. Existing synthetic
tests verify prepared substitution rejection and denominator independence.
Five repeats are summarized per input; equal-weight distinct-input medians/ratios
follow, identical contents collapse, all outliers remain. No CI/significance claim.
Accepted pilot reanalysis to a new file passes exit0 and regenerates its summary
byte-for-byte, SHA25607e69e2e0c8853f93d3f3da895337b5e4b72e5e2dd0ff0577db3cbd1f7053a22.

## Prerequisites and remaining risks

Because the tooling review failed, the conditional separate fresh prerequisite
validation was NOT started. No fresh environment readiness, Release/sanitizer/GPU
build, CUDA execution, resource allocation or complete PREREQUISITES.json is
claimed by this review. The historical19/19 Release and ASan/UBSan selections,
21/21 GPU selection and475/1900 CUB correctness outcomes are supported by the
verified old logs but are historical. The old CUDA build's341 generated line-
directive warnings remain documented; no new compiler-warning review is claimed.
Git status128 confirms absent metadata; no Git initialization/commit/push occurred.

Accepted pilot/resource evidence remains useful but does not control a future VM.
Observed pilot variation includes D2H CV65.34% atN1025 and prepared device-sort
CV17.00% at1M. Five repeats do not create independent input samples. Shared cloud,
two logical CPUs on one physical SMT core, uncontrolled clocks/thermal/cache/load
and unavailable device race/memory-safety checks limit inference. No ranking or
statistical significance is warranted. Workspace279295-byte queries atN65537 were
historically successful logical allocation requests, not measured physical footprint;
all three sizes and unchanged caps must be rechecked in the eventual study VM.

## Changes and exact next step

Only this new timestamped evidence directory was added: scripts, original and
corrected probe attempts, command logs, snapshots/hashes, synthetic probe reports,
dry-run/compatibility review, this audit, COMMANDS.md and FINAL_INTEGRITY.json.
No project code/documentation/frozen inputs, production adapter, resource limits
or earlier result file was modified. No source fix was applied during this review.

Next isolated milestone: fix and regression-test the independent analyzer's frozen
source-anchor enforcement and add a guarded non-benchmark selection path. Repeat
this review with synthetic checks and preservation sealing. After it passes,
separately authorize fresh complete frozen prerequisites, explicitly accounting
for their timing-framework tests, then review fresh all-size resource/environment
gates before any separate study authorization. Do not weaken the full prerequisite
suites or silently treat a non-timing subset as their replacement. NO-GO remains.
'''
with (base/'FINAL_AUDIT.md').open('x') as stream:stream.write(audit)
prior=json.loads((base/'START_SNAPSHOT.json').read_text())['existing_results_sha256']
old_seal=json.loads((old/'FINAL_INTEGRITY.json').read_text())
maps={'review_start_results':prior}
maps.update({key:old_seal[key] for key in ['evidence_sha256','current_source_sha256','documentation_sha256','frozen_files_sha256']})
checks={}
for name,mapping in maps.items():
    missing=[p for p in mapping if not (root/p).is_file()]
    changed=[p for p,h in mapping.items() if (root/p).is_file() and sha(root/p)!=h]
    assert not missing and not changed,(name,missing,changed)
    checks[name]=dict(checked=len(mapping),missing=missing,changed=changed)
save('FINAL_INTEGRITY.json',dict(review_evidence_complete=True,review_passed=False,recommendation='NO-GO',
    command='python3 -B '+str(base/'finalize_review.py'),exit_code=0,
    verified_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),preservation=checks,
    fresh_prerequisite_validation_run=False,actual_timing_calls=0,pilot_run=False,study_run=False,
    evidence_sha256={str(p.relative_to(root)):sha(p) for p in sorted(base.rglob('*')) if p.is_file()},
    manifest_excludes_itself=True))
print(json.dumps(dict(audit=str(base/'FINAL_AUDIT.md'),recommendation='NO-GO',preservation=checks),indent=2))
