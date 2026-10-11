import difflib,gzip,hashlib,io,json,re,shlex,tarfile
from pathlib import Path
p=json.loads(Path('build/cub_sort_final_paths.json').read_text());e=Path(p['evidence']);initial=Path(p['initial']['evidence']);h=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
records={f.stem:json.loads(f.read_text()) for f in sorted((e/'commands').glob('*.json')) if not f.stem.endswith('_started')}
assert len(records)==7 and all(r['exit_code']==0 for r in records.values())
for n in ['release_ctest','sanitize_ctest']:
 assert '100% tests passed, 0 tests failed out of 26' in records[n]['stdout']
 assert 'Ran 12 tests' in records[n]['stdout']
prior=json.loads((e/'prior_artifacts_sha256.json').read_text());assert all(h(f)==v for f,v in prior.items())
original=json.loads((initial/'prior_artifacts_sha256.json').read_text());assert all(h(f)==v for f,v in original.items())
frozen=json.loads((initial/'protocol_frozen.json').read_text());assert h(frozen['path'])==frozen['sha256']
def save(name,text):
 with (e/name).open('x') as f:f.write(text)
def js(name,value):save(name,json.dumps(value,indent=2,sort_keys=True)+'\n')
commands='# Final corrected-revision commands\n\n'
for name,r in sorted(records.items(),key=lambda x:x[1]['started_utc']):commands+='```sh\n'+shlex.join(r['argv'])+'\n```\n\nExit '+str(r['exit_code'])+'; [record](commands/'+name+'.json).\n\n'
save('COMMANDS.md',commands);js('commands_index.json',records)
times={n:float(re.search(r'Total Test time \(real\) =\s*([\d.]+) sec',records[n]['stdout']).group(1)) for n in ['release_ctest','sanitize_ctest']}
text=f'''
## CUB handoff final review revision2 — GPU correctness still pending

Final output-safety review found that resolving the requested path before mkdir
could follow a dangling symlink. Corrected to preserve the final path component
with Path.absolute(), so exclusive mkdir rejects existing and dangling symlinks.
New regression verifies no subprocess or target creation. Twelve host handoff
methods now pass. This is a host runner fix, not a CUDA algorithm change.
The initial source bundle/audit and all earlier validation evidence remain intact.
Use CUDA_SORT_VALIDATION_GUIDE_v2.md and cub_sort_source_v2.tar.gz for the corrected
handoff; v1 is retained history. Frozen CUDA_SORT_PROTOCOL_v1.md is unchanged.

Fresh narrow tests and Release configure/build/CTest all exited0:26/26 groups,
{times['release_ctest']:.2f}s. Fresh Debug ASan/UBSan configure/build/CTest exited0:
26/26 groups,{times['sanitize_ctest']:.2f}s, leak detection enabled, no ptrace retry.
Zero failed/skipped CPU groups;12 host methods pass standalone and in each suite.
GPU sorting remains uncompiled/unexecuted:1 GPU test group unexecuted,475 expected
inputs/1900 expected output checks, not passes. Earlier local CUDA configure1
(no compiler), preflight2(unavailable), Git128(no metadata) and historical T4
runtime/cloud-CPU evidence remain exactly as recorded in the initial audit.

The first candidate bundle's137 files were also independently extracted/hash
verified, relocated CUDA/CUDA-SORT/OpenMP/testing OFF configure/build/registry
returned0/0/0 and six CPU sorters; that fallback had testing OFF. Correction changes
only host handoff/script/test/docs; CUDA adapter/CMake are unchanged. The corrected
bundle is separately source-hash verified and preserves every original result.
All {len(original):,} pre-task artifacts and all {len(prior):,} pre-correction artifacts
(including first candidate archive and its relocation evidence) remain unchanged.
Current source differences/patch/manifest and final_review.json are retained here.

Evidence: {e}/COMMANDS.md, commands/*.json and FINAL_AUDIT.md.
Initial audit/evidence: {initial}/FINAL_AUDIT.md and COMMANDS.md.
No CUDA implementation validation, GPU smoke, full study, timing values or100M run
is claimed. No system configuration, driver change, commit or push. Current
roadmap CUDA work is incomplete; ready for corrected cloud handoff only.

Next: transfer the corrected v2 archive using source_bundle.json's SHA256, verify
its source manifest, follow docs/CUDA_SORT_VALIDATION_GUIDE_v2.md and run:
```sh
python3 scripts/validate_cuda_sort.py --output results/raw/NEW_CUB_CORRECTNESS
```
Preserve/return full success/failure evidence. Actual installed CUB must match the
reviewed version/header pin or be deliberately reviewed before any pin update.
Only observed GPU sorting success permits the separate timing milestone.
'''
with Path('docs/AUDIT.md').open('a') as f:f.write(text)
for name in ['README.md','docs/ROADMAP.md']:
 prefix='docs/' if name=='README.md' else ''
 with Path(name).open('a') as f:f.write(f'\nLatest CUB handoff revision2: dangling-symlink safety fixed;12 host methods and26/26 Release/ASan/UBSan groups pass, leaks enabled. GPU sorting still uncompiled/unexecuted. Use [v2 guide]({prefix}CUDA_SORT_VALIDATION_GUIDE_v2.md), cub_sort_source_v2.tar.gz and evidence at {e}/FINAL_AUDIT.md. Earlier candidate archive remains unchanged.\n')
source={str(f):h(f) for base in ['include','src','tests','scripts','cmake','docs','third_party'] for f in sorted(Path(base).rglob('*')) if f.is_file() and '__pycache__' not in f.parts}
for name in ['AGENTS.md','README.md','CMakeLists.txt','.gitignore']:source[name]=h(name)
before=json.loads((initial/'source_before.json').read_text());changed=sorted(f for f,v in before.items() if source.get(f)!=v);added=sorted(set(source)-set(before))
assert len(changed)==8 and len(added)==11
assert all(h(f)==v for f,v in prior.items())
js('source_after.json',source);js('file_changes.json',dict(modified=changed,added=added))
patch=''
for f in sorted(changed+added):
 old=(Path(p['initial']['backup'])/f).read_text().splitlines(True) if f in before else []
 patch+=''.join(difflib.unified_diff(old,Path(f).read_text().splitlines(True),fromfile='before/'+f if old else '/dev/null',tofile='after/'+f))
save('changes.patch',patch)
manifest=json.dumps(source,indent=2,sort_keys=True).encode()+b'\n';payload=io.BytesIO()
with tarfile.open(fileobj=payload,mode='w') as t:
 for name,data in [(f,Path(f).read_bytes()) for f in sorted(source)]+[('SOURCE_SHA256.json',manifest)]:
  info=tarfile.TarInfo('modern-algorithm-benchmark/'+name);info.mode=0o644;info.mtime=0;info.size=len(data);t.addfile(info,io.BytesIO(data))
a=e/'cub_sort_source_v2.tar.gz'
with a.open('xb') as f:
 with gzip.GzipFile(filename='',fileobj=f,mode='wb',mtime=0) as gz:gz.write(payload.getvalue())
with tarfile.open(a) as t:
 for name,sha in source.items():assert hashlib.sha256(t.extractfile('modern-algorithm-benchmark/'+name).read()).hexdigest()==sha
bundle=dict(archive=str(a),sha256=h(a),source_files=len(source),bytes=a.stat().st_size,members=len(source)+1,member_hashes_verified=True,earlier_candidate_preserved=True)
js('source_bundle.json',bundle);save('FINAL_AUDIT.md',text.lstrip()+'\nCorrected source bundle:\n```json\n'+json.dumps(bundle,indent=2)+'\n```\n')
js('final_review.json',dict(gpu_milestone_complete=False,cloud_runtime_historical_verified=True,new_gpu_sort_compiled=False,new_gpu_sort_executed=False,gpu_test_groups_unexecuted=1,release_groups=26,sanitizer_groups=26,failed_groups=0,skipped_groups=0,leak_detection_enabled=True,handoff_methods=12,prior_artifacts_unchanged=len(prior),pre_task_artifacts_unchanged=len(original),modified=changed,added=added,source_files=len(source),original_source_files_unchanged=len(before)-len(changed),protocol_unchanged=True,archive=bundle,audit_sha256=h(e/'FINAL_AUDIT.md')))
print(json.dumps(bundle,indent=2))
