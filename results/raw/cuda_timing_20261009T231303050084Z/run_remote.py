from pathlib import Path
import json,subprocess,time,sys
parent=Path('/content/cuda_timing_20261009T231303050084Z')
project=parent/'modern-algorithm-benchmark'
argv=[sys.executable,'scripts/validate_cuda_timing.py','--output','results/raw/NEW_GPU_TIMING','--processed','results/processed/NEW_GPU_TIMING']
start=time.monotonic()
try:
 result=subprocess.run(argv,cwd=project,capture_output=True,text=True,timeout=2400)
 record=dict(argv=argv,cwd=str(project),exit_code=result.returncode,stdout=result.stdout,stderr=result.stderr,wall_seconds=time.monotonic()-start)
except subprocess.TimeoutExpired as error:
 def text(value):return value.decode(errors='replace') if isinstance(value,bytes) else value or ''
 record=dict(argv=argv,cwd=str(project),exit_code=None,status='timeout',stdout=text(error.stdout),stderr=text(error.stderr),wall_seconds=time.monotonic()-start)
with (parent/'remote_execution.json').open('x') as f:json.dump(record,f,indent=2)
print('MAB_CUDA_TIMING_EXECUTION='+json.dumps(record))
raw=project/'results/raw/NEW_GPU_TIMING'
for name in ['COMPLETE.json','FAILED.json','build_benchmark.json','smallest_smoke.json','gpu_framework.json','smoke_matrix.json']:
 path=raw/name
 if path.exists():
  value=json.loads(path.read_text())
  if name.endswith('.json') and 'stderr' in value:value['stderr']=value['stderr'][-14000:];value['stdout']=value['stdout'][-14000:]
  print(name+'='+json.dumps(value))
if record['exit_code']!=0:raise RuntimeError('GPU timing runner failed; preserve evidence')
