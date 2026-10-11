#!/usr/bin/env python3
"""Phase 6 serial orchestration using the existing timing core and Phase 5 helpers."""
import argparse
import itertools
import json
import os
from pathlib import Path
import signal
import sys
import math
from capture_environment import capture
from experiment_model import load_json,save_json,sha256,tree_hashes,canonical
from run_experiments import resource_snapshot,check_resources,run_child,interrupted
from run_matrix import numbers,DISTRIBUTIONS

ROOT=Path(__file__).resolve().parents[1]
PROTOCOL='parallel_sort_timing_v1'
POLICY={'OMP_DYNAMIC':'FALSE','OMP_THREAD_LIMIT':'8','OMP_MAX_ACTIVE_LEVELS':'1','OMP_WAIT_POLICY':'PASSIVE'}


def preset(name):
    return dict(schema_version=1,protocol=PROTOCOL,profile=name,
                sizes=[0,32767,32768,65537] if name=='smoke' else [32768,100000,1000000],
                seeds=[1729] if name=='smoke' else [1729,42,2718],
                distributions=['uniform','duplicate_heavy'] if name=='smoke' else list(DISTRIBUTIONS),
                threads=[1,2,4,8],repetitions=5,warmups=1,distinct=16,memory_limit_mib=256,
                require_requested_teams=True,validation_only=False)


def validate_config(c):
    if not isinstance(c,dict) or set(c)!=set(preset('smoke')) or type(c['schema_version']) is not int or c['schema_version']!=1 or c['protocol']!=PROTOCOL:raise ValueError('invalid config/schema/protocol')
    if c['profile'] not in ['smoke','full','custom']:raise ValueError('unknown profile')
    if c['profile']!='custom' and c!=preset(c['profile']):raise ValueError('changed preset requires custom label')
    for k,low,high in [('repetitions',1,10000),('warmups',0,1000),('distinct',1,2**32),('memory_limit_mib',1,65536)]:
        if type(c[k]) is not int or not low<=c[k]<=high:raise ValueError('invalid '+k)
    for k,low,high in [('sizes',0,1000000),('seeds',0,2**64-1),('threads',1,8)]:
        if not isinstance(c[k],list) or not c[k] or len(c[k])>100 or any(type(x) is not int or not low<=x<=high for x in c[k]) or len(set(c[k]))!=len(c[k]):raise ValueError('invalid '+k)
    if c['threads']!=sorted(c['threads']) or any(x not in [1,2,4,8] for x in c['threads']) or 1 not in c['threads']:raise ValueError('threads require ordered subset of1,2,4,8 including baseline1')
    d=c['distributions']
    if not isinstance(d,list) or not d or any(x not in DISTRIBUTIONS for x in d) or len(set(d))!=len(d):raise ValueError('invalid distributions')
    if type(c['require_requested_teams']) is not bool or type(c['validation_only']) is not bool:raise ValueError('invalid Boolean')
    count=len(c['sizes'])*len(c['seeds'])*len(d)*len(c['threads'])
    if count>256 or count*2*(c['repetitions']+c['warmups'])>100000:raise ValueError('matrix too large')
    if max(c['sizes'])*16>c['memory_limit_mib']*1024**2:raise ValueError('array planning budget exceeded')
    return c


def make_plan(config,binary,raw,processed,figures):
    c=validate_config(config);binary=Path(binary).resolve();raw=Path(raw).absolute();processed=Path(processed).absolute();figures=Path(figures).absolute()
    paths=[raw.resolve(),processed.resolve(),figures.resolve()]
    if any(a==b or a in b.parents or b in a.parents for i,a in enumerate(paths) for b in paths[i+1:]):raise ValueError('overlapping outputs')
    cases=[dict(size=n,seed=s,distribution=d,threads=p) for n,s,d,p in itertools.product(c['sizes'],c['seeds'],c['distributions'],c['threads'])]
    names=[f'run_{i:06d}' for i in range(len(cases))];commands=[]
    for name,case in zip(names,cases):
        command=[str(binary),'--output',str(raw/name),'--sort','all','--size',str(case['size']),'--seed',str(case['seed']),
                 '--distribution',case['distribution'],'--threads',str(case['threads']),'--repetitions',str(c['repetitions']),
                 '--warmups',str(c['warmups']),'--distinct',str(c['distinct']),'--memory-limit-mib',str(c['memory_limit_mib']),
                 '--run-id',raw.name+':'+name]
        if c['validation_only']:command.append('--validation-only')
        commands.append(command)
    workspace=max(c['sizes'])*16+128*1024**2;disk=len(cases)*2*1024**2+len(cases)*2*(c['repetitions']+c['warmups'])*4096+32*1024**2
    return dict(schema_version=1,protocol=PROTOCOL,configuration=c,configuration_sha256=__import__('hashlib').sha256(canonical(c).encode()).hexdigest(),
                binary=str(binary),raw_path=str(raw),processed_path=str(processed),figure_path=str(figures),cases=cases,runs=names,commands=commands,
                environment_policy=POLICY,resources=dict(workspace_bytes_estimate=workspace,required_available_memory_bytes=max(512*1024**2,workspace*2),
                disk_bytes_allowance=disk,required_free_disk_bytes=max(128*1024**2,disk*2)))


def run(plan):
    raw=Path(plan['raw_path']);processed=Path(plan['processed_path']);figures=Path(plan['figure_path']);binary=Path(plan['binary'])
    for p in [raw,processed,figures]:
        if not p.parent.is_dir():raise ValueError('output parent must exist')
        if p.exists() or p.is_symlink():raise FileExistsError('existing output rejected')
    import matplotlib
    probe=run_child([str(binary),'--list-sorts'])
    if probe['status']!='successful' or probe['stdout'].splitlines()!=['merge_sort','parallel_merge_sort']:raise ValueError('parallel registry unavailable')
    build=next((p for p in [binary.parent,*binary.parent.parents] if (p/'CMakeCache.txt').exists()),None)
    if build is None:raise ValueError('no CMake cache')
    snapshot=resource_snapshot(raw.parent);check_resources(snapshot,plan['resources'])
    if snapshot['affinity'] is not None and max(plan['configuration']['threads'])>len(snapshot['affinity']):raise ValueError('requested study teams exceed accessible CPUs')
    # Environment policy belongs to this runner/children, never library global ICVs.
    previous={k:os.environ.get(k) for k in POLICY};os.environ.update(POLICY)
    try:
        raw.mkdir(exist_ok=False)
        try:
            save_json(raw/'matrix.json',plan);save_json(raw/'preflight.json',snapshot)
            environment=capture(build,' '.join(sys.argv));runtime=run_child(['ldd',str(binary)])
            libraries={}
            if runtime['status']=='successful':
                for line in runtime['stdout'].splitlines():
                    parts=line.split()
                    if '=>' in parts and len(parts)>2 and Path(parts[2]).is_file():libraries[parts[2]]=sha256(Path(parts[2]))
            environment.update(record_kind='parallel_scaling_environment',executable_sha256=sha256(binary),runtime_linkage=runtime,runtime_library_sha256=libraries,
                omp_environment={k:v for k,v in os.environ.items() if k.startswith('OMP_') or k.startswith('GOMP_')},registry_probe=probe,
                tools_sha256={p.name:sha256(p) for p in (ROOT/'scripts').glob('*.py')},matplotlib_version=matplotlib.__version__)
            save_json(raw/'environment.json',environment)
            protocol=ROOT/'docs/OPENMP_PROTOCOL_v1.md'
            with (raw/'PROTOCOL_v1.md').open('xb') as f:f.write(protocol.read_bytes())
            save_json(raw/'protocol.json',dict(path=str(protocol),sha256=sha256(protocol)))
            for name,command in zip(plan['runs'],plan['commands']):
                save_json(raw/(name+'_started.json'),dict(command=command))
                result=run_child(command);save_json(raw/(name+'_command.json'),result)
                if result['status']=='interrupted':raise InterruptedError(name+' interrupted')
                if result['status']!='successful':raise RuntimeError(name+' failed: '+result['stderr'])
            from analyze_parallel_results import analyze
            checked,_=analyze(raw,allow_incomplete=True)
            if checked['failed_measured'] or checked['missing_measured'] or checked['failed_warmups'] or checked['missing_warmups']:raise ValueError('incomplete raw trials')
            save_json(raw/'COLLECTED.json',dict(complete=True,runs=len(plan['runs'])))
            result=run_child([sys.executable,str(ROOT/'scripts/analyze_parallel_results.py'),str(raw),'--output',str(processed),'--figures',str(figures)])
            save_json(raw/'analysis_command.json',result)
            if result['status']=='interrupted':raise InterruptedError('analysis interrupted')
            if result['status']!='successful':raise RuntimeError('analysis failed: '+result['stderr'])
            marker=load_json(processed/'COMPLETE.json');files=tree_hashes(processed);files.pop('COMPLETE.json',None)
            if marker['complete'] is not True or marker['files_sha256']!=files or marker['figures_sha256']!=tree_hashes(figures):raise ValueError('derived hash mismatch')
            save_json(raw/'final_resources.json',resource_snapshot(raw.parent))
            save_json(raw/'COMPLETE.json',dict(complete=True,runs=len(plan['runs']),raw_sha256=tree_hashes(raw),processed_sha256=tree_hashes(processed),figures_sha256=tree_hashes(figures)))
        except (Exception,KeyboardInterrupt) as error:
            marker='INTERRUPTED.json' if isinstance(error,(InterruptedError,KeyboardInterrupt)) else 'FAILED.json'
            try:save_json(raw/marker,dict(complete=False,error=str(error)))
            except OSError:pass
            raise
    finally:
        for k,v in previous.items():
            if v is None:os.environ.pop(k,None)
            else:os.environ[k]=v
    return raw


def forecast(pilot,target):
    from analyze_parallel_results import analyze
    summary,_=analyze(Path(pilot));p=load_json(Path(pilot)/'matrix.json');validate_config(target)
    cost=lambda c:sum(max(1,n)*math.log2(n+2) for n in c['sizes'])*len(c['seeds'])*len(c['distributions'])*len(c['threads'])*2*(c['warmups']+c['repetitions'])
    wall=sum(load_json(Path(pilot)/(name+'_command.json'))['wall_seconds'] for name in p['runs'])
    estimate=wall*cost(target)/cost(p['configuration'])*4
    return dict(method='overhead-inclusive child wall * Nlog2(N+2) matrix work ratio *4; plotting separate',pilot_wall_seconds=wall,forecast_seconds=estimate,
                family_wall_budget_seconds=1800,runtime_gate_passed=estimate<=1800,target_configuration=target)


def main():
    p=argparse.ArgumentParser(description=__doc__,allow_abbrev=False);p.add_argument('--preset',choices=['smoke','full'],default='smoke');p.add_argument('--config',type=Path)
    p.add_argument('--binary',type=Path,default=Path('build/release/parallel_sort_benchmark'));p.add_argument('--output',type=Path,required=True)
    p.add_argument('--processed',type=Path,required=True);p.add_argument('--figures',type=Path,required=True);p.add_argument('--dry-run',action='store_true');args=p.parse_args()
    old=signal.signal(signal.SIGTERM,interrupted)
    try:
        plan=make_plan(load_json(args.config) if args.config else preset(args.preset),args.binary,args.output,args.processed,args.figures)
        if args.dry_run:print(json.dumps(plan,indent=2,sort_keys=True,allow_nan=False))
        else:print(run(plan))
    except (OSError,ValueError,KeyError,TypeError,RuntimeError,KeyboardInterrupt) as error:p.exit(130 if isinstance(error,(KeyboardInterrupt,InterruptedError)) else 1,'parallel experiment failed: '+str(error)+'\n')
    finally:signal.signal(signal.SIGTERM,old)
if __name__=='__main__':main()
