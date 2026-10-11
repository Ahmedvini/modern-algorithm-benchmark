import hashlib,json,pathlib,subprocess,sys,tarfile,time
archive=pathlib.Path('/content/cpu_gpu_pilot_20261010T001232473460Z_source_v1.tar.gz')
expected='b08b923d6c2215414ff11dfe513e4a6bbeebfa2276aa989706bbf2e4f54e4aa2'
actual=hashlib.sha256(archive.read_bytes()).hexdigest()
print('Remote source SHA256:',actual,flush=True)
if actual!=expected:raise RuntimeError('source checksum mismatch')
destination=pathlib.Path('/content/cpu_gpu_pilot_20261010T001232473460Z_v1')
if destination.exists() or destination.is_symlink():raise RuntimeError('destination already exists')
with tarfile.open(archive) as bundle:
 members=bundle.getmembers()
 for member in members:
  path=pathlib.PurePosixPath(member.name)
  if path.is_absolute() or '..' in path.parts or path.parts[0]!='modern-algorithm-benchmark' or not (member.isfile() or member.isdir()):raise RuntimeError('unsafe archive member '+member.name)
 print('Reviewed archive members:',len(members),flush=True)
 destination.mkdir();bundle.extractall(destination,filter='data')
root=destination/'modern-algorithm-benchmark'
(root/'results/raw').mkdir(parents=True);(root/'results/processed').mkdir(parents=True)
command=[sys.executable,'scripts/validate_cpu_gpu_pilot.py','--output','results/raw/validation_v1','--pilot-output','results/raw/pilot_v1','--processed','results/processed/pilot_v1']
record=dict(argv=command,cwd=str(root),source_archive_sha256=actual,started=time.time())
(destination/'launch_started.json').write_text(json.dumps(record,indent=2)+'\n')
print('Executing fresh prerequisites; pilot is gated:',command,flush=True)
try:
 with (destination/'launch_stdout.log').open('x') as out,(destination/'launch_stderr.log').open('x') as err:
  result=subprocess.run(command,cwd=root,stdout=out,stderr=err,timeout=2700)
 record.update(exit_code=result.returncode,status='completed')
except subprocess.TimeoutExpired:
 record.update(exit_code=None,status='timeout')
record['wall_seconds']=time.time()-record['started']
(destination/'launch_result.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2),flush=True)
print((destination/'launch_stdout.log').read_text(),flush=True)
print((destination/'launch_stderr.log').read_text(),file=sys.stderr,flush=True)
if record['exit_code']!=0:raise RuntimeError('Validation stopped; preserve diagnostics')
