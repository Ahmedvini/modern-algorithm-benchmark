import difflib, hashlib, json, re, shlex
from pathlib import Path
root=Path.cwd()
p=json.loads(Path('build/phase8_gate1_paths.json').read_text()); e=Path(p['evidence'])
h=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
records={f.stem:json.loads(f.read_text()) for f in sorted((e/'commands').glob('*.json')) if not f.stem.endswith('_started')}
assert len(records)==12
assert all(r['exit_code']==(2 if n=='local_preflight' else 0) for n,r in records.items())
def suite(name):
 r=records[name]; assert '100% tests passed, 0 tests failed out of 25' in r['stdout']
 assert 'Ran 22 tests' in r['stdout']
 return dict(exit_code=0,passed_groups=25,failed_groups=0,seconds=float(re.search(r'Total Test time \(real\) =\s*([\d.]+) sec',r['stdout']).group(1)))
release=suite('release_ctest');sanitize=suite('sanitize_ctest')
assert records['archive_cpu_registry']['stdout'].splitlines()==['std_sort','quick_sort','pdq_sort','tim_sort','merge_sort','radix_sort']
warnings=[line for n,r in records.items() if n.endswith(('build','configure')) for line in (r['stdout']+'\n'+r['stderr']).splitlines() if re.search('warning:',line,re.I)]
assert not warnings,warnings
readiness=json.loads((e/'local_preflight/report.json').read_text()); assert readiness['classification']['state']=='gpu_driver_unavailable'
before=json.loads((e/'source_before.json').read_text());prior=json.loads((e/'prior_artifacts_sha256.json').read_text())
allowed={'README.md','docs/ROADMAP.md','docs/ALGORITHMS.md','docs/BENCHMARKING.md','docs/EXPERIMENT_PROTOCOL.md','docs/AUDIT.md'}
assert all(h(root/f)==v for f,v in prior.items())
assert all(h(root/f)==v for f,v in before.items())
assert h(Path(p['archive']))==p['archive_sha256']

def save(name,text):
 with (e/name).open('x') as f:f.write(text)
def save_json(name,value):save(name,json.dumps(value,indent=2,sort_keys=True)+'\n')
def append(name,text):
 with Path(name).open('a') as f:f.write(text)
command_md='# Exact local validation commands\n\nNo command below ran in Colab/cloud. JSON records retain argv/cwd, timestamps, stdout/stderr and status.\n\n'
for name,r in sorted(records.items(),key=lambda x:x[1]['started_utc']):
 command_md+='```sh\n'+shlex.join(r['argv'])+'\n```\n\nExit '+str(r['exit_code'])+'; [record](commands/'+name+'.json).\n\n'
save('COMMANDS.md',command_md);save_json('commands_index.json',records)
brief=f'''
## Cloud GPU follow-up — Gate 1 blocked (requested Phase 8)

No cloud GPU runtime or remote execution endpoint is connected to this session.
The audited Phase 7 archive and all 126 source hashes were verified locally;
its CUDA-OFF CPU fallback built and listed all six sorters. This does not validate
Colab/cloud execution. Fresh local preflight exited 2 (gpu_driver_unavailable):
RTX 3050 Ti Mobile PCI evidence, but no driver binding/module/device nodes,
nvidia-smi, nvcc or discoverable CUDA libraries. Compute capability and CUDA
versions remain unknown. CUDA build/enumeration/kernel checks were skipped.

Fresh CPU Release and ASan/UBSan passed 25/25 groups each, with leak detection
on and 22 readiness/isolation methods passing per suite. No CUB protocol/sorter,
GPU correctness test, GPU smoke or full GPU study was started. All {len(prior):,}
earlier result artifacts remain unchanged. No installation/system change.
[Gate audit]({e}/FINAL_AUDIT.md) and
[local preflight]({e}/local_preflight/report.json) retain evidence.
Next GPU step: allocate and connect a supported NVIDIA cloud development runtime,
verify the archive and run the existing guide/preflight there. Require actual
enumeration and checked kernel before Gate 2. This follow-up remains blocked;
original roadmap Phase 8 learned-index/AlphaDev retains its pending status.
'''
append('README.md',brief)
append('docs/ROADMAP.md',brief.replace(f']({e}/',f'](../{e}/'))
append('docs/ALGORITHMS.md',f'''
## CUDA sorting availability

No CUB sorter is implemented or registered. The cloud GPU follow-up stopped at
Gate 1: no connected runtime/endpoint and unavailable local driver/toolkit.
CPU implementations/defaults are unchanged; the readiness .cu target remains
uncompiled/unrun locally. No GPU correctness/performance claim is supported.
[Gate evidence](../{e}/FINAL_AUDIT.md).
''')
append('docs/BENCHMARKING.md',f'''
## Cloud GPU benchmark gate

Gate 1 of the cloud GPU follow-up is blocked; fresh local preflight exits 2
(gpu_driver_unavailable), and no cloud runtime/endpoint is connected. No CUB
benchmark target, GPU timing schema, H2D/device/D2H/end-to-end observations,
GPU smoke or full study exists. CPU schemas/results remain unchanged. Follow
[the cloud guide](CUDA_EXECUTION_GUIDE_v1.md), verify the archive and require
actual enumeration/kernel success before defining a new sorting protocol.
[Gate evidence](../{e}/FINAL_AUDIT.md).
''')
append('docs/EXPERIMENT_PROTOCOL.md',f'''
## Cloud GPU follow-up gate

The requested cloud GPU follow-up is blocked at environment Gate 1. No GPU
sorting protocol or experiment was implemented: Gate 2 requires actual cloud
device enumeration and a checked kernel. Existing frozen protocols and studies
remain unchanged. CPU regression checks are not cloud validation.
[Gate evidence](../{e}/FINAL_AUDIT.md).
''')
audit=f'''
## Cloud GPU follow-up — Gate 1 blocked (user-requested Phase 8)

This follows the GPU milestone; it does not replace original roadmap Phase 8
learned-index/AlphaDev. Inspected AGENTS.md, roadmap/audit/README, cloud guide,
experiment protocol, CMake and Phase 7 final audit/source manifest/archive.
Workspace writable via anonymous temporary-file write; no Git metadata or Git
initialization. All 126 starting source hashes matched the Phase 7 manifest.
Before new evidence, all {len(prior):,} raw/processed/figure files were hashed.

**Gate 1 did not pass.** No cloud GPU execution tool or remote runtime endpoint
is connected/provided. Available shell is local Linux. Colab/Kaggle/SSH markers
and gcloud/aws/jupyter were absent. SSH client presence is not remote access;
marker/tool absence alone cannot prove no remote GPU exists. No credentials,
SSH configuration or provider accounts were inspected. No cloud allocation,
remote execution, installation, driver/system change or paid provisioning was
attempted. inspection.json records access scope without secret values.

Archive verification exited 0: SHA256
{p['archive_sha256']},
127 members and 126 matching source files. Extracted into a new build-only path;
original archive unchanged. The archived preflight ran **locally**, exited 2,
classified gpu_driver_unavailable. Observed Linux 6.18.7-76061807-generic/x86_64,
CMake 3.28.3 and host GNU 13.3.0. PCI shows GA107M / GeForce RTX 3050 Ti Mobile
at 0000:01:00.0, with no bound driver/module/device nodes/version file, nvidia-smi,
nvcc, discoverable libcuda/libcudart or toolkit files. Runtime device count,
compute capability and driver/runtime/toolkit versions remain unknown. CMake
CUDA_STANDARD help success does not establish compiler support. CUDA configure,
build, enumeration/kernel checks were skipped, not passed. This is unavailable
readiness, not a CPU failure or diagnosis of broken hardware.

Archived CPU fallback configure/build/registry exited 0/0/0, CUDA/OpenMP/testing
OFF, all six original sorters listed. Testing OFF means no fallback CTest claim.
Fresh current Release configure/build/CTest and Debug ASan/UBSan configure/build/
CTest exited 0/0/0 each. Release **25/25** groups passed in {release['seconds']:.2f}s;
ASan/UBSan **25/25** in {sanitize['seconds']:.2f}s. Leak detection remained enabled;
no ptrace limitation or detect_leaks=0 retry. All 22 readiness/build-isolation
methods passed per suite, including real default/explicit CUDA-OFF and mocked
states; mocks are not GPU evidence. Existing sorting/search/structure/OpenMP
checks passed unchanged. Captured configure/build output has no compiler warnings.
These are fresh invocations using existing CPU build directories; archive fallback
used a new build directory. CPU environment capture exited 0; its older 'GPU not
probed' field is distinct from the fresh preflight.

Twelve validation command records: archive verification 0; local preflight 2
(expected unavailable); fallback configure/build/registry 0/0/0; Release configure/
build/CTest 0/0/0; sanitizer configure/build/CTest 0/0/0; environment capture 0.
Exact argv/cwd/status/timestamps/stdout/stderr: commands/*.json, commands_index.json
and COMMANDS.md under {e}.
One editing-helper generation command exited 1 with a nested Python quoting
SyntaxError before executing/writing files; corrected with a literal heredoc.
editing_diagnostic.json records the failure. No failed validation command was
silently ignored. No CUDA-ON attempt, GPU correctness test or GPU timing trial ran.

Modified only README.md and docs/ROADMAP.md (blocked status/next action),
docs/ALGORITHMS.md (no CUB), docs/BENCHMARKING.md (no GPU schema/results),
docs/EXPERIMENT_PROTOCOL.md (environment gate), docs/AUDIT.md (this evidence).
No algorithms, CMake, scripts/tests, vendors/licenses or versioned protocols
changed. All 120 other original source files and all {len(prior):,} earlier result
artifacts remain byte-identical, including frozen sorting/Phase 5/6 studies,
failed attempts and Phase 7 evidence/archive. Source manifests, changes.patch
and final_review.json retain integrity/review results. The old cloud guide and
readiness protocol remain unchanged. No new GPU sorting contract was created.

Completion statuses: cloud validation **blocked/not passed**; CUB implementation/
correctness **not started/not run**; GPU smoke **not run**; full GPU study **not
run**. Gates 2–4 are deferred per the user. Requested Phase 8 GPU task is incomplete.
BLOCKED.json records a gate outcome, never completed-study status. No acceleration
or100M execution claimed. Evidence: {e}/FINAL_AUDIT.md,
local_preflight/report.json, archive_verification.json, cpu_environment.json,
COMMANDS.md, final_review.json, prior_artifacts_sha256.json and source manifests.

Exact next action: allocate/connect an NVIDIA cloud development runtime, transfer
and verify the retained Phase 7 source archive, then follow
[CUDA_EXECUTION_GUIDE_v1.md](CUDA_EXECUTION_GUIDE_v1.md). From verified source run:
```sh
python3 scripts/cuda_preflight.py --output results/raw/NEW_CLOUD_PREFLIGHT
```
Require exit 0/operational, actual model/compute capability, driver/runtime/toolkit/
compiler metadata, enumeration and checked kernel. Retain exact cloud commands
and CPU fallback evidence outside ephemeral storage. Only then define Gate 2's
new GPU sorting contract, pin/license CUB, and implement signed-int32 differential
checks with separate synchronized transfer/device/end-to-end metrics. Cloud guide
execution remains unvalidated here because no cloud runtime was available.
'''
append('docs/AUDIT.md',audit)
# The standalone audit resolves its guide link from its own retained evidence location.
save('FINAL_AUDIT.md',audit.lstrip().replace('](CUDA_EXECUTION_GUIDE_v1.md)','](../../../docs/CUDA_EXECUTION_GUIDE_v1.md)'))
after={f:h(root/f) for f in before};changed=sorted(f for f,v in after.items() if v!=before[f]);assert set(changed)==allowed
assert all(h(root/f)==v for f,v in prior.items())
assert h(Path(p['archive']))==p['archive_sha256']
save_json('source_after.json',after)
save('changes.patch',''.join(''.join(difflib.unified_diff((Path(p['backup'])/f).read_text().splitlines(True),(root/f).read_text().splitlines(True),fromfile='before/'+f,tofile='after/'+f)) for f in changed))
review=dict(task_complete=False,gate1='blocked',cloud_validated=False,gpu_sort_implemented=False,gpu_correctness='not run',gpu_smoke='not run',full_gpu_study='not run',local_readiness='gpu_driver_unavailable',local_preflight_exit=2,release=release,sanitizer=sanitize,leak_detection_enabled=True,compiler_warning_lines=warnings,preflight_methods_per_suite=22,source_files=126,modified_files=changed,protected_source_files_unchanged=120,prior_artifacts_unchanged=len(prior),archive_sha256=p['archive_sha256'],archive_unchanged=True,frozen_protocols_unchanged=True,audit_sha256=h(e/'FINAL_AUDIT.md'),validation_commands=12,editing_helper_failure_recorded=True)
save_json('final_review.json',review)
save_json('BLOCKED.json',dict(gate=1,status='blocked',reason='No connected cloud GPU runtime or remote endpoint; local CUDA driver/toolkit unavailable.',audit='FINAL_AUDIT.md',audit_sha256=h(e/'FINAL_AUDIT.md'),review='final_review.json',review_sha256=h(e/'final_review.json'),cloud_execution=False,gpu_sorting=False,gpu_smoke=False,full_gpu_study=False))
print(json.dumps(review,indent=2))
