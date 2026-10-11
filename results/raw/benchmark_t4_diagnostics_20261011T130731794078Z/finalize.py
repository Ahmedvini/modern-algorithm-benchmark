"""Finalize metadata-only inspection; no subprocess, build or GPU workload."""
import hashlib
import json
from pathlib import Path

E=Path(__file__).resolve().parent
ROOT=E.parents[2]
def read(p):return json.loads(p.read_text())
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def put(p,v):
    with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')

base=read(E/'BASELINE.json');preservation={}
for kind in ['historical_results_sha256','project_sha256','protected_sha256','frozen_sha256',
             'build_metadata_sha256','executable_sha256','report_sha256']:
    missing=[];changed=[]
    for name,value in base[kind].items():
        p=ROOT/name
        if not p.is_file():missing.append(name)
        elif sha(p)!=value:changed.append(name)
    preservation[kind]=dict(files=len(base[kind]),missing=missing,changed=changed)
    assert not missing and not changed,(kind,missing,changed)
assert sha(ROOT/base['previous_seal'])==base['previous_seal_sha256']
unexpected=[str(p.relative_to(ROOT)) for p in (ROOT/'results').rglob('*') if p.is_file()
            and not p.is_relative_to(E) and str(p.relative_to(ROOT)) not in base['historical_results_sha256']]
assert not unexpected,unexpected
offline=read(E/'OFFLINE_GATES.json');search=read(E/'USER_CONFIGURATION_SEARCH.json')
assert offline['approval']['accepted'] is False and offline['approval']['exists'] is False
assert offline['approval']['trusted_pin'] is None
assert not any(Path(v['file']).name=='CPU_GPU_EVIDENCE_REVIEW_v1.json' for v in search['candidates'])
records=[(p,read(p)) for p in sorted(E.glob('command_*.json'))]
session_records=[(p,v) for p,v in records if 'colab status --session benchmark-t4' in v['command']]
assert len(session_records)==1
session_file,session=session_records[0]
assert session['exit_code']==0 and '[benchmark-t4] gpu-t4-s-kkb-ass1c0-vef28uetz4qh' in session['stdout']
assert 'Status: IDLE' in session['stdout'] and 'Usage rate: 1.07/hr' in session['stdout']
environment=dict(record_kind='control_plane_observation_not_gpu_runtime_validation',session_name='benchmark-t4',
    endpoint='gpu-t4-s-kkb-ass1c0-vef28uetz4qh',session_status='IDLE',reported_hardware='T4',
    cli_version='0.7.4',account_balance_compute_units=0.0,account_usage_compute_units_per_hour=1.07,
    active_assignments=1,free_compute_verified=False,actual_gpu_model=None,python_version=None,
    driver_version=None,cuda_toolkit_version=None,cuda_runtime_version=None,compiler_version=None,
    cub_version=None,remote_execution_performed=False,
    limitation='CLI control-plane observation establishes accessibility, not free billing, device usability or toolchain versions. Remote execution held under no-paid-compute constraint; session left untouched.',
    evidence=session_file.name)
put(E/'ENVIRONMENT_STATUS.json',environment)
gates=[
    dict(gate='Repository/frozen48-dataset matrix/source bundle',status='PASS',evidence='OFFLINE_GATES.json'),
    dict(gate='CPU Release and ASan/UBSan evidence',status='PASS',evidence='../gpu_final_resolution_20261011T111957067481Z/REUSED_CPU_EVIDENCE.json',note='21/21 each, retained and identity-matched; no rerun'),
    dict(gate='Existing benchmark-t4 accessibility and identity',status='PASS',evidence=session_file.name),
    dict(gate='Free use of existing assignment',status='BLOCKED',evidence='ENVIRONMENT_STATUS.json',note='Account reports1.07CU/hour; free-use entitlement not established. No monetary charge is asserted.'),
    dict(gate='Current actual GPU/Python/CUDA/compiler/CUB environment',status='BLOCKED',evidence='ENVIRONMENT_STATUS.json',note='No remote execution while free-use condition unresolved'),
    dict(gate='Genuine independent approval and trust anchor',status='BLOCKED',evidence='OFFLINE_GATES.json; USER_CONFIGURATION_SEARCH.json'),
    dict(gate='Intended GPU build/link/binary/comparison_input identity',status='BLOCKED',evidence='FINAL_AUDIT.md'),
    dict(gate='Identity-matched bounded GPU/framework/resource/worker checks',status='BLOCKED',evidence='FINAL_AUDIT.md'),
    dict(gate='Production eligibility and full frozen study',status='BLOCKED',evidence='FINAL_AUDIT.md'),
    dict(gate='Historical/source/frozen/build preservation',status='PASS',evidence='FINAL_INTEGRITY.json')]
put(E/'GATES.json',gates)
with (E/'MISSING_DEPENDENCIES.md').open('x') as f:
    f.write('# Exact unresolved dependencies\n\nThe production guard expects `docs/CPU_GPU_EVIDENCE_REVIEW_v1.json` and an independently protected, non-circular authority. The artifact is absent and `scripts/cpu_gpu_evidence.py:20` retains `TRUSTED_APPROVAL_SHA256=None`. The pure approval check at lines24-56 rejects it before gated execution. User execution authorization is already granted; repeating it would not install technical trust.\n\n')
    f.write('The actual accepted artifact is strict schema1, policy `cpu_gpu_evidence_enforcement_v1`, approved=true and execution_authorized=false. It must bind session/source/build/binary/freeze context; canonical source/build/Python paths; approved selection; CPU Release/sanitizer and GPU build provenance; all nine framework-record digests; five legacy record references; and preflight-report digest. See the unchanged [requirements description](../gpu_external_resolution_20261011T121306863461Z/REQUIRED_EXTERNAL_ARTIFACT.json) and `docs/CPU_GPU_EVIDENCE_ENFORCEMENT_v1.md:22-38`. This is not an approval/signature template and no self-created hash is trusted.\n\n')
    f.write('The existing T4 account reports1.07 compute units/hour with zero balance. These fields do not prove a monetary charge, nor establish free-use entitlement for this session. A supported billing/entitlement fact establishing free use is missing. The installed consumption display maps the backend rate and balance without a free/paid assignment flag. No remote execution or alternate/metered allocation was used. The existing session is neither stopped nor changed.\n')
with (E/'COMMANDS.md').open('x') as f:
    f.write('# Exact executed commands\n\nAll recorded commands are read-only local inspection, account/session metadata, filename searches or offline byte/hash validation. No remote code, upload, build, test, GPU workload or study timing ran. Raw command JSON retains exact working directories, timestamps, stdout/stderr and exit codes.\n\n')
    for p,v in records:
        f.write('## '+p.name+'\n\n'+v['purpose']+'\n\nUTC: '+v['started_utc']+'; cwd: `'+v['working_directory']+'`; exit: '+str(v['exit_code'])+'.\n\n```sh\n'+v['command']+'\n```\n\nOutput: ['+p.name+']('+p.name+').\n\n')
    f.write('## Startup and final seal\n\nSTARTUP.md records the complete instruction/latest-audit/log read and prior-seal verification/bootstrap, terminal exit0 each. Startup output was observed rather than saved separately. Git status executed through subprocess.run in the first inspection returned128: no Git metadata; inspection continued without initialization. It is printed explicitly in the command log, whose enclosing shell exit was0.\n\n')
    f.write('A local terminal copy-only helper (exit0) copied the already inspected search_authority.py into this new evidence directory; the old helper was not edited. apply_patch created this finalizer only under the new directory. No source files changed.\n\nFinal command: `python3 -B '+str((E/'finalize.py').relative_to(ROOT))+'`; it only reads/hashes files and writes this additive audit/seal. Assertion results are in FINALIZER_STATUS.json; the terminal reports its actual exit status.\n')
with (E/'FINAL_AUDIT.md').open('x') as f:
    f.write('# benchmark-t4 diagnostics and trust gate\n\n**NO-GO — one or more required validation gates remain open. No study launched.**\n\n|Gate|Status|Evidence|\n|---|---|---|\n')
    for g in gates:f.write('|'+g['gate']+'|'+g['status']+'|'+g['evidence']+'|\n')
    f.write('\n## New session observation\n\nThe user-reported session is now confirmed through `colab sessions` and `colab status --session benchmark-t4`: endpoint `gpu-t4-s-kkb-ass1c0-vef28uetz4qh`, T4/Standard/GPU, IDLE. Installed CLI is0.7.4. `colab usage` reported0.00CU balance,1.07CU/hour and one active assignment. All metadata commands exited0; actual output, rather than exit status alone, supports accessibility. This resolves the previous absence-of-session condition.\n\n')
    f.write('Free-use status remains unverified. The inspected installed consumption.py maps `currentBalance` to `paidComputeUnitsBalance` and displays account `consumptionRateHourly`; it exposes no free/paid assignment entitlement. A positive compute-unit rate is not independently treated as proof of monetary charges, but neither is zero balance proof of free execution. Under the explicit no-paid-compute constraint no `colab exec`, upload, CUDA diagnostic, compiler command or remote build was run. The user-created session was left untouched. Actual Python, driver, GPU device model/compute capability, CUDA runtime/toolkit, compiler and CUB versions are **unverified**, recorded as null in ENVIRONMENT_STATUS.json. Historical versions are not substituted. No runtime/kernel validation is claimed from the hardware descriptor.\n\n')
    f.write('## Repository and trust inspection\n\nGit metadata is absent (git status exit128); no branch/commit is invented. The current instructions, actual frozen protocol/matrix/resources/freeze, launcher, prerequisite call path, compatibility documentation and trust validator were inspected. Prior integrity maps were verified against actual bytes before creating this directory. Current pure frozen/production/selection validators pass. The48-dataset matrix retains all five modes,1200 measured calls and240 warm-ups; the current source and all217 archive members match the earlier reviewed bundle, SHA256 `'+offline['bundle_sha256']+'`. The default19 correctness names remain unchanged. No CPU study or suite was repeated.\n\n')
    f.write('The real pure `cpu_gpu_evidence.approval()` rejected with “independent evidence/selection review not installed.” Its required file is still absent and its trusted pin remainsNone. The fresh authorized home/config filename search examined'+str(search['filenames_inspected'])+' files in'+str(search['directories_inspected'])+' directories; no required artifact or CPU/GPU trust-root configuration was found. It excludes credential/browser/private-session/package/cache directories and does not follow symlinks; absence in excluded locations is not claimed. Prior generic/system configuration searches remain preserved evidence and were not redundantly repeated. The discovered older CMake driver review is outside the required current build/framework scope.\n\n')
    f.write('`docs/CPU_GPU_EVIDENCE_ENFORCEMENT_v1.md:22-38` explains the unresolved circular digest dependency and need for genuine independent non-circular authority. No such authority was recovered; no pin, signature, approval, eligibility rule, source guard or frozen asset was fabricated or changed. MISSING_DEPENDENCIES.md specifies the exact required artifact and existing accepted schema. Standing user authorization is accepted, not relabeled as an independent cryptographic review.\n\n')
    f.write('## Gated execution and preservation\n\nBecause trust remains blocked, no source transfer, configure/build, compiler/linker capture, comparison_input execution, GPU correctness/framework/resource/worker validation or full launch was attempted. There are0 warm-ups,0 measured trials and0 GPU workloads in this task. No partial run exists and no new performance claims are possible. All available evidence is diagnostic, not full-study eligibility.\n\n')
    f.write(str(len(base['historical_results_sha256']))+' pre-existing result files,'+str(len(base['report_sha256']))+' report files,'+str(len(base['project_sha256']))+' project files,'+str(len(base['protected_sha256']))+' production/header/dependency files,'+str(len(base['frozen_sha256']))+' frozen assets,'+str(len(base['build_metadata_sha256']))+' build-metadata files and'+str(len(base['executable_sha256']))+' build artifacts retain identical SHA256 contents. The previous seal is unchanged. No new result files exist outside this unique directory. CUB3.0.1 pinning and all historical CPU/GPU artifacts remain intact. Only evidence/log/search/finalizer files were added here; no commit/push, installation, new allocation or session stop occurred.\n\n')
    f.write('## Exact remaining gates\n\nA genuine independently protected review authority and applicable approval record are still required before gated execution. Separately, free-use entitlement of the existing assignment must be established before remote compute can be used under the user constraint. Once those external facts exist, genuine current GPU build/binary/framework/resource/worker evidence and the unchanged production guard must pass before the frozen full study. No further user execution permission is requested, and no study launch is authorized by this diagnostic audit.\n')
put(E/'FINALIZER_STATUS.json',dict(assertions_passed=True,preservation=preservation,unexpected_result_additions=[],
    source_changes=0,tests_executed=0,builds_executed=0,gpu_workloads=0,measured_trials=0,warmups=0,new_cloud_assignments=0))
seal=dict(schema_version=1,seal_excludes_itself=True,previous_seal=base['previous_seal'],previous_seal_sha256=base['previous_seal_sha256'],
    preservation=preservation,gates=gates,study_launched=False,source_changes=[],gpu_workloads=0,measured_trials=0,warmups=0)
for k,v in base.items():
    if k.endswith('_sha256') and isinstance(v,dict):seal[k]=v
seal['evidence_sha256']={str(p.relative_to(ROOT)):sha(p) for p in E.rglob('*') if p.is_file()}
put(E/'FINAL_INTEGRITY.json',seal)
print('All preservation checks passed:',len(base['historical_results_sha256']),'historical result files unchanged.')
print('benchmark-t4 accessibility confirmed; trust and free-use gates BLOCKED. Zero remote execution/build/test/study trials.')
