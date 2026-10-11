#!/usr/bin/env python3
"""Serial, exclusive experiment_pipeline_v1 orchestration; no resume or overwrite."""
import argparse
import datetime
import json
import os
from pathlib import Path
import resource
import shutil
import signal
import subprocess
import sys
import time

from capture_environment import capture
from experiment_model import (ALGORITHMS, BINARIES, FAMILIES, ROOT, PROTOCOL, load_json,
                              plan, preset, save_json, sha256, tree_hashes, validate_study)


def resource_snapshot(path):
    meminfo={}
    try:
        for line in Path('/proc/meminfo').read_text().splitlines():
            key,value=line.split(':',1);meminfo[key]=int(value.split()[0])*1024
    except (OSError,ValueError):
        pass
    cgroups=[]
    try:
        relative=next(line.split(':',2)[2] for line in Path('/proc/self/cgroup').read_text().splitlines() if line.startswith('0::'))
        mount=Path('/sys/fs/cgroup');current=mount/relative.lstrip('/')
        for parent in [current,*current.parents]:
            if parent!=mount and mount not in parent.parents:continue
            try:
                maximum=(parent/'memory.max').read_text().strip();used=int((parent/'memory.current').read_text())
                cgroups.append(dict(path=str(parent),memory_max=maximum,memory_current=used,
                                    headroom_bytes=max(0,int(maximum)-used) if maximum!='max' else None))
            except (OSError,ValueError):pass
    except (OSError,StopIteration):pass
    governors={}
    for p in sorted(Path('/sys/devices/system/cpu/cpufreq').glob('policy*/scaling_governor')):
        try:governors[str(p)]=p.read_text().strip()
        except OSError:pass
    limits={name:list(resource.getrlimit(getattr(resource,'RLIMIT_'+name))) for name in ['AS','DATA','CPU','FSIZE','STACK']}
    return dict(platform=sys.platform,logical_cpu_count=os.cpu_count(),available_memory_bytes=meminfo.get('MemAvailable'),
                total_memory_bytes=meminfo.get('MemTotal'),disk_free_bytes=shutil.disk_usage(path).free,
                cgroups=cgroups,resource_limits=limits,load_average=list(os.getloadavg()),
                affinity=sorted(os.sched_getaffinity(0)) if hasattr(os,'sched_getaffinity') else None,
                frequency_policy=governors,controls='No affinity/frequency/cache/thermal/background changes; shared machine.')


def check_resources(snapshot, estimates):
    headroom=[x['headroom_bytes'] for x in snapshot['cgroups'] if x['headroom_bytes'] is not None]
    memory=snapshot['available_memory_bytes']
    if memory is None:raise ValueError('Linux available RAM could not be established')
    if headroom:memory=min(memory,*headroom)
    if memory<estimates['required_available_memory_bytes'] or snapshot['disk_free_bytes']<estimates['required_free_disk_bytes']:
        raise ValueError('available memory/disk fails protocol resource gates')
    for name,needed in [('AS',estimates['required_available_memory_bytes']),('DATA',estimates['workspace_bytes_estimate']),('FSIZE',estimates['disk_bytes_allowance'])]:
        soft=snapshot['resource_limits'][name][0]
        if soft!=resource.RLIM_INFINITY and soft<needed:raise ValueError('finite '+name+' limit fails planning gate')


def run_child(command):
    start=datetime.datetime.now(datetime.timezone.utc).isoformat();tick=time.monotonic();proc=None
    out=err='';code=None;status='failed'
    try:
        proc=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,start_new_session=True)
        out,err=proc.communicate();code=proc.returncode
        status='successful' if code==0 else ('interrupted' if code in (-signal.SIGINT,-signal.SIGTERM) else 'failed')
    except (KeyboardInterrupt,InterruptedError):
        status='interrupted'
        if proc is not None:
            try:os.killpg(proc.pid,signal.SIGTERM)
            except ProcessLookupError:pass
            try:out,err=proc.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                try:os.killpg(proc.pid,signal.SIGKILL)
                except ProcessLookupError:pass
                out,err=proc.communicate()
            code=proc.returncode
        err+='\nParent interrupted; active child process group terminated.'
    except OSError as error:
        err=str(error)
    return dict(command=command,status=status,exit_code=code,stdout=out,stderr=err,
                started_utc=start,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                wall_seconds=time.monotonic()-tick)


def interrupted(signum, frame):
    raise KeyboardInterrupt('signal '+str(signum))


def run(study):
    raw=Path(study['raw_path']);processed=Path(study['processed_path']);figures=Path(study['figure_path'])
    for p in [raw,processed,figures]:
        if not p.parent.is_dir():raise ValueError('output root must exist: '+str(p.parent))
        if p.exists() or p.is_symlink():raise FileExistsError('existing output rejected: '+str(p))
    build=Path(study['build_directory'])
    # Validate dependencies/build before taking exclusive ownership.
    import matplotlib
    environment=capture(build,' '.join(sys.argv))
    config=study['configuration']
    registries={};executables={}
    for family in FAMILIES:
        binary=build/BINARIES[family]
        option={'sorting':'--list-sorts','search':'--list-searches','structures':'--list-structures'}[family]
        probe=subprocess.run([str(binary),option],capture_output=True,text=True)
        if probe.returncode!=0 or probe.stdout.splitlines()!=ALGORITHMS[family]:raise ValueError('registry probe failed/mismatch: '+family)
        registries[family]=dict(command=[str(binary),option],exit_code=probe.returncode,stdout=probe.stdout,stderr=probe.stderr)
        executables[family]=sha256(binary)
    snapshot=resource_snapshot(raw.parent);check_resources(snapshot,study['resources'])
    # mkdir is the concurrency arbitration; never catch-and-own another run's directory.
    raw.mkdir(exist_ok=False)
    try:
        save_json(raw/'experiment.json',study)
        save_json(raw/'preflight.json',snapshot)
        environment.update(record_kind='orchestration_environment',configuration_sha256=study['configuration_sha256'],
            executables_sha256=executables,registry_probes=registries,
            tool_sha256={p.name:sha256(p) for p in sorted((ROOT/'scripts').glob('*.py'))},matplotlib_version=matplotlib.__version__)
        save_json(raw/'environment.json',environment)
        protocol=ROOT/'docs/ORCHESTRATION_PROTOCOL_v1.md'
        with (raw/'PROTOCOL_v1.md').open('xb') as stream:stream.write(protocol.read_bytes())
        save_json(raw/'protocol.json',dict(path=str(protocol),sha256=sha256(protocol)))
        for entry in study['families']:
            family=entry['family']
            save_json(raw/(family+'_started.json'),dict(command=entry['command'],started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
            result=run_child(entry['command']);save_json(raw/(family+'_command.json'),result)
            if result['status']!='successful':
                if result['status']=='interrupted':raise InterruptedError('family interrupted: '+family)
                raise RuntimeError('family failed: '+family+' exit '+str(result['exit_code']))
        validated=validate_study(raw)
        save_json(raw/'COLLECTED.json',dict(protocol=PROTOCOL,complete=True,configuration_sha256=study['configuration_sha256'],observations=len(validated['observations'])))
        command=[sys.executable,str(ROOT/'scripts/analyze_experiment.py'),str(raw),'--output',str(processed),'--figures',str(figures)]
        result=run_child(command);save_json(raw/'analysis_command.json',result)
        if result['status']=='interrupted':raise InterruptedError('analysis interrupted')
        if result['status']!='successful':raise RuntimeError('analysis failed: '+result['stderr'])
        # Verify derived artifacts before declaring pipeline completion.
        marker=load_json(processed/'COMPLETE.json')
        files=tree_hashes(processed);files.pop('COMPLETE.json',None)
        if marker.get('protocol')!=PROTOCOL or marker.get('complete') is not True or marker.get('files_sha256')!=files or marker.get('figures_sha256')!=tree_hashes(figures):
            raise ValueError('derived completion hashes differ')
        # Hash after analysis, retaining marker provenance; summaries validate raw independently.
        save_json(raw/'final_resources.json',resource_snapshot(raw.parent))
        save_json(raw/'COMPLETE.json',dict(protocol=PROTOCOL,complete=True,configuration_sha256=study['configuration_sha256'],
            raw_sha256=tree_hashes(raw),processed_sha256=tree_hashes(processed),figures_sha256=tree_hashes(figures)))
    except (Exception,KeyboardInterrupt) as error:
        marker='INTERRUPTED.json' if isinstance(error,(InterruptedError,KeyboardInterrupt)) else 'FAILED.json'
        try:save_json(raw/marker,dict(protocol=PROTOCOL,complete=False,error=str(error)))
        except OSError:pass
        raise
    return raw


def main():
    parser=argparse.ArgumentParser(description=__doc__,allow_abbrev=False)
    parser.add_argument('--preset',choices=['smoke','full'],default='smoke')
    parser.add_argument('--config',type=Path)
    parser.add_argument('--raw-root',type=Path,default=Path('results/raw'))
    parser.add_argument('--processed-root',type=Path,default=Path('results/processed'))
    parser.add_argument('--figure-root',type=Path,default=Path('results/figures'))
    parser.add_argument('--build-dir',type=Path,default=Path('build/release'))
    parser.add_argument('--run-id',required=True)
    parser.add_argument('--dry-run',action='store_true')
    args=parser.parse_args()
    old=signal.signal(signal.SIGTERM,interrupted)
    try:
        config=load_json(args.config) if args.config else preset(args.preset)
        study=plan(config,args.run_id,args.raw_root,args.processed_root,args.figure_root,args.build_dir)
        if args.dry_run:print(json.dumps(study,indent=2,sort_keys=True,allow_nan=False));return
        print(run(study))
    except (OSError,ValueError,KeyError,TypeError,RuntimeError,ImportError,InterruptedError,KeyboardInterrupt) as error:
        parser.exit(130 if isinstance(error,(InterruptedError,KeyboardInterrupt)) else 1,'experiment failed: '+str(error)+'\n')
    finally:signal.signal(signal.SIGTERM,old)


if __name__=='__main__':main()
