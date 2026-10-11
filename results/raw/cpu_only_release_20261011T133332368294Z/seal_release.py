"""Write release audit/command index and a non-self-referential integrity seal."""
import hashlib
import json
from pathlib import Path

E=Path(__file__).resolve().parent
R=E.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def write(name,value):
    with (E/name).open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
records=[(p,load(p)) for p in sorted(E.glob('command_*.json'))]
changes=load(E/'CHANGES.json');preserved=load(E/'PRESERVATION.json');base=load(E/'BASELINE.json')
assert preserved['passed']
lines=['# Commands and actual exit statuses','',
       'All commands ran from the repository root unless the retained command record says otherwise.',
       'The complete argv/cwd/stdout/stderr for guarded CTest are in cpu_release*.json.',
       'No performance experiment, collector, GPU CLI or GPU workload was launched.','']
for p,d in records:
    lines += [f"## {p.name}: exit {d['exit_code']}",'',d['purpose'],'','```sh',d['command'],'```','',
              f"Working directory: `{d['working_directory']}`; start UTC: `{d['started_utc']}`.",'',
              f'Full stdout/stderr: [{p.name}]({p.name}).','']
lines += ['## Supplemental inspection and editing','',
    'Repository/tool inspections also used pwd, rg, ls, sed/cat, read-only Python, process-status inspection, and image viewing; '
    'source/document edits used apply_patch. These did not launch algorithms or experiments. '
    'Early inspection encountered absent guessed paths (docs/LOCAL_SELECTION_v5.md and several analyzer names); '
    'the actual paths were discovered before use. One guessed NEW_CUB_CORRECTNESS path was absent; '
    'the preserved actual correctness directory is listed in DEFERRED_GPU.md. '
    'These terminal inspection outputs are in the session transcript rather than standalone command JSON. '
    'They are not represented as successful validation commands. Git metadata was absent; no Git repository was initialized.','',
    'Final evidence generation command (report writing and hashing only):','',
    '```sh',f'python3 -B {E.relative_to(R)}/seal_release.py','```','',
    'Its own completion status is recorded in SEAL_STATUS.json; the seal excludes itself explicitly.']
(E/'COMMANDS.md').open('x').write('\n'.join(lines)+'\n')
filelist='\n'.join(f'- `{p}` — '+reason for p,reason in {
    'README.md':'CPU-only release entry points, explicit CUDA-disabled build and correctness-only procedure.',
    'docs/ROADMAP.md':'CPU release status; GPU deferred rather than a required unresolved milestone.',
    'docs/AUDIT.md':'Latest CPU-only verification and historical/reused evidence distinctions.',
    'docs/ALGORITHMS.md':'Current algorithm scope; deferred GPU implementation banner.',
    'docs/BENCHMARKING.md':'Current CPU-only study/report scope and preserved historical paths.',
    'docs/METRICS.md':'CPU metric/statistical scope; GPU definitions historical.',
    'report/README.md':'New report/presentation links and analysis-only regeneration instructions.',
    'report/generate.py':'Remove GPU input dependency; raw-audit gating; OpenMP/count/RSS figures; CPU-only report/slides.',
    'docs/CPU_ONLY_RELEASE_v1.md':'Additive scope, methodology, trial counts, environment and acceptance/limitations.',
    'docs/DEFERRED_GPU.md':'In-place archive index; no GPU full-study or performance-comparison claim.',
    'report/verify_cpu.py':'Read-only recomputation using existing raw parsers with subprocess execution prohibited.',
    'report/test_cpu_release.py':'Eight inert scope/statistics/output-preservation regressions.'}.items())
audit=f'''# CPU-only academic release — final audit

## Decision and scope

PASS for the explicitly revised CPU-only release. GPU execution, CUDA/CUB and
CPU/GPU comparison are outside acceptance. This is not a GPU eligibility approval.
No performance trials, warm-ups, CPU/GPU pilot/full study or GPU workload ran for
this revision. Completed CPU experiments were reused, not repeated. No commit,
push, driver/dependency installation, remote session or Git initialization occurred.

Repository: `{R}`. Git metadata is absent; there is no branch/revision to invent.
Source identity is the retained 167-file SHA-256 map, rechecked against
`results/raw/autonomous_completion_20261011T095554571762Z/CPU_STUDY_IDENTITIES.json`.
Only reporting/documentation changed; algorithms, tests, guards, policies, pins,
CMake configuration and source-selection manifests are unchanged.

## Verified gates

|Check|Result|Direct evidence|
|---|---|---|
|CPU-only Release build|PASS; existing build up to date; no configure, no new compiler warnings|command_005.json; CUDA/SORT/COMPARISON OFF, OpenMP ON|
|Fresh correctness|PASS 21/21 CTest groups, zero failed/group skips; 10 timing groups excluded|cpu_release.json, cpu_release_selection.json, STATIC_CPU_PLAN.json; command_007.json|
|Reporting regressions|PASS 8/8 new and 8/8 existing metrics-parser tests|command_009.json and command_004.json respectively|
|ASan/UBSan|REUSED PASS 21/21, leaks enabled; source/selection/build metadata unchanged; no fresh run needed for reporting-only edits|prior cpu_sanitize.json, command_010.json and PRESERVATION.json|
|Raw numerical audit|PASS all seven CPU summary inputs agree with retained raw analysis; no GPU data consumed|RAW_NUMERIC_AUDIT.json, command_009.json|
|Report workflow|PASS 17 files regenerated byte-identically, including seven PNGs, 20-page compact report PDF and 12-slide PDF|REGENERATION.json; command_011/012/013/015.json|
|Preservation|PASS all 13,537 pre-existing result files, 24 original generated report assets, 26 protected anchors, 80 protected native/header/vendor files, four frozen inputs, 83 build metadata files|BASELINE.json, PRESERVATION.json, FINAL_INTEGRITY.json; command_017.json|
|CPU approval scope|PASS; no independent approval gate for local CPU analysis/correctness; separate deferred CPU/GPU guard unchanged and fail-closed|command_010/014.json; scripts/cpu_gpu_evidence.py; unchanged v5 local-only manifest|

The selected 21 are the unchanged approved 19 plus explicit untimed diagnostics:

`{', '.join(load(E/'STATIC_CPU_PLAN.json')['selected'])}`.

Static source/build/path validation preceded discovery and metadata was rechecked
before execution. No broad CTest run occurred. Two GPU-execution Python methods
were intentionally skipped inside the host-only analysis group; no CTest group
was skipped. Synthetic framework messages describing 1,200 rows are fixtures,
not actual benchmark trials. Correctness timing printed by CTest is test-runner
duration, not a collected algorithm performance observation.

## Numerical audit and retained studies

Raw verification reuses existing strict parsers, with subprocess.run/Popen
blocked during reanalysis. Repeated timings are summarized per input dataset,
then dataset medians receive equal weight. Minima are never relabeled medians.
Cross-seed min/max is spread, not a confidence interval. All raw outliers remain.

|Retained experiment|Measured|Warm-ups|Failed/missing|
|---|---:|---:|---|
|1M sequential sorting|450|90|0/0|
|All-family CPU sorting|1,800|360|0/0|
|All-family array search batches|7,020|1,404|0/0|
|All-family structure operations|13,200|2,640|0/0|
|OpenMP scaling|1,800|360|0/0|
|10M sequential sorting|450|90|0/0|
|100M sequential sorting|150|30|0/0|
|Learned lookup batches/builds|480/240|96/48|0/0|
|Separate key-count/RSS executions|240|Not applicable|0/0|

Exact raw paths, counts and independently recomputed environment fields are in
RAW_NUMERIC_AUDIT.json and docs/CPU_ONLY_RELEASE_v1.md. The learned matrix has
48 workload configurations but 24 distinct sorted inputs; labels are not pooled
as independent datasets. Representative report tables/figures retain full numeric
precision in RESULT_TABLES.json and reference the original detailed summaries.

Environment: retained local Intel i5-11400H, 6 physical/12 logical CPUs;
Linux 6.18.7-76061807-generic, glibc2.39, GCC13.3.0, CMake3.28.3, Release
-O3 -DNDEBUG, MemTotal16,089,028KiB. OpenMP4.5/libgomp metadata and actual teams
are retained in the original sweep. Snapshot identities are recorded in the
raw verification. Different studies are not represented as one controlled session.

## Deliverables and exact edits

New final assets: `report/cpu_only_20261011T133332368294Z/`.
Byte-identical regenerated copy: the same path with `_regenerated` suffix.
Both are new directories; earlier report and presentation assets remain intact.
The report PDF is a compact narrative/figure artifact; full numerical tables and
references are in FINAL_REPORT.md and RESULT_TABLES.json. Slide9 and slide12 were
rendered and visually inspected; review images are retained in this directory.

Eight existing files modified and four source/document files added:

{filelist}

CHANGES.json records before/after hashes; SOURCE_DIFF.patch contains the complete
existing-file diff. The four additions are bound by their hashes in the seal.
New experiment data directories were not created; only release audit evidence
and two derived reporting directories were added.

## Failures, corrections and verification limits

- command_003.json exited1: the new raw audit compared an in-memory OpenMP build
  identity tuple with its JSON list representation. command_008 proved this was
  the sole difference. JSON normalization preserves every value; an inert
  regression and successful full raw reanalysis are retained in command_009.
- command_015's final prose incorrectly called nine identity-map entries nine
  CPU binaries. command_016 corrects this: three native executables and six
  metadata/protocol/selection files. All nine entries were actually hash-checked.
- Earlier initial focused run had seven new tests; the final eight include the
  tuple serialization regression. Initial outputs were not deleted.
- Some bootstrap/read-only inspections are available in the terminal transcript
  rather than standalone JSON; COMMANDS.md explicitly distinguishes these from
  retained validation invocations. Absent guessed paths were resolved by inventory,
  not fabricated. No failed command is presented as a successful validation.
- Reused sanitizer evidence establishes its recorded run for unchanged sources,
  selection and retained build metadata. No independent before/after baseline
  for every individual sanitizer test binary is available; no fresh sanitizer
  execution or full binary-identity revalidation is claimed.

## Limitations and security boundary

CPU results remain descriptive, shared-machine observations. Frequency, background
load, thermal/cache state and SMT contention were not controlled. 100M uses one
seed. Batch averages are not directly measured individual-query durations/maxima.
RSS includes input/runtime/allocator/instrumentation and is not isolated auxiliary
or structure memory. Radix key counts and structure comparison/allocation metrics
remain unsupported. TSan/OpenMP limitations remain; ordinary correctness tests do
not prove race freedom. AlphaDev training was not reproduced, and the optional
learned sorter selector is not implemented.

GPU source, frozen full matrix/resources/protocol, CUB3.0.1 and all old GPU
correctness/smoke/pilot/failure evidence remain unchanged. Historical pilots are
excluded from current release figures/tables; the full frozen CPU/GPU study was
not executed. The missing independent CPU/GPU approval remains required if that
workflow is reopened; no trust pin or policy was fabricated or weakened.

The revised release is complete for its declared CPU scope with the limitations
above. No CPU-only independent-approval blocker was found. No further experiment
is required to regenerate these deliverables.
'''
(E/'FINAL_AUDIT.md').open('x').write(audit)
write('SEAL_STATUS.json',dict(command=f'python3 -B {E.relative_to(R)}/seal_release.py',exit_code=0,
                             purpose='Evidence generation and hashing only',study_launched=False))
# Recheck all immutable baseline entries before recording the final maps.
for group in ['historical_results_sha256','protected_sha256','frozen_sha256','build_metadata_sha256','executable_sha256']:
    for name,digest in base[group].items():assert sha(R/name)==digest,(group,name)
seal={k:base[k] for k in ['historical_results_sha256','protected_sha256','frozen_sha256','build_metadata_sha256','executable_sha256']}
seal.update(schema_version=1,scope='cpu_only_release_v1',seal_excludes_itself=True,
            previous_seal=base['previous_seal'],previous_seal_sha256=base['previous_seal_sha256'],
            preservation=preserved['groups'],source_sha256=preserved['source_sha256'],
            protected_anchor_sha256=preserved['protected_anchor_sha256'],
            authorized_changes=changes,study_launched=False,gpu_workloads=0,performance_trials=0,
            historical_report_sha256={n:d for n,d in base['report_sha256'].items() if n not in changes['modified']},
            report_sha256={str(p.relative_to(R)):sha(p) for p in sorted((R/'report').rglob('*')) if p.is_file() and '__pycache__' not in p.parts},
            project_sha256={str(p.relative_to(R)):sha(p) for directory in ['include','src','scripts','tests','cmake','third_party','docs']
                            for p in sorted((R/directory).rglob('*')) if p.is_file() and '__pycache__' not in p.parts},
            evidence_sha256={str(p.relative_to(E)):sha(p) for p in sorted(E.rglob('*')) if p.is_file() and p.name!='FINAL_INTEGRITY.json'})
seal['project_sha256'].update({n:sha(R/n) for n in ['README.md','AGENTS.md','CMakeLists.txt']})
write('FINAL_INTEGRITY.json',seal)
print('CPU-only release audit and integrity seal written; historical evidence preserved; no performance experiment executed.')
