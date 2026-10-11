"""Evidence-only consolidation. No subprocess, CTest, GPU, timer or workload APIs."""
from pathlib import Path
import collections
import datetime
import difflib
import hashlib
import json
import re
import shlex
import sys
import tarfile

r=Path.cwd();e=Path(__file__).resolve().parent
remote=e/'downloaded/evidence';failed=e/'downloaded_failed/evidence'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text())
def write(name,value):
    with (e/name).open('x') as f:
        json.dump(value,f,indent=2,sort_keys=True);f.write('\n')

before=read(e/'BEFORE.json')
old=r/'results/raw/bounded_validation_20261011T020343203635Z'
assert sha(old/'FINAL_INTEGRITY.json')==before['previous_seal_sha256']
oldseal=read(old/'FINAL_INTEGRITY.json')
assert all(sha(old/p)==h for p,h in oldseal['evidence_sha256'].items())
historical={str(p.relative_to(r)):sha(p) for p in sorted((r/'results').rglob('*')) if p.is_file() and not p.is_relative_to(e)}
assert historical==before['historical_results_sha256'], 'historical membership/content changed'
names={'CMakeCache.txt','CTestTestfile.cmake','DartConfiguration.tcl','Makefile','compile_commands.json'}
build_metadata={str(p.relative_to(r)):sha(p) for p in sorted((r/'build').rglob('*')) if p.is_file() and p.name in names}
assert build_metadata==before['build_metadata_sha256'], 'existing local build metadata changed'

allowed={'scripts/ctest_build_guard.py','scripts/non_timing_tests.py','tests/test_cpu_gpu_comparison.py','README.md','docs/ROADMAP.md'}
expected_new={'tests/test_ctest_dart_compatibility.py','docs/NON_TIMING_TEST_SELECTION_v3.json','docs/CTEST_COLAB_METADATA_v2.md'}
paths=[r/'AGENTS.md',r/'README.md',r/'CMakeLists.txt']
for name in ['cmake','docs','include','scripts','src','tests','third_party']:
    paths.extend(p for p in (r/name).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
project={str(p.relative_to(r)):sha(p) for p in sorted(set(paths))}
assert set(project)-set(before['project_sha256'])==expected_new
assert not set(before['project_sha256'])-set(project)
changed={p:dict(before=h,after=project[p]) for p,h in before['project_sha256'].items() if project[p]!=h}
assert set(changed)==allowed, 'unexpected changed source/docs'
protected={p:h for p,h in before['project_sha256'].items() if p.startswith(('include/','src/','third_party/')) or p=='CMakeLists.txt'}
assert len(protected)==80 and all(project[p]==h for p,h in protected.items())
frozen=oldseal['preservation']['frozen_sha256']
assert len(frozen)==4 and all(sha(r/p)==h for p,h in frozen.items())
sys.path.insert(0,str(r/'scripts'))
from cpu_gpu_protocol import load_protocol
from cpu_gpu_provenance import trusted_source_anchors
from cpu_gpu_validation_policy import trusted_policy,verify_current_sources
policy,anchors=trusted_policy();verify_current_sources()
original_anchors=trusted_source_anchors(load_protocol())
assert len(original_anchors)==26
assert all(sha(r/p)==h for p,h in anchors.items())
exceptions={p:dict(frozen=h,approved_current=anchors[p]) for p,h in original_anchors.items() if anchors[p]!=h}
assert set(exceptions)=={'CMakeLists.txt','include/benchmark/cuda_timing.hpp','src/cuda/cub_timing.cu'}
v2=read(r/'docs/NON_TIMING_TEST_SELECTION_v2.json');v3=read(r/'docs/NON_TIMING_TEST_SELECTION_v3.json')
assert all(v2[k]==v3[k] for k in ['tests','cpu_build_tests','cuda_additional_tests'])
assert len(v3['reviewed_source_sha256'])==150
assert all(sha(r/p)==h for p,h in v3['reviewed_source_sha256'].items())
base=sorted(n for n,a in v3['tests'].items() if a['classification']=='cpu_correctness' and not a.get('diagnostic_only'))
assert len(base)==19
selected=sorted(n for n,a in v3['tests'].items() if a['classification']=='cpu_correctness')
assert len(selected)==21
transferred=read(e/'SOURCE_MANIFEST_V2.json')
transferred_diff={p:dict(transferred=h,current=sha(r/p)) for p,h in transferred.items() if sha(r/p)!=h}
assert set(transferred_diff)=={'README.md','docs/ROADMAP.md'}
for path in allowed:
    saved=e/'before'/path
    if not saved.is_file():
        with tarfile.open(e/'reviewed_source.tar.gz','r:gz') as t:
            data=t.extractfile(path).read()
        assert hashlib.sha256(data).hexdigest()==before['project_sha256'][path]
        saved.parent.mkdir(parents=True,exist_ok=True)
        with saved.open('xb') as f:f.write(data)
    assert sha(saved)==before['project_sha256'][path]
    diff=''.join(difflib.unified_diff(saved.read_text().splitlines(keepends=True),(r/path).read_text().splitlines(keepends=True),fromfile='before/'+path,tofile=path))
    target=e/'final_diffs'/Path(path+'.diff');target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('x') as f:f.write(diff)

for directory in [remote,failed]:
    seal=read(directory/'REMOTE_INTEGRITY.json')
    assert all(sha(directory/p)==h for p,h in seal.items())
    assert {str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file()}==set(seal)|{'REMOTE_INTEGRITY.json'}
assert sha(e/'validation_evidence.tar.gz')=='7339833e631df7f5dda203b6a4ef9a42a7714682331ac558d4a25e2a798780a9'
assert sha(e/'validation_evidence_failed.tar.gz')=='7ee768cfb4dd2cad9c97d5f0866176dd1a71c89b7431ad6d0bf561519651d3a7'
complete=read(remote/'BOUNDED_COMPLETE.json');assert complete['complete'] and not complete['study_execution_authorized']
assert complete['benchmark_trials']==complete['warmups']==0
classification=read(remote/'CLASSIFICATION.json')
assert classification['bounded_validation_ready'] and not classification['study_eligible'] and not classification['execution_authorized']
assert not (remote/'LEAK_LIMITATION.json').exists()
checks={p.stem:read(p) for p in (remote/'validation_commands').glob('*.json')}
assert len(checks)==10 and all(x['exit_code']==0 for x in checks.values())
for n in ['cpu_release_ctest','cpu_sanitize_ctest']:
    assert '100% tests passed, 0 tests failed out of 21' in checks[n]['stdout']
    assert '***Skipped' not in checks[n]['stdout']
    plan=read(remote/(n+'_selection.json'));assert plan['selected']==selected
gpu=json.loads(checks['gpu_prepared_untimed']['stdout'])
workers=json.loads(checks['actual_workers_untimed']['stdout'])
assert gpu['inputs']==163 and gpu['output_checks']==489 and gpu['invalid_operations_rejected']==489 and not gpu['failures']
assert len(workers['calls'])==workers['output_checks']==12
assert all(c['correctness'] and c['actual_team_size']==(2 if c['size']>=32768 else 1) for c in workers['calls'])
warnings={}
for attempt,directory in [('initial',failed),('revision2',remote)]:
    warnings[attempt]={}
    for p in sorted((directory/'build_commands').glob('*.json')):
        d=read(p);assert d['exit_code']==0
        lines=[line for line in (d['stdout']+'\n'+d['stderr']).splitlines() if 'warning:' in line]
        categories=dict(collections.Counter(line.split('warning:',1)[1].strip() for line in lines))
        warnings[attempt][p.stem]=dict(count=len(lines),categories=categories)
        assert not categories or categories=={'style of line directive is a GCC extension':367}
workspace=read(remote/'WORKSPACE_RESOURCES.json');assert workspace['all_limits_passed']
assert [x['size'] for x in workspace['rows']]==[1025,65537,1000000]
preservation=dict(historical_files_before=len(historical),historical_files_after_excluding_new_evidence=len(historical),
                  historical_content_and_membership_identical=True,historical_sha256=historical,
                  existing_local_build_metadata_unchanged=len(build_metadata),build_metadata_sha256=build_metadata,
                  project_before_count=len(before['project_sha256']),project_after_count=len(project),project_current_sha256=project,
                  modified_existing=changed,added_project_files={p:project[p] for p in sorted(expected_new)},
                  protected_production_dependency_files_unchanged=len(protected),protected_current_sha256=protected,
                  trusted_anchor_count=26,previously_authorized_framework_exceptions=exceptions,
                  trusted_current_anchors_sha256=anchors,new_framework_changes=0,frozen_sha256=frozen,
                  cub_pin_sha256=sha(r/'third_party/cub/UPSTREAM.json'),
                  production_adapter_sha256=sha(r/'src/cuda/cub_sort.cu'),reviewed_source_files=150,
                  transferred_files=len(transferred),informational_post_transfer_changes=transferred_diff,
                  previous_evidence_seal_verified=True,failed_remote_seal_members=37,successful_remote_seal_members=52)
write('PRESERVATION_VERIFIED.json',preservation)
facts=dict(stage_status={str(i):'PASS' for i in range(6)},cpu_release_passed=21,cpu_sanitize_passed=21,
           ctest_group_skips=0,host_gpu_timing_method_skips_each_suite=2,local_focused_passed_methods=66,
           prepared_gpu=gpu,workers=workers,workspace=workspace,warnings=warnings,classification=classification,
           benchmark_trials=0,warmups=0,pilot_runs=0,full_study_executed=False,leak_detection_disabled=False)
write('VALIDATION_FACTS.json',facts)

# All subprocess invocations retain their exact argv, cwd, status and full output.
records=[]
for p in sorted(e.rglob('*.json')):
    try:d=read(p)
    except (ValueError,UnicodeError):continue
    if isinstance(d,dict) and 'argv' in d and 'exit_code' in d:
        records.append((str(p.relative_to(e)),d))
lines=['# Exact command and status ledger','',
       'All paths below are relative to this evidence directory. argv is shell-rendered with shlex.join; JSON retains the exact argument array, cwd, UTC start and full output. Local recorder exit1 means its child failed; use the child exit field. Colab CLI exit0 is not a semantic pass: inspect markers and tracebacks. Remote leaf commands are separately listed. No timing-bearing workload was authorized or executed.','',
       'Baseline hash-only command: `python3 -B -` with literal stdin in [BASELINE_COMMAND.py](BASELINE_COMMAND.py), exit0. Initial Git inspection reported absent metadata; no Git mutations occurred.','',
       'Independent read-only reviewer commands/statuses: [AGENT_COMMANDS.md](AGENT_COMMANDS.md). Source edits used apply_patch or evidence-local assembly scripts; the exact final source diffs are under final_diffs/.','',
       'Evidence-only final consolidation/seal command: `python3 -B '+str(e.relative_to(r))+'/consolidate_audit.py`, run from repository root; success is established by FINAL_INTEGRITY and the terminal completion marker. It invokes no subprocess/workload.','']
for name,d in records:
    scope=d.get('scope',d.get('classification','Inherited from enclosing bounded launcher; see exact command and source.'))
    if '/build_commands/' in name:scope='Build/configuration only; no test or benchmark invocation.'
    elif '/validation_commands/' in name:
        if 'discovery' in name:scope='Guarded ordinary CTest discovery only, after static validation.'
        elif '_ctest.json' in name:scope='Exact21 non-timing correctness groups; sequential CTest execution.'
        elif 'gpu_prepared' in name:scope='Untimed GPU correctness only, no event samples.'
        elif 'resources_' in name:scope='Non-sorting bounded workspace/allocation diagnostic.'
        elif 'actual_workers' in name:scope='Untimed public/registry worker correctness.'
        else:scope='Metadata-only --describe.'
    lines+=['## '+name,'','- UTC: '+str(d.get('started_utc',d.get('observed_utc','not recorded in this leaf'))),
            '- cwd: `'+str(d.get('cwd','see parent remote script'))+'`','- exit: `'+str(d['exit_code'])+'`','- scope: '+scope,
            '- full retained record: ['+name+']('+name+')','','```sh',shlex.join(d['argv']),'```','']
# Environment script records each diagnostic command in its own stdout JSON.
env_record=read(e/'remote_environment.json')
env=json.JSONDecoder().raw_decode(env_record['stdout'])[0]
lines+=['## Remote environment leaf diagnostics','']
for d in env['commands']:
    lines+=['```sh',shlex.join(d['argv']),'```','',f"Exit {d['exit_code']}; environment/resource observation only. Full output: remote_environment.json.",'']
lines+=['## Read-only final inspection and retained harmless lookup errors','',
        'Read-only inspection used cat/sed/rg, JSON parsing and SHA-256 over evidence/source; no external workload calls. One compound lookup attempted nonexistent `src/cpu_gpu_comparison_main.cu` and `metadata_cpu-sanitize/generated/build_metadata.hpp`; rg/cat reported missing paths, final ls exited0. Corrected inspected paths were `src/cuda/comparison_resources.cu` and generated/Debug/{benchmark_build.hpp,parallel_build.hpp,source_hashes.json}. These errors did not trigger execution or alter files.','',
        'The first v2 static review used a persistent Colab kernel and returned CLI0 with a ValueError. The isolated retry retained that failure, launched a fresh python3 -B process and passed. No discovery occurred during the rejected check.','',
        'The two local fixture harness errors are retained in fixture_focus.json and fixture_focus_corrected.json; corrected fixture_focus_final.json passed9/9 with subprocess/shell entry points blocked. Initial real Release group failure is preserved in downloaded_failed/evidence/validation_commands/cpu_release_ctest.json (exit8).','']
with (e/'COMMANDS.md').open('x') as f:f.write('\n'.join(lines))

resource_table='\n'.join('| '+str(row['size'])+' | '+str(row['query']['prepared_query_bytes'])+' | '+str(row['query']['adapter_query_bytes'])+' | '+str(row['query']['combined_device_payload_bytes'])+' | '+str(row['calculated_full_study_host_payload_bytes'])+' |' for row in workspace['rows'])
audit=f'''# Bounded validation consolidated final audit

Verdict: **VALIDATION READY — bounded validation passed; full study NOT authorized**

This resumes the immutable blocked attempt at ../bounded_validation_20261011T020343203635Z/FINAL_AUDIT.md. No Git metadata exists; no branch/revision/clean working-tree claim is made. Source identity is the complete188-file transfer manifest plus150 reviewed executable/build/test sources. Frozen inputs and production algorithms were not changed.

## Stage outcomes

| Stage | Result | Current evidence |
| --- | --- | --- |
| 0 baseline | PASS | BEFORE.json; previous seal verified before editing; current historical12,046 files and65 local build metadata files frozen as baseline |
| 1 diagnostics | PASS | Existing approved test-only shared prepared path and public/registry worker diagnostic reused unchanged; current GPU163/489 and worker12 checks passed |
| 2 classification | PASS | Existing v2 policy pinned independently,9 focused local and9 methods in each CPU suite passed; correctness classified separately, never eligible/authorized |
| 3 replacement environment/build | PASS | Exactly one new T4 session after no active session; hash-verified isolated source; all six revision2 configure/build commands exit0 |
| 4 bounded validation | PASS | Release21/21, ASan/UBSan21/21, prepared GPU correctness, all frozen-size bounded resources, actual worker teams |
| 5 audit/preservation | PASS | PRESERVATION_VERIFIED.json; FINAL_INTEGRITY.json; sealed53-file success and38-file failed remote evidence |

## Changes and reviewed boundaries

Modified this resumption: scripts/ctest_build_guard.py (exact CMake3.31 Dart compatibility), scripts/non_timing_tests.py (select additive v3 profile), tests/test_cpu_gpu_comparison.py (historical synthetic source/context isolation and2 real-guard regressions), README.md and docs/ROADMAP.md (actual status). Added tests/test_ctest_dart_compatibility.py (9 inert methods), docs/NON_TIMING_TEST_SELECTION_v3.json (same registrations/classifications,150-source review snapshot), docs/CTEST_COLAB_METADATA_v2.md (exact support contract). Source diffs and before copies are retained in final_diffs/ and before/.

The v2 guard profile accepts the old literal metadata layout or the same layout plus both empty TLSVerify/TLSVersion keys. MemoryCheckCommand is the original sentinel or exactly /usr/local/cuda/bin/compute-sanitizer; ordinary fixed CTest commands do not invoke dashboard/MemCheck. Unknown settings, hooks/includes/subdirs, modified source/commands/properties, path aliases and boundary mutation remain rejected. Independent read-only reviewers inspected the actual changes before build/discovery; AGENT_COMMANDS.md retains their exact commands. Local inert regression runs passed9+36+3+9+9=66 method invocations. These are separate focused runs, not a claim of66 unique methods or native CTest groups.

No new changes to production/header/dependency/CMake files occurred in this resumption: all80 protected files match BEFORE. The earlier explicitly authorized test-only framework extension changed CMakeLists.txt, include/benchmark/cuda_timing.hpp and src/cuda/cub_timing.cu relative to the original frozen26 anchors; those3 approved exceptions are recorded, not hidden. The current policy pins their exact reviewed digests. Frozen protocol/matrix/resources/freeze and production CUB adapter remain original; historical protocol files are immutable. The legacy analyzer/launch gates deliberately still reject this extended framework. They were not relaxed or relabeled.

## Session and source/executable identities

Alias cpu-gpu-bounded-validation-v3; actual session gpu-t4-s-kkb-usw1b1-zafww0nxdtgf. Original session unavailable; initial inventory pruned a stale earlier session, then exactly one replacement was created. GPU Tesla T4 CC7.5 UUID GPU-5d327ac4-2d0a-4a11-6bd7-97474ba6359c; driver580.82.07, CUDA runtime/API13000, toolkit/nvcc13.0.88, GCC13.3.0, CMake3.31.10, Python3.13.15, OpenMP4.5/libgomp, C++17. Two logical CPUs share one physical core; no claim of two physical cores or controlled load/frequency/thermal state. remote_environment.json and downloaded/evidence/FINAL_GPU_SNAPSHOT.json retain observations.

Revision2 source archive SHA2565303683f37e48ab03bcb287b2c560d2100293b68209f63cc354fe0923ab9102f; source manifest SHA256e5f16f241a6dd27fd5d4d751aecd06fc9d68f7dc28ae231be2fe4d608132b0c3. Both independently verified remotely before extraction; all188 members verified after transfer and after validation. Current local README/roadmap have informational post-transfer status changes only; all150 executable/test/build sources still match reviewed v3. SOURCE_MANIFEST_V2.json, downloaded/evidence/transfer.json and PRESERVATION_VERIFIED.json distinguish identities.

Current comparison executable SHA256d3416ec4fb1e6d3b3536350ae6c7340fa1cfa9831d4460bf4027421897318835; worker SHA256b68258082395578568615407281fa3437e60b3f898de616a1a9575dbf517b0c6; prepared correctness SHA25637d4f4ea6b3e0c136efce5c688127bae7bdbd6de15f5b5cb5e31d4e06b4158f7. BUILD_COMPLETE.json and LINK_BINDINGS.json prove both comparison and worker bind the same parallel library. CUB300001/3.0.1 and protected pin SHA256477b1ee70b0a9113c9f98b263c19a31d05ccee54f45ce8476aec4cc98965ced1 remain unchanged.

## Current correctness coverage

Static guard approved all three fresh canonical build trees before real discovery. CPU trees have31 registered tests, GPU tree35; the fixed selection includes exactly21. Default19 remains:

`{', '.join(base)}`

Explicit diagnostic additions: parallel_workers_correctness and validation_policy. parallel_mergesort, comparison_engine, cuda_benchmark_gpu_framework and all other timing targets excluded. No broad CTest invocation. Full exact argv, prefixes, cwd, build digests and selection JSON are retained. Release21/21 and Debug ASan/UBSan21/21 passed; failures0, missing0, CTest-group skips0. Each host-only CUDA analysis group deliberately skipped2 GPU timing Python methods; these are not passed GPU tests. The selected CPU tests include temporary CUDA-OFF configuration checks but no timing workload. Full framework synthetic suite now52/52 methods. Local policy9/9 and per-suite policy9/9 passed.

Sanitizer uses -g -fsanitize=address,undefined -fno-omit-frame-pointer; executable/link metadata retained. env -u ASAN_OPTIONS -u LSAN_OPTIONS UBSAN_OPTIONS=halt_on_error=1 selected CTest succeeded0. Leak detection was not disabled; no ptrace limitation recurred. CUDA GPU correctness is Release, not GPU sanitizer/race detection.

Prepared framework correctness:163 inputs,489 output-oracle checks,489 invalid-operation rejections,0 failures,0 skipped,0 missing. Covers empty/singleton/signed extrema/duplicates, reproducible distributions and boundary sizes through65,537, repeated/interleaved sessions. Uses execute_untimed shared production-prepared helpers, not raw-CUB replacement or sample/timing loops. Existing production475/1900 correctness suite was not rerun in this bounded task. No current performance framework or throughput result is asserted.

Worker diagnostic:12 successful public/registry calls at N0/1/32,767/32,768/32,769/65,537. Requested2, actual team1 below32,768 and team2 at/above. The same checks also passed inside CPU Release and sanitizer groups. Team size is runtime membership, not proof each worker ran tasks, physical-core parallelism, race freedom or scaling. OMP_DYNAMIC=FALSE, OMP_THREAD_LIMIT=2, OMP_MAX_ACTIVE_LEVELS=1, OMP_PROC_BIND=FALSE, OMP_WAIT_POLICY=PASSIVE; OMP_NUM_THREADS unset; explicit API requests2.

## Bounded resources (bytes)

| N | prepared query | production-parameter query | frozen conservative device payload | calculated host payload |
| --- | --- | --- | --- | --- |
{resource_table}

Both workspace requests succeeded at max(query,1); each within64MiB. The diagnostic allocates only two4N key buffers plus two queried workspaces, never full benchmark inputs or sorting trials. Conservative policy device payload16N+both workspaces is distinct from explicit key requests8N+both workspaces. At1M explicit requests total16,357,374B; conservative budget24,357,374B, below256MiB and half available GPU memory. Host estimate24N is payload only, not measured RSS or whole-process footprint. Source src/cuda/comparison_resources.cu was inspected, unchanged.

CUDA available15,527,116,800B at each query, total15,637,086,208B; host available12,493,795,328B; diskfree75,135,385,600B. Each host payload below256MiB/half available, host/disk availability above1GiB. Physical allocator footprint was not measured; production adapter allocation was not instrumented. Values are point-in-time, not launch guarantees. WORKSPACE_RESOURCES.json retains queries/calculations/request successes and exact measurement labels.

## Warnings, failures and corrective attempts

Both fresh attempts configured/built all3 configurations successfully. CPU builds0 warnings. Each CUDA build logged367 warnings, all `style of line directive is a GCC extension`, originating in nvcc-generated host/stub line markers (including diagnostics compilation), not367 different source defects. Historical341 is an earlier build count, not the current count. No suppression, source edit or compiler flag change to hide warnings; full build stderr retained. No unrelated warning category observed. This classification does not prove absence of all toolchain bugs.

Initial actual Release run:20/21 groups passed, cpu_gpu_comparison_framework failed4 assertions out of50 methods; CTest8. Three mocks unintentionally invoked the real legacy frozen-framework gate against approved new framework; another inherited CTEST_* from CTest and correctly hit the real environment guard. The test-only fix explicitly models historical frozen provenance in the synthetic fixture and isolates only its mocked environment. Two regressions verify the real legacy gate still rejects current framework and explicit CTEST_TEST_ARGS still rejects before discovery. No production eligibility weakening. Initial evidence and source remain at separate remote root, retained locally under downloaded_failed/ and validation_evidence_failed.tar.gz.

Local focused invocation1 incorrectly passed a unittest class argument to a script that interprets it as input-tool path:52 methods ran,1 error, exit1, no benchmark. Invocation2 used an explicit import loader but omitted tests/ from sys.path:9 ran,1 failure+1 error, exit1. Corrected invocation3 blocked all subprocess/shell entry points and passed9/9. Logs retained verbatim; synthetic `study complete1200` messages denote mocked records only, never1200 actual measurements.

Revision2 static guard invocation initially reused persistent Colab imports from revision1, returned CLI0 with a ValueError (`unreviewed generated command`). Guard rejected before any discovery. Fixed the evidence-only launcher by starting fresh python3 -B process; static review and bounded runner then passed with exact revision2 absolute identities. Colab CLI return0 alone was never treated as success. All failed attempts retained. No reconfiguration in the old project or evidence overwrite occurred.

## Preservation and audit limits

All12,046 historical result files match exact baseline membership and SHA256; all65 prior local build metadata files unchanged. All80 protected production/header/dependency files unchanged this resumption;26 trusted original anchors retain only the3 previously authorized framework exceptions. Four frozen inputs verified unchanged before/after; production adapter/CUB pin unchanged. New project additions exactly3 and modified existing files exactly5, as enumerated above; all other additions confined to this new evidence directory. Both remote archives independently hash/member-verified: success7339833e631df7f5dda203b6a4ef9a42a7714682331ac558d4a25e2a798780a9 (52 sealed members+self); failed7ee768cfb4dd2cad9c97d5f0866176dd1a71c89b7431ad6d0bf561519651d3a7 (37+self). Remote binaries remain on session; executable hashes/link commands retained locally, not binary copies.

No timing smoke, pilot, warmup, measured trial, scaling run, full study,100M run, commit/push or Git initialization. Ordinary test harness duration output is not benchmark data. No token/credential diagnostic was requested; allowlisted environment output and redacted CLI recorder used. A bounded common-token-pattern scan is included in FINAL_INTEGRITY; it is not an exhaustive forensic guarantee.

## Exact next gate

Independent review of this consolidated bounded evidence and reviewed compatibility/test-only changes. Full-study legacy provenance is still incompatible with the deliberate framework extension; any adaptation requires separate explicit review/approval rather than treating correctness as timing eligibility. Current-session compatible timing/pilot coverage, independent launch review and explicit study authorization are not supplied by this task. Stop here: no study execution is authorized.

Commands/statuses: [COMMANDS.md](COMMANDS.md). Hash/content/member preservation: [PRESERVATION_VERIFIED.json](PRESERVATION_VERIFIED.json). Final seal: [FINAL_INTEGRITY.json](FINAL_INTEGRITY.json). Current raw logs: downloaded/evidence/build_commands/ and validation_commands/. Policy assessment: downloaded/evidence/CLASSIFICATION.json; all-output counts: VALIDATION_FACTS.json.
'''
with (e/'FINAL_AUDIT.md').open('x') as f:f.write(audit)
token_patterns=[re.compile(r'gh[pousr]_[A-Za-z0-9]{24,}'),re.compile(r'ya29\.[A-Za-z0-9_-]{20,}'),re.compile(r'Bearer\s+[A-Za-z0-9._-]{24,}')]
hits=[]
for p in e.rglob('*'):
    if p.is_file() and p.suffix in {'.md','.json','.py','.diff'}:
        content=p.read_text(errors='replace')
        if any(pattern.search(content) for pattern in token_patterns):hits.append(str(p.relative_to(e)))
assert not hits,'bounded token-pattern scan hit; inspect privately'
manifest={str(p.relative_to(e)):sha(p) for p in sorted(e.rglob('*')) if p.is_file()}
seal=dict(schema_version=3,created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
          verdict='VALIDATION READY — bounded validation passed; full study NOT authorized',
          evidence_sha256=manifest,evidence_files_excluding_seal=len(manifest),
          preservation_reference='PRESERVATION_VERIFIED.json',historical_files_verified=len(historical),
          frozen_sha256=frozen,protected80_unchanged=True,previous_framework_exceptions=exceptions,
          old_build_metadata65_unchanged=True,stage_status=facts['stage_status'],
          benchmark_trials=0,warmups=0,pilot_runs=0,full_study_executed=False,
          study_eligible=False,study_execution_authorized=False,leak_detection_disabled=False,
          ctest_executions=3,ctest_discoveries=3,final_cpu_release_passed=21,final_cpu_sanitize_passed=21,
          gpu_correctness_inputs=163,gpu_output_checks=489,invalid_operations_rejected=489,
          workspace_sizes=[1025,65537,1000000],worker_output_checks=12,
          common_token_pattern_scan_hits=0,secret_scan_limit='Limited common PAT/OAuth/Bearer patterns; not exhaustive. No secrets requested.',
          seal_note='FINAL_INTEGRITY.json excludes itself; all other evidence members/content sealed.',
          seal_command=['python3','-B',str(e.relative_to(r))+'/consolidate_audit.py'])
write('FINAL_INTEGRITY.json',seal)
print(json.dumps(dict(verdict=seal['verdict'],historical_preserved=len(historical),protected_unchanged=len(protected),
                     build_metadata_preserved=len(build_metadata),evidence_sealed=len(manifest),new_project_files=3,modified_project_files=5),indent=2))
print('CONSOLIDATED_AUDIT_SEALED')
