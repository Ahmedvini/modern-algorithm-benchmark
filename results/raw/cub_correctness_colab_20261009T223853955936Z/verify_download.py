import hashlib,json,sys,tarfile
from pathlib import Path,PurePosixPath
p=json.loads(Path('build/colab_validation_paths.json').read_text());e=Path(p['evidence']);d=json.loads((e/'commands/remote_package.json').read_text());export=json.loads(next(x for x in d['stdout'].splitlines() if x.startswith('MAB_EXPORT_JSON=')).split('=',1)[1]);archive=e/'colab_evidence.tar.gz'
assert hashlib.sha256(archive.read_bytes()).hexdigest()==export['sha256'];assert archive.stat().st_size==export['bytes']
destination=e/'downloaded';assert not destination.exists()
with tarfile.open(archive,'r:gz') as tar:
 members=tar.getmembers();names=[m.name for m in members];assert len(names)==len(set(names))
 for m in members:
  name=PurePosixPath(m.name);assert not name.is_absolute() and '..' not in name.parts;assert m.isfile() or m.isdir()
 destination.mkdir();tar.extractall(destination,filter='data')
manifest=json.loads((destination/'EVIDENCE_SHA256.json').read_text());assert not manifest['skipped_symlinks'];assert len(manifest['files'])==export['files']
for name,record in manifest['files'].items():
 path=destination/name;assert hashlib.sha256(path.read_bytes()).hexdigest()==record['sha256'],name;assert path.stat().st_size==record['bytes']
sys.path.insert(0,'scripts');import validate_cuda_sort as validation
run=destination/'retry1/NEW_CUB_CORRECTNESS';complete=json.loads((run/'COMPLETE.json').read_text());assert complete['sorting_validated'];assert not (run/'FAILED.json').exists();result=validation.verify_result(complete['result']);direct=json.loads((run/'sorting.json').read_text());assert direct['exit_code']==0;assert json.loads(direct['stdout'])==result
ctest=json.loads((run/'ctest.json').read_text());assert ctest['exit_code']==0;validation.verify_ctest(ctest['stdout'])
for key,name in [('source_manifest_sha256','source_sha256.json'),('dependency_manifest_sha256','dependency_sha256.json'),('preflight_sha256','preflight/report.json')]:assert hashlib.sha256((run/name).read_bytes()).hexdigest()==complete[key]
preflight=json.loads((run/'preflight/report.json').read_text());assert preflight['classification']['state']=='operational';assert preflight['classification']['device0_kernel_verified']
retry=json.loads((e/'retry_source_sha256.json').read_text());sources=json.loads((run/'source_sha256.json').read_text());assert all(retry[name]==sha for name,sha in sources.items())
assert json.loads((destination/'attempt1/NEW_CUB_CORRECTNESS/configure.json').read_text())['exit_code']==1;assert (destination/'attempt1/NEW_CUB_CORRECTNESS/FAILED.json').is_file();assert not (destination/'attempt1/NEW_CUB_CORRECTNESS/COMPLETE.json').exists()
summary={'archive':str(archive),'archive_sha256':export['sha256'],'verified_files':len(manifest['files']),'verified_source_files':len(sources),'dependency_files':len(json.loads((run/'dependency_sha256.json').read_text())['files']),'result':result,'ctest_passed':1,'ctest_failed':0,'ctest_skipped':0,'failed_attempt_preserved':True,'preflight_kernel_verified':True}
with (e/'download_verification.json').open('x') as f:json.dump(summary,f,indent=2);f.write('\n')
print(json.dumps(summary,indent=2))
