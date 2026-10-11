"""Offline preservation and blocker audit; no tests, builds or GPU commands."""
import hashlib
import json
from pathlib import Path
import sys

E = Path(__file__).resolve().parent
ROOT = E.parents[2]
sys.path.insert(0, str(ROOT/'scripts'))
from cpu_gpu_protocol import source_manifest, load_protocol, canonical
from non_timing_tests import load_manifest
from cpu_gpu_validation_policy import verify_current_sources


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def read(path): return json.loads(Path(path).read_text())
def write(path,value):
    with path.open('x') as stream:
        json.dump(value,stream,indent=2,sort_keys=True,allow_nan=False);stream.write('\n')


def main():
    base=read(E/'BASELINE.json');preserved={}
    for kind in ['results_sha256','report_sha256','project_sha256','protected_sha256',
                 'frozen_sha256','build_metadata_sha256','executable_sha256']:
        missing=[];changed=[]
        for name,digest in base[kind].items():
            p=ROOT/name
            if not p.is_file():missing.append(name)
            elif sha(p)!=digest:changed.append(name)
        preserved[kind]=dict(files=len(base[kind]),missing=missing,changed=changed)
        if missing or changed:
            write(E/'PRESERVATION_FAILURE.json',preserved)
            raise ValueError('Preservation failure: '+kind)
    assert sha(ROOT/base['previous_seal'])==base['previous_seal_sha256']
    verify_current_sources();selection=load_manifest();model=load_protocol()
    source=source_manifest();bundle=read(E/'SOURCE_BUNDLE.json')
    assert source==bundle['source_sha256']
    assert sha(ROOT/bundle['archive'])==bundle['archive_sha256']
    assert len(read(E/'FROZEN_ORDER.json'))==1440
    assert read(E/'DRY_RUN.json')['expected']==model['study']['expected']
    observations=read(E/'OFFLINE_GATE_RESULTS.json')
    assert observations['approval']['accepted'] is False and observations['approval']['file_exists'] is False
    assert observations['approval']['trusted_pin'] is None
    reused=read(E/'REUSED_CPU_EVIDENCE.json')
    assert reused['source_identity_matched'] and reused['artifacts_matched']
    assert all(v['groups_passed']==21 and not v['reexecuted'] for v in reused['results'].values())
    search=read(E/'APPROVAL_SEARCH.json')
    assert not search['actual_approval_candidates'] and all(not a.get('approval_members') for a in search['archives'])
    assert not read(E/'ADDITIONAL_ARCHIVE_SEARCH.json')['approval_members']
    records=[(p,read(p)) for p in sorted(E.glob('command_*.json'))]
    gate_table=[
        dict(gate='Protocol/frozen/CUB/production guards',status='PASS',evidence=['OFFLINE_GATE_RESULTS.json','BASELINE.json']),
        dict(gate='All prior CPU/report/result preservation',status='PASS',evidence=['FINAL_INTEGRITY.json']),
        dict(gate='Current source/local correctness selection',status='PASS',evidence=['SOURCE_BUNDLE.json','OFFLINE_GATE_RESULTS.json']),
        dict(gate='CPU Release/ASan-UBSan correctness evidence',status='PASS (reused, not rerun)',evidence=['REUSED_CPU_EVIDENCE.json']),
        dict(gate='Independent evidence/selection trust authority',status='BLOCKED',evidence=['APPROVAL_SEARCH.json','ADDITIONAL_ARCHIVE_SEARCH.json','OFFLINE_GATE_RESULTS.json']),
        dict(gate='Available confirmed-free GPU session',status='BLOCKED',evidence=['command_005.json','command_006.json','command_011.json']),
        dict(gate='Intended current GPU compiler/linker/build/binary provenance',status='BLOCKED',evidence=['EXTERNAL_DEPENDENCIES.md']),
        dict(gate='Identity-matched GPU correctness and required full framework coverage',status='BLOCKED',evidence=['EXTERNAL_DEPENDENCIES.md']),
        dict(gate='Current GPU all-size resources and worker readiness',status='BLOCKED',evidence=['EXTERNAL_DEPENDENCIES.md']),
        dict(gate='Frozen full-study eligibility/launch/post-run audit',status='BLOCKED; NOT LAUNCHED',evidence=['DRY_RUN.json','FROZEN_ORDER.json'])]
    write(E/'GATES.json',gate_table)
    with (E/'COMMANDS.md').open('x') as stream:
        stream.write('# Executed commands and actual status\n\n'
            'All recorded commands are inspection, offline validation, source-only packaging or the reviewed launcher dry-run. '
            'No test, build, GPU workload, warm-up, measured trial or study executed. Raw JSON retains full stdout/stderr, '
            'timestamps and cwd. A final shell exit0 does not hide failed earlier subcommands; exceptions are listed below.\n\n')
        for p,d in records:
            stream.write('## '+p.name+'\n\n'+d['purpose']+'\n\nExit: '+str(d['exit_code'])+
                '; UTC: '+d['started_utc']+'; cwd: `'+d['working_directory']+'`.\n\n```sh\n'+d['command']+'\n```\n\n'
                'Full output: ['+p.name+']('+p.name+').\n\n')
        stream.write('## Startup, non-terminal calls and final seal\n\n'
            'Startup read `pwd`, `AGENTS.md`, the prior completion `FINAL_AUDIT.md` and `COMMANDS.md`, and printed prior integrity-map keys/counts; shell exit0. '
            'The bootstrap verified every prior seal digest map, captured all existing result/report/project/build/executable hashes, '
            'then created this exclusive directory and copied the recorder; exit0. STARTUP.md retains the scope; full bootstrap stdout was observed rather than saved.\n\n'
            'Web search/open and available-tool metadata inspection are recorded in WEB_SOURCES.json; shell exit codes do not apply. '
            'Edits used apply_patch only within this evidence directory. An orchestration-store lookup caused `python3 -B undefined/record.py` '
            'to fail with exit2 before the intended read-only command started; its diagnostics are retained in WEB_SOURCES.json. '
            'The corrected command is command_011.json. No project/credential/config files were changed.\n\n'
            'Command_001 contains `git status --short --branch` exit128 (no Git metadata), although the compound shell ends0. '
            'Command_003 contains unsupported `colab --version` and `colab connect --help`, each exit2; supported version/help reads subsequently succeeded. '
            'Command_012 contains a failed `cat cmake/cuda_sort.cmake` (file absent), although its compound shell ends0; '
            'the actual `cmake/cuda.cmake` was then inspected in command_017.json. '
            'Approval refusal in command_009 was caught and recorded explicitly: wrapper exit0 means inspection completed, not approval accepted.\n\n'
            'Final offline seal command: `python3 -B '+str((E/'finalize.py').relative_to(ROOT))+'`. '
            'It executes no subprocesses or workloads. Successful assertions are retained in FINALIZER_STATUS.json; actual exit0 is observed in the terminal.\n')
    with (E/'FINAL_AUDIT.md').open('x') as stream:
        stream.write('# Autonomous final blocker resolution\n\n'
            '**NO-GO — one or more required validation gates remain open. Full study NOT launched or completed.**\n\n'
            'User standing execution authorization is present and was not requested again. This attempt searched for usable independent '
            'approval and confirmed-free compute, completed independent offline preparation and preserved all CPU deliverables. '
            'It did not manufacture authority, bypass guards, allocate a runtime or perform measurements.\n\n'
            '## Directly evidenced gate table\n\n|Gate|Status|Evidence|\n|---|---|---|\n')
        for gate in gate_table:
            stream.write('|'+gate['gate']+'|'+gate['status']+'|'+', '.join('['+x+']('+x+')' for x in gate['evidence'])+'|\n')
        stream.write('\n## Approval investigation\n\n'
            '`scripts/cpu_gpu_evidence.py:19–27` fixes the review path and has `TRUSTED_APPROVAL_SHA256=None`. '
            'The production `approval()` rejected with “independent evidence/selection review not installed”; '
            'OFFLINE_GATE_RESULTS.json records the refusal. No alternate environment/CLI trust-root configuration exists in that path. '
            'Source inspection traced launcher prerequisites through cpu_gpu_framework_compatibility.validate_evidence to validate_full/approval; '
            'the analyzer uses the same enforcement. No legacy bypass was used.\n\n'
            'The repository search examined'+str(search['json_files_inspected'])+' JSON files and'+str(len(search['archives']))+
            ' raw archives, plus the original results/evidence/cloud_validation_evidence.tar.gz. No matching actual approved record or '
            'archive member was found. One malformed JSON is an explicitly named historical negative fixture, preserved unchanged. '
            'The one similarly named cloud_evidence_review.json is older runtime discovery, not the required approval schema or current build context. '
            'Search scope is the repository/retained archives, not a claim about every possible external filesystem or account.\n\n'
            '`docs/CPU_GPU_EVIDENCE_ENFORCEMENT_v1.md:22–38` already identifies the circular digest dependency and the need for a genuinely '
            'independent non-circular authority. Current user execution permission is recorded truthfully in AUTHORIZATION_CONTEXT.json, '
            'with no signature/trust root/independent-review claim. It cannot satisfy that technical attestation. There is no existing valid '
            'record to integrate, so no source/policy modification is justified merely to obtain a pass. '
            '`selection_manifest` accepts approved v3/v4 snapshots with exact current source; current v5 remains local-correctness-only, '
            'and inactive v4 is not promoted. Precise required context/record/build bindings are documented in EXTERNAL_DEPENDENCIES.md.\n\n'
            '## Free GPU investigation\n\n'
            'Installed CLI version0.7.4 was confirmed using the actual `colab version` command. '
            '`colab sessions` and `colab usage` both exited0 and reported no active sessions,0 assignments,0.00CU balance and0.00CU/hour. '
            'These observations, not exit codes alone, establish that no runtime was exposed at check time. '
            'Zero balance/rate with no assignment does not prove a new assignment would be free. The previously retained T4 request '
            'reported1.07CU/hour; its creation/release evidence was inspected without repeating allocation. '
            'The installed help/public client code has no free-only price latch or supported attach command. '
            'No `new`, `run`, SSH, remote exec, upload, purchase or account configuration was attempted here.\n\n'
            'Primary provider/CLI documentation was inspected and linked in WEB_SOURCES.json. '
            'Colab offers browser-based free notebook resources subject to availability; that is not proof this environment can obtain a free T4. '
            'An upstream attachment feature discussion is not an installed supported command or a verified free assignment. '
            'No browser-control or alternate authorized GPU capability was exposed by tool metadata. '
            'No unsupported attachment code, credentials or account-workaround was used. '
            'A free supported-access runtime remains a genuine external capability requirement.\n\n'
            '## Independently actionable preparation completed\n\n'
            'The exact current source/frozen/local-selection and approved compatible production anchors validate offline. '
            'Retained CPU Release and sanitizer logs were parsed with the production CTest coverage validator, bound to their '
            'selection digest and unchanged source/build artifacts:21/21 each, no tests rerun. '
            'The two internal GPU methods skipped in each historical CPU-only run remain skips. '
            'Those logs do not substitute for same-session GPU/full-study provenance.\n\n'
            'SOURCE_BUNDLE.json records a source-only archive of'+str(bundle['bundled_files'])+' files ('+str(bundle['source_files'])+
            ' source entries),'+str(bundle['archive_bytes'])+' bytes, SHA-256 `'+bundle['archive_sha256']+'`. '
            'Every member was independently read back and compared with the exact current bytes. No credentials, builds or historical result '
            'data are included; installed CUDA/CUB toolkit headers are not fabricated or bundled. The archive remains local, not uploaded.\n\n'
            'The existing runner `--dry-run` exited0 and produced48 command configurations. '
            'DRY_RUN.json and FROZEN_ORDER.json retain its exact settings/order:48 datasets, five modes, '
            '1200 measured/240 warm-up invocations,960 primary measured rows and240 prepared measured rows. '
            'Dataset/build/runtime fields not yet observed are placeholders. No executable, input generator, GPU query or timing function '
            'was invoked by this dry-run. The final study execution command was not called.\n\n'
            'The compatibility policy still requires the actual14-method timing-framework evidence from the intended binary '
            '(cpu_gpu_framework_compatibility.py:117–137); an untimed prepared correctness diagnostic cannot substitute. '
            'No such current evidence or genuine GPU compiler/linker/comparison_input identity exists. '
            'GPU build, framework/resource/worker validation and post-run audits are explicitly unexecuted, not skipped-as-passed.\n\n'
            '## Preservation, commands and failures\n\n'
            'All'+str(len(base['results_sha256']))+' pre-existing result files and all'+str(len(base['report_sha256']))+
            ' report files match their baseline paths and SHA-256 contents. '+str(len(base['project_sha256']))+
            ' existing project files,'+str(len(base['protected_sha256']))+' production/header/vendor files,'+
            str(len(base['frozen_sha256']))+' frozen assets,'+str(len(base['build_metadata_sha256']))+
            ' build-metadata files and'+str(len(base['executable_sha256']))+' prior executable/build-artifact identities also match. '
            'The previous final seal itself is unchanged. Protected compatible anchors were additionally checked using the existing policy. '
            'The original12,575 historical files are a preserved subset of this larger13,457-file starting baseline. '
            'No source, tests, documentation, manifest, pin, frozen inputs, CPU outputs or existing evidence changed. '
            'All additions are confined to this new evidence directory.\n\n'
            'COMMANDS.md and command JSON retain commands, cwd, timestamps, stdout/stderr and actual exits. '
            'Unsupported CLI help spellings, absent Git metadata, an absent read-only cmake path and the recorder-path failure are retained '
            'explicitly; none started a workload. The corrected inspections succeeded. No configuration/build/test/sanitizer/CTest discovery '
            'was executed. No compiler warning count is newly generated; historical nvcc/GCC diagnostics remain unchanged. '
            'No credentials, authorization codes, tokens or cookies were accessed or logged. No commit/push or cloud allocation occurred.\n\n'
            '## Final decision\n\n'
            '**NO-GO.** The two independent external blockers are a usable independently protected evidence authority/review '
            'and confirmed free supported GPU access. Their absence also blocks current GPU build, framework and resource provenance. '
            'The available user authorization already permits proceeding once genuine gates pass; no redundant approval is requested. '
            'No honest source integration can replace missing authority or hardware. The exact source package and frozen run plan are ready, '
            'but the full frozen study has0 attempted/completed trials in this task (all1200 measured and240 warm-up calls remain unexecuted). '
            'There are no partial GPU results to analyze or grounds to update performance conclusions/report/slides.\n')
    write(E/'FINALIZER_STATUS.json',dict(command=['python3','-B',str((E/'finalize.py').relative_to(ROOT))],
        assertions_passed=True,preservation=preserved,workloads_executed=0,
        note='Actual finalizer exit is observed in terminal; no subprocess executed by this script.'))
    evidence={str(p.relative_to(ROOT)):sha(p) for p in E.rglob('*') if p.is_file()}
    write(E/'FINAL_INTEGRITY.json',dict(schema_version=1,seal_excludes_itself=True,
        seal_command=['python3','-B',str((E/'finalize.py').relative_to(ROOT))],
        previous_seal=base['previous_seal'],previous_seal_sha256=base['previous_seal_sha256'],
        preservation=preserved,historical_results_sha256=base['results_sha256'],report_sha256=base['report_sha256'],
        project_sha256=base['project_sha256'],protected_sha256=base['protected_sha256'],frozen_sha256=base['frozen_sha256'],
        build_metadata_sha256=base['build_metadata_sha256'],executable_sha256=base['executable_sha256'],
        evidence_sha256=evidence,source_sha256=source,source_identity=hashlib.sha256(canonical(source)).hexdigest(),
        study_launched=False,measured_trials_executed=0,warmups_executed=0,gpu_workloads_executed=0,
        new_tests_executed=0,new_builds_executed=0,new_cloud_assignments=0,source_changes=[],gates=gate_table,
        verdict='NO-GO — one or more required validation gates remain open'))
    print('Final preservation verified:',len(base['results_sha256']),'prior results,',len(base['report_sha256']),
          'report files,',len(base['project_sha256']),'project files,',len(base['build_metadata_sha256']),'build metadata files; all unchanged.')
    print('Source-only preparation and dry-run complete; zero study/GPU/test/build/cloud allocation execution. External gates remain blocked.')


if __name__=='__main__':main()
