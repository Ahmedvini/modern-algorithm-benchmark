"""Evidence-only parsing, preservation hashing and audit; no subprocess imports."""
import hashlib
import json
import shlex
from pathlib import Path

root = Path.cwd()
e = Path(__file__).resolve().parent
def read(p):
    return json.loads(Path(p).read_text())
def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name, value):
    with (e / name).open('x') as f:
        json.dump(value, f, indent=2, sort_keys=True)
        f.write('\n')
def parse(name, start, end):
    log = read(e / name)
    assert log['exit_code'] == 0, name
    text = log['stdout']
    assert text.count(start) == text.count(end) == 1, name
    return json.loads(text.split(start, 1)[1].split(end, 1)[0].strip())

d = parse('remote_diagnostic_run.json', 'MAB_DIAGNOSTICS_JSON_BEGIN', 'MAB_DIAGNOSTICS_JSON_END')
t = parse('runtime_files_run.json', 'MAB_RUNTIME_FILES_BEGIN', 'MAB_RUNTIME_FILES_END')
assert d['kind'] == 'colab_session_diagnostics_only' and d['schema_version'] == 1
assert len(d['command_results']) == 9
assert all(c['exit_code'] == 0 for c in d['command_results'])
assert all(d[k] == 0 for k in ['benchmarks', 'builds_run', 'cuda_api_calls', 'cuda_kernels', 'tests_run'])
assert not d['study_authorized'] and not t['cuda_library_loaded'] and not t['cuda_api_executed']
assert d['project_roots'] == [] and d['comparison_executables'] == []
pin = read(root / 'third_party/cub/UPSTREAM.json')
assert pin['reference_release'] == 'v3.0.1' and pin['cub_version'] == 300001
checks = {}
for name, filename in [('cub_version.cuh','version.cuh'), ('device_radix_sort.cuh','device/device_radix_sort.cuh')]:
    actual = d['cuda_metadata_files']['/usr/local/cuda/include/cccl/cub/' + filename]['sha256']
    assert actual == pin['files'][name]['sha256']
    checks[name] = actual
save('REMOTE_DIAGNOSTICS.json', d)
save('RUNTIME_FILES.json', t)
mem = {line.split(':',1)[0]: int(line.split(':',1)[1].split()[0])*1024 for line in d['meminfo'].splitlines()}
gpu = next(c for c in d['command_results'] if '--query-gpu=' in ' '.join(c['argv']))['stdout'].strip().split(', ')
assert gpu[0] == 'Tesla T4'
assessment = dict(status='BLOCKED', session_alias='cpu-gpu-validation',
    session_id='gpu-t4-s-kkb-usw4b0-21qggbdn9iask', gpu=gpu,
    installed_reviewed_headers_sha256=checks, ram_total_bytes=mem['MemTotal'],
    ram_available_bytes=mem['MemAvailable'], disk=d['disk'], logical_cpu_count=d['logical_cpu_count'],
    project_present_in_inspected_scope=False, comparison_executable_present_in_inspected_scope=False,
    cuda_execution_verified=False, runtime_library_loaded=False,
    scope=d['searched_scope'], blockers=['Project source and cpu_gpu_comparison executable absent in inspected remote workspace'],
    limits=['No builds, tests or CUDA execution authorized', 'No remote project frozen-input verification possible without source',
            'Header checks do not verify the entire transitive CCCL tree', 'Resource observations are snapshots, not reservations'])
save('DIAGNOSTIC_ASSESSMENT.json', assessment)

b = read(e / 'BEFORE.json')
def compare(expected, current_paths=None):
    missing=[]; changed=[]
    for path,digest in expected.items():
        p=root/path
        if not p.is_file(): missing.append(path)
        elif sha(p)!=digest: changed.append(path)
    extra=sorted(set(current_paths)-set(expected)) if current_paths is not None else []
    return dict(count=len(expected),missing=missing,changed=changed,unexpected=extra)
historical = [str(p.relative_to(root)) for p in (root/'results').rglob('*') if p.is_file() and not p.is_relative_to(e)]
project = [str(p.relative_to(root)) for name in ['AGENTS.md','README.md','CMakeLists.txt','docs','scripts','tests','include','src','cmake','third_party']
           for base in [root/name] for p in ([base] if base.is_file() else base.rglob('*')) if p.is_file() and '__pycache__' not in p.parts]
metadata_names={'CTestTestfile.cmake','CTestCustom.cmake','CTestCustom.ctest','CTestConfig.cmake','DartConfiguration.tcl','CMakeCache.txt','build.ninja','Makefile','compile_commands.json'}
metadata=[str(p.relative_to(root)) for p in (root/'build').rglob('*') if p.is_file() and p.name in metadata_names]
preservation = dict(historical_results=compare(b['prior_results_sha256'],historical),
                    project=compare(b['project_sha256'],project),build_metadata=compare(b['build_metadata_sha256'],metadata))
freeze = root/'docs/studies/cpu_gpu_comparison_v1.freeze.json'
assert sha(freeze) == '518ac535473e50fb61dab3a70858bdfe42dfdb43570f649174f44bffe40e1ac6'
preservation['frozen_members']=compare(read(freeze)['files_sha256'])
matrix = read(root/'docs/studies/cpu_gpu_comparison_v1.matrix.json')
anchors = dict(matrix['source_at_freeze_sha256'])
review = root/'docs/CPU_GPU_DRIVER_REVIEW_v1.json'
assert sha(review) == 'b6a63a7e65827970d6b27e872e738052cd5faf94d88ee711dbccd5f77f90ef2a'
anchors['CMakeLists.txt']=read(review)['current_cmake_sha256']
preservation['protected_anchors']=compare(anchors)
old = read(root/'results/raw/cpu_gpu_safety_repair_20261010T140524185993Z/BEFORE.json')['current_source_sha256']
production={k:v for k,v in old.items() if k.startswith(('src/','include/','third_party/')) or k=='CMakeLists.txt'}
preservation['production_headers_dependencies']=compare(production)
preservation['reviewed_source']=compare(read(root/'docs/NON_TIMING_TEST_SELECTION_v1.json')['reviewed_source_sha256'])
assert sha(root/'src/cuda/cub_sort.cu')=='b6d7f37c7494587fc6e4a676c00c166dc322d31cce96710811e3a4cb9cd8b9cb'
assert sha(root/'third_party/cub/UPSTREAM.json')=='477b1ee70b0a9113c9f98b263c19a31d05ccee54f45ce8476aec4cc98965ced1'
assert all(not v['missing'] and not v['changed'] and not v['unexpected'] for v in preservation.values()), preservation
save('PRESERVATION.json',preservation)

logs=[]
for p in sorted(e.glob('*.json')):
    try: v=read(p)
    except json.JSONDecodeError:
        assert p.name=='VERIFIED_BEFORE.json'
        continue
    if isinstance(v,dict) and 'argv' in v and 'exit_code' in v: logs.append((p.name,v))
assert all(v['exit_code']==0 for _,v in logs)
lines=['# Commands and observed statuses', '', 'No CTest discovery/tests, configure/build, CUDA API/kernel, benchmark, warm-up, measured trial or full study was executed.',
       'The remote programs use metadata/file reads and management/version commands only. Full command bodies are retained in the two diagnostic .py files.', '',
       'Local capture wrapper for each record below: `python3 -B '+str(e.relative_to(root))+'/record.py NAME SCOPE CHILD_ARGV...`.',
       'Each JSON record contains exact child argv, cwd, stdout/stderr and status. Capture timestamps are collection timestamps (the helper assigns started_utc after completion).', '']
for name,v in logs:
    lines += ['## '+name, '', '```text', shlex.join(v['argv']), '```', 'Exit: '+str(v['exit_code'])+'. Scope: '+v['scope']+'.', '']
lines += ['## Remote inner commands (all exit 0)', '']
for c in d['command_results']: lines += ['- `'+shlex.join(c['argv'])+'`: '+str(c['exit_code'])+' (version, OS, NVML management or linker-cache metadata).']
lines += ['', '## Evidence authoring and direct reads', '',
    'The initial `pwd`, `cat AGENTS.md`, and cat of the readiness FINAL_AUDIT.md, COMMANDS.md, FINAL_INTEGRITY.json and docs/CUDA_EXECUTION_GUIDE_v1.md completed with shell exit 0.',
    'The exclusive baseline creation used `python3 -B -` (exit 0); its complete shell program is retained in EARLY_COMMANDS.json. Only this evidence directory was created.',
    'Subsequent `pwd` / `ls` of this evidence directory, stdlib Python JSON/key/output inspections, and cat of the prior readiness audit, local CUB pin and record.py all completed with exit 0. No project code was imported.',
    'Source authoring used apply_patch for record.py, both diagnostic programs and this finalizer; all additions are inside this new evidence directory.',
    'Finalization command: `python3 -B '+str(e.relative_to(root))+'/finalize_evidence.py` (exit 0 when FINAL_INTEGRITY.json exists; assertions precede the seal). It parses retained logs, hashes files and writes new evidence only.',
    'Polling write_stdin waited on those same diagnostic/status commands; it did not launch any extra workload.', '',
    'Retained evidence-format issue: VERIFIED_BEFORE.json had a literal trailing backslash-n and was not strict JSON. The correction command preserved it and created VERIFIED_BEFORE_V2.json; all hash checks passed. No environment or validation failure was suppressed.']
with (e/'COMMANDS.md').open('x') as f: f.write('\n'.join(lines)+'\n')
audit=f'''# Colab T4 setup and diagnostic validation

**Status: BLOCKED.** T4 session creation and non-benchmark environment diagnostics succeeded. The project source and comparison executable are absent in the inspected remote workspace. No build or study was authorized or launched.

## Session and method

Read AGENTS.md, the latest readiness audit/commands/integrity, and the historical cloud guide before setup. Installed CLI 0.7.4 syntax was confirmed using `colab new --help`, `colab exec --help` and `colab readme`. Initial `colab sessions` found no active session; `colab new --session cpu-gpu-validation --gpu T4` exited 0 and reported READY. Status and server inventory independently identify session `gpu-t4-s-kkb-usw4b0-21qggbdn9iask`, alias `cpu-gpu-validation`, T4 Standard GPU IDLE. Final status is retained in session_status_final.json. No authentication or account interaction was required; no credentials were read/requested or printed. CLI output capture redacts URLs and credential-shaped fields.

Only two read-only Python diagnostics were sent via `colab exec --file`. No project archive was uploaded, source extracted, package installed, driver modified, or runtime library loaded. CLI exit statuses, complete JSON markers and all nine inner command exit statuses were checked. Exact commands/logs are in [COMMANDS.md](COMMANDS.md), remote_diagnostic_run.json and runtime_files_run.json. The historical v1 guide's old implementation-status statements were not treated as current evidence.

## Fresh observations

Observed {d['observed_utc']}; these are snapshots, not future reservations.

| Item | Observed |
|---|---|
| OS / architecture | Linux 6.6.122+, x86_64, glibc 2.39 |
| GPU | Tesla T4, {gpu[1]} |
| Driver | 580.82.07; /proc driver metadata and /dev/nvidiactl, /dev/nvidia0 present |
| GPU memory | 15,360 MiB total; 14,913 MiB free in explicit NVML query |
| nvcc | CUDA toolkit 13.0, compiler V13.0.88 |
| Runtime files | libcudart.so.13.0.96; runtime/driver header macros 13000 |
| CMake / G++ | 3.31.10 / Ubuntu GCC 13.3.0 |
| Python | 3.13.15 |
| Package metadata | NumPy 2.1.3; Matplotlib 3.10.0; pip 24.1.2 |
| CPU | 2 logical CPUs; affinity [0,1] |
| RAM | {mem['MemTotal']:,} bytes total; {mem['MemAvailable']:,} bytes MemAvailable |
| /content disk | {d['disk']['free_bytes']:,} bytes free; {d['disk']['total_bytes']:,} bytes total |
| cgroup | cpu.max=max 100000; memory.max=max; memory.current=2,792,468,480 bytes |
| Load | 0.0791 / 0.1196 / 0.1074 |

No running compute process was listed at observation. GPU 37 C, P8, SM 300 MHz, memory 405 MHz, power limit 70 W; frequency, temperature, background activity and scheduling were not controlled. The whitelisted CUDA/OMP settings were unset. No setting was changed. RAM/disk availability exceeds the frozen 1 GiB observation thresholds; this does not validate allocations, actual two-worker OpenMP teams, resource limits at future execution or study readiness.

The nvidia-smi CUDA banner is driver compatibility metadata. Runtime library/header presence is not a successful CUDA runtime call or kernel execution. No compute capability query or CUDA execution probe ran. Package presence/version metadata is not compatibility testing; Python differs from earlier cloud records. No required dependency was repaired automatically.

## Source identity and blockers

Bounded inspection scope: {d['searched_scope']}. No project root (CMakeLists.txt plus scripts/cpu_gpu_protocol.py) or cpu_gpu_comparison executable was found there. This does not prove absence at all remote paths. Remote frozen project-input hashes cannot be checked without those files. The source/executable are missing prerequisites; no existing build was declared ready.

Installed CUB version and DeviceRadixSort headers match the local reviewed CUB 3.0.1 / 300001 hashes exactly; see DIAGNOSTIC_ASSESSMENT.json. Toolkit path aliases are not separate independent installations. This verifies the two reviewed headers, not the full transitive CCCL tree or linked implementation. Local production adapter, CUB pin, freeze identity and three frozen members remain unchanged.

Explicitly unexecuted: all tests and CTest discovery, configure/build, actual OpenMP-team checks, CUDA runtime/kernel/correctness workloads, CUB workspace queries/allocations, benchmarks, warm-ups, measured trials, pilot/full study and 100M runs. Zero such executions were initiated. The session remains available as last observed; ephemeral-session lifetime is not guaranteed. No PREREQUISITES.json eligible for study launch was generated.

## Preservation and evidence

Direct before/after membership and SHA-256 comparison: all {preservation['historical_results']['count']:,} pre-existing result files, {preservation['project']['count']} project files, {preservation['build_metadata']['count']} build-metadata files unchanged, no missing/modified/unexpected old-area files. Rechecked {preservation['protected_anchors']['count']} protected anchors with the existing pinned CMake review exception, {preservation['production_headers_dependencies']['count']} production/header/dependency files, {preservation['reviewed_source']['count']} reviewed source entries, and three frozen members. No differences. See BEFORE.json, PRESERVATION.json and FINAL_INTEGRITY.json. Every addition is confined to this uniquely named evidence directory. Historical evidence was not regenerated or overwritten.

An evidence-only formatting defect in VERIFIED_BEFORE.json (literal trailing backslash-n) is retained; VERIFIED_BEFORE_V2.json is the valid correction and has the same successful hash-check results. The correction command is preserved. Capture helper timestamps are collection timestamps despite the started_utc field name. Hash preservation is a local comparison, not external attestation or proof against arbitrary transient changes.

## Next permitted action

Stop here. Separately authorize transfer of the reviewed source and a fresh isolated build/validation on this T4, if desired. This task authorizes no build, test, CUDA workload or study execution. Source availability, executable identity and actual execution prerequisites must be established in that later scope; resource availability alone never authorizes the study.
'''
with (e/'FINAL_AUDIT.md').open('x') as f: f.write(audit)
seal=dict(status='BLOCKED', preservation=preservation,
          production_adapter_sha256=sha(root/'src/cuda/cub_sort.cu'),cub_pin_sha256=sha(root/'third_party/cub/UPSTREAM.json'),
          freeze_sha256=sha(freeze), study_authorized=False,tests_run=0,ctest_discoveries=0,builds_run=0,
          cuda_api_calls=0,cuda_kernels=0,benchmarks=0,session_created=True,
          evidence_sha256={str(p.relative_to(e)):sha(p) for p in sorted(e.rglob('*')) if p.is_file()},
          seal_excludes_itself=True)
save('FINAL_INTEGRITY.json',seal)
print(json.dumps({'status':seal['status'],'preservation':preservation,'sealed_files':len(seal['evidence_sha256'])},indent=2))
