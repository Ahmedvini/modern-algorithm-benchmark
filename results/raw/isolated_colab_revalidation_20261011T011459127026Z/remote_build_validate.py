"""Authorized isolated build and two direct correctness tests; no timing entrypoint."""
import datetime,hashlib,json,os,platform,shutil,subprocess,tarfile,traceback
from pathlib import Path
root=Path('/content/mab_isolated_20261011T011459127026Z')
source=root/'source';build=root/'build-release';e=root/'validation'
assert not build.exists() and not e.exists()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
identity=json.loads((source/'SOURCE_IDENTITY.json').read_text())
assert sha(source/'SOURCE_IDENTITY.json')=='7ce8297b76037af65d6d2dbbf3e2ccf5ec4684849090ee554a6d9552fcd50bda'
assert all(sha(source/p)==h for p,h in identity['files_sha256'].items())
e.mkdir();records=[]
def save(name,data):
    with (e/name).open('x') as f:json.dump(data,f,indent=2,sort_keys=True);f.write('\n')
def call(name,argv,timeout):
    rec=dict(name=name,argv=argv,cwd=str(source),started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    save(name+'_ATTEMPT.json',rec)
    with (e/(name+'.stdout.txt')).open('xb') as out,(e/(name+'.stderr.txt')).open('xb') as err:
        try:
            p=subprocess.run(argv,cwd=source,stdout=out,stderr=err,timeout=timeout,check=False)
            rec['exit_code']=p.returncode
        except Exception as error:
            rec.update(exit_code=None,error=str(error))
    rec['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    save(name+'.json',rec);records.append(rec)
    print('COMMAND_RESULT',json.dumps(rec),flush=True)
    assert rec['exit_code']==0, name+' failed; full logs retained'
    return (e/(name+'.stdout.txt')).read_text()
common=['cmake','-S',str(source),'-B',str(build),'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_CXX_FLAGS=',
        '-DCMAKE_CXX_FLAGS_RELEASE=-O3 -DNDEBUG','-DMAB_ENABLE_OPENMP=ON','-DBUILD_TESTING=ON',
        '-DMAB_ENABLE_CUDA=ON','-DMAB_ENABLE_CUDA_SORT=ON','-DMAB_ENABLE_CPU_GPU_COMPARISON=ON',
        '-DMAB_ENABLE_SANITIZERS=OFF','-DCMAKE_CUDA_ARCHITECTURES=75','-DCMAKE_CUDA_FLAGS=',
        '-DCMAKE_CUDA_FLAGS_RELEASE=-O3 -DNDEBUG']
plan=[('configure',common,180),('build',['cmake','--build',str(build),'--target','cpu_gpu_comparison','comparison_input','test_cuda_sorting','test_mergesort','--parallel','2'],1200),
      ('cpu_correctness',[str(build/'test_mergesort')],120),('gpu_correctness',[str(build/'test_cuda_sorting')],240),
      ('comparison_describe',[str(build/'cpu_gpu_comparison'),'--describe'],60)]
save('PLAN.json',dict(commands=[dict(name=n,argv=a,timeout=t) for n,a,t in plan],timing_trials_authorized=False,
    validation_scope='two direct existing correctness targets plus metadata-only describe; no CTest',
    prohibited=['test_comparison','test_parallel_mergesort','comparison trial invocation','--resources','pilot/study scripts']))
save('ENVIRONMENT.json',dict(platform=platform.platform(),python=platform.python_version(),cpu_count=os.cpu_count(),
    affinity=sorted(os.sched_getaffinity(0)),meminfo=Path('/proc/meminfo').read_text(),cpuinfo=Path('/proc/cpuinfo').read_text(),
    disk=shutil.disk_usage('/content')._asdict(),environment={k:os.environ.get(k) for k in ['OMP_DYNAMIC','OMP_THREAD_LIMIT','OMP_MAX_ACTIVE_LEVELS','OMP_WAIT_POLICY','OMP_PROC_BIND','CUDA_VISIBLE_DEVICES','CUDACXX','CUDA_HOME','CUDA_PATH']}))
success=False;failure=None;cuda=None;cpu=None;describe=None
try:
    outputs={}
    for n,a,t in plan:outputs[n]=call(n,a,t)
    cpu=outputs['cpu_correctness'];assert 'Passed 4015 Merge Sort differential cases' in cpu
    cuda=json.loads(outputs['gpu_correctness'])
    assert cuda['status']=='ok' and cuda['protocol']=='cuda_sort_correctness_v2'
    assert (cuda['cases'],cuda['output_checks'],cuda['cub_version'])==(475,1900,300001)
    assert (cuda['compute_major'],cuda['compute_minor'])==(7,5)
    describe=json.loads(outputs['comparison_describe'])
    assert describe['build_type']=='Release' and not describe['sanitizers'] and describe['cub_version']==300001
    assert describe['implementation_version']=='cpu_gpu_comparison_driver_v1'
    assert all(sha(source/p)==h for p,h in identity['files_sha256'].items())
    save('SOURCE_AFTER.json',identity)
    success=True
except BaseException as error:
    failure=str(error);save('FAILURE.json',dict(error=failure,traceback=traceback.format_exc()))
finally:
    for name in ['CMakeCache.txt','compile_commands.json']:
        if (build/name).is_file():shutil.copyfile(build/name,e/name)
    if (build/'generated').exists():shutil.copytree(build/'generated',e/'generated')
    shutil.copyfile(root/'TRANSFER_VERIFIED.json',e/'TRANSFER_VERIFIED.json')
    shutil.copyfile(source/'SOURCE_IDENTITY.json',e/'SOURCE_IDENTITY.json')
    binaries={n:dict(path=str(build/n),sha256=sha(build/n),bytes=(build/n).stat().st_size) for n in ['cpu_gpu_comparison','comparison_input','test_cuda_sorting','test_mergesort'] if (build/n).is_file()}
    save('BINARIES.json',binaries)
    warning_lines=[]
    for p in sorted(e.glob('*.txt')):
        if p.name in ['CMakeCache.txt','compile_commands.json']:continue
        for number,line in enumerate(p.read_text().splitlines(),1):
            if 'warning' in line.lower():warning_lines.append(dict(file=p.name,line=number,text=line))
    result=dict(validation_passed=success,study_eligible=False,full_study_authorized=False,records=records,
        cuda_correctness=cuda,cpu_correctness=cpu,description=describe,failure=failure,warnings=warning_lines,
        ctest_invocations=0,timing_trials=0,benchmarks=0,build_directory=str(build),source_directory=str(source))
    save('RESULT.json',result)
    save('EVIDENCE_SHA256.json',{str(p.relative_to(e)):sha(p) for p in sorted(e.rglob('*')) if p.is_file()})
    archive=root/'validation_evidence.tar.gz'
    with archive.open('xb') as f:
        with tarfile.open(fileobj=f,mode='w:gz') as tar:tar.add(e,arcname='validation',recursive=True)
    print('ISOLATED_VALIDATION_BEGIN',flush=True)
    print(json.dumps(dict(validation_passed=success,evidence_archive=str(archive),archive_sha256=sha(archive),result=result)),flush=True)
    print('ISOLATED_VALIDATION_END',flush=True)
if not success:raise SystemExit(1)
