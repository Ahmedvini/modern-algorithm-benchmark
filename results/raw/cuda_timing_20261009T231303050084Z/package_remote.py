from pathlib import Path
import datetime,hashlib,io,json,platform,subprocess,tarfile
parent=Path('/content/cuda_timing_20261009T231303050084Z');project=parent/'modern-algorithm-benchmark'
raw=project/'results/raw/NEW_GPU_TIMING'
conditions=dict(captured_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),timing='after benchmark, not controlled during measurements',platform=platform.platform(),probes=[])
for argv in [['nvidia-smi','--query-gpu=name,driver_version,compute_cap,memory.total,temperature.gpu,clocks.current.sm,clocks.current.memory','--format=csv,noheader'],['uptime'],['df','-h','/content']]:
 try:
  result=subprocess.run(argv,capture_output=True,text=True,timeout=30)
  conditions['probes'].append(dict(argv=argv,exit_code=result.returncode,stdout=result.stdout,stderr=result.stderr))
 except OSError as error:conditions['probes'].append(dict(argv=argv,exit_code=None,error=str(error)))
conditions['governors']={str(p):p.read_text().strip() for p in Path('/sys/devices/system/cpu').glob('cpu[0-9]*/cpufreq/scaling_governor')}
with (parent/'post_run_conditions.json').open('x') as f:json.dump(conditions,f,indent=2)
files={}
for directory,label in [(raw,'raw'),(project/'results/processed/NEW_GPU_TIMING','processed')]:
 for path in sorted(directory.rglob('*')):
  if path.is_file():
   assert not path.is_symlink(),str(path)
   files[label+'/'+str(path.relative_to(directory))]=path
for name in ['transfer_verification.json','remote_execution.json','post_run_conditions.json']:files[name]=parent/name
files['remote_source_manifest.json']=project/'SOURCE_SHA256.json'
manifest={name:hashlib.sha256(path.read_bytes()).hexdigest() for name,path in files.items()}
archive=Path('/content/cuda_timing_20261009T231303050084Z_evidence.tar.gz')
assert not archive.exists()
with tarfile.open(archive,'x:gz') as tar:
 for name,path in files.items():tar.add(path,arcname=name,recursive=False)
 content=json.dumps(manifest,indent=2,sort_keys=True).encode();entry=tarfile.TarInfo('SHA256_MANIFEST.json');entry.size=len(content);tar.addfile(entry,io.BytesIO(content))
print('MAB_EVIDENCE='+json.dumps(dict(archive=str(archive),sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),files=len(files),bytes=archive.stat().st_size)))
