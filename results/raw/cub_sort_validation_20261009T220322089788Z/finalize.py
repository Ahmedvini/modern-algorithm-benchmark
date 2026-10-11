import difflib, gzip, hashlib, io, json, re, shlex, tarfile
from pathlib import Path
root=Path.cwd();paths=json.loads(Path('build/cub_sort_paths.json').read_text());e=Path(paths['evidence'])
h=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
records={f.stem:json.loads(f.read_text()) for f in sorted((e/'commands').glob('*.json')) if not f.stem.endswith('_started')}
for n in ['reviewed_release_ctest','reviewed_sanitize_ctest']:
 assert records[n]['exit_code']==0 and '100% tests passed, 0 tests failed out of 26' in records[n]['stdout']
 assert 'Ran 11 tests' in records[n]['stdout']
assert records['local_cuda_configure']['exit_code']==1
assert records['local_preflight']['exit_code']==2
for name,r in records.items():
 expected=128 if name.startswith('git_') else 1 if name=='local_cuda_configure' else 2 if name=='local_preflight' else 0
 assert r['exit_code']==expected,(name,r['exit_code'])
warnings=[line for n,r in records.items() if n.endswith(('configure','build')) and n!='local_cuda_configure' for line in (r['stdout']+'\n'+r['stderr']).splitlines() if 'warning:' in line.lower()]
assert not warnings,warnings
before=json.loads((e/'source_before.json').read_text());prior=json.loads((e/'prior_artifacts_sha256.json').read_text())
assert all(h(p)==v for p,v in prior.items())
frozen=json.loads((e/'protocol_frozen.json').read_text());assert h(frozen['path'])==frozen['sha256']
def save(name,text):
 with (e/name).open('x') as f:f.write(text)
def save_json(name,obj):save(name,json.dumps(obj,indent=2,sort_keys=True)+'\n')
cmds='# Exact command records\n\nAll new commands ran locally. Cloud evidence is historical, separately reviewed.\n\n'
for name,r in sorted(records.items(),key=lambda x:x[1]['started_utc']):
 cmds+='```sh\n'+shlex.join(r['argv'])+'\n```\n\nExit '+str(r['exit_code'])+'; [diagnostics](commands/'+name+'.json).\n\n'
save('COMMANDS.md',cmds);save_json('commands_index.json',records)
times={n:float(re.search(r'Total Test time \(real\) =\s*([\d.]+) sec',records[n]['stdout']).group(1)) for n in ['baseline_ctest','reviewed_release_ctest','reviewed_sanitize_ctest']}
audit=f'''
## Post-cloud validation — first CUB correctness slice, hardware validation pending

Inspected AGENTS.md, README/roadmap/audit/protocols, CMake/CUDA isolation, existing
CPU and parallel sorter interfaces/registries/implementations, differential tests,
preflight and runner conventions, Phase7/blocked-gate records and new cloud archive.
Git status/branches/log each exit128: no Git metadata, branches/commits/uncommitted
status unavailable; no Git initialization/commit/push. Anonymous temporary-file
write verified access. Source before: {len(before)} files including .gitignore,
backup under {paths['backup']}; all {len(prior):,} earlier results/evidence files
hashed before edits. No existing user source was discarded.

Initial root-level cloud archive lookup failed (ls2, sha256sum1, tar2), resolved by
file search to results/evidence/cloud_validation_evidence.tar.gz before extraction.
Archive SHA256 matches 48b3e78360e7c0c1721c21a3879bc975b902f5b3603fa25a0c92230c695c0810.
Listed members first; safely extracted to new {e}/cloud_evidence. Preflight marker
hashes and four reported source hashes match the starting code. Historical Colab
report: Tesla T4, compute7.5, driver580.82.07, nvcc13.0.88, runtime/driver API13000,
CMake3.31.10, host GNU13.3.0, device0 checked kernel success. Actual preflight
configure/build/runtime return0; retained LastTest logs have23 CPU passes/0 failures
(OpenMP OFF) and1 CUDA-runtime pass/0 failures. The CUDA log's24/24 ordinal is a
filtered test index, not24 GPU tests. External full command transcript/exit statuses
for the cloud CPU build/CTest are not in the archive; LastTest.log and the CPU cache
support successful tests/Release configuration, not invented missing commands.
This proves historical readiness, not new CUB sorting or a currently connected GPU.
cloud_evidence_review.json records precisely that scope. Prior extracted cloud
evidence and original archive are unchanged.

Baseline fresh Release configure/build/CTest: exit0/0/0,25/25 groups,{times['baseline_ctest']:.2f}s.
No baseline correctness defect found. CUDA_SORT_PROTOCOL_v1.md was saved/hash-frozen
before implementation. Separate cub_radix_sort_v1 adapter: signed-int32 full-width
CUB SortKeys, per-call device input/output/scratch and host output, checked API/
launch/sync/copy/cleanup, caller host mutation only after successful cleanup. Empty/
singleton require an available device then no-op; no CPU fallback. Length/byte
bounds checked; no abs/signed overflow. Existing Sorter shape reused in a separate
GPU registry; CPU six-entry registry/std_sort and all timing implementations stay
unchanged. No performance timing or CUB comparison metric implemented.

Dependency reference: NVIDIA CCCL v3.0.0, resolved commit
 e944297b0b51a8e9c0f1b30425370c31c1c0e0a0. Revision-qualified SortKeys/version/license
bytes verified against reviewed tag downloads. CUB is BSD-3-Clause, unchanged
aggregate LICENSE/attribution/provenance retained in third_party/cub. Toolkit
headers used without network fetching or upstream modification. Sorting opt-in
MAB_ENABLE_CUDA_SORT=OFF by default requires CUDA ON/toolkit>=13.0; readiness-only
CUDA path/minimum remains unchanged. CUB_VERSION300000 and two reviewed header
hashes are enforced. Actual installed cloud CUB identity is absent from the old
archive: a mismatch is an explicit dependency-review blocker, not a hidden bypass.
Cloud runner records transitive cub/thrust/cuda header hashes when configure passes.

GPU-only test source includes475 expected inputs/1900 output checks through public,
registry, interleaved/repeated calls, extrema/mixed signs/duplicates/sorted/random/
all generator distributions and lengths0..65537 including non-power-of-two and
boundary neighbors. These counts are **planned, not executed GPU results**. Default
CPU suites do not register GPU sorting. The cloud runner demands actual direct
sort-test success and a genuinely selected/passed CTest; skip77, empty selection,
malformed/incomplete output, failed subprocess, source changes or unavailable
preflight prevent COMPLETE. Exclusive paths, manifests/command diagnostics and
FAILED/INTERRUPTED markers preserve incomplete attempts. No resume/overwrite.

Local affected CUDA configure: exit1, CUDA compiler NOTFOUND (no nvcc); sorter
compilation and execution **not run**. Fresh local preflight exit2 remains
gpu_driver_unavailable. No driver/package/system changes and no live Colab endpoint
available to this agent. A versioned handoff guide and new source archive are
provided for user-run GPU validation, not represented as a tested cloud sorter.

Final reviewed fresh Release configure/build/CTest exit0/0/0:26/26 groups,
{times['reviewed_release_ctest']:.2f}s. Debug ASan/UBSan configure/build/CTest exit0/0/0:
26/26,{times['reviewed_sanitize_ctest']:.2f}s, leaks enabled. No ptrace limitation or
detect_leaks=0 retry. Eleven new host tooling methods pass standalone and in both
final suites: schema/count validation, skip/empty CTest rejection, unavailable/
timeout/interruption diagnostics, output/symlink collisions, redaction, invalid
CLI and CUDA-SORT-with-CUDA-OFF rejection. These are host/synthetic record tests,
not mocked evidence of actual GPU sorting. Existing CPU sort/search/structure/
OpenMP tests remain passing; all22 preflight methods pass. Earlier intermediate
26/26 runs precede the final CTest-result-validator test and are retained separately.
CPU environment capture exit0. Captured CPU configure/build output has no compiler
warnings; new GPU compiler warnings cannot be reviewed before a CUDA build.

Exact argv/cwd/timestamps/exit/stdout/stderr: {e}/COMMANDS.md,
commands_index.json and commands/*.json. Nonzero commands are the explained Git
metadata errors128, unavailable CUDA configure1 and readiness2; initial misplaced
archive lookup is recorded in initial_lookup_diagnostics.json. No failed check is
silently treated as successful. Local full suites:26 passed/0 failed/0 skipped each.
New GPU sorting test:0 executed,1 group unexecuted (not registered in CPU-OFF tests).
Historical cloud runtime smoke:1 passed; historical cloud CPU:23 passed.

Files added: include/algorithms/cuda_sorting.hpp, src/cuda/cub_sort.cu,
tests/test_cuda_sorting.cpp, scripts/validate_cuda_sort.py,
tests/test_cuda_sort_handoff.py, docs/CUDA_SORT_PROTOCOL_v1.md,
docs/CUDA_SORT_VALIDATION_GUIDE_v1.md, third_party/cub/README.md/LICENSE/UPSTREAM.json.
Modified: CMakeLists.txt, cmake/cuda.cmake, README.md and docs/ROADMAP.md/AUDIT.md/
ALGORITHMS.md/BENCHMARKING.md/EXPERIMENT_PROTOCOL.md. Existing CPU algorithms/tests,
vendors/licenses and old versioned protocols/studies/results stay unchanged.
Final manifests/change patch/integrity audit retained under {e}.

Current phase: original roadmap Phase7 CUDA, requested post-cloud GPU continuation;
original Phase8 learned-index/AlphaDev remains pending. Runtime readiness validated
historically; first sorter source/build/tests/docs delivered but GPU compilation/
correctness **pending**. GPU timing/smoke/full study **not started**. No acceleration,
GPU benchmark measurements, significance or100M claim. The repository is ready
for cloud correctness handoff, not for the next research phase or timing study.

Exact next step: use the new cub_sort_source.tar.gz (source_bundle.json has its hash)
and docs/CUDA_SORT_VALIDATION_GUIDE_v1.md on an allocated supported cloud GPU.
After source verification, run:
```sh
python3 scripts/validate_cuda_sort.py --output results/raw/NEW_CUB_CORRECTNESS
```
Retain/persist COMPLETE or failed-attempt evidence and return the archive/hash for
review. Only observed build/475-case/1900-check success permits the separate GPU
timing contract/engine. If installed CUB mismatches the pin, retain actual hashes
and review that version explicitly before changing the frozen design.
'''
with Path('docs/AUDIT.md').open('a') as f:f.write(audit)
for filename in ['README.md','docs/ROADMAP.md']:
 with Path(filename).open('a') as f:f.write(f'\nFinal local CPU regression:26/26 Release and26/26 ASan/UBSan, leaks enabled;11 handoff methods pass. New GPU sorting remains uncompiled/unexecuted. Evidence: {e}/FINAL_AUDIT.md.\n')
source={str(p):h(p) for base in ['include','src','tests','scripts','cmake','docs','third_party'] for p in sorted(Path(base).rglob('*')) if p.is_file() and '__pycache__' not in p.parts}
for name in ['AGENTS.md','README.md','CMakeLists.txt','.gitignore']:source[name]=h(name)
changed=sorted(p for p,v in before.items() if source.get(p)!=v);added=sorted(set(source)-set(before))
allowed={'CMakeLists.txt','cmake/cuda.cmake','README.md','docs/ROADMAP.md','docs/AUDIT.md','docs/ALGORITHMS.md','docs/BENCHMARKING.md','docs/EXPERIMENT_PROTOCOL.md'}
assert set(changed)==allowed,(changed,added)
assert len(added)==10,added
assert all(h(p)==v for p,v in prior.items())
assert h(frozen['path'])==frozen['sha256']
save_json('source_after.json',source);save_json('file_changes.json',dict(modified=changed,added=added))
patch=''
for name in sorted(changed+added):
 old=(Path(paths['backup'])/name).read_text().splitlines(True) if name in before else []
 patch+=''.join(difflib.unified_diff(old,Path(name).read_text().splitlines(True),fromfile='before/'+name if old else '/dev/null',tofile='after/'+name))
save('changes.patch',patch)
# Archive creation occurs after all source/doc writes; final audit hash stays outside source.
manifest=json.dumps(source,indent=2,sort_keys=True).encode()+b'\n'
buffer=io.BytesIO()
with tarfile.open(fileobj=buffer,mode='w') as tar:
 for name,data in [(n,Path(n).read_bytes()) for n in sorted(source)]+[('SOURCE_SHA256.json',manifest)]:
  info=tarfile.TarInfo('modern-algorithm-benchmark/'+name);info.size=len(data);info.mtime=0;info.mode=0o644;tar.addfile(info,io.BytesIO(data))
archive=e/'cub_sort_source.tar.gz'
with archive.open('xb') as f:
 with gzip.GzipFile(filename='',mode='wb',fileobj=f,mtime=0) as gz:gz.write(buffer.getvalue())
with tarfile.open(archive) as tar:
 assert len(tar.getmembers())==len(source)+1
 for name,sha in source.items():assert hashlib.sha256(tar.extractfile('modern-algorithm-benchmark/'+name).read()).hexdigest()==sha
bundle=dict(archive=str(archive),sha256=h(archive),bytes=archive.stat().st_size,source_files=len(source),members=len(source)+1,all_member_hashes_verified=True,includes_historical_results=False)
save_json('source_bundle.json',bundle)
save('FINAL_AUDIT.md',audit.lstrip()+'\nNew cloud source archive identity:\n```json\n'+json.dumps(bundle,indent=2)+'\n```\n')
review=dict(complete_gpu_milestone=False,cloud_runtime_historical_verified=True,new_gpu_sort_compiled=False,new_gpu_sort_executed=False,new_gpu_sort_test_groups_unexecuted=1,new_gpu_smoke='not run',full_gpu_study='not run',baseline_groups=25,release_groups=26,sanitizer_groups=26,failed_ctest_groups=0,skipped_ctest_groups=0,handoff_methods=11,leak_detection_enabled=True,prior_artifacts_unchanged=len(prior),source_files=len(source),protected_original_files_unchanged=len(before)-len(changed),modified=changed,added=added,protocol_sha256=frozen['sha256'],archive=bundle,audit_sha256=h(e/'FINAL_AUDIT.md'),compiler_warnings=warnings)
save_json('final_review.json',review)
print(json.dumps(review,indent=2))
