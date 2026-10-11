#!/usr/bin/env python3
"""Run only the frozen six-dataset pilot. No full-study or resume mode exists."""
import argparse
import datetime
import hashlib
import json
import os
import platform
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path
import capture_environment
from analyze_cpu_gpu import analyze
from cpu_gpu_protocol import (BACKENDS, FREEZE, MATRIX, PROTOCOL, ROOT, canonical, dump_new,
                              load_protocol, require, sha, verify_source_extension)

def invoke(directory, name, argv, timeout=600, env=None):
    record = dict(argv=[str(x) for x in argv], cwd=str(ROOT), started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  omp_environment={k: (env or os.environ).get(k) for k in ['OMP_DYNAMIC','OMP_THREAD_LIMIT','OMP_MAX_ACTIVE_LEVELS','OMP_WAIT_POLICY','OMP_PROC_BIND']})
    dump_new(directory/(name+'_started.json'), record)
    started = time.monotonic()
    try:
        child = subprocess.Popen(record['argv'], cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 text=True, start_new_session=True)
    except OSError as error:
        record.update(exit_code=None,status='unavailable',stdout='',stderr=str(error),wall_seconds=time.monotonic()-started)
        dump_new(directory/(name+'.json'),record)
        raise RuntimeError(name+' could not launch: '+str(error)) from error
    try:
        stdout, stderr = child.communicate(timeout=timeout)
        status = 'completed'
    except (subprocess.TimeoutExpired, KeyboardInterrupt) as error:
        os.killpg(child.pid, signal.SIGTERM)
        try:stdout,stderr=child.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(child.pid,signal.SIGKILL);stdout,stderr=child.communicate()
        status = 'timeout' if isinstance(error,subprocess.TimeoutExpired) else 'interrupted'
    record.update(exit_code=child.returncode, status=status, stdout=stdout, stderr=stderr, wall_seconds=time.monotonic()-started)
    dump_new(directory/(name+'.json'),record)
    print(name, status, 'exit', child.returncode, flush=True)
    if status=='interrupted':raise KeyboardInterrupt
    if status!='completed' or child.returncode!=0:raise RuntimeError(name+' '+status+' exit '+str(child.returncode))
    return record

def read_optional(path):
    try:return Path(path).read_text().strip()
    except OSError:return None

def snapshot(build_dir, binary, output):
    env = capture_environment.capture(build_dir, 'run_cpu_gpu_pilot.py (same VM CPU/GPU)')
    env['record_kind']='cpu_gpu_pilot_environment';env['workload']='frozen six-dataset pilot'
    env['gpu_status']='see actual fresh device/workspace probes';env['affinity']=sorted(os.sched_getaffinity(0))
    env['load_average']=list(os.getloadavg());env['disk_free_bytes']=shutil.disk_usage(output).free
    paths=['/sys/fs/cgroup/cpu.max','/sys/fs/cgroup/memory.max','/sys/fs/cgroup/memory.current',
           '/sys/fs/cgroup/cpu/cpu.cfs_quota_us','/sys/fs/cgroup/cpu/cpu.cfs_period_us',
           '/sys/fs/cgroup/cpu,cpuacct/cpu.cfs_quota_us','/sys/fs/cgroup/cpu,cpuacct/cpu.cfs_period_us',
           '/sys/fs/cgroup/memory/memory.limit_in_bytes','/sys/fs/cgroup/memory/memory.usage_in_bytes']
    env['resource_files']={p:read_optional(p) for p in paths}
    env['cgroup_mountinfo']=read_optional('/proc/self/mountinfo')
    env['governors']={str(p):read_optional(p) for p in Path('/sys/devices/system/cpu').glob('cpu*/cpufreq/scaling_governor')}
    env['omp_environment']={k:os.environ.get(k) for k in ['OMP_DYNAMIC','OMP_THREAD_LIMIT','OMP_MAX_ACTIVE_LEVELS','OMP_WAIT_POLICY','OMP_PROC_BIND']}
    env['binary_linkage']=capture_environment.probe(['ldd',str(binary)])
    env['nvidia_smi']=capture_environment.probe(['nvidia-smi'])
    env['gpu_processes']=capture_environment.probe(['nvidia-smi','--query-compute-apps=pid,process_name,used_memory','--format=csv,noheader,nounits'])
    env['gpu_details']=capture_environment.probe(['nvidia-smi','--query-gpu=name,uuid,driver_version,memory.total,memory.free,temperature.gpu,clocks.sm,clocks.mem,power.limit','--format=csv,noheader,nounits'])
    env['nvcc']=capture_environment.probe(['nvcc','--version'])
    env['measurement_controls']='frequency/cache/thermal/background exclusivity not controlled; observable checks only'
    return env

def environment_gate(environment):
    require(platform.system()=='Linux', 'pilot currently requires Linux')
    require(len(environment['affinity'])>=2,'fewer than two available logical CPUs')
    require(environment['disk_free_bytes']>=1024**3,'less than1GiB free disk')
    memory={line.split(':')[0]:line.split(':')[1].strip() for line in environment['linux_meminfo'].splitlines() if ':' in line}
    require(int(memory['MemAvailable'].split()[0])*1024>=1024**3,'less than1GiB MemAvailable')
    files=environment['resource_files']
    quota=files['/sys/fs/cgroup/cpu.max']
    if quota and quota.split()[0]!='max':require(int(quota.split()[0])/int(quota.split()[1])>=2,'CPU quota below two CPUs')
    for cpu in ['/sys/fs/cgroup/cpu','/sys/fs/cgroup/cpu,cpuacct']:
        q=files[cpu+'/cpu.cfs_quota_us'];p=files[cpu+'/cpu.cfs_period_us']
        if q and p and int(q)>0:require(int(q)/int(p)>=2,'CPU quota below two CPUs')
    for maximum,current in [('/sys/fs/cgroup/memory.max','/sys/fs/cgroup/memory.current'),
                            ('/sys/fs/cgroup/memory/memory.limit_in_bytes','/sys/fs/cgroup/memory/memory.usage_in_bytes')]:
        limit=files[maximum];used=files[current]
        if limit and limit!='max' and used:require(int(limit)-int(used)>=1024**3,'less than1GiB cgroup memory headroom')
    for name in ['nvidia_smi','gpu_processes','gpu_details','nvcc']:
        require(environment[name].get('returncode')==0,'environment command unavailable: '+name)
    require(not environment['gpu_processes']['stdout'].strip(),'visible competing GPU process; stop before timing')

def input_command(tool, cell, destination):
    r=cell['recipe']
    return [str(tool),'--output',str(destination),'--size',str(r['size']),'--seed',str(r['seed']),
            '--distribution',r['distribution'],'--swaps',str(r['nearly_sorted_swaps']),'--distinct',str(r['duplicate_cardinality'])]

def worker_command(tool, cell, destination, identifiers, offset):
    r=cell['recipe']
    return [str(tool),'--output',str(destination/'measurements'),'--input',str(destination/'input.bin'),
            '--size',str(r['size']),'--seed',str(r['seed']),'--distribution',r['distribution'],
            '--swaps',str(r['nearly_sorted_swaps']),'--distinct',str(r['duplicate_cardinality']),
            '--dataset-id',cell['dataset_id'],'--base-order',','.join(cell['warmup_order'][0]),'--global-offset',str(offset)] + [
                item for key in ['input-sha256','input-fnv','matrix-sha256','build-id','environment-id','run-id']
                for item in ['--'+key,identifiers[key]]]

def validate_prerequisites(path, executable, input_tool, model):
    p=json.loads(path.read_text())
    require(p.get('protocol')==PROTOCOL and p.get('complete') is True,'prerequisite validation incomplete')
    require(p['source_sha256']==verify_source_extension(model)['current_source_sha256'],'source changed after prerequisite validation')
    require(p['binary_sha256']==sha(executable) and p['input_tool_sha256']==sha(input_tool),'binary changed after validation')
    required={'cpu_release_ctest','cpu_sanitize_ctest','cuda_ctest','cuda_correctness','preflight'}
    records=p['records']
    require(required<=set(records),'missing prerequisite commands')
    for name,record in records.items():
        command_path=path.parent/record['file']
        require(sha(command_path)==record['sha256'],'prerequisite record changed')
        result=json.loads(command_path.read_text())
        require(result['exit_code']==0 and result.get('status')=='completed','failed prerequisite '+name)
    return p

def run(args):
    model=load_protocol()
    output=args.output.absolute() # Preserve final component: mkdir rejects dangling symlinks.
    if args.dry_run:
        placeholders={k:'<'+k+'>' for k in ['input-sha256','input-fnv','build-id','environment-id']}
        placeholders.update({'matrix-sha256':sha(MATRIX),'run-id':output.name})
        print(json.dumps(dict(protocol=PROTOCOL,part='pilot',expected=model['pilot']['expected'],resources=model['resources'],
            commands=[dict(input=input_command(args.input_tool,c,output/('data_'+c['dataset_id'])),
                           worker=worker_command(args.executable,c,output/('data_'+c['dataset_id']),placeholders,i*30))
                      for i,c in enumerate(model['pilot']['cells'])]),indent=2,sort_keys=True));return 0
    require(args.prerequisites is not None,'--prerequisites is required for actual execution')
    output.mkdir();(output/'commands').mkdir()
    try:
        source=verify_source_extension(model)
        prereq=validate_prerequisites(args.prerequisites,args.executable,args.input_tool,model)
        dump_new(output/'prerequisites.json',prereq);dump_new(output/'source_review.json',source)
        policy=model['openmp_policy']['environment']
        os.environ.update(policy)
        describe=invoke(output/'commands','describe',[args.executable,'--describe'],60)
        build_description=json.loads(describe['stdout'])
        require(build_description['build_type']=='Release' and build_description['sanitizers'] is False and build_description['cub_version']==300001,'wrong build configuration')
        require(build_description['global_flags']=='' and build_description['configuration_flags'].split()==['-O3','-DNDEBUG'] and
                build_description['cuda_flags']=='' and build_description['cuda_release_flags'].split()==['-O3','-DNDEBUG'] and
                build_description['cuda_architectures']=='75','unexpected build flags')
        build_dir=Path(build_description['binary_dir'])
        build=dict(description=build_description,binary_sha256=sha(args.executable),input_tool_sha256=sha(args.input_tool),
                   compile_commands_sha256=sha(build_dir/'compile_commands.json'),source_review_sha256=sha(output/'source_review.json'))
        dump_new(output/'build.json',build)
        environment=snapshot(build_dir,args.executable,output);dump_new(output/'environment.json',environment);environment_gate(environment)
        resources={}
        for n in sorted({c['recipe']['size'] for c in model['pilot']['cells']}):
            record=invoke(output/'commands','resources_'+str(n),[args.executable,'--resources',str(n)],60)
            resources[str(n)]=json.loads(record['stdout'])
        dump_new(output/'workspace_queries.json',resources)
        meta=dict(schema_version=1,protocol=PROTOCOL,matrix_part='pilot',run_kind='performance',run_id=output.name,
                  matrix_sha256=sha(MATRIX),freeze_sha256=sha(FREEZE),build_id=hashlib.sha256(canonical(build)).hexdigest(),
                  environment_id=hashlib.sha256(canonical(environment)).hexdigest(),prerequisites_passed=True,
                  dataset_ids=[c['dataset_id'] for c in model['pilot']['cells']],
                  implementations={b:dict(source_review='source_review.json',build='build.json',cub_pin=model['dependency'] if b.startswith('gpu_') else None) for b in BACKENDS})
        dump_new(output/'run.json',meta)
        for source_file in [MATRIX,FREEZE]:shutil.copyfile(source_file,output/source_file.name)
        deadline=time.monotonic()+300
        for i,cell in enumerate(model['pilot']['cells']):
            directory=output/('data_'+cell['dataset_id'])
            invoke(output/'commands','input_'+str(i),input_command(args.input_tool,cell,directory),min(60,max(.001,deadline-time.monotonic())))
            input_meta=json.loads((directory/'input.json').read_text())
            require(all(input_meta[k]==v for k,v in cell['recipe'].items() if k!='key_type'),'generated recipe mismatch')
            dataset=dict(recipe=cell['recipe'],dataset_id=cell['dataset_id'],input_sha256=sha(directory/'input.bin'),input_hash_fnv1a64=input_meta['input_hash_fnv1a64'])
            dump_new(directory/'dataset.json',dataset)
            identifiers={'input-sha256':dataset['input_sha256'],'input-fnv':dataset['input_hash_fnv1a64'],'matrix-sha256':meta['matrix_sha256'],
                         'build-id':meta['build_id'],'environment-id':meta['environment_id'],'run-id':meta['run_id']}
            require(time.monotonic()<deadline,'pilot total timeout before dataset')
            invoke(output/'commands','dataset_'+str(i),worker_command(args.executable,cell,directory,identifiers,i*30),min(60,deadline-time.monotonic()))
        # Validate first; do not create a completion marker from subprocess exits alone.
        report=analyze(output,require_marker=False)
        dump_new(output/'COMPLETE.json',dict(complete=report['complete'],measured=report['measured'],warmups=report['warmups']))
        dump_new(output/'environment_after.json',snapshot(build_dir,args.executable,output))
        dump_new(output/'RAW_SHA256.json',{str(p.relative_to(output)):sha(p) for p in sorted(output.rglob('*')) if p.is_file()})
        print('Pilot complete:150 measured/30 warm-ups. Full study was not run.');return 0
    except KeyboardInterrupt:
        dump_new(output/'INTERRUPTED.json',dict(complete=False,error='interrupted'));return 130
    except Exception as error:
        dump_new(output/'FAILED.json',dict(complete=False,error=str(error)));print(error,file=sys.stderr);return 1

def main():
    parser=argparse.ArgumentParser(description=__doc__,allow_abbrev=False)
    parser.add_argument('--output',type=Path,required=True);parser.add_argument('--executable',type=Path,required=True)
    parser.add_argument('--input-tool',type=Path,required=True);parser.add_argument('--prerequisites',type=Path);parser.add_argument('--dry-run',action='store_true')
    args=parser.parse_args();args.executable=args.executable.absolute();args.input_tool=args.input_tool.absolute()
    try:return run(args)
    except (OSError,ValueError,KeyError) as error:print(error,file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
