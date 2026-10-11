import json,subprocess,sys
from pathlib import Path
p=json.loads(Path('build/phase8_gate1_paths.json').read_text());e=Path(p['evidence']);rec=e/'record_command.py';src=Path(p['extracted'])/'modern-algorithm-benchmark'; b=Path(p['extracted'])/'cpu_build'
commands=[
('archive',0,['python3',str(e/'validate_archive.py')]),
('local_preflight',2,['python3',str(src/'scripts/cuda_preflight.py'),'--output',str(e/'local_preflight')]),
('archive_cpu_configure',0,['cmake','-S',str(src),'-B',str(b),'-DCMAKE_BUILD_TYPE=Release','-DMAB_ENABLE_CUDA=OFF','-DMAB_ENABLE_OPENMP=OFF','-DBUILD_TESTING=OFF']),
('archive_cpu_build',0,['cmake','--build',str(b),'--target','sort_benchmark','--parallel','2']),
('archive_cpu_registry',0,[str(b/'sort_benchmark'),'--list-sorts']),
('release_configure',0,['cmake','-S','.','-B','build/release','-DCMAKE_BUILD_TYPE=Release','-DMAB_ENABLE_CUDA=OFF','-DMAB_ENABLE_OPENMP=ON','-DMAB_ENABLE_SANITIZERS=OFF']),
('release_build',0,['cmake','--build','build/release','--parallel','2']),
('release_ctest',0,['ctest','--test-dir','build/release','--output-on-failure','-V']),
('sanitize_configure',0,['cmake','-S','.','-B','build/sanitize','-DCMAKE_BUILD_TYPE=Debug','-DMAB_ENABLE_CUDA=OFF','-DMAB_ENABLE_OPENMP=ON','-DMAB_ENABLE_SANITIZERS=ON']),
('sanitize_build',0,['cmake','--build','build/sanitize','--parallel','2']),
('sanitize_ctest',0,['env','-u','ASAN_OPTIONS','-u','LSAN_OPTIONS','UBSAN_OPTIONS=halt_on_error=1','ctest','--test-dir','build/sanitize','--output-on-failure','-V']),
('cpu_environment',0,['python3','scripts/capture_environment.py','--build-dir','build/release','--output',str(e/'cpu_environment.json')])]
for name,expected,cmd in commands:
    print('START',name,flush=True)
    result=subprocess.run([sys.executable,str(rec),name,*cmd],capture_output=True,text=True)
    print('END',name,'exit',result.returncode,'expected',expected,flush=True)
    if result.returncode!=expected:
        print(result.stdout[-8000:]);print(result.stderr[-8000:]);sys.exit(1)
print('All planned local validation commands matched expected exit statuses.',flush=True)
