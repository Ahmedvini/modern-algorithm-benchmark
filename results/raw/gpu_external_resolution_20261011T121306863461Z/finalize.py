"""Offline preservation and audit only; no subprocess, tests or workloads."""
import hashlib
import json
from pathlib import Path

E = Path(__file__).resolve().parent
ROOT = E.parents[2]

def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''): h.update(block)
    return h.hexdigest()

def read(p): return json.loads(p.read_text())
def put(p, value):
    with p.open('x') as f: json.dump(value, f, indent=2, sort_keys=True); f.write('\n')

base = read(E/'BASELINE.json')
preserved = {}
for kind in ['historical_results_sha256','project_sha256','protected_sha256','frozen_sha256',
             'build_metadata_sha256','executable_sha256','report_sha256']:
    missing = []; changed = []
    for name, digest in base[kind].items():
        p = ROOT/name
        if not p.is_file(): missing.append(name)
        elif sha(p) != digest: changed.append(name)
    preserved[kind] = dict(files=len(base[kind]),missing=missing,changed=changed)
    assert not missing and not changed, (kind,missing,changed)
assert sha(ROOT/base['previous_seal']) == base['previous_seal_sha256']
historical = set(base['historical_results_sha256'])
unexpected = [str(p.relative_to(ROOT)) for p in (ROOT/'results').rglob('*')
              if p.is_file() and not p.is_relative_to(E) and str(p.relative_to(ROOT)) not in historical]
assert not unexpected, unexpected
offline = read(E/'OFFLINE_VERIFICATION.json')
assert offline['approval']['accepted'] is False and offline['approval']['exists'] is False
assert offline['approval']['trusted_pin'] is None and len(offline['default_test_names']) == 19
user = read(E/'USER_CONFIGURATION_SEARCH.json')
extra = read(E/'SUPPLEMENTARY_CONFIGURATION_SEARCH.json')
generic = read(E/'GENERIC_CONFIGURATION_SEARCH.json')
assert not any(Path(c['file']).name == 'CPU_GPU_EVIDENCE_REVIEW_v1.json' for c in user['candidates'])
assert not extra['candidates']
assert not generic['project_matches']
records = [(p,read(p)) for p in sorted(E.glob('command_*.json'))]
sessions = [(p,v) for p,v in records if 'colab sessions' in v['command']]
assert len(sessions) == 1
session_file, session = sessions[0]
assert session['exit_code'] == 0 and 'No active sessions' in session['stdout']
assert '0.00 compute units' in session['stdout'] and 'Active assignments: 0' in session['stdout']
gates = [
    dict(gate='Frozen/source/bundle/production identity',status='PASS',evidence='OFFLINE_VERIFICATION.json'),
    dict(gate='Historical evidence and CPU deliverables preserved',status='PASS',evidence='FINAL_INTEGRITY.json'),
    dict(gate='CPU Release and sanitizer coverage',status='PASS — retained 21/21 each, not rerun',evidence='../gpu_final_resolution_20261011T111957067481Z/REUSED_CPU_EVIDENCE.json'),
    dict(gate='Independent approval/trust anchor',status='BLOCKED',evidence='USER_CONFIGURATION_SEARCH.json; SUPPLEMENTARY_CONFIGURATION_SEARCH.json; OFFLINE_VERIFICATION.json'),
    dict(gate='Confirmed free authorized GPU',status='BLOCKED',evidence=session_file.name),
    dict(gate='Current GPU build/framework/resource/worker provenance',status='BLOCKED — dependent on GPU and authority',evidence='FINAL_AUDIT.md'),
    dict(gate='Full study and post-run audits',status='NOT EXECUTED',evidence='FINAL_AUDIT.md')]
put(E/'GATES.json',gates)
required_fields = ['schema_version','policy','approved','execution_authorized','context','source_dir','build_dir','python',
    'selection_sha256','cpu_build_provenance_sha256','build_provenance_sha256','record_sha256','legacy_records','preflight_report_sha256']
put(E/'REQUIRED_EXTERNAL_ARTIFACT.json',dict(
    record_kind='requirements_description_not_an_approval',
    expected_file='docs/CPU_GPU_EVIDENCE_REVIEW_v1.json',
    validator='scripts/cpu_gpu_evidence.py:24-56',
    required_fields=required_fields,
    schema_version_required=1,policy_required='cpu_gpu_evidence_enforcement_v1',
    approved_required=True,execution_authorized_required=False,
    context_fields=['session_id','source_identity','build_identity','binary_identity','freeze_sha256'],
    authority_status='absent; no configured independent pin or signing authority',
    caveat='Describing accepted fields supplies no approval. Current inline-pin/source binding is circular; independently protected non-circular authority is required before activation. No signature, hash, authority or approval is created by this description.'))
with (E/'COMMANDS.md').open('x') as f:
    f.write('# Commands and observed status\n\nAll commands were inspection, filename searches, offline byte/hash validation or audit creation. No tests, builds, CTest, GPU work, allocations or study trials ran.\n\n')
    for p,v in records:
        f.write('## '+p.name+'\n\n'+v['purpose']+'\n\nUTC: '+v['started_utc']+'; cwd: `'+v['working_directory']+'`; shell exit: '+str(v['exit_code'])+'.\n\n```sh\n'+v['command']+'\n```\n\nFull stdout/stderr: ['+p.name+']('+p.name+').\n\n')
    f.write('## Startup and finalization\n\nSTARTUP.md records the first complete instructions/audit/log read and prior-seal verification/bootstrap commands, both terminal exit0. Raw startup output was observed in the terminal rather than retained. The first recorded compound inspection contains `git status --short --branch` exit128 (Git metadata absent), though the final shell exit0; it was not repaired or initialized. Supplementary searches retained nine PermissionError entries and did not escalate or read those directories. No credential contents were read.\n\n')
    f.write('Available-tool metadata was filtered for GPU/Colab/browser/notebook capabilities: only a worktree-status tool matched; no alternate runtime/browser capability was invoked. This metadata inspection is not a terminal command and has no shell exit code.\n\n')
    f.write('Final command: `python3 -B '+str((E/'finalize.py').relative_to(ROOT))+'`. This helper only reads/hashes files and creates additive audit records; no subprocess or workload. Successful assertions are retained in FINALIZER_STATUS.json; actual terminal exit status must be observed, not inferred from this document.\n')
with (E/'FINAL_AUDIT.md').open('x') as f:
    f.write('# External-blocker continuation audit\n\n**NO-GO — one or more required validation gates remain open. No study launched.**\n\n')
    f.write('## Gate status\n\n|Gate|Status|Evidence|\n|---|---|---|\n')
    for g in gates:f.write('|'+g['gate']+'|'+g['status']+'|'+g['evidence']+'|\n')
    f.write('\n## What was independently established\n\nThe previous FINAL_INTEGRITY.json and every digest map in it were verified against actual bytes before this directory was created, including its evidence files and source map. This is fresh inspection, not reliance on the prior textual audit. All frozen assets and compatible protected anchors validated through existing pure validators. The unchanged 217-member bundle was checked against both current files and every archive member; its SHA-256 remains `'+offline['bundle_sha256']+'`. It was reused, not regenerated or uploaded. The approved 19 default test names remain unchanged; no discovery or tests ran. Prior identity-matched CPU 21/21 Release and sanitizer evidence remains applicable and was not repeated.\n\n')
    f.write('## Trust investigation and exact limitation\n\nThe production guard fixes the expected path at `scripts/cpu_gpu_evidence.py:19` and has `TRUSTED_APPROVAL_SHA256=None` at line20. Its actual pure `approval()` call rejected with “independent evidence/selection review not installed.” No environment/configuration discovery is supported by this code. The failure is an absent independent artifact/authority, not a found artifact at an incorrect path.\n\n')
    f.write('Additional authorized home/configuration search inspected '+str(user['filenames_inspected'])+' filenames in '+str(user['directories_inspected'])+' directories. Supplementary .local/share, /etc, /usr/local/etc, /opt, /mnt and /media searches inspected '+str(sum(v['filenames'] for v in extra['roots']))+' filenames. Neither found the required artifact or a CPU/GPU trust configuration. Filename-only scanning avoids reading credential contents; caches/package stores, browser/credential directories and private session/history stores were excluded. Nine inaccessible directories were recorded without bypass. These locations are not claimed verified. No relevant CPU_GPU/MAB approval/trust environment variable was present. The previous repository JSON/archive search remains sealed evidence; it was not redundantly rerun.\n\n')
    f.write('The discovered `docs/CPU_GPU_DRIVER_REVIEW_v1.json` is genuine existing older CMake-additions evidence, SHA-256 `b6a63a7e65827970d6b27e872e738052cd5faf94d88ee711dbccd5f77f90ef2a`, matching the driver-anchor pin. It lacks the current approval schema, selection, session, compiler/linker/build/binary and framework-record context. It cannot legitimately satisfy the missing independent evidence review. Existing tests explicitly mock approval for synthetic bundles; no mock is an external authorization or installed trust root.\n\n')
    f.write('A further targeted search closed the possible generic-filename discovery gap: approval/review/trust/benchmark JSON and public-key filenames in .config, .agents, .codex, .local/share and system configuration were inspected. The non-secret JSON candidates were unrelated plugin fixtures; no project reference was found. Public TLS certificate filenames were recorded without reading them and do not constitute a benchmark approval authority. Credential and private session files remained excluded; inaccessible paths were recorded. GENERIC_CONFIGURATION_SEARCH.json retains the precise scope, candidates and limitations.\n\n')
    f.write('`docs/CPU_GPU_EVIDENCE_ENFORCEMENT_v1.md:22-38` documents the circular dependency of a review digest embedded in a file included in that review’s source digest. Filling in a self-generated hash cannot repair this honestly. A genuinely independent, non-circular protected authority and its exact scoped review are indispensable; none is accessible here. REQUIRED_EXTERNAL_ARTIFACT.json describes the actual accepted fields and context without pretending to be an approval. No source integration is justified in the absence of a real artifact; no guard was changed. Standing user execution authorization is already accepted and was not requested again, but is not represented as an independent signature.\n\n')
    f.write('## Free GPU availability\n\nCurrent installed CLI0.7.4 `colab sessions` and `colab usage` both completed successfully and reported no active sessions, zero assignments, 0.00CU balance and 0.00CU/hour. These outputs, not exit0 alone, establish no available session through this account at observation time. A zero rate without a session does not establish a free future allocation. Actual supported `new` help has no free-only or cost-cap option; prior sealed billing inspection found the earlier T4 assignment metered at1.07CU/hour. No allocation was attempted, avoiding possible unauthorized metered use. No alternate authorized free GPU or browser-control capability is exposed by current tools. This is not a claim that all external free GPU services are unavailable.\n\n')
    f.write('## Dependent checks and study\n\nNo current GPU build, compiler/linker provenance, comparison_input identity, GPU/framework validation, workspace/resource query or worker diagnostic was executed. These require actual supported free GPU access. Untimed correctness also cannot be relabeled as the existing policy’s timing/framework/pilot evidence. The unchanged full matrix remains48 datasets/five modes, 1200 measured calls and240 warm-ups; the earlier actual dry-run is reused, not mistaken for measurements. No run command was invoked and no trial outcome is fabricated. No result/report/presentation update is supported by new GPU measurements.\n\n')
    f.write('## Preservation and changed files\n\n'+str(len(base['historical_results_sha256']))+' pre-existing result files, '+str(len(base['report_sha256']))+' report files, '+str(len(base['project_sha256']))+' project files, '+str(len(base['protected_sha256']))+' production/header/dependency files, '+str(len(base['frozen_sha256']))+' frozen files, '+str(len(base['build_metadata_sha256']))+' build-metadata files and '+str(len(base['executable_sha256']))+' build artifacts match before/after SHA-256 maps. The prior seal itself is unchanged. No additional result files exist outside this exclusive directory. The CUB pin, protocols, source, guards, selection and CPU deliverables remain unchanged.\n\nOnly this new evidence directory was added: recorder/search/finalizer helpers, command logs, search and offline-verification results, baseline, external requirements, gate table and final audits/seal. No source/test/build/documentation changes, commit, push or new cloud resource occurred. Known search exclusions, permission failures and absent Git metadata are retained rather than hidden. No new compiler or runtime warnings exist because nothing was built or executed.\n\n')
    f.write('## Decision\n\n**NO-GO.** The missing genuine independent trust authority/review and missing confirmed-free supported GPU runtime make further valid study execution impossible in the available environment. All independent preparation is reusable and unchanged. No repeated acquisition attempts, self-approval, paid allocation or fabricated provenance was used. No benchmark trials or warm-ups ran.\n')
put(E/'FINALIZER_STATUS.json',dict(preservation=preserved,assertions_passed=True,unexpected_external_additions=[],
    study_launched=False,measured_trials=0,warmups=0,new_tests=0,new_builds=0,new_cloud_assignments=0))
seal = dict(schema_version=1,seal_excludes_itself=True,previous_seal=base['previous_seal'],
            previous_seal_sha256=base['previous_seal_sha256'],preservation=preserved,
            gates=gates,verdict='NO-GO — one or more required validation gates remain open',
            study_launched=False,measured_trials=0,warmups=0,gpu_workloads=0,source_changes=[])
for k,v in base.items():
    if k.endswith('_sha256') and isinstance(v,dict):seal[k]=v
seal['evidence_sha256']={str(p.relative_to(ROOT)):sha(p) for p in E.rglob('*') if p.is_file()}
put(E/'FINAL_INTEGRITY.json',seal)
print('Preservation PASS:',len(historical),'historical result files; all protected/frozen/report/build maps unchanged.')
print('New source changes:0; benchmark trials:0; GPU workloads:0; new cloud assignments:0. NO-GO; external dependencies remain.')
