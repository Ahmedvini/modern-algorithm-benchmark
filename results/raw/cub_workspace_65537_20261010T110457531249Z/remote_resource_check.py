"""One isolated N=65537 resource check; never calls a sorting benchmark."""
import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tarfile
import traceback

RUN = 'cub_workspace_65537_20261010T110457531249Z'
EXPECTED = 'a923e54fb4d8323496c2e49342775d481b12af6b84bbafb4f2611614cb777510'
BASE = Path('/content') / RUN
BASE.mkdir(exist_ok=False)
E = BASE / 'evidence'
E.mkdir()

def digest(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as stream:
        for b in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()

def save(name, value):
    with (E / name).open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')

def command(name, argv, cwd=None, timeout=600):
    start = datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        p = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        record = dict(argv=argv, cwd=str(cwd) if cwd else None, started_utc=start,
                      exit_code=p.returncode, stdout=p.stdout, stderr=p.stderr)
    except Exception as error:
        save(name+'.json', dict(argv=argv, started_utc=start, exit_code=None, error=str(error)))
        raise
    save(name+'.json', record)
    print(name, 'exit', p.returncode, flush=True)
    if p.returncode != 0:
        raise RuntimeError(name+' failed: '+p.stderr[-4000:])
    return record

status = 1
try:
    archive = Path('/content/cub_workspace_source_65537.tar.gz')
    assert digest(archive) == EXPECTED, 'remote source archive checksum differs'
    with tarfile.open(archive) as tar:
        members = tar.getmembers()
        for member in members:
            p = PurePosixPath(member.name)
            assert not p.is_absolute() and '..' not in p.parts
            assert p.parts[0] == 'modern-algorithm-benchmark'
            assert member.isfile() or member.isdir(), 'nonregular archive member'
        save('archive_members.json', dict(sha256=digest(archive), members=[m.name for m in members]))
        tar.extractall(BASE, filter='data')
    root = BASE / 'modern-algorithm-benchmark'
    os.chdir(root)
    sys.path.insert(0, str(root/'scripts'))
    from cpu_gpu_protocol import load_protocol, verify_source_extension
    from run_cpu_gpu_pilot import snapshot, environment_gate
    from analyze_cpu_gpu import validate_resources
    model = load_protocol()
    source = verify_source_extension(model)
    save('source_before.json', source)
    save('frozen_sha256.json', {p:digest(root/p) for p in [
        'docs/CPU_GPU_COMPARISON_PROTOCOL_v1.md',
        'docs/studies/cpu_gpu_comparison_v1.matrix.json',
        'docs/studies/cpu_gpu_comparison_v1.resources.csv',
        'docs/studies/cpu_gpu_comparison_v1.freeze.json']})
    command('gpu_initial', ['nvidia-smi'])
    command('gpu_processes_initial', ['nvidia-smi','--query-compute-apps=pid,process_name,used_memory','--format=csv,noheader,nounits'])
    os.environ.update(model['openmp_policy']['environment'])
    build = root/'build/resource_fresh'
    assert not build.exists()
    command('configure', ['cmake','-S','.', '-B',str(build), '-DCMAKE_BUILD_TYPE=Release',
        '-DBUILD_TESTING=OFF', '-DMAB_ENABLE_SANITIZERS=OFF', '-DMAB_ENABLE_CUDA=ON',
        '-DMAB_ENABLE_CUDA_SORT=ON', '-DMAB_ENABLE_OPENMP=ON', '-DMAB_ENABLE_CPU_GPU_COMPARISON=ON',
        '-DCMAKE_CUDA_ARCHITECTURES=75', '-DCMAKE_CXX_FLAGS=', '-DCMAKE_CXX_FLAGS_RELEASE=-O3 -DNDEBUG',
        '-DCMAKE_CUDA_FLAGS=', '-DCMAKE_CUDA_FLAGS_RELEASE=-O3 -DNDEBUG'], root)
    binary = build/'cpu_gpu_comparison'
    env = snapshot(build, binary, E)
    env.update(record_kind='cub_workspace_resource_environment', workload='N=65537 queries/allocations only',
               workload_note='No sorting, pilot, timing study or correctness suite executed.')
    env['relevant_environment'] = {k:os.environ.get(k) for k in [
        'CUDA_VISIBLE_DEVICES','CUDA_HOME','CUDA_PATH','CUDACXX','LD_LIBRARY_PATH','PATH']}
    save('environment_before_build.json', env)
    environment_gate(env)
    command('build', ['cmake','--build',str(build),'--target','cpu_gpu_comparison','--parallel','2'], root)
    described = json.loads(command('describe',[str(binary),'--describe'],root)['stdout'])
    assert described['build_type']=='Release' and described['sanitizers'] is False
    assert described['cub_version']==300001 and described['cuda_architectures']=='75'
    for key in ['configuration_flags','cuda_release_flags']:
        assert described[key].split()==['-O3','-DNDEBUG']
    assert described['global_flags']=='' and described['cuda_flags']==''
    save('build_identity.json', dict(description=described, binary_sha256=digest(binary)))
    for name in ['CMakeCache.txt','compile_commands.json']:
        shutil.copyfile(build/name, E/name)
    cache = (build/'CMakeCache.txt').read_text()
    include = next(line.split('=',1)[1] for line in cache.splitlines() if line.startswith('MAB_CUB_INCLUDE_DIR:'))
    headerroot = Path(include)
    save('installed_cccl_tree_sha256.json', {str(p.relative_to(headerroot)):digest(p)
        for directory in ['cub','thrust','cuda'] for p in sorted((headerroot/directory).rglob('*')) if p.is_file()})
    environment = snapshot(build,binary,E)
    environment.update(record_kind='cub_workspace_resource_environment', workload='N=65537 workspace diagnostic',
                       workload_note='No sorting or timed benchmark run.')
    environment['relevant_environment'] = env['relevant_environment']
    save('environment.json', environment)
    environment_gate(environment)
    result = command('resources_65537',[str(binary),'--resources','65537'],root,60)
    resources = json.loads(result['stdout'])
    validate_resources(resources,65537)
    save('workspace_queries.json',resources)
    save('acceptance.json', dict(complete=True, resource_gate_passed=True, size=65537,
        prepared_diagnostic_allocation_succeeded=True, production_parameter_diagnostic_allocation_succeeded=True,
        allocation_basis='checked cudaMalloc and checked cleanup returned before valid JSON; physical footprint not measured',
        no_sort_executed=True, no_pilot_executed=True, no_full_study_executed=True,
        host_and_disk_environment_gate_passed=True))
    command('gpu_after',['nvidia-smi','--query-gpu=name,uuid,driver_version,memory.total,memory.free,temperature.gpu,clocks.sm,clocks.mem,power.limit','--format=csv,noheader,nounits'])
    assert verify_source_extension(load_protocol()) == source
    save('COMPLETE.json',dict(complete=True,exit_code=0,size=65537,benchmark_trials=0))
    status = 0
except BaseException as error:
    save('FAILED.json',dict(complete=False,exit_code=1,error=str(error),traceback=traceback.format_exc()))
    print(traceback.format_exc(),flush=True)
finally:
    save('SHA256.json',{str(p.relative_to(E)):digest(p) for p in sorted(E.rglob('*')) if p.is_file()})
    target = BASE/'workspace_evidence.tar.gz'
    with tarfile.open(target,'x:gz') as tar:
        tar.add(E,arcname='evidence')
    print('REMOTE_RESULT '+json.dumps(dict(exit_code=status,archive=str(target),sha256=digest(target))),flush=True)
if status:
    raise RuntimeError('Resource milestone failed; inspect retained evidence')
