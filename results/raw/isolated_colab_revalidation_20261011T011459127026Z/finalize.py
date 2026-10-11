"""Read retained isolated-validation evidence, verify hashes, seal additive audit."""
import hashlib,json,shlex,tarfile
from pathlib import Path,PurePosixPath
r=Path.cwd();e=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def save(name,obj):
    with (e/name).open('x') as f:json.dump(obj,f,indent=2,sort_keys=True);f.write('\n')
log=load(e/'isolated_build_validation.json')
assert log['exit_code']==0
text=log['stdout'];assert text.count('ISOLATED_VALIDATION_BEGIN')==text.count('ISOLATED_VALIDATION_END')==1
remote=json.loads(text.split('ISOLATED_VALIDATION_BEGIN')[1].split('ISOLATED_VALIDATION_END')[0])
assert remote['validation_passed'] and remote['result']['validation_passed']
assert sha(e/'downloaded_validation.tar.gz')==remote['archive_sha256']
target=e/'remote_evidence';target.mkdir()
with tarfile.open(e/'downloaded_validation.tar.gz','r:gz') as tar:
    members=tar.getmembers();names=[m.name for m in members]
    assert len(names)==len(set(names))
    for m in members:
        path=PurePosixPath(m.name)
        assert not path.is_absolute() and '..' not in path.parts and path.parts[0]=='validation'
        assert m.isfile() or m.isdir()
    for m in members:
        p=target/m.name
        if m.isdir():p.mkdir(parents=True,exist_ok=True)
        else:
            p.parent.mkdir(parents=True,exist_ok=True)
            with p.open('xb') as f:f.write(tar.extractfile(m).read())
v=target/'validation';manifest=load(v/'EVIDENCE_SHA256.json')
assert all(sha(v/p)==h for p,h in manifest.items())
assert set(manifest)=={str(p.relative_to(v)) for p in v.rglob('*') if p.is_file() and p.name!='EVIDENCE_SHA256.json'}
result=load(v/'RESULT.json');assert result==remote['result']
assert [p['name'] for p in result['records']]==['configure','build','cpu_correctness','gpu_correctness','comparison_describe']
assert all(p['exit_code']==0 for p in result['records'])
assert result['ctest_invocations']==result['timing_trials']==result['benchmarks']==0
assert not result['study_eligible'] and not result['full_study_authorized']
gpu=result['cuda_correctness'];assert (gpu['cases'],gpu['output_checks'],gpu['cub_version'])==(475,1900,300001)
identity=load(e/'SOURCE_IDENTITY.json');assert load(v/'SOURCE_AFTER.json')==identity
assert load(v/'SOURCE_IDENTITY.json')==identity
assert all(sha(r/p)==h for p,h in identity['files_sha256'].items())
save('VALIDATION_CHECKED.json',dict(status='READY',scope='isolated build and narrow correctness validation only',
     remote_archive_sha256=remote['archive_sha256'],remote_evidence_files_verified=len(manifest),
     source_files_verified=len(identity['files_sha256']),gpu_correctness=gpu,cpu_correctness=result['cpu_correctness'],
     production_benchmark_trials=0,prepared_diagnostic_samples=0,study_authorized=False))
b=load(e/'BEFORE.json')
def compare(expected,current=None):
    missing=[];changed=[]
    for p,h in expected.items():
        if not (r/p).is_file():missing.append(p)
        elif sha(r/p)!=h:changed.append(p)
    return dict(count=len(expected),missing=missing,changed=changed,
                unexpected=sorted(set(current)-set(expected)) if current is not None else [])
prior=[str(p.relative_to(r)) for p in (r/'results').rglob('*') if p.is_file() and not p.is_relative_to(e)]
project=[str(p.relative_to(r)) for name in ['AGENTS.md','README.md','CMakeLists.txt','docs','scripts','tests','include','src','cmake','third_party'] for base in [r/name] for p in ([base] if base.is_file() else base.rglob('*')) if p.is_file() and '__pycache__' not in p.parts]
metadata_names={'CTestTestfile.cmake','CTestCustom.cmake','CTestCustom.ctest','CTestConfig.cmake','DartConfiguration.tcl','CMakeCache.txt','build.ninja','Makefile','compile_commands.json'}
metadata=[str(p.relative_to(r)) for p in (r/'build').rglob('*') if p.is_file() and p.name in metadata_names]
preservation=dict(historical_results=compare(b['prior_results_sha256'],prior),project=compare(b['project_sha256'],project),build_metadata=compare(b['build_metadata_sha256'],metadata))
freeze=r/'docs/studies/cpu_gpu_comparison_v1.freeze.json'
assert sha(freeze)=='518ac535473e50fb61dab3a70858bdfe42dfdb43570f649174f44bffe40e1ac6'
preservation['frozen_members']=compare(load(freeze)['files_sha256'])
matrix=load(r/'docs/studies/cpu_gpu_comparison_v1.matrix.json');anchors=dict(matrix['source_at_freeze_sha256'])
review=r/'docs/CPU_GPU_DRIVER_REVIEW_v1.json'
assert sha(review)=='b6a63a7e65827970d6b27e872e738052cd5faf94d88ee711dbccd5f77f90ef2a'
anchors['CMakeLists.txt']=load(review)['current_cmake_sha256']
preservation['protected_anchors']=compare(anchors)
old=load(r/'results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/BEFORE.json')['current_source_sha256']
preservation['production_header_dependency']=compare({p:h for p,h in old.items() if p.startswith(('src/','include/','third_party/')) or p=='CMakeLists.txt'})
preservation['reviewed_source']=compare(load(r/'docs/NON_TIMING_TEST_SELECTION_v1.json')['reviewed_source_sha256'])
assert all(not v['missing'] and not v['changed'] and not v['unexpected'] for v in preservation.values())
save('PRESERVATION.json',preservation)
commands=['# Exact commands and statuses','',
    'Authorization: reviewed-source transfer and isolated build/narrow correctness validation only. No study, performance smoke, warm-up or measured trials.',
    'The local wrapper is `python3 -B '+str(e.relative_to(r))+'/record.py NAME SCOPE TIMEOUT CHILD_ARGV...`; individual JSON files retain full argv/cwd/status/stdout/stderr.',
    'Exclusive baseline creation and evidence-script authoring commands are retained in EARLY_COMMANDS.json (exit0). All inspection commands are individually captured. Git status/revision returned128; the initial source checker returned1 due to seal path conventions, diagnosed and corrected in a new v2 checker before transfer.','']
logs=[]
for p in sorted(e.glob('*.json')):
    obj=load(p)
    if isinstance(obj,dict) and 'argv' in obj and 'exit_code' in obj:
        logs.append((p.name,obj));commands+=['## '+p.name,'','```text',shlex.join(obj['argv']),'```','Exit '+str(obj['exit_code'])+'. '+obj['scope']+'.','']
expected_nonzero={'repository_status.json':128,'git_revision.json':128,'source_review.json':1}
assert all(o['exit_code']==expected_nonzero.get(name,0) for name,o in logs)
commands+=['## Remote build/validation commands','']
for rec in result['records']:
    commands+=['```text',shlex.join(rec['argv']),'```','cwd: '+rec['cwd']+'; exit '+str(rec['exit_code'])+'.','']
commands+=['No CTest was invoked. Tests are existing direct executable targets audited for timing behavior before execution. comparison --describe returns before input parsing, allocation, workspace diagnostics or trial invocation.',
    'Remote control scripts are retained verbatim alongside these logs. They write only the new isolated /content directory, its new evidence archive, and the explicitly uploaded source archive.',
    'Finalization: `python3 -B '+str(e.relative_to(r))+'/finalize.py` (exit 0 when this final seal is present). It validates/extracts new evidence, compares preservation hashes and writes only this new local evidence directory. Polling awaited the recorded CLI commands. apply_patch authored only evidence-control files.']
with (e/'COMMANDS.md').open('x') as f:f.write('\n'.join(commands)+'\n')
warn=result['warnings'];warnings='None detected in retained configure/build stdout/stderr.' if not warn else str(len(warn))+' retained warning diagnostics. Every recorded warning is "style of line directive is a GCC extension", from nvcc-generated host translation units under the existing -Wpedantic flag. See remote_evidence/validation/build.stderr.txt and RESULT.json for every diagnostic. No flags/source were changed or warnings suppressed; build and correctness succeeded despite this toolchain warning.'
bundle=load(e/'BUNDLE.json');desc=result['description']
audit=f'''# Reviewed-source transfer and isolated T4 build/validation

**Status: READY for this isolated build and narrow correctness scope only.** No study authorization, performance trials or full prerequisite eligibility is implied.

## Authorization and source audit

The user's request explicitly authorized both reviewed-source transfer and an isolated build with narrowly scoped validation. Read AGENTS.md, README, roadmap, experiment protocol, latest T4 audit, frozen comparison identities, CMake/CUDA configuration, direct test sources/helpers, reviewed source policy, prerequisite runner and comparison CLI control flow before execution. The broader prerequisite runner was deliberately not used: it would execute additional probes/builds/tests outside this minimum scope. Historical guides describe older pins/status; the actual reviewed source/CMake CUB3.0.1 requirements were authoritative.

`git status --porcelain=v1` and `git rev-parse HEAD` both returned128: no Git repository metadata. No repository was initialized. Exact revision is the153-file SOURCE_IDENTITY.json content manifest, SHA256 `{bundle['source_identity_sha256']}`. Its144 implementation/test/script/dependency entries match the reviewed non-timing source policy; nine additional reviewed project/protocol/identity documents match the prior preserved project baseline. The identical reviewed archive from the previous isolated run was copied additively after verifying its hash and every member against current local source; it was not regenerated or modified. Frozen protocol/matrix/resource hashes and the independently pinned freeze/CMake review identities were verified. CUB3.0.1/300001, CCCL commit f19d875da0d8bfb2e38c109b2b40522b8abbbbc3 is unchanged.

Only that allowlisted bundle was transferred. No result directories, credentials, dotfiles, caches, build artifacts, unrelated data or unreviewed working-tree differences were included. Archive SHA256: `{bundle['archive_sha256']}`. The remote archive independently matched; all154 member paths (153source files plus generated identity manifest) were inspected as regular relative files with no traversal/duplicates before extraction. All153 contents matched before/after extraction and again after validation. Extraction used the verified-absent unique directory `/content/mab_isolated_20261011T011459127026Z/source`; no remote project was overwritten.

## Fresh isolated build

Session alias cpu-gpu-validation, ID gpu-t4-s-kkb-usw4b0-21qggbdn9iask. Fresh management diagnostics observed Tesla T4, UUID GPU-c51b969a-fbb1-a810-8346-93e2f6fc1849, driver580.82.07, GPU15360MiB total/14913MiB free; nvcc13.0.88; CMake3.31.10; G++13.3.0. These snapshots do not reserve resources. Remote ENVIRONMENT.json retains CPU/RAM/disk and whitelisted environment observations without secrets.

Build directory: `{result['build_directory']}` (new, separate from source/history). Release, C++17/CUDA17, host/CUDA release flags -O3 -DNDEBUG, CUDA architecture75, OpenMPON, CUDA/CUDA_SORT/comparisonON, sanitizersOFF, BUILD_TESTINGON. Configuring only registers tests; no CTest discovery or test scheduling occurred. Built exactly requested targets cpu_gpu_comparison, comparison_input, test_cuda_sorting, test_mergesort and their dependency closure, using two build jobs. Production prepared-timing libraries are linked because the worker requires them; linking is not executing diagnostic samples.

Configure and build exited0. Actual configured OpenMP metadata: version {desc['openmp_version']}, flags {desc['openmp_flags']}; requested threads were not a workload in this task. Binary paths/hashes/sizes, compile_commands.json, CMakeCache.txt and generated metadata are retained in remote_evidence/validation/. The built cpu_gpu_comparison successfully emitted --describe metadata (exit0) identifying cpu_gpu_comparison_driver_v1, Release, no sanitizers, CUB300001. --describe returns before any sorting/trial/resource-query path. No normal comparison invocation or --resources was made.

Warnings: {warnings}

## Narrow correctness outcomes

| Direct validation | Observed result | Exit |
|---|---|---|
| test_mergesort | 4015 differential inputs through public/registry/repeated paths; stable-merge fixture passed |0|
| test_cuda_sorting |475 inputs,1900 complete-vector output checks; cub_radix_sort public/registry/repeated/interleaved paths; status ok|0|
| cpu_gpu_comparison --describe | Build/implementation metadata only; no sorting/timing |0|

GPU test protocol cuda_sort_correctness_v2 reports runtime API {gpu['runtime_api_version']}, driver API {gpu['driver_api_version']}, device{gpu['device']}, compute capability{gpu['compute_major']}.{gpu['compute_minor']}, CUB{gpu['cub_version']}. This establishes actual production CUB sorting on the current T4; it is not merely hardware visibility or a version command. Empty/singleton, boundaries, duplicates, negative/extreme values, deterministic distributions and tile-adjacent/non-power-of-two sizes up to65537 are in the unchanged existing correctness test. No CPU fallback was substituted.

Two correctness executables passed; zero failed/skipped among those two. The metadata-only command also passed. No broader CPU regression suite, sanitizer suite, OpenMP actual-team/race tests, prepared timing smoke, standalone workspace/resource diagnostic, pilot or study ran. Those remain unexecuted in this isolated run rather than claimed fresh passes. Production CUB correctness calls naturally query and allocate their required workspace internally; no sizing-only diagnostic or workspace measurements were produced. No performance metrics, benchmark CSV, warm-up batches or measured trials were generated. The comparison worker's full numerical/trial path remains unexercised here by design.

## Evidence and preservation

Downloaded remote archive SHA256 `{remote['archive_sha256']}` matches the remote value. All{len(manifest)} sealed remote evidence files were independently rehashed, with complete membership matching. Configure/build/test stdout/stderr, attempt/exit records, source identities, environment, binary hashes, failure/warning information and plan are under remote_evidence/validation/. Exact local/remote commands and statuses: COMMANDS.md, individual JSON records and EARLY_COMMANDS.json.

All{preservation['historical_results']['count']} pre-existing result files,177 project files,65 local build-metadata files preserved by before/after membership and SHA256 comparison. Rechecked26 protected anchors with the existing independently pinned CMake exception,80 production/header/dependency files,144 reviewed source entries and3 frozen members; zero missing/changed/unexpected entries. Local source/tests/protocols/build metadata and all historical evidence remained untouched. All local additions are confined to this new evidence directory. Remote writes are confined to the new upload, isolated source/build/validation directory and its new archive. No commit, push, deletion or destructive cleanup occurred. The session/source/build are left in place.

No build or correctness failure occurred. Both Git commands returned128 because metadata is absent; no clean-Git or commit identity is claimed. Exact source identity is established by the reviewed content manifest and complete177-file source-area membership/hash comparison. The first source-verifier attempt returned1 because it incorrectly interpreted older repository-relative evidence-seal paths as evidence-relative. Read-only inspection found zero unmatched entries; a separately retained v2 verifier explicitly classified the two existing conventions, checked every digest and exact membership, and passed before any upload. The failed program/log and corrective command are retained. No source digest mismatch was ignored. SOURCE_REVIEW.json records independent rehashing of27 independent-review,35 readiness,27 T4-diagnostic and60 previous-build sealed files. The independent review PASS remains limited to the trusted-tool/quiescent-tree contract; no selector or CTest is used by this run. Hash manifests provide local retained integrity evidence, not external signed attestation or proof against arbitrary transient modifications.

## Remaining gates and next action

Stop after isolated validation. Review this audit and retained evidence, then separately authorize any additional prerequisite/resource validation or study execution. This run did not produce a study-eligible PREREQUISITES.json, establish fresh workspace allocations at the full matrix sizes, validate actual two-worker teams, repeat sanitizers/full regression suites, or measure performance. Availability/compilation/correctness does not authorize or prove the frozen full study. No performance ranking is claimed.
'''
with (e/'FINAL_AUDIT.md').open('x') as f:f.write(audit)
seal=dict(status='READY',scope='isolated reviewed-source build and narrow correctness validation only',study_authorized=False,
    preservation=preservation,source_manifest_sha256=sha(e/'SOURCE_IDENTITY.json'),source_archive_sha256=sha(e/'reviewed_source.tar.gz'),
    remote_archive_sha256=remote['archive_sha256'],remote_files_verified=len(manifest),tests_passed=2,tests_failed=0,tests_skipped=0,
    gpu_cases=475,gpu_output_checks=1900,cpu_merge_cases=4015,ctest_invocations=0,timing_trials=0,benchmarks=0,
    production_adapter_sha256=sha(r/'src/cuda/cub_sort.cu'),cub_pin_sha256=sha(r/'third_party/cub/UPSTREAM.json'),
    evidence_sha256={str(p.relative_to(e)):sha(p) for p in sorted(e.rglob('*')) if p.is_file()},seal_excludes_itself=True)
save('FINAL_INTEGRITY.json',seal)
print(json.dumps(dict(status=seal['status'],gpu_cases=475,gpu_output_checks=1900,cpu_merge_cases=4015,preservation=preservation,warning_count=len(warn),evidence_files=len(seal['evidence_sha256'])),indent=2))
