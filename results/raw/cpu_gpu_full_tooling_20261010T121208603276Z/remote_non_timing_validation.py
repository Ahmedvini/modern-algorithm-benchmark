"""Fresh GPU-enabled build and explicit non-timing correctness/tooling allowlist."""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tarfile
import traceback

BASE=Path('/content/full_matrix_tooling_20261010T121208603276Z')
BASE.mkdir(exist_ok=False);E=BASE/'evidence';E.mkdir()
EXPECTED='e0624ec4fcb89e1ec627f5c74199557f86bf4ab8a7bd06b49c6b5e6c23f38d6d'
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def save(name,value):
    with (E/name).open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
def command(name,argv,timeout=900):
    result=subprocess.run(argv,capture_output=True,text=True,timeout=timeout)
    record=dict(argv=argv,cwd=os.getcwd(),exit_code=result.returncode,stdout=result.stdout,stderr=result.stderr)
    save(name+'.json',record);print(name,'exit',result.returncode,flush=True)
    if result.returncode:raise RuntimeError(name+': '+result.stderr[-2000:])
    return record
status=1
try:
    archive=Path('/content/full_matrix_tooling_source_20261010T121208Z.tar.gz')
    assert sha(archive)==EXPECTED,'remote bundle checksum differs'
    with tarfile.open(archive) as tar:
        members=tar.getmembers()
        for member in members:
            p=PurePosixPath(member.name)
            assert not p.is_absolute() and '..' not in p.parts and p.parts[0]=='modern-algorithm-benchmark'
            assert member.isfile() or member.isdir()
        save('source_archive.json',dict(sha256=sha(archive),members=[m.name for m in members]))
        tar.extractall(BASE,filter='data')
    root=BASE/'modern-algorithm-benchmark';os.chdir(root);sys.path.insert(0,str(root/'scripts'))
    from cpu_gpu_protocol import load_protocol,verify_source_extension
    from run_cpu_gpu_pilot import snapshot
    source=verify_source_extension(load_protocol());save('source_before.json',source)
    command('gpu_initial',['nvidia-smi'])
    command('nvcc',['nvcc','--version'])
    build=root/'build/non_timing_release'
    command('configure',['cmake','-S','.', '-B',str(build),'-DCMAKE_BUILD_TYPE=Release','-DMAB_ENABLE_CUDA=ON',
        '-DMAB_ENABLE_CUDA_SORT=ON','-DMAB_ENABLE_CPU_GPU_COMPARISON=ON','-DMAB_ENABLE_OPENMP=ON',
        '-DMAB_ENABLE_SANITIZERS=OFF','-DBUILD_TESTING=ON','-DCMAKE_CUDA_ARCHITECTURES=75',
        '-DCMAKE_CXX_FLAGS=','-DCMAKE_CXX_FLAGS_RELEASE=-O3 -DNDEBUG','-DCMAKE_CUDA_FLAGS=',
        '-DCMAKE_CUDA_FLAGS_RELEASE=-O3 -DNDEBUG'])
    command('build',['cmake','--build',str(build),'--parallel','2'],1200)
    # No benchmark-framework, timing-engine or parallel-mergesort timing group.
    names=['structures','searching','baselines','environment_manifest','cuda_preflight',
        'cuda_benchmark_analysis','cuda_sort_handoff','datasets','cli','quicksort','pdqsort','timsort',
        'mergesort','radixsort','comparisons','memory','memory_unsupported','metrics_cli',
        'cpu_gpu_comparison_framework','cuda_runtime_smoke','cuda_sorting']
    result=command('ctest_non_timing',['ctest','--test-dir',str(build),'--output-on-failure','-V','-R','^('+'|'.join(names)+')$'])
    assert '0 tests failed out of 21' in result['stdout'] and '***Skipped' not in result['stdout']
    lines=result['stdout'].splitlines()
    correctness=json.loads(next(line[line.index('{'):] for line in lines if '"protocol":"cuda_sort_correctness_v2"' in line))
    assert correctness['status']=='ok' and correctness['cases']==475 and correctness['output_checks']==1900
    assert correctness['cub_version']==300001 and (correctness['compute_major'],correctness['compute_minor'])==(7,5)
    runtime=json.loads(next(line[line.index('{'):] for line in lines if '"record_kind":"cuda_runtime_probe"' in line))
    assert runtime['status']=='ok' and runtime['kernel_result']==1729
    assert runtime['devices'][0]['name']=='Tesla T4'
    save('cuda_correctness_observed.json',correctness);save('runtime_observed.json',runtime)
    metadata=snapshot(build,build/'cpu_gpu_comparison',E)
    metadata.update(record_kind='full_matrix_tooling_validation_environment',workload='non-timing correctness and synthetic tooling only',
        workload_note='No pilot, study or GPU benchmark run; no performance samples.')
    save('environment.json',metadata)
    for name in ['CMakeCache.txt','compile_commands.json']:shutil.copyfile(build/name,E/name)
    cache=(build/'CMakeCache.txt').read_text();include=Path(next(line.split('=',1)[1] for line in cache.splitlines() if line.startswith('MAB_CUB_INCLUDE_DIR:PATH=')))
    save('dependency_sha256.json',{str(p.relative_to(include)):sha(p) for directory in ['cub','thrust','cuda']
        for p in sorted((include/directory).rglob('*')) if p.is_file()})
    assert verify_source_extension(load_protocol())==source
    save('binary_sha256.json',{name:sha(build/name) for name in ['cpu_gpu_comparison','comparison_input','test_cuda_sorting','cuda_runtime_probe']})
    save('COMPLETE.json',dict(complete=True,exit_code=0,ctest_passed=21,ctest_failed=0,ctest_groups_skipped=0,
        cuda_inputs=475,cuda_output_checks=1900,pilot_run=False,study_run=False,gpu_benchmark_trials=0))
    status=0
except BaseException as error:
    save('FAILED.json',dict(complete=False,error=str(error),traceback=traceback.format_exc()))
    print(traceback.format_exc(),flush=True)
finally:
    save('SHA256.json',{str(p.relative_to(E)):sha(p) for p in sorted(E.rglob('*')) if p.is_file()})
    target=BASE/'non_timing_validation_evidence.tar.gz'
    with tarfile.open(target,'x:gz') as tar:tar.add(E,arcname='evidence')
    print('REMOTE_RESULT '+json.dumps(dict(exit_code=status,archive=str(target),sha256=sha(target))),flush=True)
if status:raise RuntimeError('Non-timing validation failed; inspect evidence')
